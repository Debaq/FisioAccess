from collections import deque
import pygame
from config.settings import MAX_POINTS, VISIBLE_POINTS, WIDTH, HEIGHT, GREEN
from theming import Theming


class GraphApp:
    def __init__(self):
        """
        Inicializa la aplicación de gráfico.
        """
        self.data = deque(maxlen=MAX_POINTS *
                          2)  # Permitir hasta el doble de MAX_POINTS
        self.view_start = 0
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selected_data = []
        self.markers = {}
        self.scale_factor = 1  # Factor de escala para ajustar el gráfico
        self.grid_ms_per_div = 100  # 1 ms por división en el eje X
        self.grid_uv_per_div = 0.001  # 1 uV por división en el eje Y
        self.played = False
        self.record = False
        self.state_record = "stopped"  # stopped, init, record, end
        # Nueva variable para controlar el límite actual
        self.current_max_points = MAX_POINTS

        # Nuevas variables para los márgenes
        self.margin_left = 30
        self.margin_right = 60
        self.margin_top = 50
        self.margin_bottom = 70

        # Calcular el ancho y alto efectivos del área de dibujo
        self.graph_width = WIDTH - self.margin_left - self.margin_right
        self.graph_height = HEIGHT - self.margin_top - self.margin_bottom

    def add_data_point(self, value):
        """
        Añade un punto de datos al gráfico si se está grabando.
        """
        if self.played and not self.record:
            self.data.append(value)
            if len(self.data) >= VISIBLE_POINTS:
                self.data.popleft()
            self.view_start = max(0, len(self.data) - VISIBLE_POINTS)
            self.adjust_scale()

        if self.record and self.played:
            self.data.append(value)
            if len(self.data) >= self.current_max_points:
                if self.current_max_points < MAX_POINTS * 2:
                    self.current_max_points = min(
                        self.current_max_points * 2, MAX_POINTS * 2)
                    self.data = deque(
                        self.data, maxlen=self.current_max_points)
                else:
                    # Si hemos alcanzado el límite máximo, detener la grabación
                    self.record = False
                    self.played = False

            self.view_start = max(0, len(self.data) - VISIBLE_POINTS)
            self.adjust_scale()

    def start_recording(self):
        """
        Inicia la grabación de datos.
        """
        self.record = True
        self.played = True
        if len(self.data) >= self.current_max_points:
            self.current_max_points = min(
                self.current_max_points * 2, MAX_POINTS * 2)
            self.data = deque(self.data, maxlen=self.current_max_points)

    def stop_recording(self):
        """
        Detiene la grabación de datos.
        """
        self.record = False

    def adjust_scale(self):
        """
        Ajusta la escala del gráfico basado
        en el valor máximo y mínimo visible.
        """
        if self.data:
            visible_data = list(self.data)[
                self.view_start:self.view_start + VISIBLE_POINTS]
            min_value = min(visible_data)
            max_value = max(visible_data)
            data_range = max_value - min_value

            # Ajustar la escala para que se ajuste a la pantalla
            if data_range > 0:
                # Calcular el factor de escala para ajustar el gráfico
                self.scale_factor = self.graph_height / data_range
            else:
                self.scale_factor = 1 

    def draw_grid(self, screen):
        """Dibujar la cuadrícula del gráfico."""
        grid_color = Theming().get('grid_color')

        # Divisiones para el eje X (1 ms por división)
        step = int(self.graph_width / (VISIBLE_POINTS / self.grid_ms_per_div))
        for x in range(self.margin_left, WIDTH - self.margin_right, step):
            pygame.draw.line(screen, grid_color, (x, self.margin_top),
                             (x, HEIGHT - self.margin_bottom), 1)

        # Divisiones para el eje Y (1 uV por división)
        data_range = max(self.data) - min(self.data) if self.data else 0
        if data_range > 0:
            y_div_height = (self.graph_height / data_range 
                            * self.grid_uv_per_div)
            # Asegurarse de que no sea 0
            y_step = max(1, int(y_div_height * self.scale_factor))
            for y in range(self.margin_top,
                           HEIGHT - self.margin_bottom,
                           y_step):
                pygame.draw.line(
                    screen, grid_color, (self.margin_left, y), 
                    (WIDTH - self.margin_right, y), 1)

    def cut_data(self, data):
        try:
            return float(data) #aca el mal/vien funcionamiento
        except Exception:
            print(f"este es un error, pon atención {data}")
            return None
        try:
            data = data.rstrip(';')
            valores = data.split(';')
            values = valores[3]
            val_0 = int(values.split(',')[0])
        except Exception:
            val_0 = 0
        return val_0

    def draw_graph(self, screen, **kwargs):
        """Dibujar el gráfico escalado para que se ajuste a la pantalla."""
        value = kwargs["data"]
        value = self.cut_data(value)
        
        if self.played and value is not None:
            self.add_data_point(value)

        # Dibuja primero la cuadrícula
        self.draw_grid(screen)

        # Luego, dibuja el gráfico de datos
        visible_data = list(self.data)[
            self.view_start:self.view_start + VISIBLE_POINTS]
        if visible_data:
            min_value = min(visible_data)

            for i in range(1, len(visible_data)):
                x1 = self.margin_left + \
                    int((i-1) * self.graph_width / VISIBLE_POINTS)
                y1 = HEIGHT - self.margin_bottom - \
                    int((visible_data[i-1] - min_value) * self.scale_factor)
                x2 = self.margin_left + \
                    int(i * self.graph_width / VISIBLE_POINTS)
                y2 = HEIGHT - self.margin_bottom - \
                    int((visible_data[i] - min_value) * self.scale_factor)
                line_color_1 = Theming().get('line_graph')
                line_color_1 = pygame.Color(line_color_1['line_1'])
                pygame.draw.line(screen, line_color_1, (x1, y1), (x2, y2))

        if self.selecting:
            self.draw_selection(screen)

    def draw_selection(self, screen):
        pygame.draw.line(screen, self.selection_color, (self.selection_start,
                         self.margin_top), (self.selection_start, HEIGHT - self.margin_bottom), 2)
        pygame.draw.line(screen, RED, (self.selection_start, self.margin_top),
                         (self.selection_start, HEIGHT - self.margin_bottom), 2)
        pygame.draw.line(screen, self.selection_color, (self.selection_end,
                         self.margin_top), (self.selection_end, HEIGHT - self.margin_bottom), 2)
        pygame.draw.line(screen, RED, (self.selection_end, self.margin_top),
                         (self.selection_end, HEIGHT - self.margin_bottom), 2)

    def draw_selection_view(self, screen):
        for i in range(1, len(self.selected_data)):
            x1 = self.margin_left + \
                int((i-1) * self.graph_width / len(self.selected_data))
            y1 = self.margin_top + self.selected_data[i-1]
            x2 = self.margin_left + \
                int(i * self.graph_width / len(self.selected_data))
            y2 = self.margin_top + self.selected_data[i]
            pygame.draw.line(screen, GREEN, (x1, y1), (x2, y2))

        for letter, (x, y) in self.markers.items():
            pygame.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 5)

    def set_selection(self, start, end):
        self.selection_start = max(self.margin_left, min(
            start, WIDTH - self.margin_right))
        self.selection_end = max(self.margin_left, min(
            end, WIDTH - self.margin_right))

    def get_selected_data(self):
        if self.selection_start is None or self.selection_end is None:
            return []
        start_index = int((self.selection_start - self.margin_left)
                          * VISIBLE_POINTS / self.graph_width)
        end_index = int((self.selection_end - self.margin_left)
                        * VISIBLE_POINTS / self.graph_width)
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        return list(self.data)[self.view_start:][start_index:end_index]

    def set_marker(self, letter, x, y):
        x = max(self.margin_left, min(x, WIDTH - self.margin_right))
        y = max(self.margin_top, min(y, HEIGHT - self.margin_bottom))
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
            self.view_start = min(
                len(self.data) - VISIBLE_POINTS, self.view_start + VISIBLE_POINTS // 2)

    def find_nearest_point(self, x):
        x = max(self.margin_left, min(x, WIDTH - self.margin_right))
        index = int((x - self.margin_left) *
                    len(self.selected_data) / self.graph_width)
        index = max(0, min(index, len(self.selected_data) - 1))
        return x, self.selected_data[index]

    def play(self, true=True):
        if true:
            self.played = True
        else:
            self.played = False

    def zoom_in(self):
        """Función para hacer zoom al gráfico."""
        self.scale_factor *= 1.2  # Incrementar el factor de escala

    def zoom_out(self):
        """Función para alejar el gráfico."""
        self.scale_factor /= 1.2  # Reducir el factor de escala
