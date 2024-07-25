import threading
import time
import os
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.dialog import MDDialog
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.boxlayout import BoxLayout

import numpy as np

from graphics.interactive_plot import InteractivePlot
from utils.menu import create_menu
from utils.dialogs import create_confirm_dialog

class AppScreenManager(ScreenManager):

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app  # Referencia a la aplicación
        self.plot_data = {}
        self.threads = {}
        self.dialog = None
        self.recording = False
        self.previous_screen = None
        self.current_activity = None
        self.menu = create_menu(self.menu_callback)  # Crear el menú
        self.interactive_plot = None
        print("AppScreenManager initialized")

    def get_background_color(self):
        print("Getting background color")
        if self.app.theme_cls.theme_style == 'Light':
            return 1, 1, 1, 1  # Fondo blanco
        else:
            return 0, 0, 0, 1  # Fondo negro

    def update_graph_style(self, *args):
        print("Updating graph style")
        import matplotlib.pyplot as plt
        if self.app.theme_cls.theme_style == 'Light':
            plt.style.use('default')
        else:
            plt.style.use('dark_background')
        self.redraw_all_graphs()

    def redraw_all_graphs(self):
        print("Redrawing all graphs")
        for screen_name in self.plot_data.keys():
            self.plot_activity(screen_name)

    def open_menu(self, caller):
        print("Opening menu")
        self.menu.caller = caller
        self.menu.open()

    def menu_callback(self, text_item):
        print(f"Menu callback: {text_item}")
        self.menu.dismiss()
        self.change_screen(text_item)

    def change_screen(self, activity):
        print(f"Changing screen to: {activity}")
        self.current_activity = activity
        self.current = 'activity'
        self.plot_activity(activity)

    def confirm_back_to_welcome(self):
        print("Confirming back to welcome")
        if not self.dialog:
            self.dialog = create_confirm_dialog(self.close_dialog, self.back_to_welcome)
        self.dialog.open()

    def close_dialog(self, *args):
        print("Closing dialog")
        if self.dialog:
            self.dialog.dismiss()

    def back_to_welcome(self, *args):
        print("Back to welcome screen")
        self.close_dialog()
        self.current = 'welcome'
        self.stop_threads()

    def stop_threads(self):
        print("Stopping threads")
        for thread in self.threads.values():
            thread.running = False

        for thread in self.threads.values():
            thread.join()
        
        self.threads.clear()

    def plot_activity(self, activity):
        print(f"Plotting activity: {activity}")
        screen = self.get_screen('activity')
        plot_box = screen.ids.plot_box
        plot_box.clear_widgets()

        self.interactive_plot = InteractivePlot(activity)
        canvas = FigureCanvasKivyAgg(self.interactive_plot.fig)
        plot_box.add_widget(canvas)

        self.threads[activity] = threading.Thread(target=self.update_plot, args=(activity,))
        self.threads[activity].running = True
        self.threads[activity].start()

    def update_plot(self, activity):
        print(f"Updating plot for activity: {activity}")
        thread = self.threads[activity]
        while getattr(thread, 'running', False):
            if self.recording:
                new_y = self.interactive_plot.generate_random_data()
                Clock.schedule_once(lambda dt: self.update_plot_data(new_y), 0)
            time.sleep(0.1)  # Aumentar la frecuencia de actualización

    def update_plot_data(self, new_y):
        self.interactive_plot.update_plot(new_y)
        self.interactive_plot.fig.canvas.draw()  # Redibujar la gráfica

    def scroll_left(self):
        self.interactive_plot.scroll_left()

    def scroll_right(self):
        self.interactive_plot.scroll_right()

    def zoom_in(self):
        self.interactive_plot.zoom_in()

    def zoom_out(self):
        self.interactive_plot.zoom_out()

    def toggle_record(self):
        print("Toggling record")
        self.recording = not self.recording
        record_button = self.get_screen('activity').ids.record_button
        clear_button = self.get_screen('activity').ids.clear_button
        if self.recording:
            record_button.icon = "pause"
            clear_button.disabled = True
        else:
            record_button.icon = "play"
            clear_button.disabled = False

    def clear_plot(self):
        print("Clearing plot")
        if not self.recording:
            self.interactive_plot.ax.clear()
            self.interactive_plot.fig.canvas.draw()  # Redibujar la gráfica

    def switch_theme(self):
        print("Switching theme")
        if self.app.theme_cls.theme_style == "Light":
            self.app.theme_cls.theme_style = "Dark"
        else:
            self.app.theme_cls.theme_style = "Light"

    def go_to_preferences(self):
        print("Going to preferences screen")
        self.previous_screen = self.current
        self.current = 'preferences'
        if self.interactive_plot:
            self.interactive_plot.disconnect()

    def go_to_help(self, activity):
        print(f"Going to help screen for activity: {activity}")
        self.previous_screen = self.current
        self.current = 'help'
        if self.interactive_plot:
            self.interactive_plot.disconnect()
        self.load_help_content(activity)

    def load_help_content(self, activity):
        print(f"Loading help content for activity: {activity}")
        help_screen = self.get_screen('help')
        help_rst = help_screen.ids.help_text

        file_path = os.path.join('rst', f"{activity}.rst")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                rst_content = file.read()
                help_rst.text = rst_content
        else:
            help_rst.text = f"Aca va la ayuda de la actividad {activity}"

    def back_to_previous_screen(self):
        print("Going back to previous screen")
        if self.interactive_plot:
            self.interactive_plot.disconnect()
        self.current = self.previous_screen
        if self.current == 'activity':
            self.interactive_plot.connect_events()

    def save_preferences(self):
        print("Saving preferences")
        theme_color = self.get_screen('preferences').ids.theme_spinner.text
        baudrate = self.get_screen('preferences').ids.baudrate_spinner.text
        self.app.theme_cls.primary_palette = theme_color
        # Aquí puedes guardar el valor de baudrate en una variable o archivo
        print(f"Preferencias guardadas: Color = {self.app.theme_cls.primary_palette}, Baudrate = {baudrate}")
        self.back_to_previous_screen()
