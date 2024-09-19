import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_app import GraphApp
from src.button import Button
from src.serial_handler import SerialHandler
from src.utils import get_ip_address
from config.settings import *

from dial import DialScreen

from theming import Theming  # Importamos la clase Theming




class Screen:
    def __init__(self, game):
        self.game = game

    def draw(self,**kwargs):
        pass

    def handle_events(self, event):
        pass


class HomeScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.menu = VerticalMenu(game)  # Mover la instancia del menú aquí

    def draw(self, **kwargs):
        background = Theming().get('background')

        self.game.screen.fill(background)
        # Título centrado
        thm_title = Theming().get('title_str')
        title_surf = self.game.title_font.render(f"{NAMEAPP} v{VER}", True, thm_title)
        title_rect = title_surf.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2))
        self.game.screen.blit(title_surf, title_rect)

        # Mostrar IP en el borde derecho
        thm_text = Theming().get('text')

        ip_surf = self.game.font.render(f"IP: {self.game.ip_address}", True, thm_text)
        ip_rect = ip_surf.get_rect(topright=(self.game.WIDTH - 10, 10))
        self.game.screen.blit(ip_surf, ip_rect)
    
        fps = self.game.clock.get_fps()
        fps_text = self.game.font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        self.game.screen.blit(fps_text, (10, 10))

        # Dibujar el menú vertical
        self.menu.draw()

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Maneja eventos del menú
            self.menu.handle_events(pos)



class ECGScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.menu = ToolsBar(game)  # Mover la instancia del menú aquí
        self.graph_app = GraphApp()

        
        
    def draw(self, **kwargs):
        value = kwargs["data"]

        background = Theming().get('background')
        self.game.screen.fill(background)
        # Dibujar gráfico y botones del ECG
        self.graph_app.draw_graph(self.game.screen, data=value)
        self.menu.draw()

        fps = self.game.clock.get_fps()
        fps_text = self.game.font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
        self.game.screen.blit(fps_text, (10, 10))

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Maneja eventos del menú
            self.menu.handle_events(pos)
            


class ToolsBar:
    def __init__(self, game):
        self.game = game
        height_bar = 50
        pos_bar_y = HEIGHT - height_bar
        pos_buttons_y = pos_bar_y + 10
        self.buttons= [
            Button(10, pos_buttons_y,30,30, "Iniciar", icon="play", on_click=self.play),
            Button(45,pos_buttons_y, 30, 30, "Detener", icon="stop",on_click=self.stop, enabled=False),
            Button(80,pos_buttons_y, 30, 30, "Grabar", icon="dot-circle-o",on_click=self.record, enabled=False),
            Button(105,pos_buttons_y, 30, 30, "+", icon="plus", on_click=self.zoom_in, enabled=False),
            Button(150,pos_buttons_y, 30, 30, "-", icon="minus",on_click=self.zoom_out, enabled=False)
        ]
        self.rect_x = 0
        self.rect_y = pos_bar_y
        self.rect_width = WIDTH
        self.rect_height = height_bar  # Ajustar altura según la cantidad de botones
        self.status = "stopped"
        self.record_status = False
        self.record_tick = 0
        
    def draw(self, **kwargs):
        # Dibujar el rectángulo de fondo del menú
        FOREGROUND = Theming().get('foreground')
        pygame.draw.rect(self.game.screen, FOREGROUND, (self.rect_x, self.rect_y, self.rect_width, self.rect_height))
        
        # Dibujar los botones
        for button in self.buttons:
            button.draw(self.game.screen, self.game.font)
            
        # Variable para controlar el intervalo base del cambio de icono
        self.icon_change_interval = 10  # Intervalo base, ajusta según necesidad

        if self.record_status:
            # Si el tick está en los primeros dos tercios del intervalo, muestra "dot-circle-r"
            if self.record_tick % (self.icon_change_interval * 3) < (self.icon_change_interval * 2):
                self.buttons[2].set_icon("dot-circle-r")
            # Si el tick está en el último tercio del intervalo, muestra "dot-circle-o"
            else:
                self.buttons[2].set_icon("dot-circle-o")
            
            # Incrementar el contador de ticks
            self.record_tick += 1

    def handle_events(self, pos):
        """Manejar eventos de clic del menú"""
        for button in self.buttons:
            if button.is_clicked(pos):
                button.click()
    
    def play(self):
        self.ToggleButtonPlay()
        
    def stop(self):
        self.stop_graph()
    
    def record(self):
        self.record_status = True 
        
    def zoom_in(self):
        self.game.current_screen.graph_app.zoom_in()
    
    def zoom_out(self):
        self.game.current_screen.graph_app.zoom_out()

    def ToggleButtonPlay(self):
        if self.status == "stopped":
            self.status = "played"
            self.buttons[0].set_icon("pause")
            self.buttons[2].enable()
            self.game.current_screen.graph_app.clear_data()
            self.game.current_screen.graph_app.played = True
            
        elif self.status == "played":
            self.status = "paused"
            self.buttons[0].set_icon("play")
            self.game.current_screen.graph_app.played = False
            self.buttons[1].enable()
        elif self.status == "paused":
            self.status = "played"
            self.buttons[0].set_icon("pause")
            self.game.current_screen.graph_app.played = True

    def stop_graph(self):
        self.game.current_screen.graph_app.graphing = False
        self.game.current_screen.graph_app.clear_data()
        self.buttons[0].set_icon("play")
        self.buttons[1].disable()
        self.status = "stopped"

        


class VerticalMenu:
    def __init__(self, game):
        self.game = game
        self.buttons = [
            Button(5, 20, 30, 30, "ECG", icon='heartbeat', on_click=self.go_to_ecg),
            Button(5, 55, 30, 30, "DIAL", icon='dashboard', on_click=self.go_to_dial)
            # Puedes añadir más botones aquí
        ]
        # Definir las dimensiones del menú
        self.rect_x = 0
        self.rect_y = 0
        self.rect_width = 50
        self.rect_height = HEIGHT  # Ajustar altura según la cantidad de botones

    def draw(self, **kwargs):
        # Dibujar el rectángulo de fondo del menú
        FOREGROUND = Theming().get('foreground')

        pygame.draw.rect(self.game.screen, FOREGROUND, (self.rect_x, self.rect_y, self.rect_width, self.rect_height))
        
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
            'dial': DialScreen(self, min_value=-5, max_value=5)  # Aquí se añade la nueva pantalla
        }

        self.current_screen = self.screens['home']



    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.current_screen.handle_events(event)

    def update(self):
        #revisar si se ha conectado algun sensor, aca debemos conocer el puerto de conexión del esp32 o que este envie un strig identificandose
        #revisar el arbol de software si ha cambiado y hay algo en el usb
        #alimentar a todos los servicios de la información 
        #if self.graph_app.draw_graph:
        #    new_value = self.serial_handler.get_data(True)
        #    self.graph_app.add_data_point(new_value)
        self.data = self.serial_handler.get_data(True)

    def draw(self, **kwargs):
        self.current_screen.draw(data=self.data)
        pygame.display.flip()


    def run(self):
        self.running = True
        while self.running:


            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(40)

        self.serial_handler.close()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
