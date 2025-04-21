<template>
  <div class="session-manager">
    <div class="session-info">
      <div class="session-header">
        <h3 class="session-title">{{ sessionName }}</h3>
        <div class="session-details">
          <div class="session-id">ID: {{ sessionId }}</div>
          <div class="session-clients">
            <span class="client-count">{{ clientCount }} </span>
            <span class="client-text">{{ clientCount === 1 ? 'cliente' : 'clientes' }}</span>
          </div>
        </div>
      </div>
      
      <div class="session-actions">
        <button 
          @click="showQrCode" 
          class="btn btn-action"
          title="Mostrar código QR para conexión móvil"
        >
          <span class="icon">🔗</span>
          <span class="text">QR</span>
        </button>
        
        <button 
          @click="copySessionUrl" 
          class="btn btn-action"
          title="Copiar URL de la sesión"
        >
          <span class="icon">📋</span>
          <span class="text">URL</span>
        </button>
        
        <button 
          @click="toggleSessionConfig" 
          class="btn btn-action"
          title="Configuración de sesión"
        >
          <span class="icon">⚙️</span>
          <span class="text">Config</span>
        </button>
      </div>
    </div>
    
    <!-- Panel de configuración (expandible) -->
    <div class="session-config" v-if="showConfig">
      <h4>Configuración de Sesión</h4>
      
      <div class="config-form">
        <div class="form-group">
          <label for="session-name-input">Nombre de la sesión</label>
          <div class="input-with-action">
            <input 
              id="session-name-input" 
              v-model="sessionNameInput" 
              type="text" 
              placeholder="Nombre de la sesión"
            />
            <button 
              @click="updateSessionName" 
              class="btn btn-secondary"
              :disabled="!sessionNameChanged"
            >
              Actualizar
            </button>
          </div>
        </div>
        
        <div class="form-group">
          <label>Modo de Visualización</label>
          <div class="radio-group">
            <label class="radio-label">
              <input 
                type="radio" 
                v-model="configMode" 
                value="realtime"
                @change="updateConfig('mode', 'realtime')"
              />
              <span>Tiempo real</span>
            </label>
            <label class="radio-label">
              <input 
                type="radio" 
                v-model="configMode" 
                value="playback"
                @change="updateConfig('mode', 'playback')"
              />
              <span>Reproducción</span>
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label for="time-window">Ventana de tiempo (ms)</label>
          <div class="input-with-action">
            <input 
              id="time-window" 
              v-model.number="configTimeWindow" 
              type="number" 
              min="1000" 
              step="1000"
            />
            <button 
              @click="updateConfig('timeWindow', configTimeWindow)" 
              class="btn btn-secondary"
              :disabled="!timeWindowChanged"
            >
              Actualizar
            </button>
          </div>
        </div>
        
        <div class="form-group">
          <label>Opciones Adicionales</label>
          <div class="checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="configAutoScale"
                @change="updateConfig('autoScale', configAutoScale)"
              />
              <span>Auto-escala</span>
            </label>
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="configGridEnabled"
                @change="updateConfig('gridEnabled', configGridEnabled)"
              />
              <span>Mostrar cuadrícula</span>
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label>Tema</label>
          <div class="radio-group">
            <label class="radio-label">
              <input 
                type="radio" 
                v-model="configTheme" 
                value="light"
                @change="updateConfig('theme', 'light')"
              />
              <span>Claro</span>
            </label>
            <label class="radio-label">
              <input 
                type="radio" 
                v-model="configTheme" 
                value="dark"
                @change="updateConfig('theme', 'dark')"
              />
              <span>Oscuro</span>
            </label>
          </div>
        </div>
      </div>
      
      <div class="config-actions">
        <button @click="toggleSessionConfig" class="btn btn-secondary">Cerrar</button>
      </div>
    </div>
    
    <!-- Modal para QR Code -->
    <div v-if="showQr" class="qr-modal">
      <div class="qr-modal-content">
        <h3>Escanea para conectarte</h3>
        <div class="qr-image">
          <img :src="qrCodeUrl" alt="QR Code para conectarse a la sesión" />
        </div>
        <div class="qr-session-url">{{ sessionUrl }}</div>
        <button @click="hideQrCode" class="btn btn-primary">Cerrar</button>
      </div>
    </div>
    
    <!-- Notificación -->
    <div v-if="notification" class="notification" :class="notification.type">
      <span class="notification-message">{{ notification.message }}</span>
      <button @click="clearNotification" class="notification-close">×</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useSocket } from '@/composables/useSocket'

