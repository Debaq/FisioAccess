import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
import numpy as np

class GraphDrawer:
    def __init__(self, config):
        self.config = config
        self.fig, self.axs = plt.subplots(1, config['num_graphs'], 
                                          figsize=(7*config['num_graphs'], 5), 
                                          gridspec_kw={'width_ratios': config['graph_proportions']})
        if config['num_graphs'] == 1:
            self.axs = [self.axs]
        
        self.graphs = {}
        self.curves = {}
        
        for i, graph_config in enumerate(self.config['graphs']):
            ax = self.axs[i]
            if ax is None:
                print(f"Error: El eje para el gráfico {i} es None")
                continue
            
            graph_type = graph_config['type']
            self.graphs[graph_type] = ax
            self.curves[graph_type] = {}
            
            ax.set_title(graph_config['title'])
            ax.set_xlabel(graph_config['x_label'])
            ax.set_ylabel(graph_config['y_label'])
            ax.set_xlim(graph_config['x_limits'])
            ax.set_ylim(graph_config['y_limits'])
            ax.grid(graph_config['show_grid'])
            
            for curve in graph_config['curves']:
                line, = ax.plot([], [], color=curve['color'], label=curve['label'])
                self.curves[graph_type][curve['name']] = line
            
            ax.legend()

        if 'Main' in self.graphs and 'View' in self.graphs:
            self.setup_selection()

        plt.tight_layout()
        
        # Inicializar datos
        self.data = {curve_name: ([], []) for curve_name in self.curves['Main']}
        self.max_points = 1000
        self.selection_lines = [None, None]
        self.selection_state = 0

    def setup_selection(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        if event.inaxes != self.graphs['Main']:
            return

        x = event.xdata
        ymin, ymax = self.graphs['Main'].get_ylim()

        if self.selection_state == 0:
            # Primer clic: establecer punto A
            self.delete_infinity_line("A")  # Borra la línea A si existe
            self.selection_lines[0] = self.graphs['Main'].axvline(x=x, color='red', linestyle='--')
            self.selection_state = 1
        elif self.selection_state == 1:
            # Segundo clic: establecer punto B y actualizar vista
            self.delete_infinity_line("B")  # Borra la línea B si existe
            self.selection_lines[1] = self.graphs['Main'].axvline(x=x, color='blue', linestyle='--')
            self.selection_state = 2
            self.update_view_graph(self.selection_lines[0].get_xdata()[0], x)
        else:
            # Tercer clic: reiniciar punto A
            self.delete_infinity_line("A")  # Borra la línea A existente
            self.selection_lines[0] = self.graphs['Main'].axvline(x=x, color='red', linestyle='--')
            self.selection_state = 1

        self.fig.canvas.draw_idle()

    def delete_infinity_line(self, line=None):
        """
        Borra las líneas infinitas de selección.
        
        :param line: Opcional. "A" para borrar la primera línea, "B" para la segunda, 
                     o None para borrar ambas.
        """
        if line is None or line.upper() == "A":
            if self.selection_lines[0]:
                self.selection_lines[0].remove()
                self.selection_lines[0] = None
            if line is None:
                self.selection_state = 0
            else:
                self.selection_state = max(0, self.selection_state - 1)

        if line is None or line.upper() == "B":
            if self.selection_lines[1]:
                self.selection_lines[1].remove()
                self.selection_lines[1] = None
            if line == "B":
                self.selection_state = min(1, self.selection_state)

        # Si ambas líneas se han borrado, reseteamos el estado
        if self.selection_lines[0] is None and self.selection_lines[1] is None:
            self.selection_state = 0

        # Actualizar la vista si ambas líneas fueron borradas o si la línea B fue borrada
        if line is None or line.upper() == "B":
            if 'View' in self.graphs:
                self.graphs['View'].clear()
                self.graphs['View'].set_title("Área seleccionada")
                self.graphs['View'].set_xlabel(self.graphs['Main'].get_xlabel())
                self.graphs['View'].set_ylabel(self.graphs['Main'].get_ylabel())
                self.graphs['View'].grid(True)

        self.fig.canvas.draw_idle()

    def update_view_graph(self, xmin, xmax):
        if 'View' not in self.graphs or self.graphs['View'] is None:
            print("Error: El gráfico de vista no está disponible")
            return

        view_ax = self.graphs['View']
        view_ax.clear()
        
        for curve_name, line in self.curves['Main'].items():
            x_data, y_data = self.data[curve_name]
            x_data = np.array(x_data)
            y_data = np.array(y_data)
            if len(x_data) > 0 and len(y_data) > 0:
                mask = (x_data >= xmin) & (x_data <= xmax)
                view_ax.plot(x_data[mask], y_data[mask], color=line.get_color(), label=curve_name)

        view_ax.set_title(f"Área seleccionada ({xmin:.2f} - {xmax:.2f})")
        view_ax.set_xlabel(self.graphs['Main'].get_xlabel())
        view_ax.set_ylabel(self.graphs['Main'].get_ylabel())
        view_ax.set_xlim(xmin, xmax)
        view_ax.grid(True)
        view_ax.legend()
        self.fig.canvas.draw_idle()

    def update(self, frame):
        t = frame * 0.1  # Incremento de tiempo
        new_data = {
            'sin': (t, np.sin(t)),
            'cos': (t, np.cos(t))
        }
        
        updated_artists = []
        
        for curve_name, (new_x, new_y) in new_data.items():
            if curve_name in self.data:
                x_data, y_data = self.data[curve_name]
                x_data.append(new_x)
                y_data.append(new_y)
                
                # Limitar los datos al número máximo de puntos
                if len(x_data) > self.max_points:
                    x_data.pop(0)
                    y_data.pop(0)
                
                if 'Main' in self.curves and curve_name in self.curves['Main']:
                    line = self.curves['Main'][curve_name]
                    line.set_data(x_data, y_data)
                    updated_artists.append(line)
        
        for ax in self.axs:
            if ax is not None:
                ax.relim()
                ax.autoscale_view()
        
        for line in self.selection_lines:
            if line:
                updated_artists.append(line)
        
        return updated_artists

    def show(self):
        print("Configuración de gráficos:", self.graphs)
        print("Configuración de curvas:", self.curves)
        
        self.anim = FuncAnimation(self.fig, self.update, frames=None, 
                                  interval=100, blit=True, cache_frame_data=False)
        plt.show()

# Ejemplo de uso
from graph_config_processor import process_graph_config

config = process_graph_config('graph_config.json')
drawer = GraphDrawer(config)

# Ejemplo de cómo usar la nueva función (esto iría después de que se hayan hecho algunas selecciones)
# drawer.delete_infinity_line()  # Borra ambas líneas
# drawer.delete_infinity_line("A")  # Borra solo la línea A
# drawer.delete_infinity_line("B")  # Borra solo la línea B

drawer.show()