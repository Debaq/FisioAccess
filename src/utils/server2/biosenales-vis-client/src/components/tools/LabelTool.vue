<template>
  <div class="label-tool">
    <div v-if="active" class="label-overlay" 
         :class="{ 'labeling': isLabeling }">
      <div class="label-status">
        <template v-if="isLabeling && selectedLabel">
          <span>Haz clic en la gráfica para colocar la etiqueta "{{ selectedLabel.text }}"</span>
        </template>
        <template v-else-if="isLabeling && !selectedLabel">
          <span>Selecciona una etiqueta primero</span>
        </template>
      </div>
      
      <!-- Previsualización de etiqueta flotante (sigue al cursor) -->
      <div 
        v-if="isLabeling && selectedLabel && mousePosition.x" 
        class="label-preview"
        :style="{
          left: `${mousePosition.x}px`,
          top: `${mousePosition.y}px`,
          color: selectedLabel.color
        }"
      >
        {{ selectedLabel.text }}
      </div>
    </div>
    
    <!-- Modal de edición de etiqueta -->
    <div v-if="showEditModal" class="label-edit-modal">
      <div class="modal-content">
        <h3>Editar Etiqueta</h3>
        
        <div class="form-group">
          <label for="edit-label-text">Texto</label>
          <input 
            id="edit-label-text" 
            v-model="editLabelText" 
            type="text" 
            placeholder="Texto de la etiqueta"
          />
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="edit-label-color">Color</label>
            <input 
              id="edit-label-color" 
              v-model="editLabelColor" 
              type="color"
            />
          </div>
          
          <div class="form-group">
            <label for="edit-label-icon">Icono</label>
            <select id="edit-label-icon" v-model="editLabelIcon">
              <option value="circle">Círculo</option>
              <option value="triangle">Triángulo</option>
              <option value="square">Cuadrado</option>
            </select>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="saveEditLabel" class="btn btn-primary">Guardar</button>
          <button @click="cancelEditLabel" class="btn btn-secondary">Cancelar</button>
          <button @click="deleteLabel" class="btn btn-danger">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { addLabel } from '@/utils/d3-helpers';