export default {
  name: 'SessionManager',
  props: {
    session: {
      type: Object,
      default: () => ({
        id: '',
        name: 'Sesión sin nombre',
        client_count: 0,
        configuration: {
          mode: 'realtime',
          layout: 'single',
          theme: 'light',
          autoScale: true,
          timeWindow: 10000,
          gridEnabled: true
        }
      })
    }
  },
  
  emits: ['config-updated'],
  
  setup(props, { emit }) {
    // Socket para comunicación
    const { updateConfiguration } = useSocket()
    
    // Estado de la sesión
    const sessionId = computed(() => props.session.id || '')
    const sessionName = computed(() => props.session.name || 'Sesión sin nombre')
    const clientCount = computed(() => props.session.client_count || 0)
    
    // Estado de la UI
    const showConfig = ref(false)
    const showQr = ref(false)
    const notification = ref(null)
    
    // Valores de configuración
    const sessionNameInput = ref(props.session.name || '')
    const configMode = ref(props.session.configuration?.mode || 'realtime')
    const configTimeWindow = ref(props.session.configuration?.timeWindow || 10000)
    const configAutoScale = ref(props.session.configuration?.autoScale !== false)
    const configGridEnabled = ref(props.session.configuration?.gridEnabled !== false)
    const configTheme = ref(props.session.configuration?.theme || 'light')
    
    // URL de la sesión y QR
    const sessionUrl = computed(() => {
      const baseUrl = window.location.origin
      return `${baseUrl}?session=${sessionId.value}`
    })
    
    const qrCodeUrl = computed(() => {
      return `/api/session/${sessionId.value}/qr`
    })
    
    // Detectar cambios en la configuración
    const sessionNameChanged = computed(() => sessionNameInput.value !== sessionName.value)
    const timeWindowChanged = computed(() => configTimeWindow.value !== props.session.configuration?.timeWindow)
    
    // Observar cambios en la sesión
    watch(() => props.session, (newSession) => {
      sessionNameInput.value = newSession.name || ''
      configMode.value = newSession.configuration?.mode || 'realtime'
      configTimeWindow.value = newSession.configuration?.timeWindow || 10000
      configAutoScale.value = newSession.configuration?.autoScale !== false
      configGridEnabled.value = newSession.configuration?.gridEnabled !== false
      configTheme.value = newSession.configuration?.theme || 'light'
    }, { deep: true })
    
    // Mostrar/ocultar configuración
    const toggleSessionConfig = () => {
      showConfig.value = !showConfig.value
      
      // Si se cierra, asegurarse de que los valores reflejen el estado actual
      if (!showConfig.value) {
        sessionNameInput.value = sessionName.value
        configMode.value = props.session.configuration?.mode || 'realtime'
        configTimeWindow.value = props.session.configuration?.timeWindow || 10000
        configAutoScale.value = props.session.configuration?.autoScale !== false
        configGridEnabled.value = props.session.configuration?.gridEnabled !== false
        configTheme.value = props.session.configuration?.theme || 'light'
      }
    }
    
    // Actualizar nombre de sesión
    const updateSessionName = async () => {
      if (!sessionNameChanged.value) return
      
      try {
        const success = await updateConfiguration({ name: sessionNameInput.value })
        
        if (success) {
          showNotification('Nombre de sesión actualizado', 'success')
          emit('config-updated', { name: sessionNameInput.value })
        } else {
          showNotification('Error al actualizar nombre de sesión', 'error')
        }
      } catch (error) {
        showNotification('Error al actualizar nombre de sesión', 'error')
        console.error('Error actualizando nombre:', error)
      }
    }
    
    // Actualizar configuración
    const updateConfig = async (key, value) => {
      try {
        const success = await updateConfiguration({ [key]: value })
        
        if (success) {
          showNotification('Configuración actualizada', 'success')
          emit('config-updated', { [key]: value })
        } else {
          showNotification('Error al actualizar configuración', 'error')
        }
      } catch (error) {
        showNotification('Error al actualizar configuración', 'error')
        console.error('Error actualizando configuración:', error)
      }
    }
    
    // Mostrar código QR
    const showQrCode = () => {
      showQr.value = true
    }
    
    // Ocultar código QR
    const hideQrCode = () => {
      showQr.value = false
    }
    
    // Copiar URL al portapapeles
    const copySessionUrl = () => {
      navigator.clipboard.writeText(sessionUrl.value)
        .then(() => {
          showNotification('URL copiada al portapapeles', 'success')
        })
        .catch(err => {
          console.error('Error copiando URL:', err)
          showNotification('Error al copiar URL', 'error')
        })
    }
    
    // Mostrar notificación
    const showNotification = (message, type = 'info') => {
      notification.value = { message, type }
      
      // Auto-cerrar después de 3 segundos
      setTimeout(() => {
        if (notification.value && notification.value.message === message) {
          notification.value = null
        }
      }, 3000)
    }
    
    // Limpiar notificación
    const clearNotification = () => {
      notification.value = null
    }
    
    return {
      // Estado
      sessionId,
      sessionName,
      clientCount,
      
      // UI
      showConfig,
      showQr,
      notification,
      
      // Configuración
      sessionNameInput,
      configMode,
      configTimeWindow,
      configAutoScale,
      configGridEnabled,
      configTheme,
      
      // Computed
      sessionUrl,
      qrCodeUrl,
      sessionNameChanged,
      timeWindowChanged,
      
      // Métodos
      toggleSessionConfig,
      updateSessionName,
      updateConfig,
      showQrCode,
      hideQrCode,
      copySessionUrl,
      clearNotification
    }
  }
}
</script>

