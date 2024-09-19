import pygame
import math
from theming import Theming

class DialScreen:
    def __init__(self, game, min_value=-5, max_value=5):
        self.game = game
        self.min_value = min_value
        self.max_value = max_value
        self.center_value = 0 if min_value < 0 else min_value
        self.radius = 150  # Radio del dial
        self.center_x = self.game.WIDTH // 2
        self.center_y = self.game.HEIGHT // 2 + 50  # Ajustar centro para que se vea bien el dial

        self.font = pygame.font.Font(None, 36)
        self.calculate_positions()
        

    def calculate_positions(self):
        """Calcula las posiciones de los valores en el dial."""
        self.positions = []
        # Definimos los ángulos correspondientes a las horas 8:00, 9:00, 10:00, 11:00, 12:00, 1:00, 2:00, 3:00 y 4:00
        self.hour_angles = [
            -30,  # 8:00
            0,  # 9:00
            30,  # 10:00
            60,  # 11:00
            90,    # 12:00
            120,   # 1:00
            150,   # 2:00
            180,   # 3:00
            210   # 4:00
            
        ]
        self.hour_angles.reverse()
        # Calcular el total de valores y la distribución
        total_values = self.max_value - self.min_value
        for i, angle in enumerate(self.hour_angles):
            radian_angle = math.radians(angle)
            value = self.min_value + i * (total_values / (len(self.hour_angles) - 1))
            x = self.center_x + self.radius * math.cos(radian_angle)
            y = self.center_y - self.radius * math.sin(radian_angle)
            self.positions.append((value, (x, y)))
            

    def draw_dial(self):
        """Dibuja el dial con las marcas de valores."""
        background = Theming().get('background')
        self.game.screen.fill(background)
        
        # Dibuja el arco del dial
        dial_color = Theming().get('foreground')
        pygame.draw.arc(self.game.screen, dial_color, 
                        (self.center_x - self.radius, self.center_y - self.radius, 
                         self.radius * 2, self.radius * 2), 
                        math.radians(-30), math.radians(210), 2)  # Arco de 240° a -60°

        # Dibuja las posiciones de los valores
        for value, pos in self.positions:
            value_text = self.font.render(f"{value:.1f}", True, (255, 255, 255))
            text_rect = value_text.get_rect(center=pos)
            self.game.screen.blit(value_text, text_rect)
      

    def draw_pointer(self, current_value):
        """Dibuja un puntero en el valor actual (opcional)."""
        if self.min_value <= current_value <= self.max_value:
            total_values = self.max_value - self.min_value
            # Calcular el ángulo correspondiente al valor actual
            index = (current_value - self.min_value) / total_values * (len(self.positions) - 1)
            index = int(round(index))
            angle = math.radians(self.hour_angles[index])
            x = self.center_x + (self.radius - 10) * math.cos(angle)
            y = self.center_y - (self.radius - 10) * math.sin(angle)
            pygame.draw.line(self.game.screen, (255, 0, 0), (self.center_x, self.center_y), (x, y), 4)

    def draw(self, **kwargs):
        data = kwargs["data"]  # Accede a los argumentos nombrados
        if data < self.min_value:
            self.min_value = data
          
            
        if data > self.max_value:
            self.max_value = data
        self.draw_dial()
        self.draw_pointer(data)  # Aquí se puede cambiar el valor actual del puntero

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.current_screen = self.game.screens['home']
