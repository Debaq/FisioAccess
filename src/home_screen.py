from config.settings import NAMEAPP, VER, HEIGHT
from theming import Theming
from src.screen import Screen
from src.button import Button
from helper_qr import QRGenerator
from src.utils import get_ip_address, get_display_server
import pygame

class HomeScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.menu = VerticalMenu(game)
        
        # Generate QR code once
        qr_gen = QRGenerator()
        self.qr = qr_gen.generate_qr_surface("http://172.17.41.173:5000", (200, 200))
        
        # Pre-render title
        thm_title = Theming().get('title_str')
        self.title_surf = game.title_font.render(f"{NAMEAPP} v{VER}", True, thm_title)
        self.title_rect = self.title_surf.get_rect(center=(game.WIDTH // 2, game.HEIGHT // 2))
        
        # Pre-render IP and display server info
        self.display_server = get_display_server()
        self.update_ip_display()

    def update_ip_display(self):
        thm_text = Theming().get('text')
        self.ip_display_surf = self.game.font.render(
            f"IP: {self.game.ip_address} {self.display_server}", True, thm_text)
        self.ip_display_rect = self.ip_display_surf.get_rect(topright=(self.game.WIDTH - 10, 10))

    def draw(self, **kwargs):
        background = Theming().get('background')
        self.game.screen.fill(background)

        # Draw pre-rendered title
        self.game.screen.blit(self.title_surf, self.title_rect)

        # Draw pre-generated QR
        self.game.screen.blit(self.qr, (800, 50))

        # Draw pre-rendered IP and display info
        self.game.screen.blit(self.ip_display_surf, self.ip_display_rect)

        # FPS counter (this needs to be updated each frame)
        fps = self.game.clock.get_fps()
        fps_text = self.game.font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        self.game.screen.blit(fps_text, (10, 10))

        # Draw vertical menu
        self.menu.draw()

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
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
        pass
        # self.game.current_screen = self.game.screens['dial']
