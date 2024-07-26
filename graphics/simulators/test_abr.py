import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from abr_simulator import ABR_Simulator
import numpy as np
import threading

class ABRVis:
    def __init__(self, duration=12, sample_rate=20000, num_averages=2000):
        self.duration = duration  # en milisegundos
        self.sample_rate = sample_rate
        self.num_averages = num_averages
        self.abr = ABR_Simulator(sample_rate=sample_rate, duration=duration)
        
        # Configurar la figura y el subplot
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_ylim(-400, 400)  # Ajustamos los límites del eje Y a nV
        self.ax.set_xlim(0, duration)
        self.ax.grid(True)
        plt.title(f'ABR Promediado ({num_averages} promediaciones)')
        plt.xlabel('Tiempo (ms)')
        plt.ylabel('Amplitud (nV)')

        # Crear el eje X
        self.x_data = np.linspace(0, duration, int(duration * sample_rate / 1000))

        # Variables de control
        self.is_running = False

    def update_plot(self):
        averaged_response = self.abr.generate_averaged_response(self.num_averages)
        self.line.set_data(self.x_data, averaged_response)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def start(self):
        self.is_running = True

        # Configurar la interfaz de Tkinter
        self.root = tk.Tk()
        self.root.title("ABR Visualization")
        
        # Añadir el canvas de matplotlib a Tkinter
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Botones de control
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM)

        update_button = tk.Button(button_frame, text="Generar Nuevo ABR", command=self.update_in_thread)
        update_button.pack(side=tk.LEFT)

        stop_button = tk.Button(button_frame, text="Cerrar", command=self.stop)
        stop_button.pack(side=tk.LEFT)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def update_in_thread(self):
        thread = threading.Thread(target=self.update_plot)
        thread.start()

    def stop(self):
        self.is_running = False
        self.root.quit()

    def on_closing(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    vis = ABRVis()
    vis.start()