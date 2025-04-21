import { reactive, readonly, computed, ref } from 'vue'
import { useSocket } from '@/composables/useSocket'
import { useSignalProcessing } from '@/composables/useSignalProcessing'

/**
 * Crea el store para gestión de señales biológicas
 * @returns {Object} Store de señales con estado y métodos
 */
export function createSignalsStore() {
  // Obtener composables necesarios
  const { onDataUpdate, addToolData } = useSocket()
  const { 
    processSignal, 
    applyMovingAverage, 
    applyHighPassFilter, 
    applyLowPassFilter
  } = useSignalProcessing()

  // Referencia al módulo de sesión (será configurado después)
  const sessionStore = ref(null)

  // Estado de las señales
  const state = reactive({
    signals: {},                // Todas las señales disponibles
    activeSignalId: '',         // ID de la señal activa/seleccionada
    visibilityMap: {},          // Mapa de visibilidad por señal { signalId: boolean }
    mainPanelSignals: [],       // IDs de señales en panel principal
    secondaryPanelSignals: [],  // IDs de señales en panel secundario
    
    // Herramientas
    tools: {
      enabled: ['cursors', 'labels', 'draw', 'measure'],
      cursors: { 
        visible: false, 
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
    },
    
    // Estado de procesamiento
    processing: false,
    processingError: null,
    
    // Buffer de datos para modo de reproducción
    dataBuffer: {},
    bufferSize: 10000,  // Tamaño máximo del buffer (ms)
    
    // Filtros aplicados por señal
    filters: {}  // { signalId: { filterType: filterParams } }
  })

  // Señales visibles (computado)
  const visibleSignals = computed(() => {
    const result = {}
    
    for (const [id, signal] of Object.entries(state.signals)) {
      // Si no hay mapa de visibilidad específico, mostrar por defecto
      const isVisible = state.visibilityMap[id] !== false
      
      if (isVisible) {
        result[id] = { ...signal }
      }
    }
    
    return result
  })

  // Registrar el módulo de sesión
  const registerSessionStore = (store) => {
    sessionStore.value = store
  }

  // Procesar datos recibidos del servidor
  const processIncomingData = (data) => {
    if (!data) return
    
    // Actualizar señales si vienen en los datos
    if (data.signals) {
      for (const [signalId, signalData] of Object.entries(data.signals)) {
        // Asegurarse que el signalId existe en el estado
        if (!state.signals[signalId]) {
          state.signals[signalId] = {
            name: signalData.name || `Señal ${signalId}`,
            unit: signalData.unit || '',
            color: signalData.color || getDefaultColor(signalId),
            data: [],
            timestamps: [],
            visible: true,
            yAxisRange: signalData.yAxisRange || [-1, 1],
            sampleRate: signalData.sampleRate || 250,
            displayOrder: signalData.displayOrder || Object.keys(state.signals).length
          }
          
          // Si no hay señal activa, establecer esta como activa
          if (!state.activeSignalId) {
            state.activeSignalId = signalId
          }
        }
        
        // Actualizar propiedades de la señal
        Object.assign(state.signals[signalId], {
          name: signalData.name || state.signals[signalId].name,
          unit: signalData.unit || state.signals[signalId].unit,
          color: signalData.color || state.signals[signalId].color,
          yAxisRange: signalData.yAxisRange || state.signals[signalId].yAxisRange,
          sampleRate: signalData.sampleRate || state.signals[signalId].sampleRate,
          displayOrder: signalData.displayOrder || state.signals[signalId].displayOrder
        })
        
        // Actualizar datos de la señal
        if (signalData.data && signalData.data.length > 0) {
          // Modo de tiempo real: reemplazar o añadir datos
          const mode = sessionStore.value ? 
                  sessionStore.value.state.configuration.mode : 'realtime'
                  
          if (mode === 'realtime') {
            // Añadir nuevos datos (o reemplazar todo dependiendo de la implementación)
            state.signals[signalId].data = signalData.data
            
            // Si hay timestamps, actualizarlos también
            if (signalData.timestamps) {
              state.signals[signalId].timestamps = signalData.timestamps
            }
          } else if (mode === 'playback') {
            // Modo reproducción: añadir al buffer
            if (!state.dataBuffer[signalId]) {
              state.dataBuffer[signalId] = {
                data: [],
                timestamps: []
              }
            }
            
            // Añadir datos al buffer
            state.dataBuffer[signalId].data.push(...signalData.data)
            
            // Añadir timestamps si existen
            if (signalData.timestamps) {
              state.dataBuffer[signalId].timestamps.push(...signalData.timestamps)
            }
            
            // Limitar tamaño del buffer
            trimBuffer(signalId)
          }
          
          // Aplicar filtros configurados para esta señal
          applyFilters(signalId)
        }
      }
    }
    
    // Actualizar configuración de paneles
    if (data.visualization) {
      if (data.visualization.mainPanelSignals) {
        state.mainPanelSignals = data.visualization.mainPanelSignals
      }
      
      if (data.visualization.secondaryPanelSignals) {
        state.secondaryPanelSignals = data.visualization.secondaryPanelSignals
      }
      
      if (data.visualization.signalsVisible) {
        for (const [signalId, isVisible] of Object.entries(data.visualization.signalsVisible)) {
          state.visibilityMap[signalId] = isVisible
        }
      }
    }
    
    // Actualizar herramientas
    if (data.tools) {
      Object.assign(state.tools, data.tools)
    }
  }

  // Limitar el tamaño del buffer de datos
  const trimBuffer = (signalId) => {
    if (!state.dataBuffer[signalId]) return
    
    const buffer = state.dataBuffer[signalId]
    
    // Si hay timestamps, usar estos para limitar por tiempo
    if (buffer.timestamps && buffer.timestamps.length > 0) {
      const latestTime = buffer.timestamps[buffer.timestamps.length - 1]
      const cutoffTime = latestTime - state.bufferSize
      
      // Encontrar el índice donde comienza el tiempo válido
      let cutoffIndex = 0
      for (let i = 0; i < buffer.timestamps.length; i++) {
        if (buffer.timestamps[i] >= cutoffTime) {
          cutoffIndex = i
          break
        }
      }
      
      // Recortar buffer
      if (cutoffIndex > 0) {
        buffer.data = buffer.data.slice(cutoffIndex)
        buffer.timestamps = buffer.timestamps.slice(cutoffIndex)
      }
    } 
    // Si no hay timestamps, limitar por número de muestras
    else {
      const sampleRate = state.signals[signalId].sampleRate || 250
      const maxSamples = Math.ceil(state.bufferSize * sampleRate / 1000)
      
      if (buffer.data.length > maxSamples) {
        buffer.data = buffer.data.slice(-maxSamples)
      }
    }
  }

  // Aplicar filtros configurados a una señal
  const applyFilters = (signalId) => {
    if (!state.filters[signalId] || !state.signals[signalId]) return
    
    const filters = state.filters[signalId]
    let data = [...state.signals[signalId].data]
    
    // Aplicar filtros en el orden adecuado
    if (filters.movingAverage) {
      data = applyMovingAverage(data, filters.movingAverage.windowSize || 5)
    }
    
    if (filters.highPass) {
      data = applyHighPassFilter(data, filters.highPass.cutoff || 0.1)
    }
    
    if (filters.lowPass) {
      data = applyLowPassFilter(data, filters.lowPass.cutoff || 0.1)
    }
    
    // Actualizar datos filtrados
    state.signals[signalId].filteredData = data
  }

  // Configurar un filtro para una señal
  const setFilter = (signalId, filterType, filterParams) => {
    if (!state.signals[signalId]) return false
    
    // Inicializar objeto de filtros para esta señal si no existe
    if (!state.filters[signalId]) {
      state.filters[signalId] = {}
    }
    
    // Actualizar configuración del filtro
    state.filters[signalId][filterType] = filterParams
    
    // Aplicar filtro inmediatamente
    applyFilters(signalId)
    
    return true
  }

  // Eliminar un filtro
  const removeFilter = (signalId, filterType) => {
    if (!state.filters[signalId]) return false
    
    // Eliminar filtro
    delete state.filters[signalId][filterType]
    
    // Si no hay más filtros, eliminar el objeto de filtros
    if (Object.keys(state.filters[signalId]).length === 0) {
      delete state.filters[signalId]
      
      // Eliminar datos filtrados
      if (state.signals[signalId]) {
        delete state.signals[signalId].filteredData
      }
    } else {
      // Volver a aplicar filtros restantes
      applyFilters(signalId)
    }
    
    return true
  }

  // Establecer señal activa
  const setActiveSignal = (signalId) => {
    if (state.signals[signalId]) {
      state.activeSignalId = signalId
      return true
    }
    return false
  }

  // Mostrar/ocultar una señal
  const toggleSignalVisibility = (signalId, isVisible = null) => {
    if (!state.signals[signalId]) return false
    
    const newVisibility = isVisible !== null ? isVisible : !state.visibilityMap[signalId]
    state.visibilityMap[signalId] = newVisibility
    
    return true
  }

  // Cambiar el orden de visualización de una señal
  const setSignalOrder = (signalId, order) => {
    if (!state.signals[signalId]) return false
    
    state.signals[signalId].displayOrder = order
    return true
  }

  // Configurar señales para paneles
  const setPanelSignals = (panelType, signalIds) => {
    if (panelType === 'main') {
      state.mainPanelSignals = signalIds
    } else if (panelType === 'secondary') {
      state.secondaryPanelSignals = signalIds
    } else {
      return false
    }
    
    return true
  }

  // Actualizar herramientas - cursores
  const updateCursors = (cursors) => {
    state.tools.cursors = { ...cursors }
    
    // Propagar a otros clientes
    addToolData('cursors', cursors)
    
    return true
  }

  // Actualizar herramientas - etiquetas
  const updateLabels = (labels) => {
    state.tools.labels = { ...labels }
    
    // Propagar a otros clientes
    addToolData('labels', labels)
    
    return true
  }

  // Añadir una nueva etiqueta personalizada
  const addCustomLabel = (label) => {
    if (!label.id) {
      label.id = `label-${Date.now()}`
    }
    
    state.tools.labels.custom.push(label)
    
    // Propagar a otros clientes
    addToolData('labels', { custom: [label] })
    
    return label.id
  }

  // Actualizar herramientas - dibujo
  const updateDrawing = (drawing) => {
    state.tools.draw = { ...drawing }
    
    // Propagar a otros clientes
    addToolData('draw', drawing)
    
    return true
  }

  // Añadir nuevo dibujo
  const addDrawingPath = (path) => {
    if (!path.id) {
      path.id = `drawing-${Date.now()}`
    }
    
    state.tools.draw.paths.push(path)
    
    // Propagar a otros clientes
    addToolData('draw', { paths: [path] })
    
    return path.id
  }

  // Actualizar herramientas - medición
  const updateMeasurement = (measurement) => {
    state.tools.measure = { ...measurement }
    
    // Propagar a otros clientes
    addToolData('measure', measurement)
    
    return true
  }

  // Añadir nueva medición
  const addMeasurement = (measurement) => {
    if (!measurement.id) {
      measurement.id = `measurement-${Date.now()}`
    }
    
    state.tools.measure.measurements.push(measurement)
    
    // Propagar a otros clientes
    addToolData('measure', { measurements: [measurement] })
    
    return measurement.id
  }

  // Obtener color por defecto basado en el índice
  const getDefaultColor = (signalId) => {
    const colors = [
      '#4caf50', // Verde
      '#2196f3', // Azul
      '#f44336', // Rojo
      '#ff9800', // Naranja
      '#9c27b0', // Púrpura
      '#795548', // Marrón
      '#607d8b', // Gris azulado
      '#cddc39', // Lima
      '#00bcd4', // Cian
      '#ff5722'  // Naranja oscuro
    ]
    
    // Usar el último dígito del ID o hash simple
    let index = 0
    if (typeof signalId === 'string') {
      // Obtener un "hash" simple del signalId
      index = signalId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    } else if (typeof signalId === 'number') {
      index = signalId
    }
    
    return colors[index % colors.length]
  }

  // Escuchar actualizaciones de datos
  const dataListener = onDataUpdate(processIncomingData)

  // Limpiar al desmontar
  const cleanup = () => {
    if (dataListener) {
      dataListener()
    }
  }

  // API pública
  return {
    // Estado de sólo lectura
    state: readonly(state),
    
    // Propiedades computadas
    visibleSignals,
    
    // Métodos
    registerSessionStore,
    processIncomingData,
    setFilter,
    removeFilter,
    setActiveSignal,
    toggleSignalVisibility,
    setSignalOrder,
    setPanelSignals,
    
    // Herramientas
    updateCursors,
    updateLabels,
    addCustomLabel,
    updateDrawing,
    addDrawingPath,
    updateMeasurement,
    addMeasurement,
    
    // Limpieza
    cleanup
  }
}
