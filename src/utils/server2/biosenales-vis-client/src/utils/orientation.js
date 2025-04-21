/**
 * Utilidades para detectar y manejar la orientación del dispositivo
 */

/**
 * Verifica si el dispositivo está en orientación vertical
 * @returns {boolean} true si está en vertical, false si está en horizontal
 */
export function checkOrientation() {
  // Detectar si es dispositivo móvil
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  
  if (!isMobile) {
    return false // En no-móviles, no mostrar advertencia
  }
  
  // En móviles, verificar si está en vertical
  return window.innerWidth < window.innerHeight
}

/**
 * Muestra una advertencia para girar el dispositivo
 */
export function showOrientationWarning() {
  let warningElement = document.getElementById('orientation-warning')
  
  if (!warningElement) {
    warningElement = document.createElement('div')
    warningElement.id = 'orientation-warning'
    warningElement.className = 'orientation-warning'
    
    const content = document.createElement('div')
    content.className = 'warning-content'
    
    const icon = document.createElement('div')
    icon.className = 'rotate-icon'
    icon.innerHTML = '↺'
    
    const title = document.createElement('h2')
    title.textContent = 'Por favor, gira tu dispositivo'
    
    const message = document.createElement('p')
    message.textContent = 'Esta aplicación está optimizada para visualizarse en modo horizontal.'
    
    content.appendChild(icon)
    content.appendChild(title)
    content.appendChild(message)
    warningElement.appendChild(content)
    
    // Estilos
    const style = document.createElement('style')
    style.textContent = `
      .orientation-warning {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.9);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
      }
      .warning-content {
        padding: 20px;
      }
      .rotate-icon {
        font-size: 40px;
        margin-bottom: 20px;
        animation: rotate 2s infinite;
      }
      @keyframes rotate {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(90deg); }
        100% { transform: rotate(90deg); }
      }
    `
    document.head.appendChild(style)
    
    document.body.appendChild(warningElement)
  } else {
    warningElement.style.display = 'flex'
  }
}

/**
 * Oculta la advertencia de orientación
 */
export function hideOrientationWarning() {
  const warningElement = document.getElementById('orientation-warning')
  if (warningElement) {
    warningElement.style.display = 'none'
  }
}

/**
 * Configura un detector de cambios de orientación
 * @param {Function} callback Función a llamar cuando cambia la orientación
 * @returns {Function} Función para eliminar el detector
 */
export function setupOrientationDetector(callback) {
  const handleResize = () => {
    const isVertical = checkOrientation()
    callback(isVertical)
  }
  
  window.addEventListener('resize', handleResize)
  window.addEventListener('orientationchange', handleResize)
  
  // Verificación inicial
  handleResize()
  
  // Función para eliminar detector
  return () => {
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('orientationchange', handleResize)
  }
}
