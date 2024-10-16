from src.screen import Screen
from tools_bar_graph import ToolsBar
from src.graph_app import GraphApp
from src.slider import Slider
from theming import Theming
import pygame
from src.utils import get_ip_address, get_display_server, get_cpu_temperature
import math


class ECGScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.menu = ToolsBar(game)  # Mover la instancia del menú aquí
        self.graph_app = GraphApp()
        self.slider_vertical = Slider(1000, 40, 0, 510, direction="vertical",
                                      handles_visible=(True, False),
                                      handle_icon="caret-left",
                                      callback_function=self.slider_callback)

        self.slider_horizontal = Slider(30, 30, 0, 950, direction="horizontal",
                                        handles_visible=(True, False),
                                        handle_icon="caret-down",
                                        callback_function=self.slider_callback)

        self.slider_vertical.hide()
        self.slider_horizontal.hide()
        self.time_text = "0"
        self.voltage_text = "0"

        # self.cuadro = pygame.Rect(0,0,100,400)

    def slider_callback(self, positions):
        """Función de callback que se llama al mover los sliders"""
        slider, pos1, pos2 = positions
        if slider == 'vertical':
            self.voltage_text = self.posicion_a_voltaje(pos1, pos2)
        else:
            self.time_text = self.posicion_a_tiempo(pos1, pos2)

    def posicion_a_voltaje(self, pos1, pos2, posicion_min=83, posicion_max=428, vmin=0, vmax=1.86):
        voltaje_sup = vmin + ((pos1 - posicion_min) / (posicion_max - posicion_min)) * (vmax - vmin)
        voltaje_inf = vmin + ((pos2 - posicion_min) / (posicion_max - posicion_min)) * (vmax - vmin)
        
        voltaje = voltaje_inf - voltaje_sup
        
        return round(voltaje,2)

    def posicion_a_tiempo(self, pos1, pos2, posicion_min=425, posicion_max=760, tiempo_min=0, tiempo_max=1000):
        tiempo1 = tiempo_min + ((pos1 - posicion_min) / (posicion_max - posicion_min)) * (tiempo_max - tiempo_min)
        tiempo2 = tiempo_min + ((pos2 - posicion_min) / (posicion_max - posicion_min)) * (tiempo_max - tiempo_min)
        tiempo = tiempo2 - tiempo1
        tiempo = (tiempo / 1000)*2
        step_zoom = self.graph_app.zoom_state
        tiempo = self.fx_time_zoom(tiempo, step_zoom)
        return round(tiempo, 3)

    def fx_time_zoom(self, actual_number, step):
        factor = 1.2
        number = actual_number
        if step > 0:
            for i in range(step):
                number = number/factor
        elif step == 0:
            return number
        elif step < 0:
            for i in range(abs(step)):
                number = number*factor
        return number


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
        self.game.screen.blit(Serial_info, (400, 550))
        self.game.screen.blit(Serial_raw, (400, 570))
               
        mark_text = self.game.font.render(f"Tiempo: {str(self.time_text)}seg., Amplitud: {str(self.voltage_text)} uV.", True, thm_text)
        self.game.screen.blit(mark_text, (400, 10))       

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
