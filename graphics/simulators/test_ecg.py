import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from ecg_simulator import ECG_Simulator
import threading
import time
import numpy as np

class ECGLiveVis:
    def __init__(self, duration=10, sample_rate=100):
        self.duration = duration
        self.sample_rate = sample_rate
        self.data_len = duration * sample_rate

        # Inicializar datos
        self.y_data = [0] * self.data_len
        self.ecg = ECG_Simulator(heart_rate=150, use_pacemaker=True)
        
        # Configurar la figura y el subplot
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-2, 3)  # Ajustamos los límites del eje Y
        self.ax.set_xlim(0, duration)
        self.ax.grid(True)
        plt.title('ECG en Tiempo Real')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud (mV)')

        # Crear el eje X
        self.x_data = np.linspace(0, duration, self.data_len)

        # Variables de control
        self.is_running = False
        self.paused = False

    def update_data(self):
        while self.is_running:
            if not self.paused:
                new_val = self.ecg.get_next_value()
                self.y_data = self.y_data[1:] + [new_val]
            time.sleep(1 / self.sample_rate)

    def update_plot(self, frame):
        self.line.set_data(self.x_data, self.y_data)
        return self.line,

    def start(self):
        self.is_running = True
        self.data_thread = threading.Thread(target=self.update_data)
        self.data_thread.start()

        # Configurar la interfaz de Tkinter
        self.root = tk.Tk()
        self.root.title("ECG Live Visualization")
        
        # Añadir el canvas de matplotlib a Tkinter
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Botones de control
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM)

        pause_button = tk.Button(button_frame, text="Pause/Resume", command=self.toggle_pause)
        pause_button.pack(side=tk.LEFT)

        stop_button = tk.Button(button_frame, text="Stop", command=self.stop)
        stop_button.pack(side=tk.LEFT)

        # Iniciar la animación
        self.anim = animation.FuncAnimation(
            self.fig, self.update_plot, interval=20, blit=True,
            cache_frame_data=False
        )

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def toggle_pause(self):
        self.paused = not self.paused

    def stop(self):
        self.is_running = False
        self.root.quit()

    def on_closing(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    vis = ECGLiveVis()
    vis.start()