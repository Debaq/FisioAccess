import sys
import os

# Añadir el directorio raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.game import Game
from theming import Theming




def main():
    theming = Theming(color_scheme='purple', mode='dark')

    game = Game()
    game.run()

if __name__ == "__main__":
    main()
    