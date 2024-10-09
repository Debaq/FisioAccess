import serial
import threading
from collections import deque
from eeg_simulator import ECG_Simulator
import time  # Necesario para el control de tiempo

class SerialHandler:
    def __init__(self, port_prefix='/dev/ttyACM', baud_rate=115200, buffer_size=1000, max_ports=10, command_interval=1.0):
        self.port_prefix = port_prefix
        self.baud_rate = baud_rate
        self.buffer = deque(maxlen=buffer_size)
        self.lock = threading.Lock()
        self.thread = None
        self.running = False
        self.ser = None
        self.max_ports = max_ports
        self.ecg_demo = ECG_Simulator(heart_rate=60, use_pacemaker=False)
        self.last_command_time = 0  # Para rastrear el último tiempo de envío de comando
        self.command_interval = command_interval  # Intervalo mínimo entre comandos en segundos

    def connect(self):
        for port_number in range(self.max_ports):
            port = f"{self.port_prefix}{port_number}"
            print(port)
            try:
                self.ser = serial.Serial(port, self.baud_rate, timeout=1)
                print(f"Conexión serial establecida en {port}")
                self.send_command("COMMAND=PRINT_MODE_A")  # Envía el comando para activar el modo de impresión
                self.running = True
                self.thread = threading.Thread(target=self._read_serial)
                self.thread.start()
                return True
            except serial.SerialException as e:
                print(f"No se pudo conectar a {port}: {e}")
        
        print("No se encontró un puerto serial disponible.")
        return False

    def send_command(self, command):
        """Envía un comando al dispositivo conectado por serial."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((command + '\n').encode('utf-8'))
                print(f"Comando enviado: {command}")
            except serial.SerialException as e:
                print(f"Error al enviar comando: {e}")

    def _read_serial(self):
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        with self.lock:
                            self.buffer.append(line)
                except serial.SerialException as e:
                    print(f"Error al leer datos seriales: {e}")

    def get_data(self, use_demo_data):
        """Devuelve el siguiente valor en el buffer o datos de demostración si se especifica."""
        if use_demo_data:
            return self.ecg_demo.get_next_value()

        # Envía el comando solo si ha pasado el intervalo de tiempo especificado
        current_time = time.time()
        if not self.buffer and (current_time - self.last_command_time) >= self.command_interval:
            self.send_command("COMMAND=PRINT_MODE_A")  # Envía el comando para activar el modo de impresión
            self.last_command_time = current_time  # Actualiza el último tiempo de comando enviado

        with self.lock:
            return self.buffer.popleft() if self.buffer else ""

    def close(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Conexión serial cerrada")
