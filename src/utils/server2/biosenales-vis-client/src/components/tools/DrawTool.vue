<template>
  <div class="draw-tool">
    <div v-if="active" class="draw-overlay" 
         :class="{ 'drawing': isDrawing }">
      <div class="draw-status">
        <template v-if="isDrawing">
          <span>Dibuja directamente sobre las gráficas</span>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { enableDrawing } from '@/utils/d3-helpers';

export default {
  name: 'DrawTool',
  props: {
    active: {
      type: Boolean,
      default: false
    },
    chartRefs: {
      type: Object,
      default: () => ({})
    },
    color: {
      type: String,
      default: '#ff0000'
    },
    strokeWidth: {
      type: Number,
      default: 2
    },
    currentSignalId: {
      type: String,
      default: ''
    }
  },
  
  emits: ['drawing-complete', 'drawing-cancel'],
  
  setup(props, { emit }) {
    // Estado del dibujo
    const isDrawing = ref(false);
    
    // Referencias a funciones para deshabilitar dibujo
    const disableDrawingFunctions = ref({});
    
    // Iniciar dibujo
    const startDrawing = () => {
      isDrawing.value = true;
      
      // Habilitar dibujo en todos los charts
      for (const chartId in props.chartRefs) {
        const chart = props.chartRefs[chartId];
        if (chart) {
          // Usar la función enableDrawing de d3-helpers
          const disableFunc = enableDrawing(chart, handleDrawingComplete);
          
          // Guardar función para deshabilitar posteriormente
          disableDrawingFunctions.value[chartId] = disableFunc;
        }
      }
    };
    
    // Detener dibujo
    const stopDrawing = () => {
      isDrawing.value = false;
      
      // Deshabilitar dibujo en todos los charts
      for (const chartId in disableDrawingFunctions.value) {
        const disableFunc = disableDrawingFunctions.value[chartId];
        if (typeof disableFunc === 'function') {
          disableFunc();
        }
      }
      
      // Limpiar referencias
      disableDrawingFunctions.value = {};
    };
    
    // Manejar la finalización de un dibujo
    const handleDrawingComplete = (drawingData) => {
      if (!drawingData || !drawingData.points || drawingData.points.length < 2) {
        return;
      }
      
      // Crear objeto con datos del dibujo
      const newDrawing = {
        id: `drawing-${Date.now()}`,
        points: drawingData.points,
        path: drawingData.path,
        color: props.color,
        strokeWidth: props.strokeWidth,
        signalId: props.currentSignalId
      };
      
      // Emitir evento con el nuevo dibujo
      emit('drawing-complete', newDrawing);
    };
    
    // Observar cambios en props
    watch(() => props.active, (newActive) => {
      if (newActive) {
        startDrawing();
      } else {
        stopDrawing();
      }
    });
    
    // Observar cambios en chartRefs
    watch(() => props.chartRefs, () => {
      // Si está activo, reiniciar el dibujo con los nuevos charts
      if (props.active) {
        stopDrawing();
        startDrawing();
      }
    }, { deep: true });
    
    // Observar cambios en color y grosor
    watch([() => props.color, () => props.strokeWidth], () => {
      // Si está activo, reiniciar para aplicar los nuevos estilos
      if (props.active) {
        stopDrawing();
        startDrawing();
      }
    });
    
    // Monitorear tecla Escape para cancelar
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isDrawing.value) {
        stopDrawing();
        emit('drawing-cancel');
      }
    };
    
    // Configurar estilos de dibujo
    const setupDrawingStyles = () => {
      // Crear un estilo global para los dibujos
      const styleId = 'drawing-tool-styles';
      let styleElement = document.getElementById(styleId);
      
      // Si ya existe, eliminar para actualizar
      if (styleElement) {
        styleElement.remove();
      }
      
      // Crear nuevo estilo
      styleElement = document.createElement('style');
      styleElement.id = styleId;
      styleElement.textContent = `
        .drawing-path {
          fill: none;
          stroke: ${props.color};
          stroke-width: ${props.strokeWidth}px;
          stroke-linecap: round;
          stroke-linejoin: round;
        }
      `;
      
      document.head.appendChild(styleElement);
    };
    
    // Al montar el componente
    onMounted(() => {
      // Configurar estilos
      setupDrawingStyles();
      
      // Listener para tecla Escape
      document.addEventListener('keydown', handleKeyDown);
      
      // Iniciar dibujo si herramienta está activa
      if (props.active) {
        startDrawing();
      }
    });
    
    // Al actualizar estilos de dibujo
    watch([() => props.color, () => props.strokeWidth], () => {
      setupDrawingStyles();
    });
    
    // Al desmontar el componente
    onUnmounted(() => {
      // Detener dibujo
      stopDrawing();
      
      // Eliminar listener
      document.removeEventListener('keydown', handleKeyDown);
      
      // Eliminar estilos
      const styleElement = document.getElementById('drawing-tool-styles');
      if (styleElement) {
        styleElement.remove();
      }
    });
    
    return {
      isDrawing
    };
  }
}
</script>

<style scoped>
.draw-tool {
  width: 100%;
  height: 100%;
  position: relative;
}

.draw-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 100;
  pointer-events: none;
}

.draw-status {
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

/* Cursor específico para modo dibujo */
:global(.drawing .chart-container) {
  cursor: crosshair !important;
}
</style>
