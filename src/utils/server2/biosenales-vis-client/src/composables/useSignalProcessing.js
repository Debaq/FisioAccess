import { ref, computed } from 'vue'

/**
 * Composable para procesamiento de señales biológicas
 * Proporciona funciones para filtrar, procesar y analizar datos de bioseñales
 */
export function useSignalProcessing() {
  // Estado interno
  const processingStatus = ref('idle') // idle, processing, complete, error
  const processingError = ref(null)
  const processedSignals = ref({})
  
  /**
   * Procesa los datos de una señal aplicando filtros y transformaciones
   * @param {Array} data - Datos originales de la señal
   * @param {Object} options - Opciones de procesamiento
   * @returns {Array} - Datos procesados
   */
  const processSignal = (data, options = {}) => {
    if (!data || !Array.isArray(data)) {
      processingError.value = 'Datos de señal inválidos'
      processingStatus.value = 'error'
      return []
    }
    
    processingStatus.value = 'processing'
    processingError.value = null
    
    try {
      let processedData = [...data]
      
      // Aplicar filtro de media móvil si se solicita
      if (options.movingAverage) {
        const windowSize = options.movingAverageWindow || 5
        processedData = applyMovingAverage(processedData, windowSize)
      }
      
      // Aplicar filtro pasa-altos si se solicita
      if (options.highPass) {
        const cutoff = options.highPassCutoff || 0.1
        processedData = applyHighPassFilter(processedData, cutoff)
      }
      
      // Aplicar filtro pasa-bajos si se solicita
      if (options.lowPass) {
        const cutoff = options.lowPassCutoff || 0.1
        processedData = applyLowPassFilter(processedData, cutoff)
      }
      
      // Normalizar datos si se solicita
      if (options.normalize) {
        processedData = normalizeData(processedData)
      }
      
      // Almacenar en el estado
      processedSignals.value = {
        ...processedSignals.value,
        [options.id || 'default']: processedData
      }
      
      processingStatus.value = 'complete'
      return processedData
    } catch (error) {
      console.error('Error procesando señal:', error)
      processingError.value = error.message
      processingStatus.value = 'error'
      return []
    }
  }
  
  /**
   * Aplica un filtro de media móvil a los datos
   * @param {Array} data - Datos originales
   * @param {Number} windowSize - Tamaño de la ventana
   * @returns {Array} - Datos filtrados
   */
  const applyMovingAverage = (data, windowSize) => {
    const result = []
    
    for (let i = 0; i < data.length; i++) {
      let sum = 0
      let count = 0
      
      for (let j = Math.max(0, i - Math.floor(windowSize/2)); 
           j <= Math.min(data.length - 1, i + Math.floor(windowSize/2)); 
           j++) {
        sum += data[j]
        count++
      }
      
      result.push(sum / count)
    }
    
    return result
  }
  
  /**
   * Aplica un filtro pasa-altos simple a los datos
   * @param {Array} data - Datos originales
   * @param {Number} cutoff - Frecuencia de corte (0-1)
   * @returns {Array} - Datos filtrados
   */
  const applyHighPassFilter = (data, cutoff) => {
    const result = []
    const alpha = cutoff
    
    // Filtro pasa-altos simple (elimina componentes de baja frecuencia)
    let lastValue = data[0] || 0
    
    for (let i = 0; i < data.length; i++) {
      const highPassValue = alpha * (lastValue + data[i] - lastValue)
      result.push(highPassValue)
      lastValue = data[i]
    }
    
    return result
  }
  
  /**
   * Aplica un filtro pasa-bajos simple a los datos
   * @param {Array} data - Datos originales
   * @param {Number} cutoff - Frecuencia de corte (0-1)
   * @returns {Array} - Datos filtrados
   */
  const applyLowPassFilter = (data, cutoff) => {
    const result = []
    const alpha = 1 - cutoff
    
    // Filtro pasa-bajos simple (suavizado)
    let lastValue = data[0] || 0
    
    for (let i = 0; i < data.length; i++) {
      const lowPassValue = alpha * lastValue + (1 - alpha) * data[i]
      result.push(lowPassValue)
      lastValue = lowPassValue
    }
    
    return result
  }
  
  /**
   * Normaliza los datos a un rango [0, 1]
   * @param {Array} data - Datos originales
   * @returns {Array} - Datos normalizados
   */
  const normalizeData = (data) => {
    if (data.length === 0) return []
    
    const min = Math.min(...data)
    const max = Math.max(...data)
    
    if (max === min) return data.map(() => 0.5)
    
    return data.map(value => (value - min) / (max - min))
  }
  
  /**
   * Encuentra picos en los datos
   * @param {Array} data - Datos de la señal
   * @param {Number} threshold - Umbral para detección (0-1)
   * @param {Number} minDistance - Distancia mínima entre picos
   * @returns {Array} - Índices de los picos encontrados
   */
  const findPeaks = (data, threshold = 0.5, minDistance = 10) => {
    if (!data || data.length === 0) return []
    
    const peaks = []
    let lastPeakIndex = -minDistance
    
    // Normalizar datos para umbral relativo
    const normalizedData = normalizeData(data)
    
    for (let i = 1; i < normalizedData.length - 1; i++) {
      // Un punto es un pico si es mayor que sus vecinos y supera el umbral
      if (normalizedData[i] > normalizedData[i - 1] && 
          normalizedData[i] > normalizedData[i + 1] && 
          normalizedData[i] > threshold &&
          i - lastPeakIndex >= minDistance) {
        peaks.push(i)
        lastPeakIndex = i
      }
    }
    
    return peaks
  }
  
  /**
   * Calcula estadísticas básicas de los datos
   * @param {Array} data - Datos de la señal
   * @returns {Object} - Estadísticas (min, max, mean, std)
   */
  const calculateStats = (data) => {
    if (!data || data.length === 0) {
      return { min: 0, max: 0, mean: 0, median: 0, std: 0 }
    }
    
    const min = Math.min(...data)
    const max = Math.max(...data)
    
    // Media
    const sum = data.reduce((acc, val) => acc + val, 0)
    const mean = sum / data.length
    
    // Mediana
    const sortedData = [...data].sort((a, b) => a - b)
    const median = sortedData.length % 2 === 0
      ? (sortedData[sortedData.length / 2 - 1] + sortedData[sortedData.length / 2]) / 2
      : sortedData[Math.floor(sortedData.length / 2)]
    
    // Desviación estándar
    const variance = data.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / data.length
    const std = Math.sqrt(variance)
    
    return {
      min,
      max,
      mean,
      median,
      std
    }
  }
  
  /**
   * Submuestrea los datos para reducir el número de puntos
   * @param {Array} data - Datos originales
   * @param {Number} factor - Factor de submuestreo
   * @returns {Array} - Datos submuestreados
   */
  const downsample = (data, factor) => {
    if (!data || data.length === 0 || factor <= 1) return data
    
    const result = []
    for (let i = 0; i < data.length; i += factor) {
      result.push(data[i])
    }
    
    return result
  }
  
  /**
   * Interpola los datos para aumentar el número de puntos
   * @param {Array} data - Datos originales
   * @param {Number} factor - Factor de interpolación
   * @returns {Array} - Datos interpolados
   */
  const interpolate = (data, factor) => {
    if (!data || data.length <= 1 || factor <= 1) return data
    
    const result = []
    
    for (let i = 0; i < data.length - 1; i++) {
      const start = data[i]
      const end = data[i + 1]
      const step = (end - start) / factor
      
      result.push(start)
      for (let j = 1; j < factor; j++) {
        result.push(start + step * j)
      }
    }
    
    // Añadir el último punto
    if (data.length > 0) {
      result.push(data[data.length - 1])
    }
    
    return result
  }
  
  /**
   * Calcula la transformada rápida de Fourier (simplificada)
   * @param {Array} data - Datos en el dominio del tiempo
   * @returns {Object} - Datos en el dominio de la frecuencia {frequencies, magnitudes}
   */
  const calculateFFT = (data) => {
    if (!data || data.length === 0) return { frequencies: [], magnitudes: [] }
    
    // Esta es una implementación simplificada para fines ilustrativos
    // En un caso real, se utilizaría una biblioteca como FFT.js
    
    const n = data.length
    const frequencies = []
    const magnitudes = []
    
    // Calcular las magnitudes para cada frecuencia
    for (let k = 0; k < n / 2; k++) {
      const freq = k / n
      frequencies.push(freq)
      
      let real = 0
      let imag = 0
      
      for (let t = 0; t < n; t++) {
        const angle = -2 * Math.PI * k * t / n
        real += data[t] * Math.cos(angle)
        imag += data[t] * Math.sin(angle)
      }
      
      // Magnitud normalizada
      const magnitude = Math.sqrt(real * real + imag * imag) / n
      magnitudes.push(magnitude)
    }
    
    return { frequencies, magnitudes }
  }
  
  // Propiedades y métodos expuestos
  const isProcessing = computed(() => processingStatus.value === 'processing')
  const hasError = computed(() => processingStatus.value === 'error')
  
  return {
    // Estado
    processingStatus,
    processingError,
    processedSignals,
    isProcessing,
    hasError,
    
    // Métodos de procesamiento
    processSignal,
    findPeaks,
    calculateStats,
    downsample,
    interpolate,
    calculateFFT,
    normalizeData,
    
    // Métodos de filtrado
    applyMovingAverage,
    applyHighPassFilter,
    applyLowPassFilter
  }
}
