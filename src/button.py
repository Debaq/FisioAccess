import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, disabled_color=(100, 100, 100), selected_color=(255, 255, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.disabled_color = disabled_color
        self.selected_color = selected_color
        self.enabled = True
        self.visible = True
        self.selected = False

    def draw(self, screen, font):
        if self.visible:
            if self.selected:
                color = self.selected_color
            elif not self.enabled:
                color = self.disabled_color
            else:
                color = self.color
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(-4, -4))
            text_surf = font.render(self.text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and self.enabled and self.visible

    def set_text(self, text):
        self.text = text

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False