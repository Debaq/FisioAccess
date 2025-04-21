"""
Ejemplo de integración del ServidorBiosenales con sistemas de adquisición de datos.

Este script muestra cómo integrar el servidor con un sistema real o simulado
de adquisición de bioseñales, usando buffers circulares para gestionar datos
y formatearlos adecuadamente antes de enviarlos al visualizador.
"""

import time
import random
import math
import numpy as np
import threading
import logging
import queue
from collections import deque
from typing import Dict, List, Any, Optional
from server_fisioaccess import ServidorBiosenales

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AcquisitionSystem")

class CircularBuffer:
    """Buffer circular para almacenar valores y timestamps."""
    
    def __init__(self, max_size: int = 5000):
        self.values = deque(maxlen=max_size)
        self.timestamps = deque(maxlen=max_size)
    
    def add(self, value: float, timestamp: Optional[int] = None):
        """
        Añade un valor y su timestamp al buffer.
        
        Args:
            value: Valor a añadir
            timestamp: Timestamp en ms, si es None se usa el tiempo actual
        """
        self.values.append(value)
        self.timestamps.append(timestamp or int(time.time() * 1000))
    
    def add_batch(self, values: List[float], timestamps: Optional[List[int]] = None):
        """
        Añade múltiples valores y timestamps al buffer.
        
        Args:
            values: Lista de valores a añadir
            timestamps: Lista de timestamps, si es None se generan automáticamente
        """
        current_time = int(time.time() * 1000)
        
        if timestamps is None:
            # Generar timestamps equiespaciados
            timestamps = [current_time + i for i in range(len(values))]
        
        for value, ts in zip(values, timestamps):
            self.add(value, ts)
    
    def get_latest(self, window_ms: int = 10000) -> tuple:
        """
        Obtiene los valores más recientes dentro de una ventana de tiempo.
        
        Args:
            window_ms: Ventana de tiempo en milisegundos
            
        Returns:
            tuple: (valores, timestamps) dentro de la ventana
        """
        if not self.timestamps:
            return [], []
        
        latest_time = self.timestamps[-1]
        threshold = latest_time - window_ms
        
        # Encontrar el índice donde comienza la ventana de tiempo
        idx = 0
        for i, ts in enumerate(self.timestamps):
            if ts >= threshold:
                idx = i
                break
        
        # Extraer valores y timestamps dentro de la ventana
        return list(self.values)[idx:], list(self.timestamps)[idx:]
    
    def clear(self):
        """Limpia el buffer."""
        self.values.clear()
        self.timestamps.clear()


