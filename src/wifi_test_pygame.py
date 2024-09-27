import pygame
import subprocess

def get_wifi_networks():
    try:
        result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"], capture_output=True, text=True)
        networks = []
        for line in result.stdout.strip().split('\n'):
            ssid, signal, security = line.split(':')
            networks.append({
                'ssid': ssid,
                'signal': int(signal),
                'security': security
            })
        return sorted(networks, key=lambda x: x['signal'], reverse=True)
    except Exception as e:
        return f"Error al obtener las redes WiFi: {str(e)}"

def get_current_wifi():
    try:
        result = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "device", "wifi"], capture_output=True, text=True)
        for line in result.stdout.strip().split('\n'):
            active, ssid = line.split(':')
            if active == 'yes':
                return ssid
        return None
    except Exception:
        return None

def connect_to_wifi(ssid, password):
    try:
        subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", password], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Selector de WiFi")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

font = pygame.font.Font(None, 32)

wifi_networks = get_wifi_networks()
current_wifi = get_current_wifi()

scroll_y = 0
max_scroll = max(0, len(wifi_networks) * 40 - height)

selected_network = None
password = ""
password_active = False
connecting = False
connection_message = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                mouse_pos = pygame.mouse.get_pos()
                for i, network in enumerate(wifi_networks):
                    rect = pygame.Rect(10, i * 40 - scroll_y, width - 20, 35)
                    if rect.collidepoint(mouse_pos):
                        selected_network = network
                        password = ""
                        password_active = True
                password_rect = pygame.Rect(10, height - 40, width - 20, 35)
                password_active = password_rect.collidepoint(mouse_pos)
            elif event.button == 4:  # Rueda del ratón hacia arriba
                scroll_y = max(0, scroll_y - 20)
            elif event.button == 5:  # Rueda del ratón hacia abajo
                scroll_y = min(max_scroll, scroll_y + 20)
        elif event.type == pygame.KEYDOWN:
            if password_active:
                if event.key == pygame.K_RETURN:
                    if selected_network:
                        connecting = True
                        connection_message = "Conectando..."
                        if connect_to_wifi(selected_network['ssid'], password):
                            connection_message = "Conectado exitosamente"
                            current_wifi = selected_network['ssid']
                        else:
                            connection_message = "Error al conectar"
                        connecting = False
                elif event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                else:
                    password += event.unicode

    screen.fill(WHITE)

    for i, network in enumerate(wifi_networks):
        rect = pygame.Rect(10, i * 40 - scroll_y, width - 20, 35)
        if 0 < rect.bottom and rect.top < height:
            if network['ssid'] == current_wifi:
                pygame.draw.rect(screen, GREEN, rect)
            elif network == selected_network:
                pygame.draw.rect(screen, BLUE, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)
            ssid_text = font.render(network['ssid'], True, BLACK)
            signal_text = font.render(f"{network['signal']}%", True, BLACK)
            screen.blit(ssid_text, (rect.x + 5, rect.y + 5))
            screen.blit(signal_text, (rect.right - 50, rect.y + 5))

    password_rect = pygame.Rect(10, height - 40, width - 20, 35)
    pygame.draw.rect(screen, BLUE if password_active else GRAY, password_rect)
    password_surface = font.render('*' * len(password), True, BLACK)
    screen.blit(password_surface, (password_rect.x + 5, password_rect.y + 5))

    if connection_message:
        message_surface = font.render(connection_message, True, BLACK)
        screen.blit(message_surface, (10, height - 80))

    pygame.display.flip()

pygame.quit()