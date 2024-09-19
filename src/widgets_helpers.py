import os
import pygame
from config.settings import *



def icon(icon, width, height, size, theme): 

    theme = 'black' if theme is 'ligth' else 'white'
    icon_path = os.path.join(ICONS_PATH, theme, 'png', str(size), f'{icon}.png')
    try:
        icon = pygame.image.load(icon_path)  # Cargar el icono si existe una ruta
        icon = pygame.transform.scale(icon, (width - 10, height - 10))  # Escalar el icono al tamaño del botón
        return icon
    except FileNotFoundError:
        raise "No existe el icono"