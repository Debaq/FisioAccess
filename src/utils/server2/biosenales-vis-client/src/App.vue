<template>
  <div class="app-container" :class="{ 'app-warning': showOrientationWarning }">
    <!-- Advertencia de orientación para móviles -->
    <div v-if="showOrientationWarning" class="orientation-warning">
      <div class="warning-content">
        <i class="rotate-icon"></i>
        <h2>Por favor, gira tu dispositivo</h2>
        <p>Esta aplicación está optimizada para visualizarse en modo horizontal.</p>
      </div>
    </div>

    <!-- Pantalla de conexión a sesión -->
    <ConnectionManager v-if="!isConnected" @session-connected="handleSessionConnected" />

    <!-- Vista principal -->
    <div v-else class="main-view">
      <SessionManager :session="session" @config-updated="handleConfigUpdate" />
      <ToolsPanel
        :enabled-tools="enabledTools"
        :initial-tool="activeTool"
        :tools-state="tools"
        @update:cursors="updateCursors"
        @update:labels="updateLabels"
        @update:draw="updateDraw"
        @update:measure="updateMeasure"
        @tool-action="handleToolAction"
      />
      <div class="layout-container">
        <LayoutSingle v-if="layout === 'single'" :signals="signals" :tools="tools" />
        <LayoutVertical v-else-if="layout === 'vertical'" :signals="signals" :tools="tools" :main-panel-signals="mainPanelSignals" :secondary-panel-signals="secondaryPanelSignals" />
        <LayoutHorizontal v-else-if="layout === 'horizontal'" :signals="signals" :tools="tools" :main-panel-signals="mainPanelSignals" :secondary-panel-signals="secondaryPanelSignals" />
      </div>
      <MeasureTool v-if="isMeasureToolActive" :active="isMeasureToolActive" :chart-refs="chartRefs" :measure-type="tools.measure.type" :time-unit="tools.measure.timeUnit" :amplitude-unit="tools.measure.amplitudeUnit" :current-signal-id="activeSignalId" @measurement-complete="handleMeasurementComplete" @measurement-cancel="handleMeasurementCancel" />
      <LabelTool v-if="isLabelToolActive" :active="isLabelToolActive" :chart-refs="chartRefs" :selected-label="selectedLabel" :labels="allLabels" :current-signal-id="activeSignalId" @label-added="handleLabelAdded" @label-updated="handleLabelUpdated" @label-deleted="handleLabelDeleted" @labeling-cancel="handleLabelingCancel" />
      <DrawTool v-if="isDrawToolActive" :active="isDrawToolActive" :chart-refs="chartRefs" :color="tools.draw.color" :stroke-width="tools.draw.strokeWidth" :current-signal-id="activeSignalId" @drawing-complete="handleDrawingComplete" @drawing-cancel="handleDrawingCancel" />
    </div>

    <!-- Notificaciones -->
    <div v-if="notification" class="notification" :class="notification.type">
      <span class="notification-message">{{ notification.message }}</span>
      <button @click="clearNotification" class="notification-close">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, provide } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'
import { usePdfGenerator } from '@/composables/usePdfGenerator'
import { useSignalProcessing } from '@/composables/useSignalProcessing'
import { setupOrientationDetector } from '@/utils/orientation'

import ConnectionManager from '@/components/ConnectionManager.vue'
import SessionManager from '@/components/SessionManager.vue'
import ToolsPanel from '@/components/tools/ToolsPanel.vue'
import LayoutSingle from '@/components/LayoutSingle.vue'
import LayoutVertical from '@/components/LayoutVertical.vue'
import LayoutHorizontal from '@/components/LayoutHorizontal.vue'
import MeasureTool from '@/components/tools/MeasureTool.vue'
import LabelTool from '@/components/tools/LabelTool.vue'
import DrawTool from '@/components/tools/DrawTool.vue'