class BioseñalAdquisition:
    """
    Simula la adquisición de bioseñales de un dispositivo real.
    
    En un entorno real, esta clase se conectaría con el hardware de adquisición
    y procesaría los datos recibidos.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.running = False
        self.thread = None
        self.buffers = {
            "ecg": CircularBuffer(10000),
            "resp": CircularBuffer(10000),
            "spo2": CircularBuffer(10000),
            "temp": CircularBuffer(10000)
        }
        
        # Cola para comunicación entre hilos
        self.data_queue = queue.Queue()
        
        # Parámetros de simulación
        self.ecg_phase = 0
        self.resp_phase = 0
        self.spo2_value = 98.0
        self.temp_value = 36.8
        
        # Configuración por señal
        self.signals_config = {
            "ecg": {
                "name": "Electrocardiograma",
                "unit": "mV",
                "color": "#4caf50",
                "sample_rate": 250,  # Hz
                "visible": True,
                "y_range": [-1, 1]
            },
            "resp": {
                "name": "Respiración",
                "unit": "L/min",
                "color": "#2196f3",
                "sample_rate": 100,  # Hz
                "visible": True,
                "y_range": [0, 5]
            },
            "spo2": {
                "name": "Saturación de Oxígeno",
                "unit": "%",
                "color": "#ff5722",
                "sample_rate": 60,  # Hz
                "visible": True,
                "y_range": [90, 100]
            },
            "temp": {
                "name": "Temperatura",
                "unit": "°C",
                "color": "#9c27b0",
                "sample_rate": 10,  # Hz
                "visible": True,
                "y_range": [35, 40]
            }
        }
    
    def start(self):
        """Inicia la adquisición de datos."""
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._acquisition_thread)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Adquisición iniciada para sesión {self.session_id}")
        return True
    
    def stop(self):
        """Detiene la adquisición de datos."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        logger.info(f"Adquisición detenida para sesión {self.session_id}")
    
    def _acquisition_thread(self):
        """Hilo principal de adquisición de datos."""
        logger.info("Hilo de adquisición iniciado")
        
        next_sample_time = {
            signal: time.time() for signal in self.buffers.keys()
        }
        
        while self.running:
            current_time = time.time()
            
            # Simular adquisición para cada señal según su frecuencia
            for signal, buffer in self.buffers.items():
                if current_time >= next_sample_time[signal]:
                    # Calcular cuántas muestras deberíamos haber adquirido
                    sample_interval = 1.0 / self.signals_config[signal]["sample_rate"]
                    samples_to_generate = max(1, int((current_time - next_sample_time[signal]) / sample_interval) + 1)
                    
                    # Generar datos simulados
                    values = []
                    timestamps = []
                    
                    for i in range(samples_to_generate):
                        timestamp = int((next_sample_time[signal] + i * sample_interval) * 1000)
                        value = self._generate_sample(signal)
                        values.append(value)
                        timestamps.append(timestamp)
                    
                    # Añadir datos al buffer
                    buffer.add_batch(values, timestamps)
                    
                    # Actualizar tiempo de la próxima muestra
                    next_sample_time[signal] = next_sample_time[signal] + samples_to_generate * sample_interval
            
            # Enviar datos formateados a la cola
            self._format_and_queue_data()
            
            # Dormir un poco para no saturar la CPU
            time.sleep(0.01)
    
    def _generate_sample(self, signal_type: str) -> float:
        """
        Genera una muestra simulada para el tipo de señal especificado.
        
        Args:
            signal_type: Tipo de señal ('ecg', 'resp', 'spo2', 'temp')
            
        Returns:
            float: Valor simulado
        """
        if signal_type == "ecg":
            # Simular ECG
            self.ecg_phase += 0.025
            
            # Valor base
            value = 0.5 * math.sin(self.ecg_phase)
            
            # Añadir pico QRS ocasional
            if (self.ecg_phase % (2 * math.pi)) < 0.2:
                value += 0.8 * math.exp(-((self.ecg_phase % (2 * math.pi)) - 0.1) ** 2 / 0.01)
            
            # Añadir ruido
            value += random.uniform(-0.05, 0.05)
            
            return value
            
        elif signal_type == "resp":
            # Simular respiración
            self.resp_phase += 0.01
            value = 2.5 + 0.8 * math.sin(self.resp_phase)
            value += random.uniform(-0.03, 0.03)
            return value
            
        elif signal_type == "spo2":
            # Simular SpO2
            if random.random() < 0.05:  # Ocasionalmente cambiar un poco
                self.spo2_value += random.uniform(-0.3, 0.3)
                self.spo2_value = max(90, min(100, self.spo2_value))
            
            # Añadir un poco de ruido
            return self.spo2_value + random.uniform(-0.1, 0.1)
            
        elif signal_type == "temp":
            # Simular temperatura
            if random.random() < 0.01:  # Rara vez cambiar un poco
                self.temp_value += random.uniform(-0.05, 0.05)
                self.temp_value = max(35, min(40, self.temp_value))
            
            # Añadir un poco de ruido
            return self.temp_value + random.uniform(-0.01, 0.01)
        
        return 0.0
    
    def _format_and_queue_data(self):
        """Formatea los datos según la especificación JSON y los envía a la cola."""
        # Obtener timestamp actual para el paquete
        timestamp = int(time.time() * 1000)
        
        # Crear diccionario de datos siguiendo la especificación
        formatted_data = {
            "session": {
                "id": self.session_id,
                "timestamp": timestamp,
                "name": f"Adquisición {self.session_id[:8]}",
                "status": "active",
                "connectedClients": 0  # Se actualizará automáticamente
            },
            "visualization": {
                "mode": "realtime",
                "timeWindow": 10000,
                "autoScale": True,
                "gridEnabled": True,
                "theme": "light",
                "layout": "single",
                "signalsVisible": list(self.buffers.keys())
            },
            "signals": {}
        }
        
        # Obtener datos de cada señal
        for signal_id, buffer in self.buffers.items():
            config = self.signals_config[signal_id]
            values, timestamps = buffer.get_latest(10000)  # Últimos 10 segundos
            
            # Si no hay datos, continuar con la siguiente señal
            if not values:
                continue
            
            # Añadir datos de la señal
            formatted_data["signals"][signal_id] = {
                "name": config["name"],
                "unit": config["unit"],
                "color": config["color"],
                "visible": config["visible"],
                "yAxisRange": config["y_range"],
                "data": values,
                "timestamps": timestamps,
                "sampleRate": config["sample_rate"],
                "displayOrder": list(self.buffers.keys()).index(signal_id) + 1
            }
        
        # Si hay al menos una señal con datos, encolar para enviar
        if formatted_data["signals"]:
            try:
                self.data_queue.put(formatted_data, block=False)
            except queue.Full:
                logger.warning("Cola de datos llena, descartando paquete")
    
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el paquete de datos más reciente.
        
        Returns:
            Optional[Dict]: Paquete de datos formateado o None si no hay datos
        """
        try:
            return self.data_queue.get(block=False)
        except queue.Empty:
            return None


def main():
    """Función principal del ejemplo."""
    logger.info("Iniciando ejemplo de integración con adquisición de datos")
    
    # Crear instancia del servidor
    servidor = ServidorBiosenales()
    
    # Configurar el servidor
    servidor.set_config({
        "host": "0.0.0.0",
        "port": 8000,
        "dist_folder": "dist",
        "data_interval": 100  # 100ms entre actualizaciones
    })
    
    # Crear una sesión para la adquisición
    session_id = servidor.create_session("Adquisición de Bioseñales")
    
    # Crear sistema de adquisición
    acquisition = BioseñalAdquisition(session_id)
    
    # Función callback para proporcionar datos
    def data_callback():
        return acquisition.get_latest_data()
    
    # Establecer callback y arrancar servidor
    servidor.set_data_callback(data_callback)
    
    if servidor.start():
        logger.info(f"Servidor iniciado en http://localhost:{servidor.config['port']}")
        logger.info(f"Sesión creada: {session_id}")
        
        # Iniciar adquisición
        acquisition.start()
        
        logger.info("El sistema está ejecutándose. Presiona Ctrl+C para detener.")
        
        try:
            # Mantener el servidor ejecutándose hasta que el usuario lo detenga
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Señal de interrupción recibida")
        finally:
            # Detener la adquisición
            acquisition.stop()
            # Detener el servidor
            servidor.stop()
            logger.info("Sistema detenido")
    else:
        logger.error("No se pudo iniciar el servidor")


if __name__ == "__main__":
    main()
