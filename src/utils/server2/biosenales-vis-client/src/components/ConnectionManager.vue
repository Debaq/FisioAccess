<template>
  <div class="connection-manager">
    <div class="connection-container">
      <h1 class="title">Sistema de Visualización de Bioseñales</h1>
      
      <div v-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="resetError" class="btn btn-secondary">Reintentar</button>
      </div>
      
      <div v-if="isConnecting" class="loading">
        <div class="spinner"></div>
        <p>Conectando con el servidor...</p>
      </div>
      
      <div v-else class="connection-form">
        <div class="form-group">
          <h2>Conectar a una sesión</h2>
          
          <div class="input-group">
            <label for="session-id">ID de Sesión</label>
            <input 
              id="session-id" 
              v-model="sessionId" 
              type="text" 
              placeholder="Dejar vacío para crear nueva sesión"
              :disabled="isConnecting"
            />
          </div>
          
          <div class="input-group">
            <label for="session-name">Nombre de la Sesión</label>
            <input 
              id="session-name" 
              v-model="sessionName" 
              type="text" 
              placeholder="Opcional: Nombre personalizado"
              :disabled="isConnecting"
            />
          </div>
          
          <div class="actions">
            <button 
              @click="connectToSession" 
              class="btn btn-primary"
              :disabled="isConnecting"
            >
              {{ sessionId ? 'Conectar' : 'Crear Nueva Sesión' }}
            </button>
          </div>
        </div>
        
        <div class="active-sessions" v-if="activeSessions.length > 0">
          <h3>Sesiones Activas</h3>
          <ul class="session-list">
            <li 
              v-for="session in activeSessions" 
              :key="session.id" 
              @click="selectSession(session)"
              class="session-item"
            >
              <div class="session-info">
                <div class="session-name">{{ session.name }}</div>
                <div class="session-details">
                  <span>ID: {{ session.id }}</span>
                  <span>Clientes: {{ session.client_count }}</span>
                </div>
              </div>
              <button class="btn btn-connect">Conectar</button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useSocket } from '@/composables/useSocket'

export default {
  name: 'ConnectionManager',
  emits: ['session-connected'],
  
  setup(props, { emit }) {
    // Datos del formulario
    const sessionId = ref('')
    const sessionName = ref('')
    
    // Estado del componente
    const isConnecting = ref(false)
    const error = ref('')
    const activeSessions = ref([])
    
    // Socket y conexión
    const { 
      connect, 
      joinSession, 
      isConnected,
      socket 
    } = useSocket()
    
    // Cargar sesiones activas
    const loadActiveSessions = async () => {
      try {
        const response = await fetch('/api/sessions')
        if (response.ok) {
          const data = await response.json()
          activeSessions.value = data || []
        } else {
          console.error('Error cargando sesiones:', response.statusText)
        }
      } catch (err) {
        console.error('Error cargando sesiones:', err)
      }
    }
    
    // Seleccionar una sesión de la lista
    const selectSession = (session) => {
      sessionId.value = session.id
      sessionName.value = session.name
    }
    
    // Conectar a una sesión
    const connectToSession = async () => {
      isConnecting.value = true
      error.value = ''
      
      try {
        // Conectar socket si no está conectado
        if (!isConnected.value) {
          connect()
        }
        
        // Esperar a que el socket esté listo
        await new Promise(resolve => {
          if (socket.value.connected) {
            resolve()
          } else {
            socket.value.on('connect', resolve)
          }
        })
        
        // Unirse a la sesión
        const session = await joinSession(
          sessionId.value, 
          sessionName.value || undefined
        )
        
        // Emitir evento de conexión exitosa
        emit('session-connected', session)
      } catch (err) {
        console.error('Error conectando a sesión:', err)
        error.value = err.message || 'Error al conectar a la sesión'
      } finally {
        isConnecting.value = false
      }
    }
    
    // Resetear errores
    const resetError = () => {
      error.value = ''
    }
    
    // Cargar sesiones al montar el componente
    onMounted(async () => {
      await loadActiveSessions()
    })
    
    return {
      sessionId,
      sessionName,
      isConnecting,
      error,
      activeSessions,
      connectToSession,
      selectSession,
      resetError
    }
  }
}
</script>

<style scoped>
.connection-manager {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.connection-container {
  width: 100%;
  max-width: 600px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
  font-size: 24px;
}

.form-group {
  margin-bottom: 30px;
}

.form-group h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #2c3e50;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.input-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.input-group input:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #388e3c;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn-connect {
  background-color: #2196f3;
  color: white;
  padding: 6px 12px;
  font-size: 12px;
}

.btn-connect:hover {
  background-color: #1976d2;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(76, 175, 80, 0.2);
  border-radius: 50%;
  border-top-color: #4caf50;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  padding: 15px;
  background-color: #ffebee;
  border-left: 4px solid #f44336;
  color: #b71c1c;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-message p {
  margin: 0;
}

.active-sessions {
  margin-top: 30px;
}

.active-sessions h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #2c3e50;
}

.session-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.session-item {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-item:hover {
  background-color: #f9f9f9;
}

.session-info {
  flex: 1;
}

.session-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.session-details {
  display: flex;
  font-size: 12px;
  color: #666;
}

.session-details span {
  margin-right: 15px;
}
</style>
