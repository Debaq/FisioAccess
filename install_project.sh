#!/bin/bash

# Detectar idioma del sistema
LANG_CODE=$(echo $LANG | cut -d'_' -f1)

if [ "$LANG_CODE" = "es" ]; then
    MSG_ERROR_MICROMAMBA="❌ Error: micromamba no está instalado"
    MSG_ERROR_MICROMAMBA_INSTALL="Instálalo siguiendo las instrucciones en: https://mamba.readthedocs.io/en/latest/installation.html"
    MSG_ENV_EXISTS="⚠️ Ya existe un entorno virtual con el nombre '$PROJECT_NAME'"
    MSG_ENV_DELETE_CONFIRM="¿Deseas eliminarlo y crear uno nuevo? [s/N]: "
    MSG_ENV_DELETING="🗑️ Eliminando entorno virtual existente..."
    MSG_OPERATION_CANCELLED="❌ Operación cancelada."
    MSG_CREATING_ENV="🚀 Creando nuevo entorno virtual..."
    MSG_ACTIVATING_ENV="📦 Activando entorno virtual..."
    MSG_INSTALLING_DEPS="📥 Instalando dependencias..."
    MSG_INSTALL_COMPLETE="✅ Proyecto instalado correctamente"
    MSG_ACTIVATE_HELP="Para activar el entorno virtual, ejecuta: source activate_env.sh"
else
    MSG_ERROR_MICROMAMBA="❌ Error: micromamba is not installed"
    MSG_ERROR_MICROMAMBA_INSTALL="Install it following the instructions at: https://mamba.readthedocs.io/en/latest/installation.html"
    MSG_ENV_EXISTS="⚠️ Virtual environment '$PROJECT_NAME' already exists"
    MSG_ENV_DELETE_CONFIRM="Do you want to delete it and create a new one? [y/N]: "
    MSG_ENV_DELETING="🗑️ Deleting existing virtual environment..."
    MSG_OPERATION_CANCELLED="❌ Operation cancelled."
    MSG_CREATING_ENV="🚀 Creating new virtual environment..."
    MSG_ACTIVATING_ENV="📦 Activating virtual environment..."
    MSG_INSTALLING_DEPS="📥 Installing dependencies..."
    MSG_INSTALL_COMPLETE="✅ Project successfully installed"
    MSG_ACTIVATE_HELP="To activate the virtual environment, run: source activate_env.sh"
fi

# Verificar si micromamba está instalado
if ! command -v micromamba &> /dev/null; then
    echo "$MSG_ERROR_MICROMAMBA"
    echo "$MSG_ERROR_MICROMAMBA_INSTALL"
    exit 1
fi

# Obtener el nombre del proyecto del directorio actual
PROJECT_NAME=$(basename $(pwd))

# Verificar si ya existe el entorno
if micromamba env list | grep -q "^$PROJECT_NAME "; then
    echo "$MSG_ENV_EXISTS"
    read -p "$MSG_ENV_DELETE_CONFIRM" REMOVE_ENV
    if [[ $REMOVE_ENV =~ ^[Ss]$ ]]; then
        echo "$MSG_ENV_DELETING"
        micromamba env remove -n "$PROJECT_NAME" -y
    else
        echo "$MSG_OPERATION_CANCELLED"
        exit 1
    fi
fi

echo "$MSG_CREATING_ENV"
micromamba create -n "$PROJECT_NAME" python=3.12 -y

echo "$MSG_ACTIVATING_ENV"
eval "$(micromamba shell hook --shell bash)"
micromamba activate "$PROJECT_NAME"

echo "$MSG_INSTALLING_DEPS"
micromamba install -c conda-forge pyside6 pytest nuitka -y

echo "$MSG_INSTALL_COMPLETE"
echo "$MSG_ACTIVATE_HELP"
