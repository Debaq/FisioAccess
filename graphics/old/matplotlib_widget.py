from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.clock import Clock
import matplotlib.pyplot as plt
import numpy as np

class MatplotlibWidget(Widget):
    def __init__(self, **kwargs):
        super(MatplotlibWidget, self).__init__(**kwargs)
        self.fig, self.ax = plt.subplots()
        self.canvas_texture = Texture.create(size=(self.width, self.height))
        self.bind(size=self.update_texture_size, pos=self.update_texture_size)
        Clock.schedule_interval(self.update_canvas, 1 / 60.)

    def update_texture_size(self, *args):
        self.canvas_texture = Texture.create(size=(self.width, self.height))
        self.canvas_texture.flip_vertical()

    def update_canvas(self, dt):
        self.fig.canvas.draw()
        buffer = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
        buffer = buffer.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))
        self.canvas_texture.blit_buffer(buffer.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        with self.canvas:
            Rectangle(texture=self.canvas_texture, pos=self.pos, size=self.size)

    def plot_data(self, x, y):
        self.ax.clear()
        self.ax.plot(x, y)
        self.fig.canvas.draw()
