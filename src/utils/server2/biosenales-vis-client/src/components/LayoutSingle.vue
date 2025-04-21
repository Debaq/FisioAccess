<template>
  <div class="layout-single">
    <div id="visualization-container" class="visualization-container">
      <!-- Panel de señales -->
      <div class="signals-panel">
        <div 
          v-for="(signal, signalId) in visibleSignals" 
          :key="signalId"
          class="signal-chart"
        >
          <div class="signal-header">
            <h3>{{ signal.name }}</h3>
            <span class="signal-unit">{{ signal.unit }}</span>
          </div>
          <div :id="`chart-${signalId}`" class="chart-container"></div>
        </div>
        
        <!-- Mensaje cuando no hay señales -->
        <div v-if="!hasVisibleSignals" class="no-signals">
          <p>No hay señales disponibles para visualizar</p>
        </div>
      </div>
      
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
  name: 'LayoutSingle',
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
    }
  },
  
  setup(props) {
    // Referencias a los charts
    const charts = ref({})
    
    // Señales visibles (filtradas)
    const visibleSignals = computed(() => {
      const result = {}
      for (const [id, signal] of Object.entries(props.signals)) {
        if (signal.visible !== false) {
          result[id] = signal
        }
      }
      return result
    })
    
    // Verificar si hay señales visibles
    const hasVisibleSignals = computed(() => {
      return Object.keys(visibleSignals.value).length > 0
    })
    
    // Inicializar gráficos D3
    const initializeCharts = () => {
      // Limpiar gráficos existentes
      for (const chartId in charts.value) {
        if (charts.value[chartId]) {
          d3.select(`#chart-${chartId}`).selectAll('*').remove()
        }
      }
      
      // Crear nuevos gráficos para señales visibles
      for (const [signalId, signal] of Object.entries(visibleSignals.value)) {
        const container = document.getElementById(`chart-${signalId}`)
        if (container) {
          charts.value[signalId] = initializeD3Chart(container, signal)
          
          // Actualizar cursores si están habilitados
          if (props.tools.cursors && props.tools.cursors.visible) {
            updateCursors(charts.value[signalId], props.tools.cursors)
          }
        }
      }
    }
    
    // Actualizar gráficos con nuevos datos
    const updateCharts = () => {
      for (const [signalId, signal] of Object.entries(visibleSignals.value)) {
        if (charts.value[signalId]) {
          updateD3Chart(charts.value[signalId], signal)
          
          // Actualizar cursores si están habilitados
          if (props.tools.cursors && props.tools.cursors.visible) {
            updateCursors(charts.value[signalId], props.tools.cursors)
          }
        }
      }
    }
    
    // Observar cambios en señales
    watch(() => props.signals, () => {
      // Comprobar si hay cambios en las señales visibles
      const currentSignalIds = Object.keys(visibleSignals.value)
      const chartSignalIds = Object.keys(charts.value)
      
      // Si hay nuevas señales o señales eliminadas, reinicializar
      if (
        currentSignalIds.length !== chartSignalIds.length ||
        !currentSignalIds.every(id => chartSignalIds.includes(id))
      ) {
        initializeCharts()
      } else {
        // Solo actualizar datos
        updateCharts()
      }
    }, { deep: true })
    
    // Observar cambios en herramientas
    watch(() => props.tools, (newTools) => {
      // Actualizar cursores cuando cambien
      if (newTools.cursors) {
        for (const chartId in charts.value) {
          updateCursors(charts.value[chartId], newTools.cursors)
        }
      }
      
      // Aquí se añadirán otras actualizaciones de herramientas según sea necesario
    }, { deep: true })
    
    // Inicializar al montar el componente
    onMounted(() => {
      if (hasVisibleSignals.value) {
        initializeCharts()
      }
      
      // Redimensionar gráficos cuando cambie el tamaño de la ventana
      window.addEventListener('resize', initializeCharts)
    })
    
    // Limpiar al desmontar
    onUnmounted(() => {
      window.removeEventListener('resize', initializeCharts)
      
      // Limpiar gráficos
      for (const chartId in charts.value) {
        if (charts.value[chartId]) {
          d3.select(`#chart-${chartId}`).selectAll('*').remove()
        }
      }
    })
    
    return {
      visibleSignals,
      hasVisibleSignals
    }
  }
}
</script>

<style scoped>
.layout-single {
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

.signals-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: auto;
  padding: 10px;
}

.signal-chart {
  flex: 1;
  min-height: 200px;
  margin-bottom: 15px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.signal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
}

.signal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.signal-unit {
  font-size: 12px;
  color: #666;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 150px;
}

.annotations-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}

.no-signals {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #666;
}
</style>
