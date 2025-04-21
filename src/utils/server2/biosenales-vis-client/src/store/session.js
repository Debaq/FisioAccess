import { reactive, readonly } from 'vue'
import { useSocket } from '@/composables/useSocket'

/**
 * Crea el store para gestión de sesiones
 * @returns {Object} Store de sesión con estado y métodos
 */
export function createSessionStore() {
  // Obtener composable Socket.IO
  const { 
    connect, 
    disconnect, 
    joinSession, 
    leaveSession,
    updateConfiguration,
    onConfigUpdate,
    socket,
    isConnected
  } = useSocket()

  // Estado de la sesión
  const state = reactive({
    connected: false,
    connecting: false,
    session: {
      id: '',
      name: 'Sin conexión',
      client_count: 0,
      created_at: null,
      status: 'inactive'
    },
    configuration: {
      mode: 'realtime',   // 'realtime' o 'playback'
      layout: 'single',   // 'single', 'vertical', 'horizontal'
      theme: 'light',     // 'light' o 'dark'
      autoScale: true,    // Auto-escala de señales
      timeWindow: 10000,  // Ventana de tiempo en ms
      gridEnabled: true,  // Mostrar cuadrícula
      sampleRate: 250     // Frecuencia de muestreo por defecto
    },
    clients: [],          // Otros clientes conectados
    connectionError: null
  })

  // Conectar al servidor Socket.IO
  const connectToServer = () => {
    if (!state.connected && !state.connecting) {
      state.connecting = true
      state.connectionError = null
      
      try {
        // Iniciar conexión Socket.IO
        connect()
        
        // Configurar handler para conexión establecida
        const onConnected = () => {
          state.connected = true
          state.connecting = false
        }
        
        // Configurar handler para error de conexión
        const onError = (error) => {
          state.connectionError = error
          state.connecting = false
        }
        
        // Añadir listeners una sola vez
        if (socket.value) {
          socket.value.once('connect', onConnected)
          socket.value.once('connect_error', onError)
        }
      } catch (error) {
        state.connectionError = error
        state.connecting = false
      }
    }
    
    return isConnected
  }

  // Desconectar del servidor
  const disconnectFromServer = async () => {
    if (state.connected) {
      await disconnect()
      state.connected = false
      state.session = {
        id: '',
        name: 'Sin conexión',
        client_count: 0,
        created_at: null,
        status: 'inactive'
      }
    }
  }

  // Conectar a una sesión específica
  const connectToSession = async (sessionId = '', sessionName = '') => {
    if (!state.connected) {
      await connectToServer()
    }
    
    state.connecting = true
    state.connectionError = null
    
    try {
      // Unirse a la sesión (o crear nueva si sessionId está vacío)
      const sessionData = await joinSession(sessionId, sessionName)
      
      // Actualizar estado
      state.session = {
        id: sessionData.id,
        name: sessionData.name,
        client_count: sessionData.client_count,
        created_at: sessionData.created_at,
        status: sessionData.status
      }
      
      // Actualizar configuración
      if (sessionData.configuration) {
        Object.assign(state.configuration, sessionData.configuration)
      }
      
      state.connecting = false
      return sessionData
    } catch (error) {
      state.connectionError = error
      state.connecting = false
      throw error
    }
  }

  // Desconectar de la sesión actual
  const disconnectFromSession = async () => {
    if (state.session.id) {
      await leaveSession()
      state.session = {
        id: '',
        name: 'Sin conexión',
        client_count: 0,
        created_at: null,
        status: 'inactive'
      }
    }
  }

  // Actualizar configuración de sesión
  const updateSessionConfig = async (config) => {
    if (!state.session.id) {
      throw new Error('No hay ninguna sesión activa')
    }
    
    // Actualizar configuración local primero (optimistic update)
    Object.assign(state.configuration, config)
    
    // Enviar actualización al servidor
    try {
      await updateConfiguration(config)
      return true
    } catch (error) {
      // Si falla, podríamos revertir a la configuración anterior
      // (Implementar lógica de rollback si es necesario)
      throw error
    }
  }

  // Escuchar actualizaciones de configuración
  const setupConfigListener = () => {
    // Registrar listener para actualizaciones de configuración
    const removeListener = onConfigUpdate((newConfig) => {
      // Actualizar configuración local si viene del servidor
      Object.assign(state.configuration, newConfig)
    })
    
    // Retornar función para eliminar listener
    return removeListener
  }

  // Función para generar URL de sesión
  const getSessionUrl = () => {
    if (!state.session.id) return null
    
    const baseUrl = window.location.origin
    return `${baseUrl}?session=${state.session.id}`
  }

  // Función para generar URL de QR de sesión
  const getSessionQrUrl = () => {
    if (!state.session.id) return null
    
    return `/api/session/${state.session.id}/qr`
  }

  // Configurar listener inicial
  const configListener = setupConfigListener()

  // Limpiar al desmontar
  const cleanup = () => {
    if (configListener) {
      configListener()
    }
    disconnectFromServer()
  }

  // API pública
  return {
    // Estado de sólo lectura
    state: readonly(state),
    
    // Getters
    getSessionUrl,
    getSessionQrUrl,
    
    // Métodos
    connectToServer,
    disconnectFromServer,
    connectToSession,
    disconnectFromSession,
    updateSessionConfig,
    cleanup
  }
}
