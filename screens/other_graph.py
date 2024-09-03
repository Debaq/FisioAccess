from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy_garden.graph import Graph, MeshLinePlot, LinePlot
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import serial

class InteractiveGraph(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
      # Layout para el gráfico principal y los controles
        main_layout = BoxLayout(orientation='vertical')
        
        # Crear el gráfico principal
        self.graph = Graph(xlabel='Time', ylabel='Value', x_ticks_minor=5,
                           x_ticks_major=25, y_ticks_major=1,
                           y_grid_label=True, x_grid_label=True, padding=5,
                           x_grid=True, y_grid=True, xmin=0, xmax=100, ymin=-1, ymax=1)
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)
        
        main_layout.add_widget(self.graph)
        
        # Botones de control
        control_layout = BoxLayout(size_hint_y=None, height=50)
        self.start_stop_button = Button(text='Stop', on_press=self.toggle_update)
        self.zoom_in_button = Button(text='Zoom In', on_press=self.zoom_in)
        self.zoom_out_button = Button(text='Zoom Out', on_press=self.zoom_out)
        control_layout.add_widget(self.start_stop_button)
        control_layout.add_widget(self.zoom_in_button)
        control_layout.add_widget(self.zoom_out_button)
        main_layout.add_widget(control_layout)
        
        self.add_widget(main_layout)
        
        # Crear el gráfico secundario
        self.secondary_graph = Graph(xlabel='Time', ylabel='Value', x_ticks_minor=5,
                                     x_ticks_major=25, y_ticks_major=1,
                                     y_grid_label=True, x_grid_label=True, padding=5,
                                     x_grid=True, y_grid=True, xmin=0, xmax=100, ymin=-1, ymax=1)
        self.secondary_plot = LinePlot(color=[0, 1, 0, 1])
        self.secondary_graph.add_plot(self.secondary_plot)
        
        self.add_widget(self.secondary_graph)
        
        # Inicialización de variables
        self.all_points = []
        self.is_updating = True
        self.last_touch_pos = None
        self.selection_start = None
        self.selection_end = None
        
        # Configurar el puerto serial
        self.ser = serial.Serial('/dev/ttyS2', 115200)  # Ajusta el puerto y la velocidad según sea necesario
        
        # Iniciar actualización
        Clock.schedule_interval(self.update_plot, 0.05)

    def update_plot(self, dt):
        if self.is_updating:
            try:
                data = float(self.ser.readline().decode().strip())
                new_point = (len(self.all_points), data)
                self.all_points.append(new_point)
                self.graph.xmax = new_point[0]
                self.graph.xmin = max(0, new_point[0] - 100)
                
                # Ajustar ymin y ymax dinámicamente
                if len(self.all_points) > 1:
                    self.graph.ymin = min(p[1] for p in self.all_points[-100:])
                    self.graph.ymax = max(p[1] for p in self.all_points[-100:])
                
                self.plot.points = [p for p in self.all_points if self.graph.xmin <= p[0] <= self.graph.xmax]
                self.update_selection()

            except:
                print(f"error el dato es: {data}")
        



    def toggle_update(self, instance):
        self.is_updating = not self.is_updating
        self.start_stop_button.text = 'Start' if not self.is_updating else 'Stop'

    def zoom_in(self, instance):
        center = (self.graph.xmax + self.graph.xmin) / 2
        new_range = (self.graph.xmax - self.graph.xmin) * 0.5
        self.graph.xmin = max(0, center - new_range / 2)
        self.graph.xmax = min(len(self.all_points), center + new_range / 2)

    def zoom_out(self, instance):
        center = (self.graph.xmax + self.graph.xmin) / 2
        new_range = (self.graph.xmax - self.graph.xmin) * 2
        self.graph.xmin = max(0, center - new_range / 2)
        self.graph.xmax = min(len(self.all_points), center + new_range / 2)

    def on_touch_down(self, touch):
        if self.graph.collide_point(*touch.pos):
            self.last_touch_pos = self.graph.to_data(touch.x, touch.y)
            self.selection_start = self.last_touch_pos[0]
            self.selection_end = None
            return True
        return super(InteractiveGraph, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.last_touch_pos and self.graph.collide_point(*touch.pos):
            new_touch_pos = self.graph.to_data(touch.x, touch.y)
            if touch.is_double_tap:
                # Si es un doble toque, actualizamos la selección
                self.selection_end = new_touch_pos[0]
            else:
                # Si no, movemos el gráfico
                x_diff = new_touch_pos[0] - self.last_touch_pos[0]
                self.graph.xmin = max(0, self.graph.xmin - x_diff)
                self.graph.xmax = min(self.all_points[-1][0], self.graph.xmax - x_diff)
            self.last_touch_pos = new_touch_pos
            self.update_selection()
            return True
        return super(InteractiveGraph, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.graph.collide_point(*touch.pos):
            if self.selection_start is not None:
                self.selection_end = self.graph.to_data(touch.x, touch.y)[0]
                self.update_selection()
        self.last_touch_pos = None
        return super(InteractiveGraph, self).on_touch_up(touch)

    def update_selection(self):
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            selected_points = [p for p in self.all_points if start <= p[0] <= end]
            if selected_points:
                self.secondary_plot.points = selected_points
                self.secondary_graph.xmin = start
                self.secondary_graph.xmax = end
                self.secondary_graph.ymin = min(p[1] for p in selected_points)
                self.secondary_graph.ymax = max(p[1] for p in selected_points)

        # Dibujar rectángulo de selección en el gráfico principal
        self.graph.canvas.after.clear()
        if self.selection_start is not None and self.selection_end is not None:
            with self.graph.canvas.after:
                Color(0, 0, 1, 0.3)
                # Convertir coordenadas de datos a coordenadas de pantalla
                x1 = self.graph.pos[0] + (self.selection_start - self.graph.xmin) / (self.graph.xmax - self.graph.xmin) * self.graph.width
                x2 = self.graph.pos[0] + (self.selection_end - self.graph.xmin) / (self.graph.xmax - self.graph.xmin) * self.graph.width
                Rectangle(pos=(min(x1, x2), self.graph.pos[1]), 
                          size=(abs(x2 - x1), self.graph.height))
    def on_stop(self):
        self.ser.close()

