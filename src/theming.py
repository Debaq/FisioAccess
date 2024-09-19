import json
import pygame
from config.settings import *


class Theming:
    _instance = None  # Variable estática para la instancia única de Theming
    _current_theme = {}
    _current_scheme = 'blue'
    _current_mode = 'light'

    def __new__(cls, *args, **kwargs):
        """Override __new__ to implement el patrón singleton"""
        if cls._instance is None:
            cls._instance = super(Theming, cls).__new__(cls)
        return cls._instance

    def __init__(self, color_scheme='blue', mode='light'):
        """Inicializa el tema con el esquema y modo especificados solo si no está inicializado"""
        if not Theming._current_theme:  # Solo cargar si no está ya inicializado
            self.load_themes(THEME_PATH)
            self.set_theme(color_scheme, mode)

    def load_themes(self, filename):
        """Carga los temas desde un archivo JSON"""
        with open(filename, 'r') as f:
            self._themes = json.load(f)

    def set_theme(self, color_scheme, mode='light'):
        """Cambia el esquema y modo del tema actual y lo guarda en _current_theme"""
        if color_scheme in self._themes and mode in self._themes[color_scheme]:
            Theming._current_scheme = color_scheme
            Theming._current_mode = mode
            Theming._current_theme = self._themes[color_scheme][mode]
        else:
            raise ValueError(f"Theme '{color_scheme}' or mode '{mode}' not found in themes.")

    def get(self, color_key):
        """Obtiene el color del tema actual guardado"""
        if not Theming._current_theme:
            raise ValueError("Theme not initialized. Call set_theme() first.")
        
        try:
            # Si el valor devuelto es un diccionario (por ejemplo, line_graph), no lo convertimos a pygame.Color
            value = Theming._current_theme[color_key]
            
            # Si es un string o un valor que puede convertirse a color, lo convertimos a pygame.Color
            if isinstance(value, str) or isinstance(value, list):
                return pygame.Color(value)
            else:
                # Si no es un string (ej. es un diccionario), simplemente lo devolvemos como está
                return value
        
        except KeyError:
            raise ValueError(f"Color key '{color_key}' not found in current theme.")
