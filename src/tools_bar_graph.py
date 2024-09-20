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
            Button(10, pos_buttons_y, 30, 30, "Iniciar",
                   icon="play", on_click=self.play),
            Button(45, pos_buttons_y, 30, 30, "Detener",
                   icon="stop", on_click=self.stop, enabled=False),
            Button(80, pos_buttons_y, 30, 30, "Grabar",
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
        self.toggle_play_pause()

    def stop(self):
        if self.record_status:
            self.stop_recording()
        elif self.data_available:
            self.clear_data()
        else:
            self.toggle_stop_to_trash()

    def record(self):
        """Inicia la grabación de datos"""
        self.record_status = True
        # Cambiar icono a grabación activa
        self.buttons[2].set_icon("dot-circle-r")
        # Desactivar botón de grabar cuando está grabando
        self.buttons[2].disable()
        self.game.current_screen.graph_app.start_recording()
        self.buttons[0].disable()  # Desactivar Play/Pause durante la grabación
        self.buttons[1].set_icon("stop")  # Cambiar icono de detener grabación
        # Activar el botón de Stop para detener grabación
        self.buttons[1].enable()

    def zoom_in(self):
        self.game.current_screen.graph_app.zoom_in()

    def zoom_out(self):
        self.game.current_screen.graph_app.zoom_out()

    def toggle_play_pause(self):
        """Alterna entre iniciar y pausar la muestra de datos"""
        if self.status == "stopped":
            # Iniciar la muestra de datos
            self.status = "played"
            self.buttons[0].set_icon("pause")  # Cambiar a ícono de pausa
            self.buttons[1].set_icon("stop")  # Asegurar que sea icono de stop
            self.buttons[1].disable()
            self.buttons[2].enable()  # Habilitar botón de grabar
            self.game.current_screen.graph_app.played = True
        elif self.status == "played":
            # Pausar la muestra de datos
            self.status = "paused"
            self.buttons[0].set_icon("play")  # Cambiar a ícono de play
            self.buttons[0].enable()  # Mantener Play habilitado
            self.buttons[1].set_icon("trash")  # Cambiar a ícono de borrar
            self.buttons[1].enable()  # Habilitar botón de borrar
            self.buttons[2].disable()  # Desactivar botón de grabar
            self.buttons[3].enable()  # Habilitar Zoom In
            self.buttons[4].enable()  # Habilitar Zoom Out
            self.buttons[5].enable() # Habilita el medidor
            self.buttons[6].enable() # Habilita el marcador

            self.game.current_screen.graph_app.played = False
        elif self.status == "paused":
            # Reanudar la muestra de datos
            self.status = "played"
            self.buttons[0].set_icon("pause")  # Cambiar a ícono de pausa
            self.buttons[1].set_icon("stop")  # Volver a icono de stop
            self.buttons[1].disable()  # Desactivar botón de borrar
            # Habilitar botón de grabar cuando se reanuda
            self.buttons[2].enable()
            self.buttons[3].disable()  # Deshabilitar Zoom In
            self.buttons[4].disable()  # Deshabilitar Zoom Out
            self.game.current_screen.graph_app.played = True

    def toggle_stop_to_trash(self):
        """Cambia el botón de stop a trash si hay datos disponibles"""
        if self.status == "paused" and not self.record_status:
            self.buttons[1].set_icon("trash")  # Cambia a ícono de trash
            self.buttons[1].enable()  # Habilitar botón de trash
            self.data_available = True  # Marcar que hay datos disponibles

    def stop_recording(self):
        """Detiene la grabación y muestra de datos"""
        self.record_status = False
        self.buttons[0].enable()  # Habilitar Play/Pause
        self.buttons[1].set_icon("trash")  # Cambiar a icono de borrar
        self.buttons[1].enable()  # Habilitar botón de borrar
        # Cambiar a icono de grabación inactiva
        self.buttons[2].set_icon("dot-circle-o")
        self.record_tick = 0  # Reiniciar el contador de grabación
        self.data_available = True  # Indicar que hay datos disponibles
        self.status = "paused"

    def clear_data(self):
        """Borra los datos de la muestra"""
        self.game.current_screen.graph_app.clear_data()
        # Deshabilitar botón de borrar después de limpiar
        self.buttons[1].disable()
        self.buttons[2].disable()  # Deshabilitar botón de grabar
        self.buttons[3].disable()  # Deshabilitar Zoom In
        self.buttons[4].disable()  # Deshabilitar Zoom Out
        self.data_available = False  # Indicar que no hay datos
        self.status = "stopped"
        self.buttons[0].set_icon("play")  # Restablecer icono a play
        self.buttons[0].enable()  # Habilitar Play/Pause
        
    def measure(self):
        self.game.measure_activate(True)
        
    def marks(self):
        self.game.marks_activate(True)