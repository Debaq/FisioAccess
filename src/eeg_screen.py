from src.screen import Screen
from tools_bar_graph import ToolsBar
from src.graph_app import GraphApp
from src.slider import Slider
from theming import Theming
import pygame


class ECGScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.menu = ToolsBar(game)  # Mover la instancia del menú aquí
        self.graph_app = GraphApp()
        self.slider_vertical = Slider(1000, 40, 0, 470, direction="vertical",
                                      handles_visible=(True, False),
                                      handle_icon="caret-left",
                                      callback_function=self.slider_callback)

        self.slider_horizontal = Slider(30, 30, 0, 950, direction="horizontal",
                                        handles_visible=(True, False),
                                        handle_icon="caret-down",
                                        callback_function=self.slider_callback)

        self.slider_vertical.hide()
        self.slider_horizontal.hide()

        # self.cuadro = pygame.Rect(0,0,100,400)

    def slider_callback(self, positions):
        """Función de callback que se llama al mover los sliders"""
        print("Posiciones de los sliders:", positions)

    def measure_activate(self, active=True):
        self.slider_vertical.hide(False)
        self.slider_horizontal.hide(False)

        if active:
            self.slider_vertical.handles_visible = (True, True)
            self.slider_horizontal.handles_visible = (True, True)
        else:
            self.slider_vertical.handles_visible = (False, False)
            self.slider_horizontal.handles_visible = (False, False)

    def mark_activate(self, activate=True):
        self.slider_vertical.hide(False)
        self.slider_horizontal.hide(False)

        if activate:
            self.slider_vertical.handles_visible = (True, False)
            self.slider_horizontal.handles_visible = (True, False)
        else:
            self.slider_vertical.handles_visible = (False, False)
            self.slider_horizontal.handles_visible = (False, False)

    def draw(self, **kwargs):
        # obtener los datos del grafico
        value = kwargs["data"]
        # dibujar el fondo
        background = Theming().get('background')
        self.game.screen.fill(background)

        # Dibujar gráfico y botones del ECG
        self.graph_app.draw_graph(self.game.screen, data=value)
        self.menu.draw()



        # dibujar los sliders
        self.slider_vertical.draw(self.game.screen)
        self.slider_horizontal.draw(self.game.screen)
        
        cpu_temp = get_cpu_temperature()
        fps = self.game.clock.get_fps()

        thm_text = Theming().get('text')
        fps_temp_text = self.game.font.render(
            f"FPS: {int(fps)} | CPU: {cpu_temp}", True, thm_text)
        self.game.screen.blit(fps_temp_text, (10, 10))
        
        data_serial = kwargs["data"]
        data_info = kwargs["info"]
        
        Serial_raw = self.game.font.render(
            f"Serial Info: {data_serial}", True, thm_text)
        Serial_info = self.game.font.render(
            f"Serial Raw: {data_info}", True, thm_text)
        self.game.screen.blit(Serial_info, (400, 540))
        self.game.screen.blit(Serial_raw, (400, 560))
        

        # pygame.draw.rect(self.game.transparent_surface, (255, 0, 0, 100),
        # self.cuadro)
        # self.game.screen.blit(self.game.transparent_surface, (0, 0))

    def handle_events(self, event):
        self.slider_vertical.handle_events(event)
        self.slider_horizontal.handle_events(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Maneja eventos del menú
            self.menu.handle_events(pos)
