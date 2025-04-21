<template>
  <div class="tools-panel" :class="{ 'expanded': isExpanded, 'collapsed': !isExpanded }">
    <!-- Cabecera con título y botón de toggle -->
    <div class="tools-header">
      <h3 class="tools-title">Herramientas</h3>
      <button class="toggle-btn" @click="togglePanel">
        {{ isExpanded ? '▼' : '▲' }}
      </button>
    </div>
    
    <!-- Contenedor principal de herramientas (visible/oculto) -->
    <div class="tools-container" v-if="isExpanded">
      <!-- Barra de navegación de herramientas -->
      <div class="tools-tabs">
        <button 
          v-for="tool in availableTools" 
          :key="tool.id"
          class="tool-tab" 
          :class="{ 'active': activeTool === tool.id }"
          @click="setActiveTool(tool.id)"
          :title="tool.title"
        >
          <span class="tool-icon">{{ tool.icon }}</span>
          <span class="tool-name">{{ tool.name }}</span>
        </button>
      </div>
      
      <!-- Contenido de la herramienta activa -->
      <div class="tool-content">
        <!-- Cursores -->
        <div v-if="activeTool === 'cursors'" class="tool-section">
          <div class="tool-section-header">
            <h4>Cursores de Medición</h4>
            <div class="tool-toggle">
              <label class="switch">
                <input 
                  type="checkbox" 
                  v-model="cursorsVisible"
                  @change="updateCursors"
                >
                <span class="slider"></span>
              </label>
              <span class="toggle-label">{{ cursorsVisible ? 'Visible' : 'Oculto' }}</span>
            </div>
          </div>
          
          <div class="cursor-controls" v-if="cursorsVisible">
            <!-- Cursor A -->
            <div class="cursor-control">
              <div class="cursor-label">
                <span class="cursor-color" :style="{ backgroundColor: cursorAColor }"></span>
                <span>Cursor A</span>
              </div>
              <input 
                type="range" 
                v-model.number="cursorAPosition" 
                :min="0" 
                :max="maxPosition" 
                @change="updateCursors"
              >
              <div class="cursor-value">{{ cursorAPosition }}</div>
              <input 
                type="color" 
                v-model="cursorAColor" 
                @change="updateCursors"
                title="Cambiar color"
              >
            </div>
            
            <!-- Cursor B -->
            <div class="cursor-control">
              <div class="cursor-label">
                <span class="cursor-color" :style="{ backgroundColor: cursorBColor }"></span>
                <span>Cursor B</span>
              </div>
              <input 
                type="range" 
                v-model.number="cursorBPosition" 
                :min="0" 
                :max="maxPosition" 
                @change="updateCursors"
              >
              <div class="cursor-value">{{ cursorBPosition }}</div>
              <input 
                type="color" 
                v-model="cursorBColor" 
                @change="updateCursors"
                title="Cambiar color"
              >
            </div>
            
            <!-- Información de medición -->
            <div class="cursor-measurement">
              <div class="measurement-item">
                <span class="measurement-label">Distancia:</span>
                <span class="measurement-value">{{ cursorDistance }} unidades</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Etiquetas -->
        <div v-if="activeTool === 'labels'" class="tool-section">
          <div class="tool-section-header">
            <h4>Etiquetas</h4>
          </div>
          
          <!-- Etiquetas predefinidas -->
          <div class="predefined-labels">
            <h5>Etiquetas Predefinidas</h5>
            <div class="label-list">
              <div 
                v-for="label in predefinedLabels" 
                :key="label.id"
                class="label-item"
                @click="selectPredefinedLabel(label)"
                :class="{ 'active': selectedLabel && selectedLabel.id === label.id }"
              >
                <span class="label-color" :style="{ backgroundColor: label.color }"></span>
                <span class="label-text">{{ label.text }}</span>
              </div>
              
              <div v-if="predefinedLabels.length === 0" class="empty-state">
                No hay etiquetas predefinidas
              </div>
            </div>
          </div>
          
          <!-- Crear etiqueta personalizada -->
          <div class="custom-label">
            <h5>Crear Etiqueta</h5>
            <div class="label-form">
              <div class="form-group">
                <label for="label-text">Texto</label>
                <input 
                  id="label-text" 
                  v-model="customLabelText" 
                  type="text" 
                  placeholder="Texto de la etiqueta"
                />
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="label-color">Color</label>
                  <input 
                    id="label-color" 
                    v-model="customLabelColor" 
                    type="color"
                  />
                </div>
                
                <div class="form-group">
                  <label for="label-icon">Icono</label>
                  <select id="label-icon" v-model="customLabelIcon">
                    <option value="circle">Círculo</option>
                    <option value="triangle">Triángulo</option>
                    <option value="square">Cuadrado</option>
                  </select>
                </div>
              </div>
              
              <button 
                @click="addCustomLabel" 
                class="btn btn-primary"
                :disabled="!customLabelText"
              >
                Añadir Etiqueta
              </button>
            </div>
          </div>
          
          <div class="tool-footer">
            <p>Haz clic en la gráfica para colocar la etiqueta seleccionada.</p>
          </div>
        </div>
        
        <!-- Dibujo -->
        <div v-if="activeTool === 'draw'" class="tool-section">
          <div class="tool-section-header">
            <h4>Herramienta de Dibujo</h4>
          </div>
          
          <div class="drawing-controls">
            <div class="form-group">
              <label for="draw-color">Color</label>
              <input 
                id="draw-color" 
                v-model="drawColor" 
                type="color" 
                @change="updateDrawSettings"
              />
            </div>
            
            <div class="form-group">
              <label for="stroke-width">Grosor</label>
              <div class="input-with-value">
                <input 
                  id="stroke-width" 
                  v-model.number="strokeWidth" 
                  type="range" 
                  min="1" 
                  max="10" 
                  @change="updateDrawSettings"
                />
                <span class="input-value">{{ strokeWidth }}px</span>
              </div>
            </div>
            
            <div class="drawing-actions">
              <button @click="startDrawing" class="btn btn-primary" :class="{ 'active': isDrawing }">
                {{ isDrawing ? 'Detener Dibujo' : 'Iniciar Dibujo' }}
              </button>
              
              <button @click="clearDrawings" class="btn btn-secondary">
                Limpiar Dibujos
              </button>
            </div>
          </div>
          
          <div class="tool-footer">
            <p>Dibuja directamente sobre las gráficas para resaltar áreas de interés.</p>
          </div>
        </div>
        
        <!-- Mediciones -->
        <div v-if="activeTool === 'measure'" class="tool-section">
          <div class="tool-section-header">
            <h4>Mediciones</h4>
          </div>
          
          <div class="measurement-controls">
            <div class="form-group">
              <label>Tipo de Medición</label>
              <div class="radio-group">
                <label class="radio-label">
                  <input 
                    type="radio" 
                    v-model="measureType" 
                    value="time"
                  />
                  <span>Tiempo</span>
                </label>
                <label class="radio-label">
                  <input 
                    type="radio" 
                    v-model="measureType" 
                    value="amplitude"
                  />
                  <span>Amplitud</span>
                </label>
                <label class="radio-label">
                  <input 
                    type="radio" 
                    v-model="measureType" 
                    value="both"
                  />
                  <span>Ambos</span>
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label>Unidades</label>
              <div class="form-row">
                <div class="form-group">
                  <label for="time-unit">Tiempo</label>
                  <select id="time-unit" v-model="timeUnit">
                    <option value="ms">ms</option>
                    <option value="s">s</option>
                    <option value="min">min</option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label for="amplitude-unit">Amplitud</label>
                  <input 
                    id="amplitude-unit" 
                    v-model="amplitudeUnit" 
                    type="text" 
                    placeholder="Unidad (ej. mV)"
                  />
                </div>
              </div>
            </div>
            
            <div class="measurement-actions">
              <button @click="startMeasuring" class="btn btn-primary" :class="{ 'active': isMeasuring }">
                {{ isMeasuring ? 'Cancelar' : 'Nueva Medición' }}
              </button>
              
              <button @click="clearMeasurements" class="btn btn-secondary">
                Limpiar Mediciones
              </button>
            </div>
          </div>
          
          <!-- Lista de mediciones -->
          <div class="measurements-list" v-if="measurements.length > 0">
            <h5>Mediciones</h5>
            <div class="measurements-table">
              <div class="table-header">
                <div class="table-cell">Tipo</div>
                <div class="table-cell">Valor</div>
                <div class="table-cell">Acciones</div>
              </div>
              <div 
                v-for="(measurement, index) in measurements" 
                :key="measurement.id"
                class="table-row"
              >
                <div class="table-cell">{{ getMeasurementTypeLabel(measurement.type) }}</div>
                <div class="table-cell">{{ formatMeasurementValue(measurement) }}</div>
                <div class="table-cell">
                  <button 
                    @click="removeMeasurement(index)" 
                    class="btn-icon"
                    title="Eliminar"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="tool-footer">
            <p>Haz clic en dos puntos de la gráfica para realizar una medición.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'

