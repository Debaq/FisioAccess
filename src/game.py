from serial_handler import SerialHandler
from theming import Theming
from dial import DialScreen
from config.settings import *
from src.utils import get_ip_address
from src.eeg_screen import ECGScreen
from src.home_screen import HomeScreen
import pygame
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

        self.serial_handler = SerialHandler(SERIAL_PORT, BAUD_RATE)
        self.ip_address = get_ip_address()
        self.data = []

        self.screens = {
            'home': HomeScreen(self),
            'ecg': ECGScreen(self),
            # Aquí se añade la nueva pantalla
            'dial': DialScreen(self, min_value=-5, max_value=5)
        }

        self.current_screen = self.screens['home']
        self.ctrl_pressed = False
        self.alt_pressed = False

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.ctrl_pressed = True
                elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    self.alt_pressed = True
                elif event.key == pygame.K_BACKSPACE:
                    if self.ctrl_pressed and self.alt_pressed:
                        print("Ctrl+Alt+Backspace pressed. Exiting game...")
                        self.running = False
                        return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.ctrl_pressed = False
                elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    self.alt_pressed = False
            
            self.current_screen.handle_events(event)

    def update(self):
        # revisar si se ha conectado algun sensor, aca debemos conocer el
        # puerto de conexión del esp32 o que este envie un string
        # identificandose
        # revisar el arbol de software si ha cambiado y hay algo en el usb
        # alimentar a todos los servicios de la información
        # if self.graph_app.draw_graph:
        #    new_value = self.serial_handler.get_data(True)
        #    self.graph_app.add_data_point(new_value)
        self.data = self.serial_handler.get_data(True)

    def draw(self, **kwargs):
        self.transparent_surface.fill((0, 0, 0, 0))

        self.current_screen.draw(data=self.data)
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
