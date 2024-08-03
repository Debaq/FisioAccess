import matplotlib as mpl
import matplotlib.pyplot as plt
from kivy.metrics import dp
from matplotlib import animation
import matplotlib.font_manager as fm
import os

def find_font_file(start_path, font_name, max_depth=5):
    """
    Busca el archivo de fuente en la estructura de directorios.
    """
    for root, dirs, files in os.walk(start_path):
        if font_name in files:
            return os.path.join(root, font_name)
        
        # Limitar la profundidad de búsqueda
        if root[len(start_path):].count(os.sep) >= max_depth:
            del dirs[:]
    
    raise FileNotFoundError(f"No se pudo encontrar el archivo de fuente {font_name}")

# Obtenemos la ruta del script actual
script_dir = os.path.dirname(os.path.abspath(__file__))

# Subimos dos niveles para llegar a la raíz del proyecto
project_root = os.path.dirname(os.path.dirname(script_dir))

# Buscamos el archivo de fuente
font_name = 'Hack-Regular.ttf'
try:
    font_path = find_font_file(project_root, font_name)
except FileNotFoundError:
    print(f"No se pudo encontrar el archivo {font_name}.")
    print("Por favor, verifica que el archivo existe y está en la carpeta 'fonts'.")
    print(f"Buscando desde: {project_root}")
    raise

font_prop = fm.FontProperties(fname=font_path)


#optimized draw on Agg backend
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 1.0
mpl.rcParams['agg.path.chunksize'] = 1000

#define some matplotlib figure parameters
#mpl.rcParams['font.family'] = 'Hack'
mpl.rcParams['font.family'] = font_prop.get_name()

mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.linewidth'] = 1.0



font_size_axis_title=dp(13)
font_size_axis_tick=dp(12)        


class GraphGenerator(object):
    """class that generate Matplotlib graph."""

    def __init__(self):
        """Create empty structure plot."""
        super().__init__()

        # Create subplots with specified width ratios
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [2, 1]})

        # Main ECG plot
        self.line1, = self.ax1.plot([], [], label='ECG')

        # Selection plot
        self.line2, = self.ax2.plot([], [], label='Selección')

        # Adjust plot layout
        self.fig.subplots_adjust(left=0.1, top=0.96, right=0.95, bottom=0.2, wspace=0.3)

        # Setting axis labels
        self.ax1.set_ylabel("mV", fontsize=8)
        #self.ax1.set_title("ECG")

        self.ax2.set_ylabel("mV", fontsize=8)
        #self.ax2.set_title("Selección")

        # Initialize axis limits for both plots
        self.ax1.set_xlim(0, 20)  # Example limits, adjust as needed
        self.ax1.set_ylim(-1, 1)
        self.ax2.set_xlim(0, 5)
        self.ax2.set_ylim(-1, 1)

        # Add grid to both plots
        self.ax1.grid(True)
        self.ax2.grid(True)

    def update_main_ecg(self, x_data, y_data):
        """Update the main ECG plot with new data."""
        self.line1.set_data(x_data, y_data)
        self.ax1.set_xlim(min(x_data), max(x_data))
        self.ax1.set_ylim(min(y_data), max(y_data))
        self.fig.canvas.draw()

    def update_selection(self, x_data, y_data):
        """Update the selection plot with new data."""
        self.line2.set_data(x_data, y_data)
        self.ax2.set_xlim(min(x_data), max(x_data))
        self.ax2.set_ylim(min(y_data), max(y_data))
        self.fig.canvas.draw()

# Example usage
if __name__ == "__main__":
    import numpy as np

    graph_gen = GraphGenerator()

    # Generate some example ECG data
    x = np.linspace(0, 10, 1000)
    y = np.sin(x)  # Replace with real ECG data

    # Update plots with the example data
    graph_gen.update_main_ecg(x, y)
    graph_gen.update_selection(x[:100], y[:100])

    plt.show()
# Example usage
if __name__ == "__main__":
    import numpy as np

    graph_gen = GraphGenerator()

    # Generate some example ECG data
    x = np.linspace(0, 10, 1000)
    y = np.sin(x)  # Replace with real ECG data

    # Update plots with the example data
    graph_gen.update_main_ecg(x, y)
    graph_gen.update_selection(x[:100], y[:100])

    plt.show()