import time
import uuid
import logging
from typing import Dict, Set, Optional, Any

logger = logging.getLogger("ServidorBiosenales")

class Session:
    """Representa una sesión de visualización de bioseñales."""
    
    def __init__(self, session_id: str = None, name: str = None):
        """
        Inicializa una nueva sesión.
        
        Args:
            session_id: ID único de la sesión. Si es None, se genera uno automáticamente.
            name: Nombre descriptivo de la sesión.
        """
        self.id = session_id or str(uuid.uuid4())
        self.name = name or f"Sesión {self.id[:8]}"
        self.clients: Set[str] = set()  # Conjunto de IDs de clientes WebSocket
        self.created_at = int(time.time() * 1000)
        self.status = "active"  # "active" o "closed"
        self.client_count = 0
        
        # Último estado de datos para retransmitir a clientes que se reconectan
        self.last_data: Optional[Dict[str, Any]] = None
        
        # Configuración de visualización
        self.configuration = {
            "mode": "realtime",
            "layout": "single",  # "single", "vertical", "horizontal"
            "theme": "light",
            "autoScale": True,
            "timeWindow": 10000,  # ms
            "gridEnabled": True,
            "signalsVisible": []  # IDs de señales visibles
        }
        
        logger.info(f"Sesión creada: {self.id} - {self.name}")
    
    def add_client(self, client_id: str) -> bool:
        """
        Añade un cliente a la sesión.
        
        Args:
            client_id: ID único del cliente WebSocket.
            
        Returns:
            bool: True si se añadió correctamente, False si ya estaba.
        """
        if client_id in self.clients:
            return False
        
        self.clients.add(client_id)
        self.update_client_count()
        logger.info(f"Cliente {client_id} añadido a sesión {self.id}. Total: {self.client_count}")
        return True
    
    def remove_client(self, client_id: str) -> bool:
        """
        Elimina un cliente de la sesión.
        
        Args:
            client_id: ID único del cliente WebSocket.
            
        Returns:
            bool: True si se eliminó correctamente, False si no existía.
        """
        if client_id not in self.clients:
            return False
        
        self.clients.remove(client_id)
        self.update_client_count()
        logger.info(f"Cliente {client_id} eliminado de sesión {self.id}. Total: {self.client_count}")
        return True
    
    def update_client_count(self) -> None:
        """Actualiza el contador de clientes conectados."""
        self.client_count = len(self.clients)
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """
        Actualiza la configuración de visualización.
        
        Args:
            config: Diccionario con los parámetros a actualizar.
        """
        self.configuration.update(config)
        logger.info(f"Configuración actualizada para sesión {self.id}: {config}")
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Actualiza los últimos datos de la sesión.
        
        Args:
            data: Datos actualizados de bioseñales.
        """
        self.last_data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la sesión a un diccionario para serialización JSON.
        
        Returns:
            Dict: Representación en diccionario de la sesión.
        """
        return {
            "session": {
                "id": self.id,
                "name": self.name,
                "timestamp": self.created_at,
                "status": self.status,
                "connectedClients": self.client_count,
                "accessUrl": f"/s/{self.id}"  # URL relativa
            },
            "visualization": self.configuration
        }
    
    def close(self) -> None:
        """Marca la sesión como cerrada."""
        self.status = "closed"
        logger.info(f"Sesión {self.id} cerrada")


class SessionManager:
    """Gestiona las sesiones de visualización de bioseñales."""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}  # Diccionario de sesiones por ID
        self.client_to_session: Dict[str, str] = {}  # Mapeo client_id -> session_id
        logger.info("SessionManager inicializado")
    
    def create_session(self, name: Optional[str] = None) -> Session:
        """
        Crea una nueva sesión.
        
        Args:
            name: Nombre opcional para la sesión.
            
        Returns:
            Session: La sesión creada.
        """
        session = Session(name=name)
        self.sessions[session.id] = session
        logger.info(f"Nueva sesión creada: {session.id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Obtiene una sesión por su ID.
        
        Args:
            session_id: ID de la sesión.
            
        Returns:
            Optional[Session]: La sesión si existe, None en caso contrario.
        """
        return self.sessions.get(session_id)
    
    def get_session_by_client(self, client_id: str) -> Optional[Session]:
        """
        Obtiene la sesión a la que pertenece un cliente.
        
        Args:
            client_id: ID del cliente.
            
        Returns:
            Optional[Session]: La sesión si existe, None en caso contrario.
        """
        session_id = self.client_to_session.get(client_id)
        if session_id:
            return self.get_session(session_id)
        return None
    
    def get_active_sessions(self) -> Dict[str, Session]:
        """
        Obtiene todas las sesiones activas.
        
        Returns:
            Dict[str, Session]: Diccionario de sesiones activas.
        """
        return {sid: session for sid, session in self.sessions.items() 
                if session.status == "active"}
    
    def add_client_to_session(self, session_id: str, client_id: str) -> bool:
        """
        Añade un cliente a una sesión.
        
        Args:
            session_id: ID de la sesión.
            client_id: ID del cliente.
            
        Returns:
            bool: True si se añadió correctamente, False en caso contrario.
        """
        # Primero verificar si el cliente ya está en otra sesión
        if client_id in self.client_to_session:
            old_session_id = self.client_to_session[client_id]
            # Si es la misma sesión, no hacer nada
            if old_session_id == session_id:
                return True
            # Eliminar de la sesión anterior
            old_session = self.get_session(old_session_id)
            if old_session:
                old_session.remove_client(client_id)
        
        # Añadir a la nueva sesión
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Intento de añadir cliente {client_id} a sesión inexistente {session_id}")
            return False
        
        success = session.add_client(client_id)
        if success:
            self.client_to_session[client_id] = session_id
        return success
    
    def remove_client_from_session(self, client_id: str) -> bool:
        """
        Elimina un cliente de su sesión actual.
        
        Args:
            client_id: ID del cliente.
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario.
        """
        session_id = self.client_to_session.get(client_id)
        if not session_id:
            return False
        
        session = self.get_session(session_id)
        if not session:
            return False
        
        success = session.remove_client(client_id)
        if success:
            del self.client_to_session[client_id]
        return success
    
    def close_session(self, session_id: str) -> bool:
        """
        Cierra una sesión existente.
        
        Args:
            session_id: ID de la sesión a cerrar.
            
        Returns:
            bool: True si se cerró correctamente, False en caso contrario.
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Cerrar la sesión
        session.close()
        
        # Eliminar mapeos de clientes
        client_ids = list(session.clients)
        for client_id in client_ids:
            session.remove_client(client_id)
            if client_id in self.client_to_session:
                del self.client_to_session[client_id]
        
        logger.info(f"Sesión {session_id} cerrada y todos los clientes ({len(client_ids)}) desconectados")
        return True
    
    def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de una sesión.
        
        Args:
            session_id: ID de la sesión.
            data: Nuevos datos.
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario.
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.update_data(data)
        return True
    
    def get_client_ids_in_session(self, session_id: str) -> Set[str]:
        """
        Obtiene los IDs de los clientes en una sesión.
        
        Args:
            session_id: ID de la sesión.
            
        Returns:
            Set[str]: Conjunto de IDs de clientes.
        """
        session = self.get_session(session_id)
        if not session:
            return set()
        
        return session.clients.copy()  # Devolver copia para evitar modificaciones accidentales
