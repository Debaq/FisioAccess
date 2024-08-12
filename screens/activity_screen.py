from kivymd.uix.screen import MDScreen
from graphics.graph_generator import GraphGenerator
import kivy_matplotlib_widget
from kivymd.uix.menu import MDDropdownMenu
from graphics.simulators.ecg_simulator import ECG_Simulator
from kivy.clock import Clock
import numpy as np

class ActivityScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recording = False
        self.mygraph = GraphGenerator(update_callback=self.update_graph_limits)
        self.figure_wgt.figure = self.mygraph.fig
        self.heart_rate = 50
        self.ecg = ECG_Simulator(heart_rate=self.heart_rate, use_pacemaker=True)
        self.sample_rate = 100  # Hz
        self.display_time = 10  # segundos de datos para mostrar
        self.max_data_points = self.sample_rate * 3600  # 1 hora de datos
        self.x_data = np.array([])
        self.y_data = np.array([])
        self.total_time = 0
        self.data_event = None
        self.plot_event = None
        self.viewing_latest = True

    
    def config_activity(self):
        self.activity = 'ECG'
        
    def menu_measure(self, menu_button):
        items = ["P", "Q", "R", "S", "T"]
        menu_items = [
            {
                "text": item,
                "on_release": lambda x=item: self.selected_mark(x),
            } for item in items
        ]
        self.menu = MDDropdownMenu(
            caller=menu_button,
            items=menu_items,
        )
        self.menu.open()

    def selected_mark(self, item):
        print(f"Selected: {item}")
        self.menu.dismiss()

    def toggle_record(self):
        self.recording = not self.recording
        record_button = self.ids.record_button
        clear_button = self.ids.clear_button
        if self.recording:
            record_button.icon = "pause"
            clear_button.disabled = True
            self.start_recording()
        else:
            record_button.icon = "play"
            clear_button.disabled = False
            self.stop_recording()

    def start_recording(self):
        self.mygraph.ax1.set_ylim(-1.5, 3.5)
        self.mygraph.ax1.set_xlim(0, self.display_time)
        self.data_event = Clock.schedule_interval(self.update_data, 1.0/self.sample_rate)
        self.plot_event = Clock.schedule_interval(self.update_plot, 1.0/30)  # 30 FPS

    def stop_recording(self):
        if self.data_event:
            self.data_event.cancel()
        if self.plot_event:
            self.plot_event.cancel()

    def update_data(self, dt):
        new_val = self.ecg.get_next_value()
        self.y_data = np.append(self.y_data, new_val)
        self.x_data = np.append(self.x_data, self.total_time)
        if len(self.x_data) > self.max_data_points:
            self.x_data = self.x_data[-self.max_data_points:]
            self.y_data = self.y_data[-self.max_data_points:]
        self.total_time += 1.0 / self.sample_rate

    def update_plot(self, dt):
        if len(self.x_data) > 0:
            if self.viewing_latest:
                x_max = self.total_time
                x_min = max(0, x_max - self.display_time)
                self.mygraph.ax1.set_xlim(x_min, x_max)
            else:
                x_min, x_max = self.mygraph.ax1.get_xlim()
            
            self.mygraph.update_main_ecg(self.x_data, self.y_data, x_min, x_max)
            self.mygraph.fig.canvas.draw_idle()
            self.mygraph.fig.canvas.flush_events()

    def update_graph_limits(self, xmin, xmax):
        self.viewing_latest = False
        visible_data = self.y_data[(self.x_data >= xmin) & (self.x_data <= xmax)]
        if len(visible_data) > 0:
            ymin, ymax = visible_data.min(), visible_data.max()
            self.mygraph.ax1.set_ylim(ymin - 0.1 * (ymax - ymin), ymax + 0.1 * (ymax - ymin))
        self.mygraph.fig.canvas.draw_idle()

    def reset_view(self):
        self.viewing_latest = True