export default {
  name: 'ToolsPanel',
  props: {
    enabledTools: {
      type: Array,
      default: () => ['cursors', 'labels', 'draw', 'measure']
    },
    initialTool: {
      type: String,
      default: 'cursors'
    },
    toolsState: {
      type: Object,
      default: () => ({
        cursors: { 
          visible: true, 
          cursorA: { position: 100, color: '#ff6384' },
          cursorB: { position: 300, color: '#36a2eb' }
        },
        labels: {
          predefined: [
            { id: 'p-wave', text: 'Onda P', color: '#ff6384', icon: 'triangle' },
            { id: 'qrs', text: 'Complejo QRS', color: '#36a2eb', icon: 'square' },
            { id: 't-wave', text: 'Onda T', color: '#ffcd56', icon: 'circle' }
          ],
          custom: []
        },
        draw: {
          color: '#ff0000',
          strokeWidth: 2,
          paths: []
        },
        measure: {
          type: 'both',
          timeUnit: 'ms',
          amplitudeUnit: 'mV',
          measurements: []
        }
      })
    },
    maxPosition: {
      type: Number,
      default: 1000
    }
  },
  
  emits: [
    'update:cursors', 
    'update:labels', 
    'update:draw', 
    'update:measure',
    'tool-action'
  ],
  
  setup(props, { emit }) {
    // Estado general del panel
    const isExpanded = ref(true)
    const activeTool = ref(props.initialTool)
    
    // Herramientas disponibles
    const availableTools = computed(() => {
      const allTools = [
        { id: 'cursors', name: 'Cursores', icon: '↔', title: 'Cursores de medición' },
        { id: 'labels', name: 'Etiquetas', icon: '🏷', title: 'Añadir etiquetas' },
        { id: 'draw', name: 'Dibujo', icon: '✏', title: 'Herramienta de dibujo' },
        { id: 'measure', name: 'Medición', icon: '📏', title: 'Realizar mediciones' }
      ]
      
      return allTools.filter(tool => props.enabledTools.includes(tool.id))
    })
    
    // Estado de herramientas
    
    // 1. Cursores
    const cursorsVisible = ref(props.toolsState.cursors?.visible !== false)
    const cursorAPosition = ref(props.toolsState.cursors?.cursorA?.position || 100)
    const cursorAColor = ref(props.toolsState.cursors?.cursorA?.color || '#ff6384')
    const cursorBPosition = ref(props.toolsState.cursors?.cursorB?.position || 300)
    const cursorBColor = ref(props.toolsState.cursors?.cursorB?.color || '#36a2eb')
    
    const cursorDistance = computed(() => {
      return Math.abs(cursorBPosition.value - cursorAPosition.value)
    })
    
    // 2. Etiquetas
    const predefinedLabels = ref(props.toolsState.labels?.predefined || [])
    const selectedLabel = ref(null)
    const customLabelText = ref('')
    const customLabelColor = ref('#4caf50')
    const customLabelIcon = ref('circle')
    
    // 3. Dibujo
    const drawColor = ref(props.toolsState.draw?.color || '#ff0000')
    const strokeWidth = ref(props.toolsState.draw?.strokeWidth || 2)
    const isDrawing = ref(false)
    
    // 4. Mediciones
    const measureType = ref(props.toolsState.measure?.type || 'both')
    const timeUnit = ref(props.toolsState.measure?.timeUnit || 'ms')
    const amplitudeUnit = ref(props.toolsState.measure?.amplitudeUnit || 'mV')
    const isMeasuring = ref(false)
    const measurements = ref(props.toolsState.measure?.measurements || [])
    
    // Funciones del panel
    const togglePanel = () => {
      isExpanded.value = !isExpanded.value
    }
    
    const setActiveTool = (toolId) => {
      activeTool.value = toolId
    }
    
    // Funciones de herramientas
    
    // 1. Cursores
    const updateCursors = () => {
      const cursorsData = {
        visible: cursorsVisible.value,
        cursorA: {
          position: cursorAPosition.value,
          color: cursorAColor.value
        },
        cursorB: {
          position: cursorBPosition.value,
          color: cursorBColor.value
        }
      }
      
      emit('update:cursors', cursorsData)
      emit('tool-action', { tool: 'cursors', action: 'update', data: cursorsData })
    }
    
    // 2. Etiquetas
    const selectPredefinedLabel = (label) => {
      selectedLabel.value = label
      emit('tool-action', { 
        tool: 'labels', 
        action: 'select', 
        data: label 
      })
    }
    
    const addCustomLabel = () => {
      if (!customLabelText.value) return
      
      const newLabel = {
        id: `custom-${Date.now()}`,
        text: customLabelText.value,
        color: customLabelColor.value,
        icon: customLabelIcon.value
      }
      
      // Añadir a etiquetas predefinidas para futuros usos
      const updatedLabels = [...predefinedLabels.value, newLabel]
      predefinedLabels.value = updatedLabels
      
      // Seleccionar automáticamente
      selectedLabel.value = newLabel
      
      // Emitir evento
      emit('update:labels', {
        predefined: updatedLabels,
        custom: props.toolsState.labels?.custom || []
      })
      
      emit('tool-action', {
        tool: 'labels',
        action: 'add',
        data: newLabel
      })
      
      // Limpiar formulario
      customLabelText.value = ''
    }
    
    // 3. Dibujo
    const updateDrawSettings = () => {
      emit('update:draw', {
        color: drawColor.value,
        strokeWidth: strokeWidth.value,
        paths: props.toolsState.draw?.paths || []
      })
    }
    
    const startDrawing = () => {
      isDrawing.value = !isDrawing.value
      
      emit('tool-action', {
        tool: 'draw',
        action: isDrawing.value ? 'start' : 'stop',
        data: {
          color: drawColor.value,
          strokeWidth: strokeWidth.value
        }
      })
    }
    
    const clearDrawings = () => {
      emit('tool-action', {
        tool: 'draw',
        action: 'clear',
        data: null
      })
    }
    
    // 4. Mediciones
    const startMeasuring = () => {
      isMeasuring.value = !isMeasuring.value
      
      emit('tool-action', {
        tool: 'measure',
        action: isMeasuring.value ? 'start' : 'cancel',
        data: {
          type: measureType.value,
          timeUnit: timeUnit.value,
          amplitudeUnit: amplitudeUnit.value
        }
      })
    }
    
    const clearMeasurements = () => {
      measurements.value = []
      
      emit('update:measure', {
        type: measureType.value,
        timeUnit: timeUnit.value,
        amplitudeUnit: amplitudeUnit.value,
        measurements: []
      })
      
      emit('tool-action', {
        tool: 'measure',
        action: 'clear',
        data: null
      })
    }
    
    const removeMeasurement = (index) => {
      const updatedMeasurements = [...measurements.value]
      updatedMeasurements.splice(index, 1)
      measurements.value = updatedMeasurements
      
      emit('update:measure', {
        type: measureType.value,
        timeUnit: timeUnit.value,
        amplitudeUnit: amplitudeUnit.value,
        measurements: updatedMeasurements
      })
    }
    
    // Funciones auxiliares
    const getMeasurementTypeLabel = (type) => {
      const types = {
        time: 'Tiempo',
        amplitude: 'Amplitud',
        both: 'Tiempo y Amplitud'
      }
      
      return types[type] || type
    }
    
    const formatMeasurementValue = (measurement) => {
      if (measurement.type === 'time') {
        return `${measurement.value} ${timeUnit.value}`
      } else if (measurement.type === 'amplitude') {
        return `${measurement.value} ${amplitudeUnit.value}`
      } else {
        return `Δt: ${measurement.timeValue} ${timeUnit.value}, ΔA: ${measurement.amplitudeValue} ${amplitudeUnit.value}`
      }
    }
    
    // Observar cambios en props
    watch(() => props.toolsState, (newState) => {
      // Actualizar cursores
      cursorsVisible.value = newState.cursors?.visible !== false
      cursorAPosition.value = newState.cursors?.cursorA?.position || 100
      cursorAColor.value = newState.cursors?.cursorA?.color || '#ff6384'
      cursorBPosition.value = newState.cursors?.cursorB?.position || 300
      cursorBColor.value = newState.cursors?.cursorB?.color || '#36a2eb'
      
      // Actualizar etiquetas
      predefinedLabels.value = newState.labels?.predefined || []
      
      // Actualizar dibujo
      drawColor.value = newState.draw?.color || '#ff0000'
      strokeWidth.value = newState.draw?.strokeWidth || 2
      
      // Actualizar mediciones
      measureType.value = newState.measure?.type || 'both'
      timeUnit.value = newState.measure?.timeUnit || 'ms'
      amplitudeUnit.value = newState.measure?.amplitudeUnit || 'mV'
      measurements.value = newState.measure?.measurements || []
    }, { deep: true })
    
    // Inicializar
    onMounted(() => {
      // Emitir valores iniciales
      updateCursors()
    })
    
    return {
      // Panel general
      isExpanded,
      activeTool,
      availableTools,
      togglePanel,
      setActiveTool,
      
      // Cursores
      cursorsVisible,
      cursorAPosition,
      cursorAColor,
      cursorBPosition,
      cursorBColor,
      cursorDistance,
      updateCursors,
      
      // Etiquetas
      predefinedLabels,
      selectedLabel,
      customLabelText,
      customLabelColor,
      customLabelIcon,
      selectPredefinedLabel,
      addCustomLabel,
      
      // Dibujo
      drawColor,
      strokeWidth,
      isDrawing,
      updateDrawSettings,
      startDrawing,
      clearDrawings,
      
      // Mediciones
      measureType,
      timeUnit,
      amplitudeUnit,
      isMeasuring,
      measurements,
      startMeasuring,
      clearMeasurements,
      removeMeasurement,
      getMeasurementTypeLabel,
      formatMeasurementValue
    }
  }
}
</script>

