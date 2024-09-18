import pygame

class Button:
    def __init__(self, x, y, width, height, text, color=None, size_icon=16,disabled_color=(100, 100, 100), selected_color=(255, 255, 0), icon=None, on_click=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color  # Color inicial del botón
        self.disabled_color = disabled_color  # Color cuando está deshabilitado
        self.selected_color = selected_color  # Color cuando está seleccionado
        self.icon = None  # Icono como imagen opcional
        if icon:
            icon_path=f'assets/icons/white/png/{size_icon}/{icon}.png'
            self.icon = pygame.image.load(icon_path)  # Cargar el icono si existe una ruta
            self.icon = pygame.transform.scale(self.icon, (width - 10, height - 10))  # Escalar el icono al tamaño del botón
        
        self.enabled = True
        self.visible = True
        self.selected = False
        self.on_click = on_click  # Función a ejecutar al hacer clic

    def draw(self, screen, font):
        if self.visible:
            # Dibuja el fondo del botón
            if self.selected:
                color = self.selected_color
            elif not self.enabled:
                color = self.disabled_color
            else:
                color = self.color  # Usar el color actual del botón
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(-4, -4))  # Borde negro

            # Dibuja el texto o el icono
            if self.icon:
                # Si hay un icono, lo dibuja en el centro del botón
                icon_rect = self.icon.get_rect(center=self.rect.center)
                screen.blit(self.icon, icon_rect)
            else:
                # Si no hay icono, dibuja el texto
                text_surf = font.render(self.text, True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=self.rect.center)
                screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        """Verifica si el botón fue clicado."""
        return self.rect.collidepoint(pos) and self.enabled and self.visible

    def click(self):
        """Llama a la función on_click si está definida y el botón es clicado."""
        if self.on_click:
            self.on_click()

    def set_text(self, text):
        """Actualiza el texto del botón."""
        self.text = text

    def set_color(self, color):
        """Permite cambiar el color del botón dinámicamente."""
        self.color = color

    def set_selected_color(self, selected_color):
        """Permite cambiar el color de selección del botón."""
        self.selected_color = selected_color

    def set_disabled_color(self, disabled_color):
        """Permite cambiar el color del botón cuando está deshabilitado."""
        self.disabled_color = disabled_color

    def enable(self):
        """Habilita el botón."""
        self.enabled = True

    def disable(self):
        """Deshabilita el botón."""
        self.enabled = False

    def show(self):
        """Muestra el botón."""
        self.visible = True

    def hide(self):
        """Oculta el botón."""
        self.visible = False

    def select(self):
        """Selecciona el botón (cambio de color)."""
        self.selected = True

    def deselect(self):
        """Deselecciona el botón (restablece el color)."""
        self.selected = False
