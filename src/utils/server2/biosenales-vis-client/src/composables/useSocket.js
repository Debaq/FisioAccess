import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

export function useSocket() {
  const socket = ref(null)
  const isConnected = ref(false)
  const error = ref(null)
  
  // Listeners para eventos
  const dataUpdateListeners = ref([])
  const configUpdateListeners = ref([])
  const toolUpdateListeners = ref({
    labels: [],
    draw: [],
    measure: []
  })
  
  // Crear conexión Socket.IO
  const connect = () => {
    socket.value = io({
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 20000
    })
    
    // Configurar listeners de conexión
    socket.value.on('connect', () => {
      isConnected.value = true
      error.value = null
    })
    
    socket.value.on('disconnect', () => {
      isConnected.value = false
    })
    
    socket.value.on('connect_error', (err) => {
      error.value = err.message
    })
    
    // Configurar listeners de eventos
    setupSocketListeners()
    
    return socket.value
  }
  
  // Configurar listeners para eventos del servidor
  const setupSocketListeners = () => {
    if (!socket.value) return
    
    // Listener para actualización de datos
    socket.value.on('data_update', (data) => {
      dataUpdateListeners.value.forEach(callback => callback(data))
    })
    
    // Listener para actualización de configuración
    socket.value.on('configuration_updated', (config) => {
      configUpdateListeners.value.forEach(callback => callback(config))
    })
    
    // Listeners para actualizaciones de herramientas
    socket.value.on('tool_update_labels', (data) => {
      toolUpdateListeners.value.labels.forEach(callback => callback(data))
    })
    
    socket.value.on('tool_update_draw', (data) => {
      toolUpdateListeners.value.draw.forEach(callback => callback(data))
    })
    
    socket.value.on('tool_update_measure', (data) => {
      toolUpdateListeners.value.measure.forEach(callback => callback(data))
    })
  }
  
  // Desconectar
  const disconnect = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
    }
  }
  
  // Unirse a una sesión
  const joinSession = async (sessionId = '', sessionName = '') => {
    if (!socket.value) {
      connect()
    }
    
    return new Promise((resolve, reject) => {
      socket.value.emit('join_session', {
        session_id: sessionId,
        name: sessionName
      }, (response) => {
        if (response && response.success) {
          resolve(response.session)
        } else {
          reject(new Error(response?.error || 'No se pudo unir a la sesión'))
        }
      })
    })
  }
  
  // Salir de una sesión
  const leaveSession = async () => {
    if (!socket.value) return Promise.resolve(false)
    
    return new Promise((resolve) => {
      socket.value.emit('leave_session', (response) => {
        resolve(response?.success || false)
      })
    })
  }
  
  // Actualizar configuración
  const updateConfiguration = async (config) => {
    if (!socket.value) return Promise.resolve(false)
    
    return new Promise((resolve) => {
      socket.value.emit('update_configuration', config, (response) => {
        resolve(response?.success || false)
      })
    })
  }
  
  // Añadir datos de herramientas
  const addToolData = async (type, data) => {
    if (!socket.value) return Promise.resolve(false)
    
    return new Promise((resolve) => {
      socket.value.emit('add_tool_data', {
        type,
        data
      }, (response) => {
        resolve(response?.success || false)
      })
    })
  }
  
  // Registrar callback para actualizaciones de datos
  const onDataUpdate = (callback) => {
    dataUpdateListeners.value.push(callback)
    return () => {
      const index = dataUpdateListeners.value.indexOf(callback)
      if (index !== -1) {
        dataUpdateListeners.value.splice(index, 1)
      }
    }
  }
  
  // Registrar callback para actualizaciones de configuración
  const onConfigUpdate = (callback) => {
    configUpdateListeners.value.push(callback)
    return () => {
      const index = configUpdateListeners.value.indexOf(callback)
      if (index !== -1) {
        configUpdateListeners.value.splice(index, 1)
      }
    }
  }
  
  // Registrar callback para actualizaciones de herramientas
  const onToolUpdate = (type, callback) => {
    if (toolUpdateListeners.value[type]) {
      toolUpdateListeners.value[type].push(callback)
      return () => {
        const index = toolUpdateListeners.value[type].indexOf(callback)
        if (index !== -1) {
          toolUpdateListeners.value[type].splice(index, 1)
        }
      }
    }
    return () => {}
  }
  
  // Limpiar listeners al desmontar
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    socket,
    isConnected,
    error,
    connect,
    disconnect,
    joinSession,
    leaveSession,
    updateConfiguration,
    addToolData,
    onDataUpdate,
    onConfigUpdate,
    onToolUpdate
  }
}
