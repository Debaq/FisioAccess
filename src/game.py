import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_app import GraphApp
from src.button import Button
from src.serial_handler import SerialHandler
from src.utils import get_ip_address
from config.settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 50))
        pygame.display.set_caption("Fisioaccess")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.title_font = pygame.font.Font(FONT_PATH, 48)
        
        self.graph_app = GraphApp()
        self.running = True
        self.graphing = False
        self.paused = False
        self.use_demo_data = False
        self.working_on_selection = False
        self.current_marker = None

        self.initialize_buttons()
        self.serial_handler = SerialHandler(SERIAL_PORT, BAUD_RATE)

        self.ip_address = get_ip_address()

        self.try_serial_connection()

    def initialize_buttons(self):
        self.start_button = Button(10, HEIGHT + 10, 100, 30, "Iniciar", GREEN)
        self.stop_button = Button(120, HEIGHT + 10, 100, 30, "Detener", RED)
        self.stop_button.disable()
        self.work_selection_button = Button(230, HEIGHT + 10, 180, 30, "Trabajar en selección", BLUE)
        self.work_selection_button.disable()
        self.left_arrow = Button(10, HEIGHT // 2, 30, 60, "<", (150, 150, 150))
        self.right_arrow = Button(WIDTH - 40, HEIGHT // 2, 30, 60, ">", (150, 150, 150))
        self.left_arrow.hide()
        self.right_arrow.hide()
        self.back_button = Button(WIDTH - 110, HEIGHT + 10, 100, 30, "Volver", (150, 150, 150))
        self.back_button.hide()
        self.marker_buttons = [
            Button(10 + i*40, HEIGHT + 10, 30, 30, letter, YELLOW)
            for i, letter in enumerate(['P', 'Q', 'R', 'S', 'T'])
        ]

    def try_serial_connection(self):
        if not self.serial_handler.connect():
            self.show_error_message()

    def show_error_message(self):
        self.error_message = "Puerto serial no encontrado. ¿Usar datos de demostración?"
        self.yes_button = Button(WIDTH // 2 - 110, HEIGHT // 2 + 20, 100, 30, "Sí", GREEN)
        self.no_button = Button(WIDTH // 2 + 10, HEIGHT // 2 + 20, 100, 30, "No", RED)

    def update(self):
        if self.graphing and not self.paused:
            new_value = self.serial_handler.get_data(self.use_demo_data)
            self.graph_app.add_data_point(new_value)

    def draw(self):
        self.screen.fill(BLACK)
        
        if not self.graph_app.data and not hasattr(self, 'error_message'):
            self.draw_title_screen()
        elif hasattr(self, 'error_message'):
            self.draw_error_screen()
        elif self.working_on_selection:
            self.graph_app.draw_selection_view(self.screen)
            self.draw_markers()
        else:
            self.graph_app.draw_graph(self.screen)
        
        self.draw_buttons()
        pygame.display.flip()

    def draw_title_screen(self):
        title_surf = self.title_font.render("Fisioaccess", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(title_surf, title_rect)
        
        ip_surf = self.font.render(f"IP: {self.ip_address}", True, WHITE)
        ip_rect = ip_surf.get_rect(topright=(WIDTH - 10, 10))
        self.screen.blit(ip_surf, ip_rect)

    def draw_error_screen(self):
        text_surf = self.font.render(self.error_message, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(text_surf, text_rect)
        self.yes_button.draw(self.screen, self.font)
        self.no_button.draw(self.screen, self.font)

    def draw_buttons(self):
        if not self.working_on_selection:
            self.start_button.draw(self.screen, self.font)
            self.stop_button.draw(self.screen, self.font)
            
            if self.paused or not self.graphing:
                self.left_arrow.draw(self.screen, self.font)
                self.right_arrow.draw(self.screen, self.font)
            
            if self.graph_app.selecting and self.graph_app.selection_start is not None and self.graph_app.selection_end is not None:
                self.work_selection_button.draw(self.screen, self.font)
        else:
            self.back_button.draw(self.screen, self.font)
            for button in self.marker_buttons:
                button.draw(self.screen, self.font)

    def draw_markers(self):
        for letter, (x, y) in self.graph_app.markers.items():
            text_surf = self.font.render(letter, True, YELLOW)
            self.screen.blit(text_surf, (int(x) + 10, int(y) - 10))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_key_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down_event(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.graph_app.dragging = None
            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion_event(event)

    def handle_key_event(self, event):
        if event.key == pygame.K_q:
            self.running = False
        elif event.key == pygame.K_ESCAPE and self.working_on_selection:
            self.exit_selection_mode()

    def handle_mouse_down_event(self, event):
        pos = event.pos
        if hasattr(self, 'error_message'):
            self.handle_error_buttons(pos)
        elif self.working_on_selection:
            self.handle_selection_buttons(pos)
        else:
            self.handle_main_buttons(pos)

    def handle_error_buttons(self, pos):
        if self.yes_button.is_clicked(pos):
            self.use_demo_data = True
            delattr(self, 'error_message')
        elif self.no_button.is_clicked(pos):
            self.running = False

    def handle_selection_buttons(self, pos):
        for button in self.marker_buttons:
            if button.is_clicked(pos):
                self.current_marker = button.text
                for b in self.marker_buttons:
                    b.deselect()
                button.select()
        if pos[1] < HEIGHT and self.current_marker:
            x, y = self.graph_app.find_nearest_point(pos[0])
            self.graph_app.set_marker(self.current_marker, x, y)
            self.current_marker = None
            for button in self.marker_buttons:
                button.deselect()

    def handle_main_buttons(self, pos):
        if self.start_button.is_clicked(pos):
            self.toggle_graph()
        elif self.stop_button.is_clicked(pos):
            self.stop_graph()
        elif self.graph_app.selecting and self.graph_app.selection_start is not None and self.graph_app.selection_end is not None:
            if self.work_selection_button.is_clicked(pos):
                self.enter_selection_mode()
        elif self.graph_app.selecting:
            self.handle_selection(pos)
        elif self.left_arrow.is_clicked(pos):
            self.graph_app.move_view('left')
        elif self.right_arrow.is_clicked(pos):
            self.graph_app.move_view('right')

    def toggle_graph(self):
        if not self.graphing:
            self.start_graphing()
        elif self.paused:
            self.resume_graphing()
        else:
            self.pause_graphing()

    def start_graphing(self):
        self.graphing = True
        self.paused = False
        self.start_button.set_text("Pausar")
        self.stop_button.enable()
        self.left_arrow.hide()
        self.right_arrow.hide()

    def resume_graphing(self):
        self.paused = False
        self.start_button.set_text("Pausar")
        self.left_arrow.hide()
        self.right_arrow.hide()

    def pause_graphing(self):
        self.paused = True
        self.start_button.set_text("Iniciar")
        self.left_arrow.show()
        self.right_arrow.show()

    def stop_graph(self):
        if self.graphing:
            self.graphing = False
            self.graph_app.selecting = True
            self.start_button.disable()
            self.stop_button.set_text("Borrar")
            self.left_arrow.show()
            self.right_arrow.show()
        else:
            self.graph_app.clear_data()
            self.graph_app.selecting = False
            self.start_button.enable()
            self.start_button.set_text("Iniciar")
            self.stop_button.disable()
            self.stop_button.set_text("Detener")
            self.left_arrow.hide()
            self.right_arrow.hide()

    def handle_selection(self, pos):
        if self.graph_app.selection_start is None:
            self.graph_app.selection_start = pos[0]
        elif self.graph_app.selection_end is None or abs(pos[0] - self.graph_app.selection_start) < abs(pos[0] - self.graph_app.selection_end):
            self.graph_app.selection_end = self.graph_app.selection_start
            self.graph_app.selection_start = pos[0]
            self.graph_app.dragging = 'start'
        else:
            self.graph_app.selection_end = pos[0]
            self.graph_app.dragging = 'end'

    def handle_mouse_motion_event(self, event):
        if self.graph_app.selecting and self.graph_app.dragging:
            if self.graph_app.dragging == 'start':
                self.graph_app.selection_start = max(0, min(event.pos[0], self.graph_app.selection_end - 1))
            else:
                self.graph_app.selection_end = min(WIDTH, max(event.pos[0], self.graph_app.selection_start + 1))

    def enter_selection_mode(self):
        self.graph_app.selected_data = self.graph_app.get_selected_data()
        self.working_on_selection = True
        self.graph_app.markers = {}
        self.start_button.hide()
        self.stop_button.hide()
        self.left_arrow.hide()
        self.right_arrow.hide()
        self.back_button.show()

    def exit_selection_mode(self):
        self.working_on_selection = False
        self.current_marker = None
        for button in self.marker_buttons:
            button.deselect()
        self.start_button.show()
        self.stop_button.show()
        self.left_arrow.show()
        self.right_arrow.show()
        self.back_button.hide()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        self.serial_handler.close()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()