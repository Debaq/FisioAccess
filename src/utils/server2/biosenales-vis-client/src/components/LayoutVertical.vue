<template>
  <div class="layout-vertical">
    <div id="visualization-container" class="visualization-container">
      <!-- Panel principal (80%) -->
      <div class="main-panel">
        <div 
          v-for="(signal, signalId) in mainSignals" 
          :key="`main-${signalId}`"
          class="signal-chart main-chart"
        >
          <div class="signal-header">
            <h3>{{ signal.name }}</h3>
            <span class="signal-unit">{{ signal.unit }}</span>
          </div>
          <div :id="`chart-main-${signalId}`" class="chart-container"></div>
        </div>
        
        <!-- Mensaje cuando no hay señales -->
        <div v-if="!hasMainSignals" class="no-signals">
          <p>No hay señales disponibles para visualizar en panel principal</p>
        </div>
      </div>
      
      <!-- Panel secundario (20%) -->
      <div class="secondary-panel">
        <div 
          v-for="(signal, signalId) in secondarySignals" 
          :key="`secondary-${signalId}`"
          class="signal-chart secondary-chart"
        >
          <div class="signal-header compact">
            <h3>{{ signal.name }}</h3>
            <span class="signal-unit">{{ signal.unit }}</span>
          </div>
          <div :id="`chart-secondary-${signalId}`" class="chart-container"></div>
        </div>
        
        <!-- Mensaje cuando no hay señales -->
        <div v-if="!hasSecondarySignals" class="no-signals">
          <p>No hay señales disponibles para visualizar en panel secundario</p>
        </div>
      </div>
      
      <!-- Separador (resizable) -->
      <div class="resizer" @mousedown="startResize" :style="{ top: `${splitPosition}%` }"></div>
      
      <!-- Capa de anotaciones (etiquetas, dibujos, mediciones) -->
      <div class="annotations-layer">
        <!-- Esta capa se utiliza para overlays de D3.js -->
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import * as d3 from 'd3'
import { initializeD3Chart, updateD3Chart, updateCursors } from '@/utils/d3-helpers'

