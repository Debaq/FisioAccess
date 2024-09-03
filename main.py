import os
import os
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_TEXT'] = 'sdl2'
os.environ['KIVY_IMAGE'] = 'sdl2'


from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
#from kivy.metrics import dp
from kivymd.app import MDApp
#from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDSharedAxisTransition
from utils.notification import Notificador
from utils.theme_manager import ThemeManager

from kivy.core.window import Window
from kivy.graphics import gl_init_resources
from kivy.graphics import opengl as gl

#from kivy.factory import Factory

# Importamos la clase HomeScree
from screens.home_screen import HomeScreen
from screens.activity_screen import ActivityScreen
from screens.preferences_screen import PreferencesScreen
from screens.help_screen import HelpScreen
from screens.other_graph import InteractiveGraph



#Config.set('input', 'mouse', 'mouse,disable_multitouch')



def print_gl_info():
    print('OpenGL version:', gl.glGetString(gl.GL_VERSION))
    print('OpenGL vendor:', gl.glGetString(gl.GL_VENDOR))
    print('OpenGL renderer:', gl.glGetString(gl.GL_RENDERER))
    print('GLSL version:', gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION))

gl_init_resources()


class FisioAccess(MDApp):
    def build(self):
        self.title = "FisioAccess"
        self.transition = MDSharedAxisTransition()
        self.transition.transition_axis = "x"
        self.transition.duration = 0.35
        self.screen_manager = MDScreenManager()

        # Cargar archivos KV
        Builder.load_file("screens/activity_screen.kv")
        Builder.load_file('screens/preferences_screen.kv')
        Builder.load_file('screens/home_screen.kv')
        Builder.load_file('screens/help_screen.kv')

        # Agregar pantallas
        self.screen_manager.add_widget(HomeScreen(name='HomeScreen'))
        self.screen_manager.add_widget(PreferencesScreen(name='ConfigureScreen'))
        self.screen_manager.add_widget(ActivityScreen(name='ActivityScreen'))
        self.screen_manager.add_widget(HelpScreen(name='HelpScreen'))
        self.screen_manager.add_widget(InteractiveGraph(name='InteractiveGraphScreen'))


        #verificar estilo:
        self.theme_manager = ThemeManager()
        preferences = self.theme_manager.load_theme_preferences()
        self.theme_manager.apply_theme_preferences(preferences) 
        self.light_switch()
        # Agregar notificador a cada pantalla
        for screen in self.screen_manager.screens:
            self.add_notificador_to_screen(screen)
        return self.screen_manager
    
 

    def config_load_set(self,config):
        config_screen = self.screen_manager.get_screen('ConfigureScreen')
        config_screen.ids.style_text_conf.text= config["style"]
        config_screen.ids.styledin_text_conf.text =config["dinamic"] 
        config_screen.ids.schemeColor_text_conf.text = config["schemeColor"]
        config_screen.ids.paletteColor_text_conf.text = config["paletteColor"]

    def light_switch(self, change = False):
        home_screen = self.screen_manager.get_screen('HomeScreen')
        icon_button = home_screen.ids.btn_light
        
        if change:
            self.theme_cls.switch_theme()
        if self.theme_cls.theme_style == "Dark":
            icon_button.icon = "light-switch"
        else:
            icon_button.icon = "light-switch-off"
            

    def add_notificador_to_screen(self, screen):
        notificador = Notificador()
        screen.add_widget(notificador)
        setattr(screen, 'notificador', notificador)

    def show_notification(self, mensaje, icono='information', duracion=3):
        current_screen = self.screen_manager.current_screen
        if hasattr(current_screen, 'notificador'):
            current_screen.notificador.mostrar(mensaje, icono, duracion)

    def change_screen(self, activity, area=None):
        direction = 'right' if activity == 'HomeScreen' else 'left'
        self.screen_manager.transition.direction = direction
        self.current_activity = activity
        self.current = 'activity'
        self.root.current = self.current_activity
        if activity == 'HelpScreen' and area is not None:
            help_screen = self.screen_manager.get_screen('HelpScreen')
            help_screen.selected_area(area)

            


    def on_start(self):
        Window.size = (1024, 600)
        Window.borderless = True
        #Window.bind(on_draw=lambda _: print_gl_info())

        
    def on_stop(self):
        # Guarda las preferencias al cerrar la aplicación
        preferences = {
            'theme_style': self.theme_cls.theme_style,
            'dynamic_color': self.theme_cls.dynamic_color,
            'dynamic_scheme_name': self.theme_cls.dynamic_scheme_name,
            'primary_palette': self.theme_cls.primary_palette
        }
        self.theme_manager.save_theme_preferences(preferences)

if __name__ == "__main__":
    FisioAccess().run()
