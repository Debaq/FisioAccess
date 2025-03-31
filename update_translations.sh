#!/bin/bash

# Verificar instalación de lupdate-qt6
if command -v lupdate-qt6 &> /dev/null; then
    LUPDATE="lupdate-qt6"
elif command -v lupdate6 &> /dev/null; then
    LUPDATE="lupdate6"
elif command -v lupdate &> /dev/null; then
    LUPDATE="lupdate"
else
    echo "❌ Error: Qt6 lupdate tools no están instalados"
    echo "Instala qt6-tools:"
    echo "  Ubuntu/Debian: sudo apt-get install qt6-tools-dev"
    echo "  Fedora: sudo dnf install qt6-linguist"
    echo "  Arch: sudo pacman -S qt6-tools"
    exit 1
fi

# Actualizar/generar archivos de traducción
$LUPDATE src/ -ts resources/translations/es.ts
$LUPDATE src/ -ts resources/translations/en.ts
