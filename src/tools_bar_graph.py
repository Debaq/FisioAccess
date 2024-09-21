from config.settings import HEIGHT, WIDTH
from src.button import Button
from theming import Theming
import pygame


class ToolsBar:
    def __init__(self, game):
        self.game = game
        height_bar = 50
        pos_bar_y = HEIGHT - height_bar
        pos_buttons_y = pos_bar_y + 10
        self.buttons = [
            Button(10, pos_buttons_y, 30, 30, "play",
                   icon="play", on_click=self.play),
            Button(45, pos_buttons_y, 30, 30, "stop",
                   icon="stop", on_click=self.stop, enabled=False),
            Button(80, pos_buttons_y, 30, 30, "record",
                   icon="dot-circle-o", on_click=self.record, enabled=False),
            Button(115, pos_buttons_y, 30, 30, "+", icon="plus",
                   on_click=self.zoom_in, enabled=False),
            Button(150, pos_buttons_y, 30, 30, "-", icon="minus",
                   on_click=self.zoom_out, enabled=False),
            Button(185, pos_buttons_y, 65, 30, "Medir",
                   on_click=self.measure, enabled=False),
            Button(250, pos_buttons_y, 70, 30, "Marcar",
                   on_click=self.marks, enabled=False),
        ]
        self.rect_x = 0
        self.rect_y = pos_bar_y
        self.rect_width = WIDTH
        self.rect_height = height_bar
        self.status = "stopped"
        self.record_status = False
        self.record_tick = 0
        # Intervalo base para el cambio de icono
        self.icon_change_interval = 10
        # Indica si hay datos disponibles para borrar
        self.data_available = False
        self.last_button = None

    def draw(self, **kwargs):
        # Dibujar el rectángulo de fondo del menú
        FOREGROUND = Theming().get('foreground')
        pygame.draw.rect(self.game.screen, FOREGROUND, (self.rect_x,
                         self.rect_y, self.rect_width, self.rect_height))

        # Dibujar los botones
        for button in self.buttons:
            button.draw(self.game.screen, self.game.font)

        # Control de cambio de icono durante la grabación
        if self.record_status:
            if (self.record_tick % (self.icon_change_interval * 3) <
                    self.icon_change_interval * 2):
                self.buttons[2].set_icon("dot-circle-r")  # Grabando
            else:
                self.buttons[2].set_icon("dot-circle-o")  # No grabando (flash)
            self.record_tick += 1

    def handle_events(self, pos):
        """Manejar eventos de clic del menú"""
        for button in self.buttons:
            if button.is_clicked(pos):
                button.click()

    def play(self):
        if self.status == "stopped" or self.status == "paused":
            self.game.current_screen.graph_app.play()
        else:
            self.game.current_screen.graph_app.play(False)
        self.last_button = "play"
        self.toggle_play_pause()

    def stop(self):
        if self.status == "paused":
            self.clear_data()
        elif self.status == "recored":
            self.stop_recording()
        elif self.status == "stopped" and self.last_button == "stop":
            self.clear_data()

        self.last_button = "stop"
        self.toggle_play_pause()
        self.record_status = False

    def record(self):
        """Inicia la grabación de datos"""
        self.last_button = "record"
        self.toggle_play_pause()

        self.record_status = True

        # Desactivar botón de grabar cuando está grabando
        # self.game.current_screen.graph_app.start_recording()

    def zoom_in(self):
        self.game.current_screen.graph_app.zoom_in()

    def zoom_out(self):
        self.game.current_screen.graph_app.zoom_out()

    def measure(self):
        self.game.measure_activate(True)

    def marks(self):
        self.game.marks_activate(True)

    def toggle_play_pause(self):
        """Alterna entre iniciar y pausar la muestra de datos"""
        if self.status == "stopped" and self.last_button == "stop":
            self.buttons[0].set_icon("play")  # Cambiar a ícono de play
            self.buttons[0].enable()  # Mantener Play habilitado
            self.buttons[1].set_icon("stop")  # Cambiar a ícono de stop
            self.buttons[1].disable()  # Desactivar botón de stop
            self.buttons[2].disable()  # Desactivar botón de grabar
            self.buttons[3].disable()  # Desactivar Zoom In
            self.buttons[4].disable()  # Desactivar Zoom Out
            self.buttons[5].disable()  # Desactivar el medidor
            self.buttons[6].disable()  # Desactivar el marcador

        elif self.status == "stopped":
            # Iniciar la muestra de datos
            self.status = "played"
            self.buttons[0].set_icon("pause")  # Cambiar a ícono de pausa
            self.buttons[1].set_icon("stop")  # Asegurar que sea icono de stop
            self.buttons[1].disable()
            self.buttons[2].enable()  # Habilitar botón de grabar

        elif self.status == "played" and self.last_button == "play":
            # Pausar la muestra de datos
            self.status = "paused"
            self.buttons[0].set_icon("play")  # Cambiar a ícono de play
            self.buttons[0].enable()  # Mantener Play habilitado
            self.buttons[1].set_icon("trash")  # Cambiar a ícono de borrar
            self.buttons[1].enable()  # Habilitar botón de borrar
            self.buttons[2].disable()  # Desactivar botón de grabar
            self.buttons[3].enable()  # Habilitar Zoom In
            self.buttons[4].enable()  # Habilitar Zoom Out
            self.buttons[5].enable()  # Habilita el medidor
            self.buttons[6].enable()  # Habilita el marcador

        elif self.status == "played" and self.last_button == "record":
            # graba los datos
            self.status = "recored"

            self.buttons[0].set_icon("play")  # Cambiar a ícono de play
            self.buttons[0].disable()
            self.buttons[1].set_icon("stop")
            self.buttons[1].enable()  # Habilitar botón de borrar
            self.buttons[2].disable()  # Desactivar botón de grabar
            self.buttons[3].disable()  # Habilitar Zoom In
            self.buttons[4].disable()  # Habilitar Zoom Out
            self.buttons[5].disable()  # Habilita el medidor
            self.buttons[6].disable()  # Habilita el marcador

        elif self.status == "recored" and self.last_button == "stop":
            self.status = "stopped"
            self.buttons[0].disable()  # Desactivar botón de borrar
            self.buttons[1].enable()  # Habilita botón de borrar
            self.buttons[1].set_icon("trash")  # Cambiar a ícono de borrar
            self.buttons[2].set_icon(
                "dot-circle-o")  # Cambiar icono a grabación activa
            self.buttons[2].disable()  # Desactivar botón de grabar
            self.buttons[3].enable()  # Habilita Zoom In
            self.buttons[4].enable()  # Habilita Zoom Out
            self.buttons[5].enable()  # Habilita el medidor
            self.buttons[6].enable()  # Habilita el marcador

        elif self.status == "paused" and self.last_button == "stop":
            # Reanudar la muestra de datos
            self.status = "stopped"
            self.buttons[0].enable()  # Habilitar botón de borrar
            self.buttons[1].disable()  # Desactivar botón de borrar
            self.buttons[2].set_icon(
                "dot-circle-o")  # Cambiar icono a grabación activa
            self.buttons[2].disable()  # Desactivar botón de grabar
            self.buttons[3].disable()  # Desactivar Zoom In
            self.buttons[4].disable()  # Desactivar Zoom Out
            self.buttons[5].disable()  # Desactivar el medidor
            self.buttons[6].disable()  # Desactivar el marcador

        elif self.status == "paused" and self.last_button == "play":
            # Reanudar la muestra de datos
            self.status = "played"
            self.buttons[0].set_icon("pause")  # Cambiar a ícono de pausa
            self.buttons[1].set_icon("stop")  # Asegurar que sea icono de stop
            self.buttons[1].disable()
            self.buttons[2].enable()  # Habilitar botón de grabar

    def stop_recording(self):
        """Detiene la grabación y muestra de datos"""
        self.record_status = False
        self.record_tick = 0  # Reiniciar el contador de grabación
        self.data_available = True  # Indicar que hay datos disponibles
        self.game.current_screen.graph_app.play(False)

    def clear_data(self):
        """Borra los datos de la muestra"""
        self.game.current_screen.graph_app.clear_data()
        self.data_available = False  # Indicar que no hay datos
