import os
import sys
import json
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Union, Optional, Callable

# Importaciones para el servidor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ServidorWeb")

class WebSocketManager:
    """Gestor de conexiones WebSocket."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nueva conexión WebSocket. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Conexión WebSocket cerrada. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Envía datos a todos los clientes conectados."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando datos: {str(e)}")
                disconnected.append(connection)
        
        # Eliminar conexiones cerradas
        for conn in disconnected:
            self.disconnect(conn)


class ServidorBiosenales:
    """Servidor para servir la aplicación Vite y enviar datos de bioseñales por WebSocket."""
    
    def __init__(self):
        self.app = FastAPI()
        self.ws_manager = WebSocketManager()
        self.server = None
        self.is_running = False
        self.config = {
            "host": "localhost",
            "port": 8000,
            "dist_folder": "dist",  # Carpeta donde está tu build de Vite
            "api_external": False,  # Si es True, enviará datos a una API externa
            "api_url": "",
            "data_interval": 100  # Intervalo de envío de datos en ms
        }
        self.thread = None
        self.stop_event = threading.Event()
        self.data_callback = None  # Función que proporcionará datos de bioseñales
        
        # Configurar rutas
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas del servidor."""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.ws_manager.connect(websocket)
            try:
                while True:
                    # Solo mantenemos la conexión abierta
                    # Los datos se envían mediante broadcast desde otro hilo
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.ws_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"Error en WebSocket: {str(e)}")
                self.ws_manager.disconnect(websocket)
    
    def _mount_static_files(self):
        """Monta los archivos estáticos de la aplicación Vite."""
        static_folder = Path(self.config["dist_folder"])
        if static_folder.exists():
            self.app.mount("/", StaticFiles(directory=str(static_folder), html=True), name="static")
            logger.info(f"Archivos estáticos montados desde: {static_folder}")
        else:
            logger.warning(f"Carpeta de archivos estáticos no encontrada: {static_folder}")
    
    def set_config(self, config: Dict):
        """Actualiza la configuración del servidor."""
        self.config.update(config)
        logger.info(f"Configuración actualizada: {self.config}")
        return True
    
    def set_data_callback(self, callback: Callable):
        """Establece la función que proporcionará los datos de bioseñales."""
        self.data_callback = callback
        return True
    
    def _run_server(self):
        """Ejecuta el servidor en un proceso separado."""
        config = uvicorn.Config(
            app=self.app,
            host=self.config["host"],
            port=self.config["port"],
            log_level="error"
        )
        self.server = uvicorn.Server(config)
        self.is_running = True
        self.server.run()
        self.is_running = False
        logger.info("Servidor detenido")
    
    def _data_sender(self):
        """Envía datos periódicamente a los clientes WebSocket."""
        logger.info("Iniciando envío de datos")
        
        while not self.stop_event.is_set():
            if self.data_callback:
                try:
                    # Obtener datos desde la callback
                    data = self.data_callback()
                    
                    if self.config["api_external"] and self.config["api_url"]:
                        # TODO: Implementar envío a API externa
                        pass
                    
                    # Crear tarea asíncrona para enviar datos por WebSocket
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.ws_manager.broadcast(data))
                    
                except Exception as e:
                    logger.error(f"Error enviando datos: {str(e)}")
            
            # Esperar el intervalo configurado
            time.sleep(self.config["data_interval"] / 1000)
    
    def start(self):
        """Inicia el servidor y el envío de datos en hilos separados."""
        if self.is_running:
            logger.warning("El servidor ya está en ejecución")
            return False
        
        # Montar archivos estáticos
        self._mount_static_files()
        
        # Iniciar servidor en un hilo
        self.stop_event.clear()
        self.thread_server = threading.Thread(target=self._run_server)
        self.thread_server.daemon = True
        self.thread_server.start()
        
        # Iniciar envío de datos en otro hilo
        self.thread_data = threading.Thread(target=self._data_sender)
        self.thread_data.daemon = True
        self.thread_data.start()
        
        logger.info(f"Servidor iniciado en http://{self.config['host']}:{self.config['port']}")
        return True
    
    def stop(self):
        """Detiene el servidor y el envío de datos."""
        if not self.is_running:
            logger.warning("El servidor no está en ejecución")
            return False
        
        logger.info("Deteniendo servidor...")
        self.stop_event.set()
        
        if self.server:
            self.server.should_exit = True
        
        return True


