import os
import sys
import json
import time
import threading
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Union, Optional, Callable, Set, Any

# Importaciones para el servidor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

# Importar las clases de gestión de sesiones
from Session import Session, SessionManager

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ServidorBiosenales")

class WebSocketManager:
    """Gestor de conexiones WebSocket con soporte para sesiones."""
    
    def __init__(self, session_manager: SessionManager):
        self.active_connections: Dict[str, WebSocket] = {}  # client_id -> WebSocket
        self.session_manager = session_manager
    
    async def connect(self, websocket: WebSocket) -> str:
        """
        Establece una conexión WebSocket.
        
        Args:
            websocket: Conexión WebSocket entrante.
            
        Returns:
            str: ID generado para el cliente.
        """
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        logger.info(f"Nueva conexión WebSocket: {client_id}. Total: {len(self.active_connections)}")
        return client_id
    
    def disconnect(self, client_id: str) -> None:
        """
        Cierra una conexión WebSocket.
        
        Args:
            client_id: ID del cliente a desconectar.
        """
        if client_id in self.active_connections:
            # Eliminar de la sesión si estaba en una
            self.session_manager.remove_client_from_session(client_id)
            # Eliminar la conexión
            del self.active_connections[client_id]
            logger.info(f"Conexión WebSocket cerrada: {client_id}. Total: {len(self.active_connections)}")
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """
        Envía un mensaje a un cliente específico.
        
        Args:
            client_id: ID del cliente destinatario.
            message: Mensaje a enviar en formato JSON.
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario.
        """
        if client_id not in self.active_connections:
            logger.warning(f"Intento de enviar mensaje a cliente inexistente: {client_id}")
            return False
        
        try:
            await self.active_connections[client_id].send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a cliente {client_id}: {str(e)}")
            # Si hay error, desconectar el cliente
            self.disconnect(client_id)
            return False
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any], exclude_client: Optional[str] = None) -> int:
        """
        Envía un mensaje a todos los clientes en una sesión específica.
        
        Args:
            session_id: ID de la sesión.
            message: Mensaje a enviar en formato JSON.
            exclude_client: ID de cliente a excluir del broadcast (opcional).
            
        Returns:
            int: Número de clientes a los que se envió el mensaje correctamente.
        """
        # Obtener clientes en la sesión
        client_ids = self.session_manager.get_client_ids_in_session(session_id)
        
        # Filtrar cliente excluido si es necesario
        if exclude_client and exclude_client in client_ids:
            client_ids.remove(exclude_client)
        
        success_count = 0
        for client_id in client_ids:
            if await self.send_to_client(client_id, message):
                success_count += 1
        
        return success_count
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> int:
        """
        Envía un mensaje a todos los clientes conectados.
        
        Args:
            message: Mensaje a enviar en formato JSON.
            
        Returns:
            int: Número de clientes a los que se envió el mensaje correctamente.
        """
        disconnected = []
        success_count = 0
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
                success_count += 1
            except Exception as e:
                logger.error(f"Error enviando a {client_id}: {str(e)}")
                disconnected.append(client_id)
        
        # Eliminar conexiones cerradas
        for client_id in disconnected:
            self.disconnect(client_id)
        
        return success_count