const isConnected = ref(false)
const showOrientationWarning = ref(false)
const session = ref({ id: '', name: 'Sin conexión', client_count: 0, configuration: { mode: 'realtime', layout: 'single', theme: 'light', autoScale: true, timeWindow: 10000, gridEnabled: true } })
const layout = ref('single')
const signals = ref({})
const tools = ref({
  enabled: ['cursors', 'labels', 'draw', 'measure'],
  cursors: { visible: false, cursorA: { position: 100, color: '#ff6384' }, cursorB: { position: 300, color: '#36a2eb' } },
  labels: { predefined: [], custom: [] },
  draw: { color: '#ff0000', strokeWidth: 2, paths: [] },
  measure: { type: 'both', timeUnit: 'ms', amplitudeUnit: 'mV', measurements: [] }
})
const notification = ref(null)
const chartRefs = ref({})
const activeTool = ref('cursors')
const selectedLabel = ref(null)
const activeSignalId = ref('')
const mainPanelSignals = ref([])
const secondaryPanelSignals = ref([])

const { connect, disconnect, send, on } = useWebSocket()

const handleSessionConnected = (sessionData) => {
  session.value = sessionData
  layout.value = sessionData.configuration?.layout || 'single'
  isConnected.value = true
  showNotification(`Conectado a sesión: ${sessionData.name}`, 'success')
}

const disconnectSession = async () => {
  send({ type: 'leave_session' })
  isConnected.value = false
  session.value = { id: '', name: 'Sin conexión', client_count: 0, configuration: { mode: 'realtime', layout: 'single', theme: 'light', autoScale: true, timeWindow: 10000, gridEnabled: true } }
  signals.value = {}
  showNotification('Desconectado de la sesión', 'info')
}

const handleToolAction = (action) => {
  const { tool, action: actionType, data } = action
  switch (tool) {
    case 'cursors':
      if (actionType === 'update') updateCursors(data)
      break
    case 'labels':
      if (actionType === 'select') selectedLabel.value = data
      else if (actionType === 'add') {
        const updatedPredefined = [...tools.value.labels.predefined, data]
        updateLabels({ predefined: updatedPredefined, custom: tools.value.labels.custom })
      }
      break
    case 'draw':
      if (actionType === 'clear') updateDraw({ ...tools.value.draw, paths: [] })
      break
    case 'measure':
      if (actionType === 'clear') updateMeasure({ ...tools.value.measure, measurements: [] })
      break
  }
}

const updateLabels = (labelsData) => {
  tools.value.labels = labelsData
  send({ type: 'tool_action', tool: 'labels', data: labelsData })
}
const updateDraw = (drawData) => {
  tools.value.draw = drawData
  send({ type: 'tool_action', tool: 'draw', data: drawData })
}
const updateMeasure = (measureData) => {
  tools.value.measure = measureData
  send({ type: 'tool_action', tool: 'measure', data: measureData })
}
const updateCursors = (cursorsData) => {
  tools.value.cursors = cursorsData
  send({ type: 'tool_action', tool: 'cursors', data: cursorsData })
}

const handleMeasurementComplete = (measurement) => {
  const updatedMeasurements = [...tools.value.measure.measurements, measurement]
  updateMeasure({ ...tools.value.measure, measurements: updatedMeasurements })
}
const handleLabelAdded = (label) => {
  const updatedCustom = [...tools.value.labels.custom, label]
  updateLabels({ ...tools.value.labels, custom: updatedCustom })
}
const handleLabelUpdated = (label) => {
  const updatedCustom = tools.value.labels.custom.map(l => l.id === label.id ? label : l)
  updateLabels({ ...tools.value.labels, custom: updatedCustom })
}
const handleLabelDeleted = (labelId) => {
  const updatedCustom = tools.value.labels.custom.filter(l => l.id !== labelId)
  updateLabels({ ...tools.value.labels, custom: updatedCustom })
}
const handleLabelingCancel = () => {
  selectedLabel.value = null
}
const handleDrawingComplete = (drawing) => {
  const updatedPaths = [...tools.value.draw.paths, drawing]
  updateDraw({ ...tools.value.draw, paths: updatedPaths })
}
const handleDrawingCancel = () => {}
const handleMeasurementCancel = () => {}

