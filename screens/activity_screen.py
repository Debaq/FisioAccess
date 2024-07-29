from kivymd.uix.screen import MDScreen
from graphics.graph_generator import GraphGenerator
import kivy_matplotlib_widget
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
import threading
import time
from graphics.simulators.ecg_simulator import ECG_Simulator


from matplotlib import animation

class ActivityScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recording = False
        self.mygraph = GraphGenerator()
        self.figure_wgt.figure = self.mygraph.fig
        self.ecg = ECG_Simulator(heart_rate=50, use_pacemaker=True)
        self.sample_rate = 100  # Hz
        self.data_points = 1000  # Número de puntos a mostrar
        self.x_data = list(range(self.data_points))
        self.y_data = [0] * self.data_points
        self.is_running = False
        self.paused = False
        
        
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

    # Función para crear un MDListItem personalizado si es necesario
    def custom_list_item(self, text, on_release):
        return MDListItem(
            MDListItemHeadlineText(
                text=text,
            ),
            on_release=on_release,
        )

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
        self.is_running = True
        self.paused = False
        self.data_thread = threading.Thread(target=self.update_data)
        self.data_thread.start()
        self.mygraph.ax1.set_ylim(-1.5, 3.5)  # Ajusta según tus necesidades
        self.mygraph.fig.canvas.draw()
        self.anim = animation.FuncAnimation(
            self.mygraph.fig, self.update_plot, interval=50, blit=True, cache_frame_data=False)
    def stop_recording(self):
        self.is_running = False
        self.paused = True
        if hasattr(self, 'data_thread'):
            self.data_thread.join()
        if hasattr(self, 'anim'):
            self.anim.event_source.stop()

    def update_data(self):
        while self.is_running:
            if not self.paused:
                new_val = self.ecg.get_next_value()
                self.y_data = self.y_data[1:] + [new_val]
                self.x_data = self.x_data[1:] + [self.x_data[-1] + 1]
            time.sleep(1 / self.sample_rate)

    def update_plot(self, frame):
        self.mygraph.update_main_ecg(self.x_data, self.y_data)
        return self.mygraph.line1,