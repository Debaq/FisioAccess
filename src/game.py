from theming import Theming
from dial import DialScreen
from config.settings import *
from src.utils import get_ip_address
from src.serial_handler import SerialHandler
from src.button import Button
from src.eeg_screen import ECGScreen
from src.screen import Screen
import pygame
import sys
import os



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class HomeScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.menu = VerticalMenu(game)  # Mover la instancia del menú aquí

    def draw(self, **kwargs):
        background = Theming().get('background')

        self.game.screen.fill(background)
        # Título centrado
        thm_title = Theming().get('title_str')
        title_surf = self.game.title_font.render(
            f"{NAMEAPP} v{VER}", True, thm_title)
        title_rect = title_surf.get_rect(
            center=(self.game.WIDTH // 2, self.game.HEIGHT // 2))
        self.game.screen.blit(title_surf, title_rect)

        # Mostrar IP en el borde derecho
        thm_text = Theming().get('text')

        ip_surf = self.game.font.render(
            f"IP: {self.game.ip_address}", True, thm_text)
        ip_rect = ip_surf.get_rect(topright=(self.game.WIDTH - 10, 10))
        self.game.screen.blit(ip_surf, ip_rect)

        fps = self.game.clock.get_fps()
        fps_text = self.game.font.render(
            f"FPS: {int(fps)}", True, (255, 255, 255))
        self.game.screen.blit(fps_text, (10, 10))

        # Dibujar el menú vertical
        self.menu.draw()

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Maneja eventos del menú
            self.menu.handle_events(pos)





class VerticalMenu:
    def __init__(self, game):
        self.game = game
        self.buttons = [
            Button(5, 20, 30, 30, "ECG", icon='heartbeat',
                   on_click=self.go_to_ecg),
            Button(5, 55, 30, 30, "DIAL", icon='dashboard',
                   on_click=self.go_to_dial)
            # Puedes añadir más botones aquí
        ]
        # Definir las dimensiones del menú
        self.rect_x = 0
        self.rect_y = 0
        self.rect_width = 50
        self.rect_height = HEIGHT

    def draw(self, **kwargs):
        # Dibujar el rectángulo de fondo del menú
        FOREGROUND = Theming().get('foreground')

        pygame.draw.rect(self.game.screen, FOREGROUND, (self.rect_x,
                         self.rect_y, self.rect_width, self.rect_height))

        # Dibujar los botones
        for button in self.buttons:
            button.draw(self.game.screen, self.game.font)

    def handle_events(self, pos):
        """Manejar eventos de clic del menú"""
        for button in self.buttons:
            if button.is_clicked(pos):
                button.click()

    def go_to_ecg(self):
        self.game.current_screen = self.game.screens['ecg']

    def go_to_dial(self):
        self.game.current_screen = self.game.screens['dial']


class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.transparent_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

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
