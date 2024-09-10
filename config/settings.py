import os

# Configuración de la ventana
WIDTH = 1024
HEIGHT = 560

# Configuración del gráfico
MAX_POINTS = 1000
VISIBLE_POINTS = 100

# Configuración serial
SERIAL_PORT = '/dev/ttyS2'
BAUD_RATE = 115600

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR, 'assets', 'fonts', 'Space_Mono/SpaceMono-Regular.ttf')

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)