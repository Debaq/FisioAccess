import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

import { createStore, provideStore } from './store'

// Creación de la aplicación Vue
const app = createApp(App)
const store = createStore()
provideStore(app, store)

// Directiva personalizada para detectar clics fuera de un elemento
app.directive('click-outside', {
  beforeMount(el, binding) {
    el.clickOutsideEvent = (event) => {
      // Si el elemento que recibió el clic no es el elemento donde
      // está aplicada la directiva ni uno de sus descendientes
      if (!(el === event.target || el.contains(event.target))) {
        // Ejecutar el método proporcionado en la directiva
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
})

// Directiva para manejar el redimensionamiento de elementos
app.directive('resizable', {
  beforeMount(el, binding) {
    const minWidth = binding.value?.minWidth || 100
    const minHeight = binding.value?.minHeight || 100
    const direction = binding.value?.direction || 'both'
    
    el.style.position = 'relative'
    
    // Crear elemento para el redimensionamiento
    const resizer = document.createElement('div')
    resizer.className = `resizer resizer-${direction}`
    el.appendChild(resizer)
    
    // Variables para el redimensionamiento
    let startX, startY, startWidth, startHeight
    
    const startResize = (e) => {
      e.preventDefault()
      startX = e.clientX
      startY = e.clientY
      startWidth = el.offsetWidth
      startHeight = el.offsetHeight
      document.addEventListener('mousemove', resize)
      document.addEventListener('mouseup', stopResize)
    }
    
    const resize = (e) => {
      if (direction === 'horizontal' || direction === 'both') {
        const newWidth = startWidth + e.clientX - startX
        if (newWidth > minWidth) {
          el.style.width = `${newWidth}px`
        }
      }
      
      if (direction === 'vertical' || direction === 'both') {
        const newHeight = startHeight + e.clientY - startY
        if (newHeight > minHeight) {
          el.style.height = `${newHeight}px`
        }
      }
    }
    
    const stopResize = () => {
      document.removeEventListener('mousemove', resize)
      document.removeEventListener('mouseup', stopResize)
      
      // Disparar evento de cambio de tamaño completado
      el.dispatchEvent(new CustomEvent('resize-end', {
        detail: {
          width: el.offsetWidth,
          height: el.offsetHeight
        }
      }))
    }
    
    resizer.addEventListener('mousedown', startResize)
    
    // Limpiar eventos al desmontar
    el._cleanup = () => {
      resizer.removeEventListener('mousedown', startResize)
      el.removeChild(resizer)
    }
  },
  unmounted(el) {
    if (el._cleanup) {
      el._cleanup()
    }
  }
})

// Detectar soporte táctil
if ('ontouchstart' in window || navigator.msMaxTouchPoints) {
  document.body.classList.add('touch-device')
}

// Montar la aplicación en el elemento #app
app.mount('#app')

// Función para manejar la orientación en dispositivos móviles
const handleOrientation = () => {
  if (window.innerWidth < window.innerHeight) {
    document.body.classList.add('portrait')
  } else {
    document.body.classList.remove('portrait')
  }
}

// Configuración inicial y listeners
window.addEventListener('load', () => {
  handleOrientation()
  
  // Definir variables CSS para altura real de viewport en móviles
  const setViewportHeight = () => {
    const vh = window.innerHeight * 0.01
    document.documentElement.style.setProperty('--vh', `${vh}px`)
  }
  
  setViewportHeight()
  window.addEventListener('resize', () => {
    setViewportHeight()
    handleOrientation()
  })
  
  window.addEventListener('orientationchange', () => {
    setTimeout(handleOrientation, 100)
    setTimeout(setViewportHeight, 100)
  })
})

// Prevenir zoom en dispositivos táctiles
document.addEventListener('touchmove', (e) => {
  if (e.touches.length > 1) {
    e.preventDefault()
  }
}, { passive: false })
