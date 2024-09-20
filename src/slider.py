import pygame
import sys
from config.settings import *
from widgets_helpers import icon as help_icon
from theming import Theming


class Slider:
    """
    Slider class to create and manage a slider widget with two handles.
    Attributes:
        direction (str): Direction of the slider, either "horizontal" or "vertical".
        handles_visible (tuple): Tuple indicating the visibility of the two handles.
        handle_icon (Any): Icon for the handles.
        callback_function (Callable): Function to call when the slider positions are updated.
        line_pos (tuple): Initial position of the slider line.
        line_length (int): Length of the slider line.
        line_width (int): Width of the slider line.
        selected_slider (pygame.Rect): The currently selected slider handle for dragging.
    Methods:
        __init__(x, y, w, length, direction="horizontal", handles_visible=(True, True), handle_icon=None, callback_function=None):
            Initializes the Slider object with the given parameters.
        create_sliders():
            Creates the slider handles based on the configuration.
        draw(surface):
            Draws the slider line and handles on the given surface.
        handle_events(event):
            Handles mouse events to manage slider interaction.
        update_slider_position(mouse_pos):
            Updates the position of the selected slider handle based on mouse movement.
        get_positions():
            Returns the current positions of the slider handles.
    
    """
    def __init__(self, x, y, w, length, direction="horizontal",
                 handles_visible=(True, True), handle_icon=None,
                 callback_function=None):
        """
        Args:
            x (int): The x-coordinate of the slider's initial position.
            y (int): The y-coordinate of the slider's initial position.
            w (int): The width of the slider.
            length (int): The length of the slider.
            direction (str, optional): The direction of the slider, either
            "horizontal" or "vertical". Defaults to "horizontal".
            handles_visible (tuple, optional): A tuple indicating the
            visibility of the handles. Defaults to (True, True).
            handle_icon (object, optional): An icon for the handle.
            Defaults to None.
            callback_function (callable, optional): A function to be called
            when the slider value changes. Defaults to None.
        """
        self.direction = direction
        self.handles_visible = handles_visible
        self.handle_icon = handle_icon
        self.callback_function = callback_function

        # Icono del deslizador si se proporciona
        self.icon = None
        if handle_icon:
            self.icon = help_icon(handle_icon, SLIDER_WIDTH, SLIDER_HEIGHT, 128, 'dark')

        # Configurar la posición inicial de la línea
        if self.direction == "horizontal":
            self.line_pos = (x, y)  # Posición inicial de la línea horizontal (x, y)
        else:
            self.line_pos = (x, y)  # Posición inicial de la línea vertical (x, y)
        
        self.line_length = length
        self.line_width = w

        # Crear sliders
        self.create_sliders()
        
        # Deslizador seleccionado para arrastrar
        self.selected_slider = None
        self.visible = True
    
    def create_sliders(self):
        """Crear los deslizadores en función de la configuración"""
        if self.direction == "horizontal":
            self.slider1 = pygame.Rect(
                self.line_pos[0] + SLIDER_PADDING,
                self.line_pos[1] - SLIDER_HEIGHT // 2,
                SLIDER_WIDTH,
                SLIDER_HEIGHT
            )
            self.slider2 = pygame.Rect(
                self.line_pos[0] + self.line_length - SLIDER_WIDTH - SLIDER_PADDING,
                self.line_pos[1] - SLIDER_HEIGHT // 2,
                SLIDER_WIDTH,
                SLIDER_HEIGHT
            )
        else:
            self.slider1 = pygame.Rect(
                self.line_pos[0] - SLIDER_WIDTH // 2,
                self.line_pos[1] + SLIDER_PADDING,
                SLIDER_WIDTH,
                SLIDER_HEIGHT
            )
            self.slider2 = pygame.Rect(
                self.line_pos[0] - SLIDER_WIDTH // 2,
                self.line_pos[1] + self.line_length - SLIDER_HEIGHT - SLIDER_PADDING,
                SLIDER_WIDTH,
                SLIDER_HEIGHT
            )

    def draw(self, surface):
        """Dibujar la línea y los deslizadores"""
        if self.visible:
            # Dibujar la línea
            if self.direction == "horizontal":
                if self.line_width > 0:
                    pygame.draw.line(surface, GRAY, self.line_pos,
                                     (self.line_pos[0] + self.line_length,
                                      self.line_pos[1]),
                                     self.line_width)
                pygame.draw.line(surface, GRAY, (self.slider1.x + 15 , self.slider1.y + 30),(self.slider1.x + 15 , self.slider1.y + 470), 1)
                if self.handles_visible[1]:
                    pygame.draw.line(surface, GRAY, (self.slider2.x + 15 , self.slider2.y + 30),(self.slider2.x + 15 , self.slider2.y + 470), 1)

            else:
                if self.line_width > 0:
                    pygame.draw.line(surface, GRAY, self.line_pos,
                                     (self.line_pos[0],
                                      self.line_pos[1] + self.line_length),
                                     self.line_width)
                pygame.draw.line(surface, GRAY, (self.slider1.x, self.slider1.y + 15),(self.slider1.x - 1000, self.slider1.y+15), 1)
                if self.handles_visible[1]:
                    pygame.draw.line(surface, GRAY, (self.slider2.x, self.slider2.y + 15),(self.slider2.x - 1000, self.slider2.y+15), 1)


            # Dibujar sliders si están visibles
            if self.handles_visible[0]:
                self.draw_slider(surface, self.slider1)
            if self.handles_visible[1]:
                self.draw_slider(surface, self.slider2)

    def draw_slider(self, surface, slider_rect):
        """Dibujar un deslizador con o sin ícono"""
        if self.icon:
            # Dibujar el ícono en el centro del deslizador
            icon_rect = self.icon.get_rect(center=slider_rect.center)
            surface.blit(self.icon, icon_rect)
        else:
            # Dibujar rectángulo estándar si no hay ícono
            pygame.draw.rect(surface, RED, slider_rect)

    def handle_events(self, event):
        """Manejar eventos del ratón"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.slider1.collidepoint(event.pos):
                self.selected_slider = self.slider1
            elif self.slider2.collidepoint(event.pos):
                self.selected_slider = self.slider2

        elif event.type == pygame.MOUSEBUTTONUP:
            self.selected_slider = None

        elif event.type == pygame.MOUSEMOTION:
            if self.selected_slider:
                self.update_slider_position(event.pos)

    def update_slider_position(self, mouse_pos):
        """Actualizar la posición del deslizador seleccionado"""
        if self.direction == "horizontal":
            min_pos = self.line_pos[0] + SLIDER_PADDING
            max_pos = self.line_pos[0] + self.line_length - SLIDER_WIDTH - SLIDER_PADDING
            new_pos = max(min(mouse_pos[0], max_pos), min_pos)

            # Asegurarse de que no se crucen los sliders
            if self.selected_slider == self.slider1:
                if new_pos + SLIDER_WIDTH >= self.slider2.x:
                    self.slider2.x = new_pos + SLIDER_WIDTH
                else:
                    self.slider1.x = new_pos
            elif self.selected_slider == self.slider2:
                if new_pos <= self.slider1.x + SLIDER_WIDTH:
                    self.slider1.x = new_pos - SLIDER_WIDTH
                else:
                    self.slider2.x = new_pos

        elif self.direction == "vertical":
            min_pos = self.line_pos[1] + SLIDER_PADDING
            max_pos = self.line_pos[1] + self.line_length - SLIDER_HEIGHT - SLIDER_PADDING
            new_pos = max(min(mouse_pos[1], max_pos), min_pos)

            # Asegurarse de que no se crucen los sliders
            if self.selected_slider == self.slider1:
                if new_pos + SLIDER_HEIGHT >= self.slider2.y:
                    self.slider2.y = new_pos + SLIDER_HEIGHT
                else:
                    self.slider1.y = new_pos
            elif self.selected_slider == self.slider2:
                if new_pos <= self.slider1.y + SLIDER_HEIGHT:
                    self.slider1.y = new_pos - SLIDER_HEIGHT
                else:
                    self.slider2.y = new_pos

        # Llamar al callback con la posición actual
        if self.callback_function:
            self.callback_function(self.get_positions())

    def get_positions(self):
        """Obtener las posiciones actuales de los deslizadores"""
        if self.direction == "horizontal":
            return (self.direction, self.slider1.x, self.slider2.x)
        else:
            return (self.direction, self.slider1.y, self.slider2.y)
    
    def hide(self, hide=True):
        """Ocultar o mostrar el deslizador"""
        self.visible = not hide
        
    def slider_visibility(self, visibility):
        """
        Args:
            visibility (tuple): (True, True)
        """
        self.handles_visible = visibility
    
    def slider_is_visibility(self):
        return self.handles_visible




if __name__ == "__main__":
    
    def slider_callback(positions):
        """Función de callback que se llama al mover los sliders"""
        print("Posiciones de los sliders:", positions)

    # Inicializar Pygame
    pygame.init()

    # Configuración de la pantalla
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Deslizadores con Orientación")

    
    
    # Crear instancia de Slider
    slider = Slider(200,0, 3, 200, direction="vertical", handles_visible=(True, False), 
                    callback_function=slider_callback)

    # Bucle principal del programa
    running = True
    while running:
        screen.fill(WHITE)

        # Dibujar el slider
        slider.draw(screen)

        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            slider.handle_events(event)

        # Actualizar pantalla
        pygame.display.flip()

    # Salir del programa
    pygame.quit()
    sys.exit()
