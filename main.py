import kivy
kivy.require('1.11.1')  # Cambia la versión según tu necesidad

# Configurar Kivy para usar el archivo de configuración
from kivy.config import Config
Config.read('config.ini')

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.factory import Factory

from managers.screen_manager import AppScreenManager
from utils.theme import set_theme
from screens.welcome_screen import WelcomeScreen
from screens.activity_screen import ActivityScreen
from screens.preferences_screen import PreferencesScreen
from screens.help_screen import HelpScreen

# Registrar pantallas en la fábrica de Kivy
Factory.register('WelcomeScreen', cls=WelcomeScreen)
Factory.register('ActivityScreen', cls=ActivityScreen)
Factory.register('PreferencesScreen', cls=PreferencesScreen)
Factory.register('HelpScreen', cls=HelpScreen)

class MainApp(MDApp):

    def build(self):
        print("Building the application...")
        set_theme(self)
        self.title = "FisioAccess"
        self.icon = 'img/icon.png'  # Establecer el ícono de la aplicación
        self.screen_manager = AppScreenManager(self)
        
        # Cargar archivos KV separados
        Builder.load_file('screens/welcome_screen.kv')
        Builder.load_file('screens/activity_screen.kv')
        Builder.load_file('screens/preferences_screen.kv')
        Builder.load_file('screens/help_screen.kv')
        
        # Añadir las pantallas al ScreenManager
        self.screen_manager.add_widget(WelcomeScreen(name='welcome'))
        self.screen_manager.add_widget(ActivityScreen(name='activity'))
        self.screen_manager.add_widget(PreferencesScreen(name='preferences'))
        self.screen_manager.add_widget(HelpScreen(name='help'))
        
        print("KV files loaded, returning screen manager")
        return self.screen_manager

    def on_start(self):
        Window.size = (1024, 600)
        print("App started with window size 1024x600")
    
    def on_stop(self):
        print("App is stopping, performing cleanup...")
        self.screen_manager.stop_threads()  # Detener hilos u otros recursos


if __name__ == '__main__':
    print("Starting the application...")
    MainApp().run()