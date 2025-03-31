#!/bin/bash

# Detectar idioma del sistema
LANG_CODE=$(echo $LANG | cut -d'_' -f1)

if [ "$LANG_CODE" = "es" ]; then
    MSG_ERROR_ENV="Error: No se detectó un entorno virtual activo"
    MSG_ERROR_ENV_ACTIVATE="Activa tu entorno virtual primero con: source activate_env.sh"
	MSG_ERROR_CONFIG="❌ Error: No se pudieron cargar todos los datos de configuración"
	MSG_COMPILE_COMPLETE="✅ Compilación completada"
    MSG_COMPILING="🔨 Compilando con Nuitka..."
    MSG_CONFIG="📦 Compilando con la siguiente configuración:"
    MSG_APP_NAME="   - Nombre de la aplicación:"
    MSG_VERSION="   - Versión:"
    MSG_COMPANY="   - Compañía:"
	MSG_EXECUTABLE_LOCATION="El ejecutable se encuentra en: build/nuitka/main.dist/main"

else
    MSG_ERROR_ENV="Error: No active virtual environment detected"
    MSG_ERROR_ENV_ACTIVATE="Activate your virtual environment first with: source activate_env.sh"
	MSG_ERROR_CONFIG="❌ Error: Could not load all configuration data"
	MSG_COMPILE_COMPLETE="✅ Compilation completed"
    MSG_COMPILING="🔨 Compiling with Nuitka..."
    MSG_CONFIG="📦 Compiling with the following configuration:"
    MSG_APP_NAME="   - Application name:"
    MSG_VERSION="   - Version:"
    MSG_COMPANY="   - Company:"
	MSG_EXECUTABLE_LOCATION="The executable can be found at: build/nuitka/main.dist/main"
fi

# Verificar si estamos en un entorno virtual
if [ -z "$CONDA_PREFIX" ]; then
    echo "$MSG_ERROR_ENV"
    echo "$MSG_ERROR_ENV_ACTIVATE"
    exit 1
fi

echo "$MSG_COMPILING"

# Cargar información de configuración usando Python para leer el JSON
APP_NAME=$(python -c "import json; print(json.load(open('src/config/config.json'))['app_name'])")
VERSION=$(python -c "import json; print(json.load(open('src/config/config.json'))['version'])")
COMPANY=$(python -c "import json; print(json.load(open('src/config/config.json'))['author']['company'] or 'Unknown')")
AUTHOR_NAME=$(python -c "import json; print(json.load(open('src/config/config.json'))['author']['name'])")

# Asegurarse de que tengamos valores por defecto
APP_NAME=${APP_NAME:-"$PROJECT_NAME"}
VERSION=${VERSION:-"1.0.0"}
COMPANY=${COMPANY:-"$AUTHOR_NAME"}

# Verificar que tenemos todos los valores necesarios
if [ -z "$COMPANY" ] || [ -z "$APP_NAME" ] || [ -z "$VERSION" ]; then
    echo "$MSG_ERROR_CONFIG"
    exit 1
fi

echo "$MSG_CONFIG"
echo "$MSG_APP_NAME $APP_NAME"
echo "$MSG_VERSION $VERSION"
echo "$MSG_COMPANY $COMPANY"

python -m nuitka \
    --follow-imports \
    --plugin-enable=pyside6 \
    --standalone \
    --include-package=PySide6 \
    --include-data-dir=src/config=config \
    --include-data-dir=resources=resources \
    --show-progress \
    --show-memory \
    --output-dir=build/nuitka \
    --company-name="$COMPANY" \
    --product-name="$APP_NAME" \
    --file-version="$VERSION" \
    --product-version="$VERSION" \
    --file-description="$APP_NAME Application" \
    --copyright="Copyright © $(date +%Y) $COMPANY" \
    src/main.py
    
# Limpiar directorio temporal
rm -rf build/nuitka/resources

echo "$MSG_COMPILE_COMPLETE"
echo "$MSG_EXECUTABLE_LOCATION"
