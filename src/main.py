import sys
import os

# Añadir el directorio raíz del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
    