<style scoped>
.session-manager {
  position: relative;
  width: 100%;
  background-color: #f5f5f5;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.session-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
}

.session-header {
  flex: 1;
}

.session-title {
  margin: 0 0 5px 0;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.session-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
}

.session-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background-color: #e0e0e0;
  color: #333;
  transition: background-color 0.2s;
}

.btn:hover:not(:disabled) {
  background-color: #d0d0d0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 10px;
  font-size: 12px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
}

.btn-action .icon {
  font-size: 16px;
  margin-bottom: 2px;
}

.btn-action .text {
  font-size: 10px;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #388e3c;
}

.btn-secondary {
  background-color: #e0e0e0;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #c0c0c0;
}

/* Panel de configuración */
.session-config {
  padding: 15px;
  border-top: 1px solid #ddd;
  background-color: #f9f9f9;
}

.session-config h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.config-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.input-with-action {
  display: flex;
  gap: 8px;
}

.input-with-action input {
  flex: 1;
}

.radio-group,
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.radio-label,
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
}

.config-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Modal QR */
.qr-modal {
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

.qr-modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.qr-modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #333;
}

.qr-image {
  margin: 15px 0;
  display: flex;
  justify-content: center;
}

.qr-image img {
  max-width: 200px;
  height: auto;
}

.qr-session-url {
  margin: 15px 0 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 14px;
  word-break: break-all;
}

/* Notificaciones */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  background-color: #333;
  color: white;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-width: 400px;
}

.notification.success {
  background-color: #4caf50;
}

.notification.error {
  background-color: #f44336;
}

.notification.info {
  background-color: #2196f3;
}

.notification-message {
  flex: 1;
  margin-right: 10px;
}

.notification-close {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0 5px;
}

@media (max-width: 768px) {
  .session-info {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .session-actions {
    margin-top: 10px;
    width: 100%;
    justify-content: flex-end;
  }
  
  .config-form {
    grid-template-columns: 1fr;
  }
}
</style>