# Componente PySide6 para configurar y gestionar el servidor
class ServidorWebConfigUI:
    """Componente de UI para configurar y gestionar el servidor web desde la aplicación PySide6."""
    
    def __init__(self, parent=None):
        from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                                      QLabel, QLineEdit, QSpinBox, QCheckBox, 
                                      QPushButton, QGroupBox, QFileDialog)
        from PySide6.QtCore import Qt, QSize
        
        self.servidor = ServidorBiosenales()
        
        # Crear widget principal
        self.widget = QWidget(parent)
        self.main_layout = QVBoxLayout(self.widget)
        
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
        
        # Configurar tamaño
        self.widget.setMinimumSize(QSize(400, 300))
    
    def _select_folder(self):
        """Abre un diálogo para seleccionar la carpeta de distribución."""
        from PySide6.QtWidgets import QFileDialog
        
        folder = QFileDialog.getExistingDirectory(
            self.widget,
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
            "data_interval": self.interval_input.value()
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
    
    def _stop_server(self):
        """Detiene el servidor."""
        if self.servidor.stop():
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.qr_btn.setEnabled(False)
            self.status_label.setText("Servidor: Detenido")
    
    def set_data_callback(self, callback):
        """Establece la función que proporcionará los datos de bioseñales."""
        return self.servidor.set_data_callback(callback)
    
    def get_widget(self):
        """Retorna el widget para incluirlo en la aplicación principal."""
        return self.widget
    
    def get_server_url(self):
        """Retorna la URL del servidor."""
        host = self.servidor.config["host"]
        port = self.servidor.config["port"]
        if host == "0.0.0.0" or host == "localhost":
            host = self.get_local_ip()
        return f"http://{host}:{port}"
    
    def get_local_ip(self):
        """Obtiene la dirección IP local del equipo."""
        import socket
        try:
            # Crear una conexión para obtener la IP (no se establece realmente)
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
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
        from PySide6.QtGui import QPixmap, QImage
        from PySide6.QtCore import Qt
        import qrcode
        from io import BytesIO
        from PIL import Image
        import numpy as np
        
        # Verificar si el servidor está ejecutándose
        if not self.servidor.is_running:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.widget, 
                "Servidor no iniciado", 
                "Por favor, inicia el servidor antes de mostrar el código QR."
            )
            return
        
        # Obtener URL del servidor
        url = self.get_server_url()
        
        # Crear código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
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
        
        # Crear QPixmap desde QImage
        pixmap = QPixmap.fromImage(q_img)
        
        # Crear diálogo
        dialog = QDialog(self.widget)
        dialog.setWindowTitle("Escanear para conectar")
        layout = QVBoxLayout(dialog)
        
        # Etiqueta con información
        info_label = QLabel(f"Escanea el código QR para acceder al visualizador:")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Etiqueta con URL
        url_label = QLabel(url)
        url_label.setAlignment(Qt.AlignCenter)
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(url_label)
        
        # Etiqueta con QR
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)
        
        # Mostrar diálogo
        dialog.setMinimumSize(400, 450)
        dialog.exec()
    
    def closeEvent(self):
        """Se llama cuando se cierra la aplicación principal."""
        self.servidor.stop()


# Ejemplo de uso
if __name__ == "__main__":
    # Este ejemplo muestra cómo usar el componente en una aplicación PySide6
    from PySide6.QtWidgets import QApplication, QMainWindow
    import sys
    
    # Callback de ejemplo para proporcionar datos
    def get_biosignal_data():
        import random
        import time
        
        # Simular datos de ECG
        ecg_data = [random.uniform(0, 1) for _ in range(50)]
        
        return {
            "timestamp": int(time.time() * 1000),
            "ecg": ecg_data,
            "heart_rate": random.randint(60, 100)
        }
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Demo Servidor Web para Bioseñales")
    
    # Crear el componente de configuración
    server_config = ServidorWebConfigUI(window)
    
    # Establecer la función que proporcionará los datos
    server_config.set_data_callback(get_biosignal_data)
    
    # Establecer como widget central
    window.setCentralWidget(server_config.get_widget())
    
    # Asegurar que el servidor se detenga al cerrar la aplicación
    original_close_event = window.closeEvent
    def close_handler(event):
        server_config.closeEvent()
        if original_close_event:
            original_close_event(event)
    window.closeEvent = close_handler
    
    window.resize(500, 400)
    window.show()
    
    sys.exit(app.exec())
