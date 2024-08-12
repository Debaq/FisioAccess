import matplotlib as plt
plt.use('Agg')
import matplotlib.pyplot as plt
from kivy.metrics import dp
import numpy as np

plt.rcParams['path.simplify'] = True
plt.rcParams['path.simplify_threshold'] = 1.0
plt.rcParams['agg.path.chunksize'] = 1000
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.linewidth'] = 1.0

font_size_axis_title = dp(13)
font_size_axis_tick = dp(12)

class GraphGenerator(object):
    def __init__(self, update_callback):
        super().__init__()
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [2, 1]})
        self.line1, = self.ax1.plot([], [], label='ECG')
        self.line2, = self.ax2.plot([], [], label='Selección')
        self.fig.subplots_adjust(left=0.1, top=0.96, right=0.95, bottom=0.2, wspace=0.3)
        self.ax1.set_ylabel("mV", fontsize=8)
        self.ax2.set_ylabel("mV", fontsize=8)
        self.ax1.set_xlabel("Tiempo (s)", fontsize=8)
        self.ax2.set_xlabel("Tiempo (s)", fontsize=8)
        self.ax1.set_xlim(0, 10)
        self.ax1.set_ylim(-1.5, 3.5)
        self.ax2.set_xlim(0, 5)
        self.ax2.set_ylim(-1.5, 3.5)
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.update_callback = update_callback

        # Configurar eventos de interacción
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.press = None

    def update_main_ecg(self, x_data, y_data, x_min, x_max):
        mask = (x_data >= x_min) & (x_data <= x_max)
        self.line1.set_data(x_data[mask], y_data[mask])
        self.ax1.set_xlim(x_min, x_max)
        visible_y_data = y_data[mask]
        if len(visible_y_data) > 0:
            self.ax1.set_ylim(min(visible_y_data) - 0.1, max(visible_y_data) + 0.1)

    def update_selection(self, x_data, y_data):
        self.line2.set_data(x_data, y_data)
        self.ax2.set_xlim(min(x_data), max(x_data))
        self.ax2.set_ylim(min(y_data) - 0.1, max(y_data) + 0.1)

    def on_press(self, event):
        print(f"se preiosno - {event}")
        if event.inaxes == self.ax1:
            self.press = event.xdata, event.ydata

    def on_motion(self, event):
        print(f"se preiosno - {event}")

        if self.press is None or event.inaxes != self.ax1:
            return
        xpress, ypress = self.press
        dx = event.xdata - xpress
        self.ax1.set_xlim(self.ax1.get_xlim() - dx)
        self.fig.canvas.draw_idle()

    def on_release(self, event):
        print(f"se preiosno - {event}")

        if event.inaxes == self.ax1:
            self.press = None
            xmin, xmax = self.ax1.get_xlim()
            self.update_callback(xmin, xmax)