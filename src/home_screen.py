from config.settings import *
from theming import Theming
from src.screen import Screen
from src.button import Button
import pygame

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
