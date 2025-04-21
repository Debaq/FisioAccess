<template>
  <div class="measure-tool">
    <div v-if="active" class="measure-overlay" 
         :class="{ 'measuring': isMeasuring }">
      <div class="measure-status">
        <span v-if="isMeasuring && !pointA">Selecciona el primer punto</span>
        <span v-if="isMeasuring && pointA && !pointB">Selecciona el segundo punto</span>
        <span v-if="isMeasuring && pointA && pointB" class="measure-result">
          <template v-if="measureType === 'time' || measureType === 'both'">
            Tiempo: {{ formatValue(timeValue) }} {{ timeUnit }}
          </template>
          <template v-if="measureType === 'amplitude' || measureType === 'both'">
            <template v-if="measureType === 'both'"> | </template>
            Amplitud: {{ formatValue(amplitudeValue) }} {{ amplitudeUnit }}
          </template>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { addMeasurement } from '@/utils/d3-helpers';

export default {
  name: 'MeasureTool',
  props: {
    active: {
      type: Boolean,
      default: false
    },
    chartRefs: {
      type: Object,
      default: () => ({})
    },
    measureType: {
      type: String,
      default: 'both', // 'time', 'amplitude', 'both'
    },
    timeUnit: {
      type: String,
      default: 'ms'
    },
    amplitudeUnit: {
      type: String,
      default: 'mV'
    },
    currentSignalId: {
      type: String,
      default: ''
    }
  },
  
  emits: ['measurement-complete', 'measurement-cancel'],
  
  setup(props, { emit }) {
    // Estado de la medición
    const isMeasuring = ref(false);
    const pointA = ref(null);
    const pointB = ref(null);
    const timeValue = ref(0);
    const amplitudeValue = ref(0);
    
    // Elementos visuales 
    const measureLine = ref(null);
    
    // Iniciar medición
    const startMeasuring = () => {
      isMeasuring.value = true;
      pointA.value = null;
      pointB.value = null;
      timeValue.value = 0;
      amplitudeValue.value = 0;
    };
    
    // Cancelar medición
    const cancelMeasuring = () => {
      isMeasuring.value = false;
      pointA.value = null;
      pointB.value = null;
      // Eliminar la línea visual si existe
      if (measureLine.value) {
        measureLine.value.remove();
        measureLine.value = null;
      }
      
      emit('measurement-cancel');
    };
    
    // Completar medición
    const completeMeasuring = () => {
      if (!pointA.value || !pointB.value) return;
      
      const measurementData = {
        id: `measurement-${Date.now()}`,
        type: props.measureType,
        pointA: pointA.value.dataX,
        pointB: pointB.value.dataX,
        valueA: pointA.value.dataY,
        valueB: pointB.value.dataY,
        timeValue: timeValue.value,
        amplitudeValue: amplitudeValue.value,
        timeUnit: props.timeUnit,
        amplitudeUnit: props.amplitudeUnit,
        signalId: props.currentSignalId
      };
      
      // Emitir evento con los datos de la medición
      emit('measurement-complete', measurementData);
      
      // Reiniciar para la siguiente medición
      isMeasuring.value = false;
      pointA.value = null;
      pointB.value = null;
      measureLine.value = null;
    };
    
    // Calcular valores de medición
    const calculateMeasurement = () => {
      if (!pointA.value || !pointB.value) return;
      
      // Calcular delta de tiempo
      timeValue.value = Math.abs(pointB.value.dataX - pointA.value.dataX);
      
      // Calcular delta de amplitud
      amplitudeValue.value = Math.abs(pointB.value.dataY - pointA.value.dataY);
    };
    
    // Manejar clic en gráfica
    const handleChartClick = (event) => {
      if (!isMeasuring.value || !props.active) return;
      
      const chartContainer = event.currentTarget;
      const chart = findChartForContainer(chartContainer);
      
      if (!chart) return;
      
      // Obtener punto de datos correspondiente
      const { xScale, yScale } = chart;
      const [x, y] = d3.pointer(event);
      const dataX = xScale.invert(x);
      const dataY = yScale.invert(y);
      
      // Guardar punto
      if (!pointA.value) {
        pointA.value = { x, y, dataX, dataY, chartId: chart.id };
      } else if (!pointB.value) {
        // Solo aceptar segundo punto en la misma gráfica
        if (chart.id !== pointA.value.chartId) return;
        
        pointB.value = { x, y, dataX, dataY, chartId: chart.id };
        
        // Dibujar medición en la gráfica
        renderMeasurement(chart);
        
        // Calcular valores
        calculateMeasurement();
        
        // Completar medición automáticamente
        completeMeasuring();
      }
    };
    
    // Encontrar referencia al chart basado en el contenedor
    const findChartForContainer = (container) => {
      for (const [id, chart] of Object.entries(props.chartRefs)) {
        if (chart.container === container) {
          return { ...chart, id };
        }
      }
      return null;
    };
    
    // Renderizar medición visualmente
    const renderMeasurement = (chart) => {
      if (!pointA.value || !pointB.value) return;
      
      // Usar función de D3 helpers para añadir medición
      measureLine.value = addMeasurement(chart, {
        pointA: pointA.value.dataX,
        valueA: pointA.value.dataY,
        pointB: pointB.value.dataX,
        valueB: pointB.value.dataY,
        timeUnit: props.timeUnit,
        amplitudeUnit: props.amplitudeUnit
      });
    };
    
    // Formatear valor con 2 decimales
    const formatValue = (value) => {
      return Number(value).toFixed(2);
    };
    
    // Observar cambios en props
    watch(() => props.active, (newActive) => {
      if (newActive) {
        startMeasuring();
      } else {
        cancelMeasuring();
      }
    });
    
    // Monitorear tecla Escape para cancelar
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isMeasuring.value) {
        cancelMeasuring();
      }
    };
    
    // Añadir listeners al montar componente
    onMounted(() => {
      // Añadir listener para clics en gráficas
      for (const chartId in props.chartRefs) {
        const chart = props.chartRefs[chartId];
        if (chart && chart.container) {
          chart.container.addEventListener('click', handleChartClick);
        }
      }
      
      // Listener para tecla Escape
      document.addEventListener('keydown', handleKeyDown);
      
      // Iniciar medición si herramienta está activa
      if (props.active) {
        startMeasuring();
      }
    });
    
    // Limpiar listeners al desmontar
    onUnmounted(() => {
      for (const chartId in props.chartRefs) {
        const chart = props.chartRefs[chartId];
        if (chart && chart.container) {
          chart.container.removeEventListener('click', handleChartClick);
        }
      }
      
      document.removeEventListener('keydown', handleKeyDown);
    });
    
    return {
      isMeasuring,
      pointA,
      pointB,
      timeValue,
      amplitudeValue,
      formatValue,
      startMeasuring,
      cancelMeasuring
    };
  }
}
</script>

<style scoped>
.measure-tool {
  width: 100%;
  height: 100%;
  position: relative;
}

.measure-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 100;
  pointer-events: none;
}

.measure-overlay.measuring {
  cursor: crosshair;
}

.measure-status {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 101;
}

.measure-result {
  font-weight: bold;
}

/* Cursor específico para la herramienta de medición */
:global(.measuring .chart-container) {
  cursor: crosshair !important;
}

:global(.measure-point) {
  fill: #ff6384;
  r: 4;
}

:global(.measure-line) {
  stroke: #36a2eb;
  stroke-width: 2;
  stroke-dasharray: 5,5;
}

:global(.measure-label) {
  font-size: 11px;
  font-weight: bold;
}
</style>
