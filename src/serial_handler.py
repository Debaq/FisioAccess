import serial
import random

class SerialHandler:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print(f"Conexión serial establecida en {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error de conexión serial: {e}")
            return False

    def get_data(self, use_demo_data):
        if use_demo_data:
            return random.randint(0, 1023)
        elif self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    return int(float(line))
            except (ValueError, serial.SerialException):
                print("Error al leer datos seriales")
        return 0

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Conexión serial cerrada")