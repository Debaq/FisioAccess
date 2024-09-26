import sys
import os
import subprocess
import time

# Añadir el directorio raíz del proyecto al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos


def run_git_command(command, timeout=30):
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                check=True, timeout=timeout)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Error al ejecutar el comando Git {' '.join(command)}: {e}")
        return None


def print_git_info():
    print("\n--- Información de Git ---")

    # Obtener la versión de Git
    git_version = run_git_command(["git", "--version"])
    if git_version:
        print(f"Versión de Git: {git_version}")

    # Obtener el hash del commit actual
    current_commit = run_git_command(["git", "rev-parse", "HEAD"])
    if current_commit:
        print(f"Commit actual: {current_commit}")

    # Obtener la rama actual
    current_branch = run_git_command(["git", "rev-parse",
                                      "--abbrev-ref", "HEAD"])
    if current_branch:
        print(f"Rama actual: {current_branch}")

    # Obtener los últimos 5 commits
    print("\nÚltimos 5 commits:")
    last_commits = run_git_command(["git", "log", "-5", "--oneline"])
    if last_commits:
        print(last_commits)

    # Obtener los cambios no commiteados
    uncommitted_changes = run_git_command(["git", "status", "-s"])
    if uncommitted_changes:
        print("\nCambios no commiteados:")
        print(uncommitted_changes)
    else:
        print("\nNo hay cambios no commiteados.")

    print("---------------------------\n")


def update_from_github():
    print("Verificando actualizaciones en GitHub...")
    for attempt in range(MAX_RETRIES):
        try:
            # Obtener la ruta absoluta del directorio raíz del proyecto
            project_root = os.path.abspath(os.path.join(
                                            os.path.dirname(__file__), '..'))
            os.chdir(project_root)

            # Obtener los cambios más recientes sin aplicarlos
            subprocess.run(["git", "fetch"], check=True, timeout=30)

            # Comprobar si hay cambios
            result = subprocess.run(["git", "status", "-uno"],
                                    capture_output=True, text=True,
                                    check=True, timeout=30)

            if "Your branch is up to date" in result.stdout:
                print("El proyecto está actualizado.")
                return False
            else:
                print("Se encontraron actualizaciones. Aplicando cambios...")
                # Aplicar los cambios
                subprocess.run(["git", "pull"], check=True, timeout=30)
                print("Proyecto actualizado exitosamente.")
                return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"""Error al actualizar desde GitHub (intento {attempt + 1}
                  de {MAX_RETRIES}): {e}""")
            if attempt < MAX_RETRIES - 1:
                print(f"Reintentando en {RETRY_DELAY} segundos...")
                time.sleep(RETRY_DELAY)
            else:
                print("""No se pudo actualizar después de varios intentos.
                      Continuando con la versión actual.""")
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
        # Si ya se intentó actualizar, imprimir 
        # información de Git y ejecutar el juego
        print_git_info()
        main()
    else:
        updated = update_from_github()
        if updated:
            print("""Se realizaron actualizaciones. 
                  Reiniciando el script para cargar los cambios...""")
            # Reiniciar el script con un flag para indicar que ya se actualizó
            os.execv(sys.executable,
                     [sys.executable] + [sys.argv[0], "--updated"])
        else:
            print_git_info()
            main()
