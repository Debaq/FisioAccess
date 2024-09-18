from collections import deque
import pygame
from config.settings import MAX_POINTS, VISIBLE_POINTS, WIDTH, HEIGHT, GREEN, RED

class GraphApp:
    def __init__(self):
        self.data = deque(maxlen=MAX_POINTS)
        self.view_start = 0
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selected_data = []
        self.markers = {}
        self.scale_factor = 1  # Nuevo: factor de escala para ajustar el gráfico


    def add_data_point(self, value):
        self.data.append(value)
        self.view_start = max(0, len(self.data) - VISIBLE_POINTS)
        self.adjust_scale()  # Ajuste automático de la escala cuando se agregan nuevos datos

    def adjust_scale(self):
        """Ajustar la escala del gráfico basado en el valor máximo y mínimo visible."""
        if self.data:
            visible_data = list(self.data)[self.view_start:self.view_start + VISIBLE_POINTS]
            min_value = min(visible_data)
            max_value = max(visible_data)
            data_range = max_value - min_value

            # Ajustar la escala para que se ajuste a la pantalla
            if data_range > 0:
                self.scale_factor = HEIGHT / data_range
            else:
                self.scale_factor = 1  # Evitar división por cero si todos los valores son iguales

    def draw_graph(self, screen):
        """Dibujar el gráfico escalado para que se ajuste a la pantalla."""
        visible_data = list(self.data)[self.view_start:self.view_start + VISIBLE_POINTS]
        if visible_data:
            min_value = min(visible_data)
            
            for i in range(1, len(visible_data)):
                x1 = int((i-1) * WIDTH / VISIBLE_POINTS)
                y1 = HEIGHT - int((visible_data[i-1] - min_value) * self.scale_factor)
                x2 = int(i * WIDTH / VISIBLE_POINTS)
                y2 = HEIGHT - int((visible_data[i] - min_value) * self.scale_factor)
                pygame.draw.line(screen, GREEN, (x1, y1), (x2, y2))

        if self.selecting:
            self.draw_selection(screen)

    def draw_selection(self, screen):
        if self.selection_start is not None:
            pygame.draw.line(screen, RED, (self.selection_start, 0), (self.selection_start, HEIGHT), 2)
        if self.selection_end is not None:
            pygame.draw.line(screen, RED, (self.selection_end, 0), (self.selection_end, HEIGHT), 2)

    def draw_selection_view(self, screen):
        for i in range(1, len(self.selected_data)):
            x1 = int((i-1) * WIDTH / len(self.selected_data))
            y1 = self.selected_data[i-1]
            x2 = int(i * WIDTH / len(self.selected_data))
            y2 = self.selected_data[i]
            pygame.draw.line(screen, GREEN, (x1, y1), (x2, y2))

        for letter, (x, y) in self.markers.items():
            pygame.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 5)

    def set_selection(self, start, end):
        self.selection_start = start
        self.selection_end = end

    def get_selected_data(self):
        if self.selection_start is None or self.selection_end is None:
            return []
        start_index = int(self.selection_start * VISIBLE_POINTS / WIDTH)
        end_index = int(self.selection_end * VISIBLE_POINTS / WIDTH)
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        return list(self.data)[self.view_start:][start_index:end_index]

    def set_marker(self, letter, x, y):
        self.markers[letter] = (x, y)

    def clear_data(self):
        self.data.clear()
        self.view_start = 0
        self.selection_start = None
        self.selection_end = None
        self.selected_data = []
        self.markers = {}

    def move_view(self, direction):
        if direction == 'left':
            self.view_start = max(0, self.view_start - VISIBLE_POINTS // 2)
        elif direction == 'right':
            self.view_start = min(len(self.data) - VISIBLE_POINTS, self.view_start + VISIBLE_POINTS // 2)

    def find_nearest_point(self, x):
        index = int(x * len(self.selected_data) / WIDTH)
        index = max(0, min(index, len(self.selected_data) - 1))
        return x, self.selected_data[index]

    def zoom_in(self):
        """Función para hacer zoom al gráfico."""
        self.scale_factor *= 1.2  # Incrementar el factor de escala

    def zoom_out(self):
        """Función para alejar el gráfico."""
        self.scale_factor /= 1.2  # Reducir el factor de escala