const handleConfigUpdate = (config) => {
  if (config.layout) layout.value = config.layout
  if (config.theme) {
    document.body.classList.remove('theme-light', 'theme-dark')
    document.body.classList.add(`theme-${config.theme}`)
  }
}

const showNotification = (message, type = 'info') => {
  notification.value = { message, type }
  setTimeout(() => {
    if (notification.value?.message === message) clearNotification()
  }, 3000)
}
const clearNotification = () => (notification.value = null)

const setupSocketListeners = () => {
  const removeList = []
  removeList.push(on('session_joined', (msg) => handleSessionConnected(msg.session)))
  removeList.push(on('data_update', (msg) => {
    if (msg.data?.signals) signals.value = msg.data.signals
    if (msg.data?.visualization?.layout) layout.value = msg.data.visualization.layout
    if (msg.data?.tools) tools.value = msg.data.tools
  }))
  removeList.push(on('config_updated', (msg) => handleConfigUpdate(msg.config)))
  removeList.push(on('tool_update', (msg) => {
    const { tool, data } = msg
    if (tool === 'labels') tools.value.labels.custom.push(data)
    if (tool === 'draw') tools.value.draw.paths.push(data)
    if (tool === 'measure') tools.value.measure.measurements.push(data)
  }))
  return () => removeList.forEach(fn => fn())
}

onMounted(() => {
  connect()
  send({ type: 'join_session', session_id: '', name: 'Cliente Vue' })
  setupSocketListeners()
  setupOrientationDetector((isVertical) => {
    showOrientationWarning.value = isVertical
  })
  document.body.classList.add('theme-light')
})

onUnmounted(() => {
  disconnect()
})

provide('registerChartRef', (id, chart) => chartRefs.value[id] = chart)
provide('unregisterChartRef', (id) => delete chartRefs.value[id])
provide('generatePDF', usePdfGenerator().generatePDF)

const enabledTools = computed(() => tools.value.enabled || [])
const isMeasureToolActive = computed(() => activeTool.value === 'measure')
const isLabelToolActive = computed(() => activeTool.value === 'labels' && selectedLabel.value)
const isDrawToolActive = computed(() => activeTool.value === 'draw')
const allLabels = computed(() => [...tools.value.labels.predefined, ...tools.value.labels.custom])
</script>


<style>
/* Estilos globales */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.4;
  color: #333333;
  background-color: #f5f5f5;
}

/* Temas */
body.theme-light {
  --bg-color: #f5f5f5;
  --card-bg: #ffffff;
  --text-color: #333333;
  --border-color: #e0e0e0;
  --primary-color: #4caf50;
  --secondary-color: #2196f3;
  --danger-color: #f44336;
  --warning-color: #ff9800;
  --success-color: #4caf50;
  --info-color: #2196f3;
}

body.theme-dark {
  --bg-color: #1e1e1e;
  --card-bg: #2d2d2d;
  --text-color: #e0e0e0;
  --border-color: #444444;
  --primary-color: #66bb6a;
  --secondary-color: #42a5f5;
  --danger-color: #ef5350;
  --warning-color: #ffa726;
  --success-color: #66bb6a;
  --info-color: #42a5f5;
}

/* Layout principal */
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.app-warning {
  overflow: hidden;
}

/* Vista principal */
.main-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

/* Contenedor de layout */
.layout-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  width: 100%;
}

/* Notificaciones */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  background-color: var(--info-color);
  color: white;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-width: 400px;
}

.notification.success {
  background-color: var(--success-color);
}

.notification.error {
  background-color: var(--danger-color);
}

.notification.info {
  background-color: var(--info-color);
}

.notification-message {
  flex: 1;
  margin-right: 10px;
}

.notification-close {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0 5px;
}

/* Advertencia de orientación */
.orientation-warning {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
}

.warning-content {
  padding: 20px;
}

.rotate-icon {
  display: inline-block;
  font-size: 40px;
  margin-bottom: 20px;
  animation: rotate 2s infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(90deg); }
  100% { transform: rotate(90deg); }
}

/* Media queries para responsividad */
@media (max-width: 768px) {
  .notification {
    left: 20px;
    right: 20px;
    max-width: calc(100% - 40px);
  }
}
</style>
