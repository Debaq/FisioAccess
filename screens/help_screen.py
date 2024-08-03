from kivymd.uix.screen import MDScreen
import os

class HelpScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("HelpScreen initialized")

    def selected_area(self, area):
        self.load_help_content(area)

        
    def load_help_content(self, area):
            print(f"Loading help content for activity: {area}")
            help_rst = self.ids.help_text

            file_path = os.path.join('rst', f"{area}.rst")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    rst_content = file.read()
                    help_rst.text = rst_content
            else:
                help_rst.text = f"Aca va la ayuda de la actividad {area}"