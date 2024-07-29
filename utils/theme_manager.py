import json
from kivymd.app import MDApp
import os
import shutil

class ThemeManager:
    PREFERENCES_FILE = 'config/theme_preferences.json'
    DEFAULT_PREFERENCES_FILE = 'config/default_theme_preferences.json'

    @classmethod
    def load_theme_preferences(cls):
        try:
            with open(cls.PREFERENCES_FILE, 'r') as file:
                preferences = json.load(file)
            # Verificar que todas las claves necesarias estén presentes
            required_keys = ['theme_style', 'dynamic_color', 'dynamic_scheme_name', 'primary_palette']
            if all(key in preferences for key in required_keys):
                return preferences
            else:
                raise ValueError("JSON file is missing required keys")
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            # Si el archivo no existe, está corrupto o le faltan claves, usamos el de respaldo
            cls._restore_from_backup()
            return cls.load_theme_preferences()  # Intentamos cargar de nuevo

    @classmethod
    def save_theme_preferences(cls, preferences):
        try:
            with open(cls.PREFERENCES_FILE, 'w') as file:
                json.dump(preferences, file, indent=4)
        except Exception as e:
            print(f"Error saving preferences: {e}")

    @classmethod
    def _restore_from_backup(cls):
        if os.path.exists(cls.DEFAULT_PREFERENCES_FILE):
            shutil.copy(cls.DEFAULT_PREFERENCES_FILE, cls.PREFERENCES_FILE)
            print("Preferences file restored from backup.")
        else:
            print("Default preferences file not found. Creating a new one.")
            default_preferences = {
                'theme_style': 'Dark',
                'dynamic_color': False,
                'dynamic_scheme_name': 'SPRITZ',
                'primary_palette': 'Darkviolet'
            }
            cls.save_theme_preferences(default_preferences)

    @staticmethod
    def apply_theme_preferences(preferences):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = preferences['theme_style']
        app.theme_cls.dynamic_color = preferences['dynamic_color']
        app.theme_cls.dynamic_scheme_name = preferences['dynamic_scheme_name']
        app.theme_cls.primary_palette = preferences['primary_palette']
        
        if preferences['dynamic_color']:
            dinamic = "Activado"
        else:
            dinamic = "Desactivado"
            
        config = {"style":preferences['theme_style'], "dinamic":dinamic,
                  "schemeColor":preferences['dynamic_scheme_name'], "paletteColor":preferences['primary_palette']}
        app.config_load_set(config)