class ServidorBiosenales:
    """Servidor para servir la aplicación y gestionar sesiones de bioseñales."""
    
    def __init__(self):
        self.app = FastAPI()
        self.session_manager = SessionManager()
        self.ws_manager = WebSocketManager(self.session_manager)
        
        self.server = None
        self.is_running = False
        self.config = {
            "host": "0.0.0.0",  # Escuchar en todas las interfaces
            "port": 8000,
            "dist_folder": "dist",  # Carpeta donde está tu build de Vite
            "api_external": False,  # Si es True, enviará datos a una API externa
            "api_url": "",
            "data_interval": 100,  # Intervalo de envío de datos en ms
            "buffer_size": 1000,   # Cantidad de puntos a mantener en buffer por señal
            "default_session": None  # ID de sesión por defecto, None para crear automáticamente
        }
        
        self.stop_event = threading.Event()
        self.data_callback = None  # Función que proporcionará datos de bioseñales
        
        # Inicializar las rutas
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas del servidor."""
        
        # Ruta para WebSocket
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            client_id = await self.ws_manager.connect(websocket)
            session_id = None
            
            try:
                while True:
                    # Esperar mensajes del cliente
                    message = await websocket.receive_json()
                    
                    # Procesar mensaje según su tipo
                    message_type = message.get("type", "")
                    
                    if message_type == "join_session":
                        # Unirse a una sesión
                        requested_session = message.get("session_id")
                        
                        # Si no se especifica sesión, usar la predeterminada o crear una nueva
                        if not requested_session:
                            if self.config["default_session"]:
                                requested_session = self.config["default_session"]
                            else:
                                # Crear nueva sesión
                                session = self.session_manager.create_session(message.get("name"))
                                requested_session = session.id
                        
                        # Verificar si la sesión existe
                        session = self.session_manager.get_session(requested_session)
                        if not session:
                            await websocket.send_json({
                                "type": "error",
                                "message": "Sesión no encontrada"
                            })
                            continue
                        
                        # Añadir cliente a la sesión
                        self.session_manager.add_client_to_session(requested_session, client_id)
                        session_id = requested_session
                        
                        # Enviar confirmación y datos de la sesión
                        await websocket.send_json({
                            "type": "session_joined",
                            "session": session.to_dict()
                        })
                        
                        # Enviar datos actuales si existen
                        if session.last_data:
                            await websocket.send_json({
                                "type": "data_update",
                                "data": session.last_data
                            })
                    
                    elif message_type == "leave_session":
                        # Salir de la sesión actual
                        if session_id:
                            self.session_manager.remove_client_from_session(client_id)
                            session_id = None
                            await websocket.send_json({
                                "type": "session_left"
                            })
                    
                    elif message_type == "update_config":
                        # Actualizar configuración de la sesión
                        if not session_id:
                            await websocket.send_json({
                                "type": "error",
                                "message": "No estás en ninguna sesión"
                            })
                            continue
                        
                        config_data = message.get("config", {})
                        session = self.session_manager.get_session(session_id)
                        if session:
                            session.update_configuration(config_data)
                            
                            # Notificar a todos los clientes en la sesión
                            await self.ws_manager.broadcast_to_session(
                                session_id,
                                {
                                    "type": "config_updated",
                                    "config": session.configuration
                                },
                                exclude_client=client_id  # No reenviar al emisor
                            )
                    
                    elif message_type == "tool_action":
                        # Acciones de herramientas (etiquetas, dibujos, mediciones)
                        if not session_id:
                            await websocket.send_json({
                                "type": "error",
                                "message": "No estás en ninguna sesión"
                            })
                            continue
                        
                        # Retransmitir la acción a todos los demás clientes en la sesión
                        tool_data = message.get("data", {})
                        await self.ws_manager.broadcast_to_session(
                            session_id,
                            {
                                "type": "tool_update",
                                "tool": message.get("tool", "unknown"),
                                "data": tool_data,
                                "client_id": client_id
                            },
                            exclude_client=client_id  # No reenviar al emisor
                        )
            
            except WebSocketDisconnect:
                # Desconectar el cliente
                self.ws_manager.disconnect(client_id)
            except Exception as e:
                logger.error(f"Error en WebSocket ({client_id}): {str(e)}")
                self.ws_manager.disconnect(client_id)
        
        # Rutas HTTP para API REST
        @self.app.get("/api/sessions")
        async def get_sessions():
            """Retorna todas las sesiones activas."""
            active_sessions = self.session_manager.get_active_sessions()
            return [session.to_dict() for session in active_sessions.values()]
        
        @self.app.get("/api/session/{session_id}")
        async def get_session(session_id: str):
            """Retorna información de una sesión específica."""
            session = self.session_manager.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Sesión no encontrada")
            return session.to_dict()
        
        @self.app.post("/api/session/create")
        async def create_session(name: Optional[str] = None):
            """Crea una nueva sesión."""
            session = self.session_manager.create_session(name)
            return session.to_dict()
        
        @self.app.post("/api/session/{session_id}/close")
        async def close_session(session_id: str):
            """Cierra una sesión existente."""
            success = self.session_manager.close_session(session_id)
            if not success:
                raise HTTPException(status_code=404, detail="Sesión no encontrada")
            return {"success": True}
    
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
    
    def create_session(self, name: Optional[str] = None) -> str:
        """
        Crea una nueva sesión.
        
        Args:
            name: Nombre opcional para la sesión.
            
        Returns:
            str: ID de la sesión creada.
        """
        session = self.session_manager.create_session(name)
        return session.id
    
    def close_session(self, session_id: str) -> bool:
        """
        Cierra una sesión existente.
        
        Args:
            session_id: ID de la sesión a cerrar.
            
        Returns:
            bool: True si se cerró correctamente, False en caso contrario.
        """
        return self.session_manager.close_session(session_id)
    
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
        import asyncio
        
        async def send_data():
            while not self.stop_event.is_set():
                if self.data_callback:
                    try:
                        # Obtener datos del callback
                        data = self.data_callback()
                        
                        if data:
                            # Verificar si hay un ID de sesión en los datos
                            session_id = None
                            if isinstance(data, dict) and "session" in data:
                                session_id = data.get("session", {}).get("id")
                            
                            if session_id:
                                # Enviar datos solo a esa sesión
                                session = self.session_manager.get_session(session_id)
                                if session:
                                    # Guardar datos para clientes que se reconecten
                                    session.update_data(data)
                                    # Enviar a todos los clientes en la sesión
                                    await self.ws_manager.broadcast_to_session(
                                        session_id,
                                        {
                                            "type": "data_update",
                                            "data": data
                                        }
                                    )
                            else:
                                # Si no hay sesión especificada, crear una predeterminada si no existe
                                if not self.config["default_session"]:
                                    default_session = self.session_manager.create_session("Sesión Predeterminada")
                                    self.config["default_session"] = default_session.id
                                
                                # Enviar a la sesión predeterminada
                                default_id = self.config["default_session"]
                                session = self.session_manager.get_session(default_id)
                                if session:
                                    # Guardar datos
                                    session.update_data(data)
                                    # Enviar a todos los clientes en la sesión predeterminada
                                    await self.ws_manager.broadcast_to_session(
                                        default_id,
                                        {
                                            "type": "data_update",
                                            "data": data
                                        }
                                    )
                    except Exception as e:
                        logger.error(f"Error procesando o enviando datos: {str(e)}")
                
                # Esperar hasta el próximo intervalo
                await asyncio.sleep(self.config["data_interval"] / 1000)
        
        # Crear y ejecutar el loop asíncrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(send_data())
        finally:
            loop.close()
    
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
        
        # Cerrar todas las sesiones activas
        active_sessions = list(self.session_manager.get_active_sessions().keys())
        for session_id in active_sessions:
            self.session_manager.close_session(session_id)
        
        return True

# Mantener la clase ServidorWebConfigUI compatible con la versión actualizada
class ServidorWebConfigUI:
    """Componente de UI para configurar y gestionar el servidor web desde la aplicación PySide6."""
    
    def __init__(self, parent=None):
        from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                                      QLabel, QLineEdit, QSpinBox, QCheckBox, 
                                      QPushButton, QGroupBox, QFileDialog, QComboBox,
                                      QTableWidget, QTableWidgetItem, QHeaderView)
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
        
        # Grupo de gestión de sesiones
        session_group = QGroupBox("Gestión de Sesiones")
        session_layout = QVBoxLayout(session_group)
        
        # Tabla de sesiones
        self.sessions_table = QTableWidget(0, 4)  # filas, columnas
        self.sessions_table.setHorizontalHeaderLabels(["ID", "Nombre", "Clientes", "Estado"])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        session_layout.addWidget(self.sessions_table)
        
        # Botones de sesión
        session_buttons = QHBoxLayout()
        
        self.new_session_btn = QPushButton("Nueva Sesión")
        self.new_session_btn.clicked.connect(self._create_new_session)
        session_buttons.addWidget(self.new_session_btn)
        
        self.close_session_btn = QPushButton("Cerrar Sesión")
        self.close_session_btn.clicked.connect(self._close_selected_session)
        self.close_session_btn.setEnabled(False)
        session_buttons.addWidget(self.close_session_btn)
        
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.clicked.connect(self._refresh_sessions)
        session_buttons.addWidget(self.refresh_btn)
        
        session_layout.addLayout(session_buttons)
        
        # Añadir grupo de sesiones al layout principal
        self.main_layout.addWidget(session_group)
        
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
        self.widget.setMinimumSize(QSize(600, 500))
        
        # Conexiones de tabla
        self.sessions_table.itemSelectionChanged.connect(self._update_session_buttons)
        
        # Temporizador para actualizar las sesiones (cada 5 segundos)
        from PySide6.QtCore import QTimer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_sessions)
        self.refresh_timer.start(5000)  # 5000 ms = 5 segundos
    
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
            "data_interval": self.interval_input.value(),
            "buffer_size": self.buffer_input.value()
        }
        return self.servidor.set_config(config)
    
    def _create_new_session(self):
        """Crea una nueva sesión."""
        from PySide6.QtWidgets import QInputDialog
        
        session_name, ok = QInputDialog.getText(
            self.widget,
            "Nueva Sesión",
            "Nombre de la sesión:"
        )
        
        if ok and session_name:
            session_id = self.servidor.create_session(session_name)
            self._refresh_sessions()
    
    def _close_selected_session(self):
        """Cierra la sesión seleccionada en la tabla."""
        selected_items = self.sessions_table.selectedItems()
        if not selected_items:
            return
        
        # Obtener ID de la sesión seleccionada (primera columna)
        row = selected_items[0].row()
        session_id = self.sessions_table.item(row, 0).text()
        
        # Cerrar la sesión
        self.servidor.close_session(session_id)
        self._refresh_sessions()
    
    def _update_session_buttons(self):
        """Actualiza el estado de los botones de sesión según la selección."""
        self.close_session_btn.setEnabled(len(self.sessions_table.selectedItems()) > 0)
    
    def _refresh_sessions(self):
        """Actualiza la tabla de sesiones con los datos actuales."""
        if not self.servidor.is_running:
            # Limpiar tabla si el servidor no está en ejecución
            self.sessions_table.setRowCount(0)
            return
        
        active_sessions = self.servidor.session_manager.get_active_sessions()
        self.sessions_table.setRowCount(len(active_sessions))
        
        for i, (session_id, session) in enumerate(active_sessions.items()):
            # ID
            id_item = QTableWidgetItem(session_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # No editable
            self.sessions_table.setItem(i, 0, id_item)
            
            # Nombre
            name_item = QTableWidgetItem(session.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.sessions_table.setItem(i, 1, name_item)
            
            # Clientes
            clients_item = QTableWidgetItem(str(session.client_count))
            clients_item.setFlags(clients_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.sessions_table.setItem(i, 2, clients_item)
            
            # Estado
            status_item = QTableWidgetItem(session.status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.sessions_table.setItem(i, 3, status_item)
    
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
            if not self.servidor.config["default_session"]:
                default_session = self.servidor.create_session("Sesión Predeterminada")
                self.servidor.config["default_session"] = default_session.id
            
            # Actualizar tabla de sesiones
            self._refresh_sessions()
    
    def _stop_server(self):
        """Detiene el servidor."""
        if self.servidor.stop():
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.qr_btn.setEnabled(False)
            self.status_label.setText("Servidor: Detenido")
            
            # Limpiar tabla de sesiones
            self.sessions_table.setRowCount(0)
    
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
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QPushButton
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
        
        # Crear diálogo
        dialog = QDialog(self.widget)
        dialog.setWindowTitle("Acceso al Visualizador")
        layout = QVBoxLayout(dialog)
        
        # Selector de sesión
        session_layout = QHBoxLayout()
        session_layout.addWidget(QLabel("Sesión:"))
        session_selector = QComboBox()
        
        # Obtener sesiones activas
        active_sessions = self.servidor.session_manager.get_active_sessions()
        for session_id, session in active_sessions.items():
            session_selector.addItem(f"{session.name} ({session_id})", session_id)
        
        session_layout.addWidget(session_selector)
        layout.addLayout(session_layout)
        
        # Obtener URL del servidor
        base_url = self.get_server_url()
        
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
        
        # Etiqueta con información
        info_label = QLabel("Escanea el código QR para acceder al visualizador:")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Etiqueta para la URL
        url_label = QLabel()
        url_label.setAlignment(Qt.AlignCenter)
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(url_label)
        
        # Etiqueta para el QR
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)
        
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
        dialog.setMinimumSize(500, 600)
        dialog.exec()
    
    def _copy_to_clipboard(self, text):
        """Copia texto al portapapeles."""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
    
    def closeEvent(self):
        """Se llama cuando se cierra la aplicación principal."""
        # Detener temporizador
        self.refresh_timer.stop()
        # Detener servidor
        self.servidor.stop()
