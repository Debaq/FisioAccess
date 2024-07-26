from kivy.uix.screenmanager import ScreenManager
from managers.plot_manager import PlotManager

def switch_theme(screen_manager):
    screen_manager.switch_theme()

def go_to_preferences(screen_manager):
    screen_manager.go_to_preferences()

def go_to_help(screen_manager, activity):
    screen_manager.go_to_help(activity)

def save_preferences(screen_manager):
    screen_manager.save_preferences()

def back_to_previous_screen(screen_manager):
    screen_manager.back_to_previous_screen()

def plot_activity(plot_manager, activity):
    plot_manager.plot_activity(activity)

def scroll_left(plot_manager):
    plot_manager.scroll_left()

def scroll_right(plot_manager):
    plot_manager.scroll_right()

def zoom_in(plot_manager):
    plot_manager.zoom_in()

def zoom_out(plot_manager):
    plot_manager.zoom_out()

def toggle_record(plot_manager):
    plot_manager.toggle_record()

def clear_plot(plot_manager):
    plot_manager.clear_plot()
