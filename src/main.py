
import eventlet
eventlet.monkey_patch()

import sys
import os
import threading
# Añadir el directorio 'src/' al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.game import Game
from theming import Theming

# Importar la función para iniciar el servidor
from server import start_server

def main():
    theming = Theming(color_scheme='purple', mode='dark')

    game = Game()

    # Iniciar el servidor en un hilo separado
    server_thread = threading.Thread(target=start_server, args=(game.serial_handler,))
    server_thread.daemon = True
    server_thread.start()

    game.run()

if __name__ == "__main__":
    main()
