import sys
import os
import subprocess

# Añadir el directorio raíz del proyecto al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def update_from_github():
    print("Verificando actualizaciones en GitHub...")
    try:
        # Obtener la ruta absoluta del directorio raíz del proyecto
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        os.chdir(project_root)
        
        # Obtener los cambios más recientes sin aplicarlos
        subprocess.run(["git", "fetch"], check=True)
        
        # Comprobar si hay cambios
        result = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True, check=True)
        
        if "Your branch is up to date" in result.stdout:
            print("El proyecto está actualizado.")
            return False
        else:
            print("Se encontraron actualizaciones. Aplicando cambios...")
            # Aplicar los cambios
            subprocess.run(["git", "pull"], check=True)
            print("Proyecto actualizado exitosamente.")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error al actualizar desde GitHub: {e}")
        return False

def main():
    print("Importando módulos y iniciando el juego...")
    try:
        from src.game import Game
        
        game = Game()
        game.run()
    except ImportError as e:
        print(f"Error al importar módulos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar si ya se ha intentado una actualización
    if len(sys.argv) > 1 and sys.argv[1] == "--updated":
        # Si ya se intentó actualizar, simplemente ejecutar el juego
        main()
    else:
        updated = update_from_github()
        if updated:
            print("Se realizaron actualizaciones. Reiniciando el script para cargar los cambios...")
            # Reiniciar el script con un flag para indicar que ya se actualizó
            os.execv(sys.executable, [sys.executable] + [sys.argv[0], "--updated"])
        else:
            main()