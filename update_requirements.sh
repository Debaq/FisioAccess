#!/bin/bash


# Detectar idioma del sistema
LANG_CODE=$(echo $LANG | cut -d'_' -f1)

if [ "$LANG_CODE" = "es" ]; then
	MSG_ERROR_ENV="Error: No se detectó un entorno virtual activo"
	MSG_ERROR_ENV_ACTIVATE="Activa tu entorno virtual primero con: source activate_env.sh"
	MSG_UPDATE_REQS="📝 Actualizando requirements.txt..."
	MSG_BACKUP_CREATED="💾 Backup creado en requirements.txt.bak"
	MSG_REQS_UPDATED="✅ requirements.txt actualizado exitosamente"
	MSG_CURRENT_REQS="📋 Contenido actual de requirements.txt:"
else
	MSG_ERROR_ENV="Error: No active virtual environment detected"
	MSG_ERROR_ENV_ACTIVATE="Activate your virtual environment first with: source activate_env.sh"
	MSG_UPDATE_REQS="📝 Updating requirements.txt..."
	MSG_BACKUP_CREATED="💾 Backup created in requirements.txt.bak"
	MSG_REQS_UPDATED="✅ requirements.txt successfully updated"
	MSG_CURRENT_REQS="📋 Current requirements.txt content:"
fi

# Verificar si estamos en un entorno virtual de micromamba
if [ -z "$CONDA_PREFIX" ]; then
    echo "$MSG_ERROR_ENV"
    echo "$MSG_ERROR_ENV_ACTIVATE"
    exit 1
fi

echo "$MSG_UPDATE_REQS"

# Crear backup del requirements.txt actual
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements.txt.bak
    echo "$MSG_BACKUP_CREATED"
fi

# Obtener todas las dependencias instaladas con pip
pip list --format=freeze > requirements.txt

# Eliminar paquetes que no queremos en requirements.txt
sed -i '/pkg-resources/d' requirements.txt  # Eliminar pkg-resources si existe
sed -i '/pkg_resources/d' requirements.txt  # Eliminar pkg_resources si existe
sed -i '/setuptools/d' requirements.txt     # Eliminar setuptools si existe
sed -i '/pip/d' requirements.txt           # Eliminar pip si existe
sed -i '/wheel/d' requirements.txt         # Eliminar wheel si existe

echo "$MSG_REQS_UPDATED"
echo "📋$MSG_CURRENT_REQS"
echo "----------------------------------------"
cat requirements.txt
echo "----------------------------------------"
