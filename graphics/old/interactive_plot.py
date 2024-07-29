import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
from graphics.simulation import DataSimulator
from graphics.plot_config import PlotConfig


class InteractivePlot:
    def __init__(self, data_type='random'):
        self.fig, self.ax = plt.subplots()
        self.x = np.array([])  # Inicializar con un array vacío
        self.y = np.array([])  # Inicializar con un array vacío
        self.line, = self.ax.plot([], [])  # Inicializar la línea vacía

        self.simulator = DataSimulator(data_type)
        self.configurator = PlotConfig(data_type)
        self.configurator.apply_config(self.ax)

        self.window_size = self.configurator.get_window_size()
        self.x_min = 0
        self.x_max = self.window_size
        self.next_x_value = 0  # Mantener el próximo valor de x

        self.rectangle_selector = RectangleSelector(self.ax, self.on_select, useblit=True,
                                                    button=[1], minspanx=5, minspany=5,
                                                    spancoords='pixels', interactive=True)
        self.cid_move = self.fig.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def on_select(self, eclick, erelease):
        print(f'Selected region from {eclick.xdata}, {eclick.ydata} to {erelease.xdata}, {erelease.ydata}')

    def on_move(self, event):
        if event.inaxes:
            print(f'Mouse moved to {event.xdata}, {event.ydata}')

    def on_click(self, event):
        if event.inaxes:
            print(f'Mouse clicked at {event.xdata}, {event.ydata}')

    def update_plot(self, new_y):
        self.x = np.append(self.x, self.next_x_value)
        self.y = np.append(self.y, new_y)
        self.next_x_value += 1

        if len(self.y) > len(self.x):
            self.y = self.y[-len(self.x):]  # Limitar el tamaño de y para que coincida con x

        self.line.set_data(self.x, self.y)
        self.update_limits()
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()  # Redibujar la gráfica

    def update_limits(self):
        if len(self.y) > 0 and self.x[-1] >= self.x_max:
            last_x = self.x[-1]
            self.x_min = last_x - self.window_size
            self.x_max = last_x
        self.ax.set_xlim(self.x_min, self.x_max)

    def generate_random_data(self):
        return self.simulator.generate_data()

    def scroll_left(self):
        if self.x_min > 0:
            self.x_min = max(0, self.x_min - 1)
            self.x_max = self.x_min + self.window_size
            self.ax.set_xlim(self.x_min, self.x_max)
            self.fig.canvas.draw()

    def scroll_right(self):
        if self.x_max < self.x[-1]:
            self.x_min = min(self.x[-1] - self.window_size, self.x_min + 1)
            self.x_max = self.x_min + self.window_size
            self.ax.set_xlim(self.x_min, self.x_max)
            self.fig.canvas.draw()

    def zoom_in(self):
        new_window_size = max(1, self.window_size / 2)
        center = (self.x_max + self.x_min) / 2
        self.x_min = center - new_window_size / 2
        self.x_max = center + new_window_size / 2
        self.window_size = new_window_size
        self.ax.set_xlim(self.x_min, self.x_max)
        self.fig.canvas.draw()

    def zoom_out(self):
        new_window_size = min(len(self.x), self.window_size * 2)
        center = (self.x_max + self.x_min) / 2
        self.x_min = max(0, center - new_window_size / 2)
        self.x_max = min(self.x[-1], center + new_window_size / 2)
        self.window_size = new_window_size
        self.ax.set_xlim(self.x_min, self.x_max)
        self.fig.canvas.draw()

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_move)
        self.fig.canvas.mpl_disconnect(self.cid_click)
        self.rectangle_selector.disconnect_events()

    def connect_events(self):
        self.cid_move = self.fig.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.rectangle_selector.connect_default_events()