export default {
  name: 'LayoutVertical',
  props: {
    signals: {
      type: Object,
      default: () => ({})
    },
    tools: {
      type: Object,
      default: () => ({
        enabled: [],
        labels: { predefined: [], custom: [] },
        draw: { paths: [] },
        measure: { measurements: [] },
        cursors: { visible: false, cursorA: null, cursorB: null }
      })
    },
    mainPanelSignals: {
      type: Array,
      default: () => []
    },
    secondaryPanelSignals: {
      type: Array,
      default: () => []
    }
  },
  
  setup(props) {
    // Referencias a los charts
    const mainCharts = ref({})
    const secondaryCharts = ref({})
    
    // Posición del separador (por defecto 80%)
    const splitPosition = ref(80)
    const isResizing = ref(false)
    
    // Señales para panel principal y secundario
    const mainSignals = computed(() => {
      const result = {}
      
      for (const [id, signal] of Object.entries(props.signals)) {
        // Si hay una lista específica de señales para el panel principal,
        // usar solo esas. Si no, usar todas las visibles.
        if (signal.visible !== false && (
            props.mainPanelSignals.length === 0 || 
            props.mainPanelSignals.includes(id)
        )) {
          result[id] = signal
        }
      }
      return result
    })
    
    const secondarySignals = computed(() => {
      const result = {}
      
      for (const [id, signal] of Object.entries(props.signals)) {
        // Si hay una lista específica de señales para el panel secundario,
        // usar solo esas. Si no, usar ninguna.
        if (signal.visible !== false && props.secondaryPanelSignals.includes(id)) {
          result[id] = signal
        }
      }
      return result
    })
    
    // Verificar si hay señales en cada panel
    const hasMainSignals = computed(() => {
      return Object.keys(mainSignals.value).length > 0
    })
    
    const hasSecondarySignals = computed(() => {
      return Object.keys(secondarySignals.value).length > 0
    })
    
    // Inicializar gráficos D3 para panel principal
    const initializeMainCharts = () => {
      // Limpiar gráficos existentes
      for (const chartId in mainCharts.value) {
        if (mainCharts.value[chartId]) {
          d3.select(`#chart-main-${chartId}`).selectAll('*').remove()
        }
      }
      
      // Crear nuevos gráficos para señales del panel principal
      for (const [signalId, signal] of Object.entries(mainSignals.value)) {
        const container = document.getElementById(`chart-main-${signalId}`)
        if (container) {
          mainCharts.value[signalId] = initializeD3Chart(container, signal)
          
          // Actualizar cursores si están habilitados
          if (props.tools.cursors && props.tools.cursors.visible) {
            updateCursors(mainCharts.value[signalId], props.tools.cursors)
          }
        }
      }
    }
    
    // Inicializar gráficos D3 para panel secundario
    const initializeSecondaryCharts = () => {
      // Limpiar gráficos existentes
      for (const chartId in secondaryCharts.value) {
        if (secondaryCharts.value[chartId]) {
          d3.select(`#chart-secondary-${chartId}`).selectAll('*').remove()
        }
      }
      
      // Crear nuevos gráficos para señales del panel secundario
      for (const [signalId, signal] of Object.entries(secondarySignals.value)) {
        const container = document.getElementById(`chart-secondary-${signalId}`)
        if (container) {
          secondaryCharts.value[signalId] = initializeD3Chart(container, signal)
          
          // Actualizar cursores si están habilitados
          if (props.tools.cursors && props.tools.cursors.visible) {
            updateCursors(secondaryCharts.value[signalId], props.tools.cursors)
          }
        }
      }
    }
    
    // Inicializar todos los gráficos
    const initializeCharts = () => {
      initializeMainCharts()
      initializeSecondaryCharts()
    }
    
    // Actualizar gráficos con nuevos datos
    const updateCharts = () => {
      // Actualizar panel principal
      for (const [signalId, signal] of Object.entries(mainSignals.value)) {
        if (mainCharts.value[signalId]) {
          updateD3Chart(mainCharts.value[signalId], signal)
          
          // Actualizar cursores si están habilitados
          if (props.tools.cursors && props.tools.cursors.visible) {
            updateCursors(mainCharts.value[signalId], props.tools.cursors)
          }
        }
      }
      
      // Actualizar panel secundario
      for (const [signalId, signal] of Object.entries(secondarySignals.value)) {
        if (secondaryCharts.value[signalId]) {
          updateD3Chart(secondaryCharts.value[signalId], signal)
          
          // Actualizar cursores si están habilitados
          if (props.tools.cursors && props.tools.cursors.visible) {
            updateCursors(secondaryCharts.value[signalId], props.tools.cursors)
          }
        }
      }
    }
    
    // Control de redimensionamiento del separador
    const startResize = (event) => {
      isResizing.value = true
      document.addEventListener('mousemove', onResize)
      document.addEventListener('mouseup', stopResize)
      
      // Prevenir selección de texto durante resize
      event.preventDefault()
    }
    
    const onResize = (event) => {
      if (!isResizing.value) return
      
      const container = document.querySelector('.visualization-container')
      const containerRect = container.getBoundingClientRect()
      
      // Calcular posición relativa del mouse en el contenedor
      const relativePosition = ((event.clientY - containerRect.top) / containerRect.height) * 100
      
      // Limitar el rango de 10% a 90%
      splitPosition.value = Math.min(Math.max(relativePosition, 10), 90)
      
      // Actualizar tamaños de paneles
      updatePanelSizes()
    }
    
    const stopResize = () => {
      isResizing.value = false
      document.removeEventListener('mousemove', onResize)
      document.removeEventListener('mouseup', stopResize)
      
      // Reinicializar gráficos para adaptarse al nuevo tamaño
      initializeCharts()
    }
    
    const updatePanelSizes = () => {
      const mainPanel = document.querySelector('.main-panel')
      const secondaryPanel = document.querySelector('.secondary-panel')
      
      if (mainPanel && secondaryPanel) {
        mainPanel.style.height = `${splitPosition.value}%`
        secondaryPanel.style.height = `${100 - splitPosition.value}%`
        secondaryPanel.style.top = `${splitPosition.value}%`
      }
    }
    
    // Observar cambios en señales
    watch(() => props.signals, () => {
      // Comprobar si hay cambios en las señales
      const currentMainSignalIds = Object.keys(mainSignals.value)
      const currentSecondarySignalIds = Object.keys(secondarySignals.value)
      const mainChartSignalIds = Object.keys(mainCharts.value)
      const secondaryChartSignalIds = Object.keys(secondaryCharts.value)
      
      // Si hay cambios en panel principal, reinicializar
      if (
        currentMainSignalIds.length !== mainChartSignalIds.length ||
        !currentMainSignalIds.every(id => mainChartSignalIds.includes(id))
      ) {
        initializeMainCharts()
      }
      
      // Si hay cambios en panel secundario, reinicializar
      if (
        currentSecondarySignalIds.length !== secondaryChartSignalIds.length ||
        !currentSecondarySignalIds.every(id => secondaryChartSignalIds.includes(id))
      ) {
        initializeSecondaryCharts()
      }
      
      // Actualizar datos en todos los casos
      updateCharts()
    }, { deep: true })
    
    // Observar cambios en config de paneles
    watch([() => props.mainPanelSignals, () => props.secondaryPanelSignals], () => {
      initializeCharts()
    })
    
    // Observar cambios en herramientas
    watch(() => props.tools, (newTools) => {
      // Actualizar cursores cuando cambien
      if (newTools.cursors) {
        // Panel principal
        for (const chartId in mainCharts.value) {
          updateCursors(mainCharts.value[chartId], newTools.cursors)
        }
        
        // Panel secundario
        for (const chartId in secondaryCharts.value) {
          updateCursors(secondaryCharts.value[chartId], newTools.cursors)
        }
      }
      
      // Aquí se añadirán otras actualizaciones de herramientas según sea necesario
    }, { deep: true })
    
    // Inicializar al montar el componente
    onMounted(() => {
      updatePanelSizes()
      
      if (hasMainSignals.value || hasSecondarySignals.value) {
        initializeCharts()
      }
      
      // Redimensionar gráficos cuando cambie el tamaño de la ventana
      window.addEventListener('resize', initializeCharts)
    })
    
    // Limpiar al desmontar
    onUnmounted(() => {
      window.removeEventListener('resize', initializeCharts)
      
      // Remover listeners de resize si existen
      document.removeEventListener('mousemove', onResize)
      document.removeEventListener('mouseup', stopResize)
      
      // Limpiar gráficos
      for (const chartId in mainCharts.value) {
        if (mainCharts.value[chartId]) {
          d3.select(`#chart-main-${chartId}`).selectAll('*').remove()
        }
      }
      
      for (const chartId in secondaryCharts.value) {
        if (secondaryCharts.value[chartId]) {
          d3.select(`#chart-secondary-${chartId}`).selectAll('*').remove()
        }
      }
    })
    
    return {
      mainSignals,
      secondarySignals,
      hasMainSignals,
      hasSecondarySignals,
      splitPosition,
      startResize
    }
  }
}
</script>

