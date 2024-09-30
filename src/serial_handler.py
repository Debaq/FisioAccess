import serial
import threading
from collections import deque
from eeg_simulator import ECG_Simulator

class SerialHandler:
    def __init__(self, port, baud_rate, buffer_size=1000):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.ecg_demo = ECG_Simulator(heart_rate=60, use_pacemaker=False)
        self.buffer = deque(maxlen=buffer_size)
        self.lock = threading.Lock()
        self.thread = None
        self.running = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Conexión serial establecida en {self.port}")
            self.running = True
            self.thread = threading.Thread(target=self._read_serial)
            self.thread.start()
            return True
        except serial.SerialException as e:
            print(f"Error de conexión serial: {e}")
            return False

    def _read_serial(self):
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        with self.lock:
                            self.buffer.append(float(line))
                except (ValueError, serial.SerialException) as e:
                    print(f"Error al leer datos seriales: {e}")

    def get_data(self, use_demo_data):
        if use_demo_data:
            return self.ecg_demo.get_next_value()
        with self.lock:
            return self.buffer.popleft() if self.buffer else 0

    def close(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Conexión serial cerrada")