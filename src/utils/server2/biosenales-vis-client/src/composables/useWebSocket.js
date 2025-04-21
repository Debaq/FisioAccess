// src/composables/useWebSocket.js
import { ref, onUnmounted } from 'vue'

export function useWebSocket() {
  const ws = ref(null)
  const isConnected = ref(false)
  const error = ref(null)
  const listeners = {}

  const connect = () => {
    ws.value = new WebSocket('ws://localhost:8000/ws')

    ws.value.onopen = () => {
      isConnected.value = true
      error.value = null
    }

    ws.value.onerror = (e) => {
      error.value = e.message
    }

    ws.value.onclose = () => {
      isConnected.value = false
    }

    ws.value.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        const type = msg.type
        if (listeners[type]) {
          listeners[type].forEach(cb => cb(msg))
        }
      } catch (e) {
        console.error('Error parseando mensaje WS:', e)
      }
    }
  }

  const send = (message) => {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
    }
  }

  const on = (type, callback) => {
    if (!listeners[type]) listeners[type] = []
    listeners[type].push(callback)
    return () => {
      listeners[type] = listeners[type].filter(cb => cb !== callback)
    }
  }

  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }

  onUnmounted(() => disconnect())

  return {
    connect,
    disconnect,
    send,
    on,
    isConnected,
    error
  }
}