<style scoped>
.layout-vertical {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.visualization-container {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #f9f9f9;
}

.main-panel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 80%; /* Por defecto, se actualiza con JS */
  overflow: auto;
  padding: 10px;
  z-index: 1;
}

.secondary-panel {
  position: absolute;
  top: 80%; /* Por defecto, se actualiza con JS */
  left: 0;
  width: 100%;
  height: 20%; /* Por defecto, se actualiza con JS */
  overflow: auto;
  padding: 10px;
  border-top: 1px solid #ddd;
  z-index: 1;
  background-color: #f0f0f0;
}

.resizer {
  position: absolute;
  left: 0;
  width: 100%;
  height: 10px;
  background-color: #e0e0e0;
  cursor: ns-resize;
  z-index: 10;
  border-top: 1px solid #ccc;
  border-bottom: 1px solid #ccc;
}

.resizer:hover {
  background-color: #d0d0d0;
}

.signal-chart {
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.main-chart {
  flex: 1;
  min-height: 200px;
  margin-bottom: 15px;
}

.secondary-chart {
  flex: 1;
  min-height: 100px;
  margin-bottom: 10px;
}

.signal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
}

.signal-header.compact {
  padding: 5px 10px;
}

.signal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.signal-header.compact h3 {
  font-size: 14px;
}

.signal-unit {
  font-size: 12px;
  color: #666;
}

.signal-header.compact .signal-unit {
  font-size: 10px;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 150px;
}

.secondary-chart .chart-container {
  min-height: 80px;
}

.annotations-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
}

.no-signals {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #666;
  font-size: 14px;
}

.secondary-panel .no-signals {
  font-size: 12px;
}
</style>
