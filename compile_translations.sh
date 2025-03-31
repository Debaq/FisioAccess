#!/bin/bash

# Verificar instalación de lrelease-qt6 o lrelease6
if command -v lrelease-qt6 &> /dev/null; then
    LRELEASE="lrelease-qt6"
elif command -v lrelease6 &> /dev/null; then
    LRELEASE="lrelease6"
elif command -v lrelease &> /dev/null; then
    LRELEASE="lrelease"
    
else
    echo "❌ Error: Qt6 release tools no están instalados"
    echo "Instala qt6-tools:"
    echo "  Ubuntu/Debian: sudo apt-get install qt6-tools-dev"
    echo "  Fedora: sudo dnf install qt6-linguist"
    echo "  Arch: sudo pacman -S qt6-tools"
    exit 1
fi

# Compilar traducciones
$LRELEASE resources/translations/es.ts -qm resources/translations/es.qm
$LRELEASE resources/translations/en.ts -qm resources/translations/en.qm
