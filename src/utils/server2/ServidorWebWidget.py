#!/usr/bin/env python3
"""
Widget independiente para gestión del Servidor de Bioseñales.

Este módulo proporciona un QWidget que puede integrarse fácilmente
en aplicaciones PySide6 existentes, permitiendo controlar el servidor
de bioseñales sin depender de una aplicación completa.
"""

import os
import sys
import time
import random
import math
import threading
import logging
from pathlib import Path
from typing import Dict, List, Union, Optional, Callable, Any

# Importaciones PySide6
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLabel, QLineEdit, QSpinBox, QCheckBox, 
                              QPushButton, QGroupBox, QFileDialog, QMessageBox,
                              QDialog, QComboBox, QApplication)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QImage

# Importar servidor de bioseñales (asegúrate de tener las implementaciones actualizadas)
from server_fisioaccess import ServidorBiosenales

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ServidorWebWidget")

class ServidorWebWidget(QWidget):
    """Widget para controlar el servidor de bioseñales desde cualquier aplicación PySide6."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.servidor = ServidorBiosenales()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del widget."""
        self.main_layout = QVBoxLayout(self)
        
        # Grupo de configuración
        config_group = QGroupBox("Configuración del Servidor")
        config_layout = QFormLayout(config_group)
        
        # Campos de configuración
        self.host_input = QLineEdit(self.servidor.config["host"])
        config_layout.addRow("Host:", self.host_input)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1024, 65535)
        self.port_input.setValue(self.servidor.config["port"])
        config_layout.addRow("Puerto:", self.port_input)
        
        self.folder_input = QLineEdit(self.servidor.config["dist_folder"])
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_btn = QPushButton("...")
        folder_btn.setMaximumWidth(30)
        folder_btn.clicked.connect(self._select_folder)
        folder_layout.addWidget(folder_btn)
        config_layout.addRow("Carpeta Dist:", folder_layout)
        
        self.interval_input = QSpinBox()
        self.interval_input.setRange(10, 10000)
        self.interval_input.setValue(self.servidor.config["data_interval"])
        config_layout.addRow("Intervalo (ms):", self.interval_input)
        
        self.buffer_input = QSpinBox()
        self.buffer_input.setRange(100, 10000)
        self.buffer_input.setValue(self.servidor.config.get("buffer_size", 1000))
        config_layout.addRow("Tamaño buffer:", self.buffer_input)
        
        self.api_external_check = QCheckBox("Enviar a API externa")
        self.api_external_check.setChecked(self.servidor.config["api_external"])
        config_layout.addRow("", self.api_external_check)
        
        self.api_url_input = QLineEdit(self.servidor.config["api_url"])
        self.api_url_input.setEnabled(self.servidor.config["api_external"])
        config_layout.addRow("URL API:", self.api_url_input)
        
        self.api_external_check.stateChanged.connect(
            lambda state: self.api_url_input.setEnabled(state == Qt.CheckState.Checked)
        )
        
        # Añadir grupo de configuración al layout principal
        self.main_layout.addWidget(config_group)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Iniciar Servidor")
        self.start_btn.clicked.connect(self._start_server)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Detener Servidor")
        self.stop_btn.clicked.connect(self._stop_server)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        self.qr_btn = QPushButton("Mostrar QR")
        self.qr_btn.clicked.connect(self.show_qr_dialog)
        self.qr_btn.setEnabled(False)
        button_layout.addWidget(self.qr_btn)
        
        self.main_layout.addLayout(button_layout)
        
        # Estado del servidor
        self.status_label = QLabel("Servidor: Detenido")
        self.main_layout.addWidget(self.status_label)
        
        # Configurar tamaño mínimo
        self.setMinimumSize(QSize(450, 300))
    
    def _select_folder(self):
        """Abre un diálogo para seleccionar la carpeta de distribución."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de distribución",
            self.folder_input.text()
        )
        
        if folder:
            self.folder_input.setText(folder)
    
    def _update_config(self):
        """Actualiza la configuración del servidor con los valores de la UI."""
        config = {
            "host": self.host_input.text(),
            "port": self.port_input.value(),
            "dist_folder": self.folder_input.text(),
            "api_external": self.api_external_check.isChecked(),
            "api_url": self.api_url_input.text(),
            "data_interval": self.interval_input.value(),
            "buffer_size": self.buffer_input.value()
        }
        return self.servidor.set_config(config)
    
    def _start_server(self):
        """Inicia el servidor con la configuración actual."""
        if self._update_config() and self.servidor.start():
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.qr_btn.setEnabled(True)
            
            # Mostrar URL con IP real si es localhost o 0.0.0.0
            host = self.servidor.config['host']
            if host == "localhost" or host == "0.0.0.0" or host == "127.0.0.1":
                ip = self.get_local_ip()
                self.status_label.setText(f"Servidor: Ejecutando en http://{ip}:{self.servidor.config['port']}")
            else:
                self.status_label.setText(f"Servidor: Ejecutando en http://{host}:{self.servidor.config['port']}")
            
            # Crear sesión predeterminada si no existe
            if not self.servidor.config.get("default_session"):
                default_session = self.servidor.create_session("Sesión Predeterminada")
                self.servidor.config["default_session"] = default_session.id
    
    def _stop_server(self):
        """Detiene el servidor."""
        if self.servidor.stop():
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.qr_btn.setEnabled(False)
            self.status_label.setText("Servidor: Detenido")
    
    def set_data_callback(self, callback: Callable):
        """
        Establece la función que proporcionará los datos de bioseñales.
        
        Args:
            callback: Función que retornará los datos de bioseñales en formato JSON.
        """
        return self.servidor.set_data_callback(callback)
    
    def get_server_url(self):
        """
        Retorna la URL completa del servidor.
        
        Returns:
            str: URL del servidor
        """
        host = self.servidor.config["host"]
        port = self.servidor.config["port"]
        if host == "0.0.0.0" or host == "localhost" or host == "127.0.0.1":
            host = self.get_local_ip()
        return f"http://{host}:{port}"
    
    def get_local_ip(self):
        """
        Obtiene la dirección IP local del equipo.
        
        Returns:
            str: Dirección IP local
        """
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.error(f"Error al obtener IP local: {str(e)}")
            return "127.0.0.1"
    
    def show_qr_dialog(self):
        """Muestra un diálogo con el código QR para acceder al servidor."""
        # Verificar si el servidor está ejecutándose
        if not self.servidor.is_running:
            QMessageBox.warning(
                self, 
                "Servidor no iniciado", 
                "Por favor, inicia el servidor antes de mostrar el código QR."
            )
            return
        
        try:
            # Intentar importar las bibliotecas necesarias
            import qrcode
            from io import BytesIO
            from PIL import Image
            import numpy as np
        except ImportError:
            QMessageBox.critical(
                self,
                "Error de importación",
                "Por favor, instala las bibliotecas requeridas: qrcode, pillow, numpy"
            )
            return
        
        # Crear diálogo
        dialog = QDialog(self)
        dialog.setWindowTitle("Acceso al Visualizador")
        layout = QVBoxLayout(dialog)
        
        # Selector de sesión si hay múltiples
        session_layout = QHBoxLayout()
        session_layout.addWidget(QLabel("Sesión:"))
        session_selector = QComboBox()
        
        # Obtener sesiones activas
        active_sessions = self.servidor.session_manager.get_active_sessions()
        for session_id, session in active_sessions.items():
            session_selector.addItem(f"{session.name} ({session_id[:8]}...)", session_id)
        
        session_layout.addWidget(session_selector)
        layout.addLayout(session_layout)
        
        # Obtener URL base del servidor
        base_url = self.get_server_url()
        
        # Crear etiquetas para la información
        info_label = QLabel("Escanea el código QR para acceder al visualizador:")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        url_label = QLabel()
        url_label.setAlignment(Qt.AlignCenter)
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(url_label)
        
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)
        
        # Función para actualizar el QR cuando cambia la sesión
        def update_qr():
            selected_session_id = session_selector.currentData()
            if not selected_session_id:
                return
            
            # Construir URL con parámetro de sesión
            full_url = f"{base_url}?session={selected_session_id}"
            
            # Crear código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(full_url)
            qr.make(fit=True)
            
            # Generar imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a formato que PySide6 pueda manejar
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            pil_img = Image.open(buffer)
            
            # Convertir PIL Image a QImage
            img_array = np.array(pil_img)
            height, width = img_array.shape
            bytes_per_line = width
            q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            
            # Actualizar QR en la etiqueta
            qr_label.setPixmap(QPixmap.fromImage(q_img))
            
            # Actualizar URL en la etiqueta
            url_label.setText(full_url)
        
        # Botones
        buttons_layout = QHBoxLayout()
        copy_btn = QPushButton("Copiar URL")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(url_label.text()))
        buttons_layout.addWidget(copy_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Conectar el selector de sesión
        session_selector.currentIndexChanged.connect(update_qr)
        
        # Generar QR inicial
        if session_selector.count() > 0:
            update_qr()
        
        # Mostrar diálogo
        dialog.setMinimumSize(400, 500)
        dialog.exec()
    
    def _copy_to_clipboard(self, text):
        """Copia texto al portapapeles."""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
    
    def closeEvent(self, event):
        """
        Gestiona el cierre del widget.
        Se llama automáticamente cuando el widget se cierra.
        
        Args:
            event: Evento de cierre
        """
        # Detener servidor al cerrar
        if self.servidor.is_running:
            logger.info("Deteniendo servidor al cerrar widget")
            self.servidor.stop()


# Función para generar datos de ejemplo, útil para pruebas
def generate_example_data():
    """
    Genera datos de ejemplo para el servidor de bioseñales.
    
    Returns:
        dict: Datos en formato JSON compatible con la especificación
    """
    # Variables estáticas para mantener estado entre llamadas
    if not hasattr(generate_example_data, "ecg_phase"):
        generate_example_data.ecg_phase = 0
        generate_example_data.resp_phase = 0
    
    # Avanzar fases
    generate_example_data.ecg_phase += 0.3
    generate_example_data.resp_phase += 0.15
    
    # Timestamp común
    timestamp = int(time.time() * 1000)
    
    # Crear datos simulados para ECG
    ecg_data = []
    for i in range(50):
        phase = generate_example_data.ecg_phase + (i * 0.063)
        value = 0.5 * math.sin(phase)
        
        # Añadir pico QRS ocasional
        if (phase % (2 * math.pi)) < 0.2:
            value += 0.8 * math.exp(-((phase % (2 * math.pi)) - 0.1) ** 2 / 0.01)
        
        # Añadir ruido
        value += random.uniform(-0.05, 0.05)
        ecg_data.append(value)
    
    # Crear datos simulados para respiración
    resp_data = []
    for i in range(50):
        phase = generate_example_data.resp_phase + (i * 0.031)
        value = 2.5 + 0.8 * math.sin(phase)
        value += random.uniform(-0.03, 0.03)
        resp_data.append(value)
    
    # Generar timestamps para cada punto
    ecg_timestamps = [timestamp + i * 4 for i in range(len(ecg_data))]
    resp_timestamps = [timestamp + i * 10 for i in range(len(resp_data))]
    
    # Construir datos en formato compatible
    data = {
        "session": {
            "id": "session-demo",
            "timestamp": timestamp,
            "name": "Registro de bioseñales - Demo",
            "status": "active",
            "connectedClients": 0
        },
        "visualization": {
            "mode": "realtime",
            "timeWindow": 10000,
            "autoScale": True,
            "gridEnabled": True,
            "theme": "light",
            "layout": "single",
            "signalsVisible": ["ecg", "resp"]
        },
        "signals": {
            "ecg": {
                "name": "Electrocardiograma",
                "unit": "mV",
                "color": "#4caf50",
                "visible": True,
                "yAxisRange": [-1, 1],
                "data": ecg_data,
                "timestamps": ecg_timestamps,
                "sampleRate": 250,
                "displayOrder": 1
            },
            "resp": {
                "name": "Respiración",
                "unit": "L/min",
                "color": "#2196f3",
                "visible": True,
                "yAxisRange": [0, 5],
                "data": resp_data,
                "timestamps": resp_timestamps,
                "sampleRate": 100,
                "displayOrder": 2
            }
        },
        "tools": {
            "enabled": ["labels", "draw", "measure"],
            "labels": {
                "predefined": [
                    {"id": "p-wave", "text": "Onda P", "color": "#ff6384", "icon": "triangle"},
                    {"id": "qrs", "text": "Complejo QRS", "color": "#36a2eb", "icon": "square"},
                    {"id": "t-wave", "text": "Onda T", "color": "#ffcd56", "icon": "circle"}
                ],
                "custom": []
            },
            "draw": {
                "strokeWidth": 2,
                "color": "#ff0000",
                "paths": []
            },
            "measure": {
                "timeUnit": "ms",
                "amplitudeUnits": {"ecg": "mV", "resp": "L/min"},
                "measurements": []
            }
        }
    }
    
    return data


# Código para probar el widget de forma independiente
if __name__ == "__main__":
    # Este bloque solo se ejecuta si se llama directamente a este script
    app = QApplication(sys.argv)
    widget = ServidorWebWidget()
    
    # Establecer función para generar datos de ejemplo
    widget.set_data_callback(generate_example_data)
    
    # Mostrar widget como ventana independiente
    widget.setWindowTitle("Control del Servidor de Bioseñales")
    widget.show()
    
    sys.exit(app.exec())
