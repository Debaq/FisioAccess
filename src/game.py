from serial_handler import SerialHandler
from theming import Theming
from dial import DialScreen
from config.settings import *
from src.utils import get_ip_address
from src.eeg_screen import ECGScreen
from src.home_screen import HomeScreen
import pygame
import pygame
from pygame import cursors
import sys
import os

theming = Theming(color_scheme='purple', mode='dark')

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.transparent_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        pygame.display.set_caption(f"{NAMEAPP}")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.title_font = pygame.font.Font(FONT_PATH, 48)

        self.serial_handler = SerialHandler()
        self.serial_handler.connect()
        self.ip_address = get_ip_address()
        self.data = []
        self.data_serial_info = None
        self.data_serial_raw = None

        self.screens = {
            'home': HomeScreen(self),
            'ecg': ECGScreen(self),
            # Aquí se añade la nueva pantalla
            'dial': DialScreen(self, min_value=-5, max_value=5)
        }

        self.current_screen = self.screens['home']
        self.ctrl_pressed = False
        self.alt_pressed = False
        #pygame.mouse.set_cursor(cursors.arrow)  # O cualquier otro cursor que prefieras
        #cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        #pygame.mouse.set_cursor(cursor)  # O cualquier otro cursor que prefieras
         # Offset para ajustar la posición del toque
        self.touch_offset_x = 0
        self.touch_offset_y = 0
        self.touch_indicator = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.touch_indicator, (255, 0, 0, 128), (10, 10), 10)

    def measure_activate(self, state):
        try:
            self.current_screen.measure_activate(state)
        except Exception:
            pass

    def marks_activate(self, state):
        try:
            self.current_screen.mark_activate(state)
        except Exception:
            pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Ajustar la posición del clic
                pos = (event.pos[0] + self.touch_offset_x, 
                       event.pos[1] + self.touch_offset_y)
                # Pasar el evento ajustado a la pantalla actual
                adjusted_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': event.button})
                self.current_screen.handle_events(adjusted_event)
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.handle_key_events(event)
            else:
                # Para otros tipos de eventos, pasarlos directamente
                self.current_screen.handle_events(event)

    def handle_key_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                self.ctrl_pressed = True
            elif event.key in (pygame.K_LALT, pygame.K_RALT):
                self.alt_pressed = True
            elif event.key == pygame.K_BACKSPACE:
                if self.ctrl_pressed and self.alt_pressed:
                    print("Ctrl+Alt+Backspace pressed. Exiting game...")
                    self.running = False
                    return
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                self.ctrl_pressed = False
            elif event.key in (pygame.K_LALT, pygame.K_RALT):
                self.alt_pressed = False

                
    def update(self):
        # revisar si se ha conectado algun sensor, aca debemos conocer el
        # puerto de conexión del esp32 o que este envie un string
        # identificandose
        # revisar el arbol de software si ha cambiado y hay algo en el usb
        # alimentar a todos los servicios de la información
        # if self.graph_app.draw_graph:
        #    new_value = self.serial_handler.get_data(True)
        #    self.graph_app.add_data_point(new_value)
        self.data_serial_raw = self.serial_handler.get_data(False)
        
#        if data_serial_raw != "":
 #           if data_serial_raw.startswith("INFO"):
 #               self.data_serial_info = data_serial_raw
 #           elif data_serial_raw.startswith("ECG"): 
 #               self.data_serial_raw = data_serial_raw


    def draw(self, **kwargs):
        self.transparent_surface.fill((0, 0, 0, 0))

        self.current_screen.draw(data=self.data_serial_raw, info=self.data_serial_info)

        # Dibujar el indicador de toque si se está tocando la pantalla
        if pygame.mouse.get_pressed()[0]:  # Si se está presionando el botón izquierdo del mouse (o tocando la pantalla)
            pos = pygame.mouse.get_pos()
            self.screen.blit(self.touch_indicator, 
                             (pos[0] - 10 + self.touch_offset_x, 
                              pos[1] - 10 + self.touch_offset_y))

        
        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:

            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        self.serial_handler.close()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
