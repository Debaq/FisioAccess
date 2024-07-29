from kivy.utils import hex_colormap
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from materialyoucolor.utils.platform_utils import SCHEMES

class PreferencesScreen(MDScreen):

    def switch_palette(self, selected_palette):
        print(selected_palette)
        app = MDApp.get_running_app()
        app.theme_cls.primary_palette = selected_palette
        self.save_preferences()

    def set_palette(self, menu_button):
        available_palettes = [name_color.capitalize() for name_color in hex_colormap.keys()]
        menu_items = []
        for name_palette in available_palettes:
            menu_items.append({"text": name_palette,
                 "on_release": lambda x=name_palette: self.switch_palette(x)})
        MDDropdownMenu( caller=menu_button, items=menu_items).open()

    def switch_theme(self, *args):
        app = MDApp.get_running_app()
        app.light_switch(change=True)
        self.save_preferences()

    def set_scheme_type(self, menu_button):
        menu_items = []
        for scheme_name in SCHEMES.keys():
            menu_items.append({"text": scheme_name,
                    "on_release": lambda x=scheme_name: self.update_scheme_name(x)})
        MDDropdownMenu( caller=menu_button, items=menu_items).open()
        
    def update_scheme_name(self, scheme):
        app = MDApp.get_running_app()
        app.theme_cls.dynamic_scheme_name = scheme
        self.save_preferences()

    def toggle_dynamic_color(self, *args):
        app = MDApp.get_running_app()
        app.theme_cls.dynamic_color = not app.theme_cls.dynamic_color
        self.save_preferences()

    def save_preferences(self):
        app = MDApp.get_running_app()
        preferences = {
            'theme_style': app.theme_cls.theme_style,
            'dynamic_color': app.theme_cls.dynamic_color,
            'dynamic_scheme_name': app.theme_cls.dynamic_scheme_name,
            'primary_palette': app.theme_cls.primary_palette
        }
        app.theme_manager.save_theme_preferences(preferences)
        app.theme_manager.apply_theme_preferences(preferences)


