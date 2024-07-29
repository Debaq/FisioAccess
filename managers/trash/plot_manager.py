import threading
import time
from kivy.clock import Clock
from graphics.interactive_plot import InteractivePlot

class PlotManager:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
        self.plot_data = {}
        self.threads = {}
        self.recording = False

    def plot_activity(self, activity):
        screen = self.screen_manager.get_screen('activity')
        plot_box = screen.ids.plot_box
        plot_box.clear_widgets()

        self.interactive_plot = InteractivePlot(activity)
        plot_box.add_widget(self.interactive_plot)

        self.threads[activity] = threading.Thread(target=self.update_plot, args=(activity,))
        self.threads[activity].running = True
        self.threads[activity].start()

    def update_plot(self, activity):
        thread = self.threads[activity]
        while getattr(thread, 'running', False):
            if self.recording:
                Clock.schedule_once(lambda dt: self.interactive_plot.update_plot(), 0)
            time.sleep(0.1)

    def stop_threads(self):
        for thread in self.threads.values():
            thread.running = False

        for thread in self.threads.values():
            thread.join()
        
        self.threads.clear()

    def scroll_left(self):
        self.interactive_plot.scroll_left()

    def scroll_right(self):
        self.interactive_plot.scroll_right()

    def zoom_in(self):
        self.interactive_plot.zoom_in()

    def zoom_out(self):
        self.interactive_plot.zoom_out()

    def toggle_record(self):
        self.recording = not self.recording
        record_button = self.screen_manager.get_screen('activity').ids.record_button
        clear_button = self.screen_manager.get_screen('activity').ids.clear_button
        if self.recording:
            record_button.icon = "pause"
            clear_button.disabled = True
        else:
            record_button.icon = "play"
            clear_button.disabled = False

    def clear_plot(self):
        if not self.recording:
            self.interactive_plot.data_widget.ax.clear()
            if hasattr(self.interactive_plot, 'ax_selection'):
                self.interactive_plot.ax_selection.clear()
            self.interactive_plot.data_widget.fig.canvas.draw()
