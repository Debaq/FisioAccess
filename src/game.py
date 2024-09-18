import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_app import GraphApp
from src.button import Button
from src.serial_handler import SerialHandler
from src.utils import get_ip_address
from config.settings import *


class Screen:
    def __init__(self, game):
        self.game = game

    def draw(self):
        pass

    def handle_events(self, event):
        pass


class HomeScreen(Screen):
    def draw(self):
        self.game.screen.fill(BLACK)
        # Título centrado
        title_surf = self.game.title_font.render("FissioAccess", True, WHITE)
        title_rect = title_surf.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2))
        self.game.screen.blit(title_surf, title_rect)

        # Mostrar IP en el borde derecho
        ip_surf = self.game.font.render(f"IP: {self.game.ip_address}", True, WHITE)
        ip_rect = ip_surf.get_rect(topright=(self.game.WIDTH - 10, 10))
        self.game.screen.blit(ip_surf, ip_rect)

    def handle_events(self, event):
        pass


class ECGScreen(Screen):
    def draw(self):
        self.game.screen.fill(BLACK)
        # Dibujar gráfico y botones del ECG
        self.game.graph_app.draw_graph(self.game.screen)
        self.game.start_button.draw(self.game.screen, self.game.font)
        self.game.stop_button.draw(self.game.screen, self.game.font)

    def handle_events(self, event):
        pos = event.pos
        if self.game.start_button.is_clicked(pos):
            self.game.toggle_graph()
        elif self.game.stop_button.is_clicked(pos):
            self.game.stop_graph()


class VerticalMenu:
    def __init__(self, game):
        self.game = game
        self.buttons = [
            Button(10, 50, 60, 60, "", icon='heartbeat', on_click=self.go_to_ecg),
            # Puedes añadir más botones aquí
        ]

    def draw(self):
        for button in self.buttons:
            button.draw(self.game.screen, self.game.font)

    def go_to_ecg(self):
        self.game.current_screen = self.game.screens['ecg']


class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
        pygame.display.set_caption("FissioAccess")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.title_font = pygame.font.Font(FONT_PATH, 48)

        self.graph_app = GraphApp()
        self.serial_handler = SerialHandler(SERIAL_PORT, BAUD_RATE)
        self.ip_address = get_ip_address()

        self.screens = {
            'home': HomeScreen(self),
            'ecg': ECGScreen(self),
            # Aquí agregarás más pantallas
        }

        self.current_screen = self.screens['home']

        self.menu = VerticalMenu(self)

        self.initialize_buttons()

    def initialize_buttons(self):
        self.start_button = Button(10, self.HEIGHT + 10, 100, 30, "Iniciar", GREEN)
        self.stop_button = Button(120, self.HEIGHT + 10, 100, 30, "Detener", RED)
        self.zoom_in_button = Button(self.WIDTH - 150, self.HEIGHT + 10, 50, 30, "+", (0, 255, 0))
        self.zoom_out_button = Button(self.WIDTH - 90, self.HEIGHT + 10, 50, 30, "-", (255, 0, 0))

        self.stop_button.disable()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.current_screen.handle_events(event)

    def update(self):
        if self.graph_app.draw_graph:
            new_value = self.serial_handler.get_data(True)
            self.graph_app.add_data_point(new_value)

    def draw(self):
        self.current_screen.draw()
        self.menu.draw()  # Dibujar menú en todas las pantallas
        pygame.display.flip()

    def toggle_graph(self):
        if not self.graph_app.graphing:
            self.graph_app.graphing = True
            self.start_button.set_text("Pausar")
            self.stop_button.enable()
        else:
            self.graph_app.graphing = False
            self.start_button.set_text("Iniciar")
            self.stop_button.disable()

    def stop_graph(self):
        self.graph_app.graphing = False
        self.graph_app.clear_data()
        self.start_button.set_text("Iniciar")
        self.stop_button.disable()

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