<style scoped>
.tools-panel {
  background-color: #f5f5f5;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.tools-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #ddd;
  cursor: pointer;
}

.tools-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.toggle-btn {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  color: #666;
  padding: 4px 8px;
}

.tools-container {
  padding: 15px;
}

.tools-tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 15px;
}

.tool-tab {
  padding: 8px 16px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.2s ease;
}

.tool-tab.active {
  border-bottom-color: #4caf50;
  color: #4caf50;
}

.tool-icon {
  font-size: 18px;
  margin-bottom: 4px;
}

.tool-name {
  font-size: 12px;
}

.tool-content {
  min-height: 200px;
}

.tool-section {
  padding: 10px 0;
}

.tool-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.tool-section-header h4 {
  margin: 0;
  font-size: 15px;
}

/* Toggle Switch */
.tool-toggle {
  display: flex;
  align-items: center;
}

.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
  margin-right: 8px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .3s;
  border-radius: 20px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #4caf50;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.toggle-label {
  font-size: 12px;
  color: #666;
}

/* Cursores */
.cursor-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.cursor-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cursor-label {
  width: 70px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.cursor-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.cursor-control input[type="range"] {
  flex: 1;
}

.cursor-value {
  width: 40px;
  text-align: right;
  font-size: 12px;
}

.cursor-control input[type="color"] {
  width: 24px;
  height: 24px;
  border: none;
  cursor: pointer;
}

.cursor-measurement {
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
  margin-top: 10px;
}

.measurement-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.measurement-label {
  font-weight: 500;
}

/* Etiquetas */
.predefined-labels {
  margin-bottom: 20px;
}

.predefined-labels h5,
.custom-label h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #555;
}

