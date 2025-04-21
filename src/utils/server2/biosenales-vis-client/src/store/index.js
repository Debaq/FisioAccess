import { reactive, readonly, provide, inject } from 'vue'
import { createSessionStore } from './session'
import { createSignalsStore } from './signals'

// Símbolo único para inyección de dependencias
const StoreSymbol = Symbol()

/**
 * Crea el store global para la aplicación
 * @returns {Object} Store global con estado y métodos
 */
export function createStore() {
  // Estado global compartido
  const state = reactive({
    loading: false,
    error: null,
    notifications: []
  })

  // Métodos para manipular estado global
  const setLoading = (value) => {
    state.loading = value
  }

  const setError = (error) => {
    state.error = error
    // Si hay un error, añadir notificación
    if (error) {
      addNotification({
        type: 'error',
        message: error.message || 'Se ha producido un error',
        duration: 5000
      })
    }
  }

  const clearError = () => {
    state.error = null
  }

  const addNotification = (notification) => {
    // Generar ID único para la notificación
    const id = Date.now().toString()
    const newNotification = {
      id,
      type: notification.type || 'info',
      message: notification.message,
      duration: notification.duration || 3000,
      timestamp: Date.now()
    }

    state.notifications.push(newNotification)

    // Auto-eliminar después de la duración especificada
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    return id
  }

  const removeNotification = (id) => {
    const index = state.notifications.findIndex(n => n.id === id)
    if (index !== -1) {
      state.notifications.splice(index, 1)
    }
  }

  const clearAllNotifications = () => {
    state.notifications = []
  }

  // Crear módulos de store
  const sessionStore = createSessionStore()
  const signalsStore = createSignalsStore()

  // Conectar los stores para que puedan comunicarse entre sí
  signalsStore.registerSessionStore(sessionStore)

  // Store global que combina todos los módulos
  const store = {
    // Estado global
    state: readonly(state),
    
    // Métodos globales
    setLoading,
    setError,
    clearError,
    addNotification,
    removeNotification,
    clearAllNotifications,
    
    // Módulos
    session: sessionStore,
    signals: signalsStore
  }

  return store
}

/**
 * Proporciona el store a todos los componentes de la aplicación
 * @param {Object} app Instancia de la aplicación Vue
 * @param {Object} store Store global
 */
export function provideStore(app, store) {
  app.provide(StoreSymbol, store)
}

/**
 * Hook para consumir el store desde un componente
 * @returns {Object} Store global
 */
export function useStore() {
  const store = inject(StoreSymbol)
  if (!store) {
    throw new Error('No se ha proporcionado el store. Asegúrate de llamar a provideStore primero.')
  }
  return store
}