export default {
  name: 'LabelTool',
  props: {
    active: {
      type: Boolean,
      default: false
    },
    chartRefs: {
      type: Object,
      default: () => ({})
    },
    selectedLabel: {
      type: Object,
      default: null
    },
    labels: {
      type: Array,
      default: () => []
    },
    currentSignalId: {
      type: String,
      default: ''
    }
  },
  
  emits: [
    'label-added', 
    'label-updated', 
    'label-deleted', 
    'labeling-cancel'
  ],
  
  setup(props, { emit }) {
    // Estado de etiquetado
    const isLabeling = ref(false);
    const mousePosition = ref({ x: 0, y: 0 });
    
    // Estado para edición de etiqueta
    const showEditModal = ref(false);
    const editLabelId = ref(null);
    const editLabelText = ref('');
    const editLabelColor = ref('#4caf50');
    const editLabelIcon = ref('circle');
    const editLabelPosition = ref(null);
    const editLabelValue = ref(null);
    const editLabelSignalId = ref('');
    
    // Referencias a elementos de etiqueta en el DOM
    const labelElements = ref({});
    
    // Iniciar etiquetado
    const startLabeling = () => {
      isLabeling.value = true;
    };
    
    // Cancelar etiquetado
    const cancelLabeling = () => {
      isLabeling.value = false;
      emit('labeling-cancel');
    };
    
    // Manejar clic en gráfica para añadir etiqueta
    const handleChartClick = (event) => {
      if (!isLabeling.value || !props.active || !props.selectedLabel) return;
      
      const chartContainer = event.currentTarget;
      const chart = findChartForContainer(chartContainer);
      
      if (!chart) return;
      
      // Obtener punto de datos correspondiente
      const { xScale, yScale } = chart;
      const [x, y] = d3.pointer(event);
      const dataPosition = xScale.invert(x);
      const dataValue = yScale.invert(y);
      
      // Crear nueva etiqueta
      const newLabel = {
        id: `label-${Date.now()}`,
        text: props.selectedLabel.text,
        color: props.selectedLabel.color,
        icon: props.selectedLabel.icon || 'circle',
        position: dataPosition,
        value: dataValue,
        signalId: props.currentSignalId
      };
      
      // Añadir etiqueta visualmente
      const labelElement = addLabel(chart, {
        id: newLabel.id,
        text: newLabel.text,
        color: newLabel.color,
        icon: newLabel.icon,
        position: newLabel.position,
        value: newLabel.value
      });
      
      // Guardar referencia al elemento
      if (labelElement) {
        labelElements.value[newLabel.id] = {
          element: labelElement,
          chartId: chart.id
        };
        
        // Hacer clickeable para editar
        labelElement.on('click', () => openEditLabel(newLabel));
      }
      
      // Emitir evento
      emit('label-added', newLabel);
      
      // Seguir en modo etiquetado para añadir más etiquetas
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
    
    // Seguimiento del cursor para preview de etiqueta
    const handleMouseMove = (event) => {
      if (!isLabeling.value || !props.active || !props.selectedLabel) return;
      
      mousePosition.value = {
        x: event.pageX + 15, // Offset para no tapar el cursor
        y: event.pageY + 15
      };
    };
    
    // Abrir modal para editar etiqueta
    const openEditLabel = (label) => {
      // Solo permitir edición cuando la herramienta está activa
      if (!props.active) return;
      
      editLabelId.value = label.id;
      editLabelText.value = label.text;
      editLabelColor.value = label.color;
      editLabelIcon.value = label.icon || 'circle';
      editLabelPosition.value = label.position;
      editLabelValue.value = label.value;
      editLabelSignalId.value = label.signalId || props.currentSignalId;
      
      showEditModal.value = true;
    };
    
    // Guardar cambios en etiqueta
    const saveEditLabel = () => {
      if (!editLabelId.value) return;
      
      const updatedLabel = {
        id: editLabelId.value,
        text: editLabelText.value,
        color: editLabelColor.value,
        icon: editLabelIcon.value,
        position: editLabelPosition.value,
        value: editLabelValue.value,
        signalId: editLabelSignalId.value
      };
      
      // Emitir evento de actualización
      emit('label-updated', updatedLabel);
      
      // Actualizar visualmente (reimplementar la etiqueta)
      updateLabelVisual(updatedLabel);
      
      // Cerrar modal
      showEditModal.value = false;
    };
    
    // Actualizar visual de etiqueta
    const updateLabelVisual = (label) => {
      const labelRef = labelElements.value[label.id];
      if (!labelRef) return;
      
      // Obtener chart
      const chart = props.chartRefs[labelRef.chartId];
      if (!chart) return;
      
      // Eliminar etiqueta anterior
      if (labelRef.element) {
        labelRef.element.remove();
      }
      
      // Añadir etiqueta actualizada
      const updatedElement = addLabel(chart, {
        id: label.id,
        text: label.text,
        color: label.color,
        icon: label.icon,
        position: label.position,
        value: label.value
      });
      
      // Actualizar referencia
      if (updatedElement) {
        labelElements.value[label.id] = {
          element: updatedElement,
          chartId: labelRef.chartId
        };
        
        // Hacer clickeable para editar
        updatedElement.on('click', () => openEditLabel(label));
      }
    };
    
    // Cancelar edición
    const cancelEditLabel = () => {
      showEditModal.value = false;
    };
    
    // Eliminar etiqueta
    const deleteLabel = () => {
      if (!editLabelId.value) return;
      
      // Eliminar visualmente
      const labelRef = labelElements.value[editLabelId.value];
      if (labelRef && labelRef.element) {
        labelRef.element.remove();
      }
      
      // Eliminar de referencias
      delete labelElements.value[editLabelId.value];
      
      // Emitir evento
      emit('label-deleted', editLabelId.value);
      
      // Cerrar modal
      showEditModal.value = false;
    };
    
    // Observar cambios en props
    watch(() => props.active, (newActive) => {
      if (newActive) {
        startLabeling();
      } else {
        cancelLabeling();
      }
    });
    
    // Monitorear tecla Escape para cancelar
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        if (showEditModal.value) {
          cancelEditLabel();
        } else if (isLabeling.value) {
          cancelLabeling();
        }
      }
    };
    
    // Renderizar etiquetas existentes
    const renderExistingLabels = () => {
      // Limpiar elementos existentes
      for (const labelId in labelElements.value) {
        const labelRef = labelElements.value[labelId];
        if (labelRef && labelRef.element) {
          labelRef.element.remove();
        }
      }
      
      labelElements.value = {};
      
      // Renderizar labels desde props
      for (const label of props.labels) {
        // Encontrar el chart apropiado
        let targetChart = null;
        
        // Si la etiqueta tiene un signalId, buscar el chart correspondiente
        if (label.signalId) {
          targetChart = props.chartRefs[label.signalId];
        } 
        
        // Si no se encuentra, usar el primer chart disponible
        if (!targetChart) {
          for (const chartId in props.chartRefs) {
            targetChart = props.chartRefs[chartId];
            break;
          }
        }
        
        if (targetChart) {
          // Añadir etiqueta visualmente
          const labelElement = addLabel(targetChart, {
            id: label.id,
            text: label.text,
            color: label.color,
            icon: label.icon,
            position: label.position,
            value: label.value
          });
          
          // Guardar referencia al elemento
          if (labelElement) {
            labelElements.value[label.id] = {
              element: labelElement,
              chartId: label.signalId || Object.keys(props.chartRefs)[0]
            };
            
            // Hacer clickeable para editar
            labelElement.on('click', () => openEditLabel(label));
          }
        }
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
      
      // Listener para seguimiento del cursor
      document.addEventListener('mousemove', handleMouseMove);
      
      // Listener para tecla Escape
      document.addEventListener('keydown', handleKeyDown);
      
      // Iniciar etiquetado si herramienta está activa
      if (props.active) {
        startLabeling();
      }
      
      // Renderizar etiquetas existentes
      renderExistingLabels();
    });
    
    // Actualizar etiquetas cuando cambien en props
    watch(() => props.labels, () => {
      renderExistingLabels();
    }, { deep: true });
    
    // Actualizar etiquetas cuando cambien los charts
    watch(() => props.chartRefs, () => {
      renderExistingLabels();
    }, { deep: true });
    
    // Limpiar listeners al desmontar
    onUnmounted(() => {
      for (const chartId in props.chartRefs) {
        const chart = props.chartRefs[chartId];
        if (chart && chart.container) {
          chart.container.removeEventListener('click', handleChartClick);
        }
      }
      
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('keydown', handleKeyDown);
    });
    
    return {
      isLabeling,
      mousePosition,
      showEditModal,
      editLabelText,
      editLabelColor,
      editLabelIcon,
      saveEditLabel,
      cancelEditLabel,
      deleteLabel
    };
  }
}
</script>

<style scoped>
.label-tool {
  width: 100%;
  height: 100%;
  position: relative;
}

.label-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 100;
  pointer-events: none;
}

.label-status {
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

.label-preview {
  position: absolute;
  padding: 5px 10px;
  background-color: white;
  border-radius: 3px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  font-size: 12px;
  white-space: nowrap;
  z-index: 102;
  pointer-events: none;
}

/* Cursor específico para la herramienta de etiquetado */
:global(.labeling .chart-container) {
  cursor: crosshair !important;
}

/* Modal de edición */
.label-edit-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #555;
}

.form-group input[type="text"],
.form-group select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input[type="color"] {
  padding: 2px;
  width: 100%;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
}

.btn-primary:hover {
  background-color: #388e3c;
}

.btn-secondary {
  background-color: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #c0c0c0;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .modal-actions .btn {
    width: 100%;
  }
}
</style>