.label-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.label-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.label-item:hover {
  background-color: #f0f0f0;
}

.label-item.active {
  background-color: #e8f5e9;
  border-color: #4caf50;
}

.label-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.empty-state {
  font-size: 12px;
  color: #999;
  padding: 8px;
}

.label-form {
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  color: #666;
}

.form-group input[type="text"],
.form-group select,
.form-group input[type="number"] {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.form-group input[type="color"] {
  padding: 2px;
  width: 60px;
  height: 30px;
  cursor: pointer;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-row .form-group {
  flex: 1;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  background-color: #e0e0e0;
  color: #333;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #388e3c;
}

.btn-primary.active {
  background-color: #f44336;
}

.btn-secondary {
  background-color: #e0e0e0;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #c0c0c0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tool-footer {
  margin-top: 15px;
  font-size: 12px;
  color: #666;
  font-style: italic;
}

/* Dibujo */
.drawing-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-with-value {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-value {
  width: 40px;
  font-size: 12px;
}

.drawing-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

/* Mediciones */
.measurement-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.radio-group {
  display: flex;
  gap: 15px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  cursor: pointer;
}

.measurement-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.measurements-list {
  margin-top: 20px;
}

.measurements-list h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #555;
}

.measurements-table {
  width: 100%;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #ddd;
}

.table-header {
  display: flex;
  background-color: #f0f0f0;
  font-weight: 500;
  font-size: 12px;
}

.table-row {
  display: flex;
  border-top: 1px solid #ddd;
  font-size: 12px;
}

.table-cell {
  padding: 8px 10px;
}

.table-cell:nth-child(1) {
  width: 30%;
}

.table-cell:nth-child(2) {
  width: 50%;
}

.table-cell:nth-child(3) {
  width: 20%;
  text-align: center;
}

.btn-icon {
  background: none;
  border: none;
  color: #f44336;
  font-size: 18px;
  cursor: pointer;
  padding: 2px 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .cursor-control {
    flex-wrap: wrap;
  }
  
  .cursor-label {
    width: auto;
  }
  
  .tool-tab {
    padding: 8px 10px;
  }
  
  .table-cell:nth-child(1) {
    width: 25%;
  }
  
  .table-cell:nth-child(2) {
    width: 55%;
  }
  
  .table-cell:nth-child(3) {
    width: 20%;
  }
}
</style>
