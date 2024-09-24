import serial
from eeg_simulator import ECG_Simulator
from threading import Lock


class SerialHandler:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.ecg_demo = ECG_Simulator(heart_rate=60, use_pacemaker=False)
        self.lock = Lock()  # Añadimos un lock para sincronización

    def connect(self):
        with self.lock:
            try:
                self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
                print(f"Conexión serial establecida en {self.port}")
                return True
            except serial.SerialException as e:
                print(f"Error de conexión serial: {e}")
                return False

    def get_data(self, use_demo_data):
        with self.lock:
            if use_demo_data:
                data = self.ecg_demo.get_next_value()
                return data
            elif self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        return float(line)
                except (ValueError, serial.SerialException) as e:
                    print(f"Error al leer datos seriales: {e}")
            return 0

    def close(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("Conexión serial cerrada")
