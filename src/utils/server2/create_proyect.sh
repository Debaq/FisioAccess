#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Configurando proyecto cliente para sistema de visualización de bioseñales...${NC}"

# Crear proyecto base con Vite y Vue
echo -e "${GREEN}Creando proyecto base con Vite y Vue...${NC}"
npm create vite@latest biosenales-vis-client -- --template vue
cd biosenales-vis-client

# Instalar dependencias
echo -e "${GREEN}Instalando dependencias...${NC}"
npm install
npm install d3 socket.io-client html2canvas jspdf

# Configurar estructura de directorios
echo -e "${GREEN}Creando estructura de directorios...${NC}"

# Directorios principales
mkdir -p src/assets
mkdir -p src/components/tools
mkdir -p src/composables
mkdir -p src/store
mkdir -p src/utils

# Crear archivos principales (vacíos)
echo -e "${GREEN}Creando archivos principales...${NC}"

# Root files
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/socket.io': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
EOF

# Crear App.vue principal (vacío por ahora)
cat > src/App.vue << 'EOF'
<template>
  <div id="app">
    <!-- Contenido principal de la aplicación -->
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
EOF

# Crear main.js
cat > src/main.js << 'EOF'
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'

createApp(App).mount('#app')
EOF

# Crear CSS base
cat > src/assets/main.css << 'EOF'
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
    Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
EOF

# Componentes
echo -e "${GREEN}Creando archivos de componentes...${NC}"

# ConnectionManager
touch src/components/ConnectionManager.vue

# Layouts
touch src/components/LayoutSingle.vue
touch src/components/LayoutVertical.vue
touch src/components/LayoutHorizontal.vue

# Tools
touch src/components/tools/ToolsPanel.vue
touch src/components/tools/LabelTool.vue
touch src/components/tools/DrawTool.vue
touch src/components/tools/MeasureTool.vue

# Session
touch src/components/SessionManager.vue

# Composables
echo -e "${GREEN}Creando composables...${NC}"
touch src/composables/useSocket.js
touch src/composables/useSignalProcessing.js
touch src/composables/usePdfGenerator.js

# Store
echo -e "${GREEN}Creando archivos de store...${NC}"
touch src/store/index.js
touch src/store/session.js
touch src/store/signals.js

# Utils
echo -e "${GREEN}Creando archivos de utilidades...${NC}"
touch src/utils/d3-helpers.js
touch src/utils/orientation.js

echo -e "${BLUE}Configuración completada. El proyecto está listo para comenzar el desarrollo.${NC}"
echo -e "${GREEN}Para iniciar el desarrollo, ejecuta:${NC}"
echo -e "cd biosenales-vis-client"
echo -e "npm run dev"
