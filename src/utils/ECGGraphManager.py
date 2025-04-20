import pyqtgraph as pg
from PySide6.QtCore import Slot
import numpy as np
from utils.filters import FILTERS


from utils.BaseGraphManager import BaseGraphManager, DataManager

class ECGGraphManager(BaseGraphManager):
    """
    Gestor de gráficos específico para la visualización de datos de electrocardiograma (ECG).
    """
    def __init__(self, parent=None):
        # Definir constantes para los límites del ROI
        self.LIMIT_MIN = 0
        self.LIMIT_MAX = 60
        # Tamaño inicial del ROI (en segundos)
        self.roi_size = 5
        # Bandera para controlar si es la primera actualización
        self.first_update = True
        # Llamar al constructor de la clase base después de definir las constantes
        super().__init__(parent, layout_type='vertical')
        self.filtro = FILTERS(fs=1000)

        # Configurar filtros
        configuracion = {
            "highpass": {
                "cutoff": 0.16,
                "order": 1
            },
            "notch50": {
                "frequency": 50.0,
                "q_factor": 1.00
            },
            "lowpass": {
                "cutoff": 100.00,
                "order": 2
            }
        }
                
        # Aplicar configuración
        self.filtro.set_param(configuracion)


    def setup_data_manager(self):
        """Inicializa el gestor de datos con configuración mínima para ECG"""
        # Por defecto solo gestionamos tiempo y una derivación
        self.data_manager = DataManager(['timestamp', 'analog'])
        self.analog_subkeys = ['gpio2', 'gpio3', 'gpio4']
        self.active_subkey = self.analog_subkeys  # Por defecto, todos los canales están activos
        # Metadatos específicos para ECG
        self.data_manager.metadata['qrs_intervals'] = []
        self.data_manager.metadata['heart_rate'] = 0

    def convert_raw_to_mv(self, raw_value):
        """Convierte valores raw del ADC (0-4095) a milivoltios (0-3300)"""
        return (raw_value * 3300.0) / 4095.0  # 3300 mV = 3.3V

    def setup_graphs(self):
        """Configurar los widgets de gráficos para ECG"""
        # Crear el widget principal para el ECG
        self.ecg_widget = pg.PlotWidget()
        
        # Configurar el gráfico ECG vs Tiempo
        self.ecg_plot = self.ecg_widget.getPlotItem()
        self.ecg_plot.setLabel('left', 'Amplitud', 'mV')
        self.ecg_plot.setLabel('bottom', 'Tiempo', 's')
        self.ecg_plot.showGrid(x=True, y=True)
        
        # Establecer límites en el eje Y
        view_box = self.ecg_plot.getViewBox()
        #view_box.setLimits(yMin=-3, yMax=4000)  # Valores ajustados para múltiples canales con offset
        #view_box.setYRange(-2, 10, padding=0)
        self.update_view_range()


        # Desactivar autoRange para el eje X para evitar cambios inesperados
        view_box.disableAutoRange(axis=pg.ViewBox.XAxis)
        
        # Configurar el fondo del gráfico
        self.ecg_widget.setBackground('w')
        
        # Widget para el ritmo continuo
        self.rhythm_widget = pg.PlotWidget()
        self.rhythm_plot = self.rhythm_widget.getPlotItem()
        self.rhythm_plot.setLabel('left', 'ECG', 'mV')
        self.rhythm_plot.setLabel('bottom', 'Tiempo', 's')
        self.rhythm_plot.showGrid(x=True, y=True)
        self.rhythm_widget.setBackground('w')
        self.rhythm_plot.setXRange(0, self.LIMIT_MAX)
        
        # Reducir el margen para la etiqueta y del gráfico de ritmo
        self.rhythm_plot.getAxis('left').setWidth(40)
        
        # Configurar layout para mostrar el gráfico de ritmo debajo del ECG principal
        self.layout.addWidget(self.ecg_widget, stretch=7)
        self.layout.addWidget(self.rhythm_widget, stretch=3)
        
        # Añadir ROI al gráfico de ritmo
        self.setup_roi()

    def update_view_range(self):
        """Ajusta dinámicamente el rango de visualización según el número de canales activos"""
        # Determinar cuántos canales están activos
        subkeys = self.active_subkey if isinstance(self.active_subkey, list) else [self.active_subkey]
        num_channels = len(subkeys)
        
        # Calcular el rango base para un solo canal (0-3300 mV)
        base_range = 3300  # mV para un canal
        
        # Calcular el offset entre canales (separación vertical)
        channel_offset = 3000  # mV de separación entre canales
        
        # Calcular el rango total necesario
        total_range = (num_channels * base_range) + ((num_channels - 1) * channel_offset)
        
        # Añadir margen adicional
        margin = 500  # mV de margen
        
        # Configurar el ViewBox
        view_box = self.ecg_plot.getViewBox()
        view_box.setLimits(yMin=-margin, yMax=total_range + margin)
        view_box.setYRange(-margin, total_range + margin, padding=0)
        
        #print(f"ViewBox ajustado para {num_channels} canales: {-margin} a {total_range + margin} mV")

    def setup_roi(self):
        """Configurar la región de interés (ROI) en el gráfico de ritmo como un intervalo de tamaño fijo"""
        # Crear un LinearRegionItem (región seleccionable)
        self.roi = pg.LinearRegionItem()
        self.roi.setZValue(10)  # Asegurar que esté por encima de las curvas
        
        # Configurar colores para que sea visible con el fondo blanco
        self.roi.setBrush(pg.mkBrush(color=(100, 100, 255, 50)))
        self.roi.setRegion([0, self.roi_size])  # Valores iniciales
        
        # Establecer límites para el ROI
        self.roi.setBounds([self.LIMIT_MIN, self.LIMIT_MAX])
        
        # Añadir ROI al gráfico de ritmo
        self.rhythm_plot.addItem(self.roi)
        
        # Deshabilitar la capacidad de redimensionar el ROI modificando su implementación interna
        # Esto hace que los bordes no sean interactivos, solo se puede mover como unidad
        for line in self.roi.lines:
            line.setMovable(False)
        
        # Conectar la señal de cambio de región para monitorear movimientos del ROI
        self.roi.sigRegionChanged.connect(self.maintain_roi_size)
        self.roi.sigRegionChanged.connect(self.update_roi)

    def maintain_roi_size(self):
        """Asegura que el ROI mantenga un tamaño fijo al ser movido"""
        min_x, max_x = self.roi.getRegion()
        current_size = max_x - min_x
        
        # Si el tamaño ha cambiado (por alguna razón), restaurarlo
        if abs(current_size - self.roi_size) > 0.001:  # Pequeña tolerancia para errores de coma flotante
            # Calcular el punto medio
            mid_point = (min_x + max_x) / 2
            
            # Calcular los nuevos límites manteniendo el punto medio
            new_min = mid_point - self.roi_size / 2
            new_max = mid_point + self.roi_size / 2
            
            # Asegurar que los límites están dentro del rango permitido
            if new_min < self.LIMIT_MIN:
                new_min = self.LIMIT_MIN
                new_max = new_min + self.roi_size
            elif new_max > self.LIMIT_MAX:
                new_max = self.LIMIT_MAX
                new_min = new_max - self.roi_size
            
            # Establecer la nueva región sin activar esta misma función (para evitar recursión)
            self.roi.blockSignals(True)
            self.roi.setRegion([new_min, new_max])
            self.roi.blockSignals(False)

    def set_size_roi(self, size_seconds):
        """
        Establece el tamaño del ROI en segundos
        
        Args:
            size_seconds (float): Tamaño del ROI en segundos
        """
        # Validar tamaño
        if size_seconds <= 0:
            print("El tamaño del ROI debe ser positivo")
            return
        
        # Limitar el tamaño máximo al rango disponible
        if size_seconds > self.LIMIT_MAX - self.LIMIT_MIN:
            size_seconds = self.LIMIT_MAX - self.LIMIT_MIN
            print(f"Tamaño del ROI limitado a {size_seconds} segundos")
        
        # Guardar el nuevo tamaño
        self.roi_size = size_seconds
        
        # Obtener la posición actual del ROI
        min_x, max_x = self.roi.getRegion()
        mid_point = (min_x + max_x) / 2
        
        # Calcular los nuevos límites manteniendo el punto medio
        new_min = mid_point - size_seconds / 2
        new_max = mid_point + size_seconds / 2
        
        # Asegurar que los límites están dentro del rango permitido
        if new_min < self.LIMIT_MIN:
            new_min = self.LIMIT_MIN
            new_max = new_min + size_seconds
        elif new_max > self.LIMIT_MAX:
            new_max = self.LIMIT_MAX
            new_min = new_max - size_seconds
        
        # Establecer la nueva región
        self.roi.blockSignals(True)
        self.roi.setRegion([new_min, new_max])
        self.roi.blockSignals(False)
        
        # Actualizar el gráfico principal
        self.update_roi()

    def update_roi(self):
        """Actualizar el gráfico principal cuando cambia la ROI"""
        # Obtener los límites de la región seleccionada
        min_x, max_x = self.roi.getRegion()
        
        # Aplicar esos límites al gráfico principal manteniendo el tamaño fijo
        self.ecg_plot.setXRange(min_x, max_x, padding=0)
        
        # NO volver a llamar a update_plots aquí para evitar recursión y cambios inesperados
        # La actualización de los datos se hará desde el método principal update_plots

    def setup_curve_styles(self):
        """Configurar las curvas de los gráficos para ECG"""
        # Por defecto solo tenemos una derivación
        self.leads = ['analog']
        self.lead_colors = ['r', 'g', 'b', 'm', 'c', 'y', 'k']
        
        # Derivación activa (por defecto la única disponible)
        self.active_lead = 'analog'
        
        # Definir el número máximo de GPIOs que podríamos tener
        max_gpios = 3 # Por ejemplo, gpio2 hasta gpio9
        
        # Crear diccionarios para almacenar todas las curvas y etiquetas
        self.ecg_curves = {}
        self.channel_labels = {}
        
        # Crear curvas para todos los posibles GPIOs
        for i in range(max_gpios):
            gpio_name = f'gpio{i+2}'  # Empezando desde gpio2

            # Crear curva con su propio color
            pen = pg.mkPen(color=self.lead_colors[i % len(self.lead_colors)], width=2)
            curve = self.ecg_plot.plot([], [], pen=pen, name=gpio_name)
            self.ecg_curves[gpio_name] = curve

            # Inicialmente ocultar todas las curvas
            #curve.setVisible(True) #cambiar a False <<<<<<<<<<<<<<ojo
            
            # Crear etiqueta para este canal (inicialmente oculta)
            label = pg.TextItem(text=gpio_name, color=self.lead_colors[i % len(self.lead_colors)], anchor=(0, 0.5))
            self.ecg_plot.addItem(label)
            #label.setVisible(False) <<<<<<<<<<<<<<<<<<<ojo
            self.channel_labels[gpio_name] = label
        
        
        # Curva para el ritmo (primera subkey por defecto)
        self.rhythm_curve = self.rhythm_plot.plot(
            pen=pg.mkPen('b', width=2)
        )
        
        # Configurar el color de las etiquetas y ejes
        for plot in [self.ecg_plot, self.rhythm_plot]:
            plot.getAxis('bottom').setPen('k')
            plot.getAxis('left').setPen('k')
            plot.getAxis('bottom').setTextPen('k')
            plot.getAxis('left').setTextPen('k')

    def setup_markers(self):
        """Configurar los marcadores para ECG"""
        # Crear las líneas verticales para marcar intervalos
        self.qrs_line1 = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2)
        )
        self.qrs_line2 = pg.InfiniteLine(
            pos=1, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('g', width=2)
        )
        
        # Línea horizontal para el nivel de base
        self.baseline = pg.InfiniteLine(
            pos=0, 
            angle=0, 
            movable=True,
            pen=pg.mkPen('b', width=1, style=pg.QtCore.Qt.DashLine)
        )
        
        # Configurar los límites
        self.qrs_line1.setBounds((None, None))
        self.qrs_line2.setBounds((None, None))
        
        # Crear etiquetas para los intervalos
        self.qrs_label = pg.TextItem(text='', color='r', anchor=(0.5, 0))
        self.hr_label = pg.TextItem(text='', color='g', anchor=(0, 0))
        
        # Agregar las líneas y etiquetas al gráfico
        self.ecg_plot.addItem(self.qrs_line1)
        self.ecg_plot.addItem(self.qrs_line2)
        self.ecg_plot.addItem(self.baseline)
        self.ecg_plot.addItem(self.qrs_label)
        self.ecg_plot.addItem(self.hr_label)
        
        # Conectar señales para actualizar cuando las líneas se muevan
        self.qrs_line1.sigPositionChanged.connect(self.update_interval_info)
        self.qrs_line2.sigPositionChanged.connect(self.update_interval_info)

    def update_interval_info(self):
        """Actualizar la información de los intervalos QRS"""
        try:
            # Solo aplica si hay al menos una subclave activa
            if not self.active_subkey or (isinstance(self.active_subkey, list) and len(self.active_subkey) == 0):
                self.qrs_label.setText('')
                self.hr_label.setText('')
                return

            x1 = self.qrs_line1.value()
            x2 = self.qrs_line2.value()
            rr_interval = abs(x2 - x1)
            heart_rate = 60 / rr_interval if rr_interval > 0 else 0
            self.data_manager.metadata['heart_rate'] = heart_rate

            # Obtener subclave para análisis (primera si es lista)
            analysis_key = self.active_subkey[0] if isinstance(self.active_subkey, list) else self.active_subkey

            # Posicionar etiquetas
            x_mid = min(x1, x2) + rr_interval / 2
            y_position = self.ecg_plot.getViewBox().viewRange()[1][1] * 0.9

            self.qrs_label.setPos(x_mid, y_position)
            self.qrs_label.setText(
                f'RR: {rr_interval*1000:.0f} ms\nHR: {heart_rate:.0f} bpm'
            )

            self.hr_label.setPos(
                self.ecg_plot.getViewBox().viewRange()[0][0],
                self.ecg_plot.getViewBox().viewRange()[1][1] * 0.8
            )
            self.hr_label.setText(f'Heart Rate: {heart_rate:.0f} bpm')

        except Exception as e:
            print(f"Error actualizando intervalos: {e}")

    def get_subvalue_at_x(self, x_pos, subkey=None):
        """
        Interpola el valor para una subclave específica de 'analog' en un tiempo dado.
        
        Args:
            x_pos (float): Posición en el tiempo para interpolar
            subkey (str, optional): Subclave específica a interpolar. Por defecto, usa la primera activa.
            
        Returns:
            float: Valor interpolado, None si no es posible
        """
        timestamps = self.data_manager.display_data['timestamp']
        analog_data = self.data_manager.display_data['analog']

        if not timestamps or not analog_data:
            return None
            
        # Determinar qué subclave usar
        if subkey is None:
            if isinstance(self.active_subkey, list) and self.active_subkey:
                subkey = self.active_subkey[0]
            else:
                subkey = self.active_subkey
        
        x_data = np.array(timestamps)
        
        # Extraer valores para la subclave específica
        y_data = np.array([
            a.get(subkey, 0) if isinstance(a, dict) else 0
            for a in analog_data
        ])

        if x_pos < x_data[0] or x_pos > x_data[-1]:
            return None

        idx = np.searchsorted(x_data, x_pos)
        if idx > 0 and idx < len(x_data):
            x0, x1 = x_data[idx-1], x_data[idx]
            y0, y1 = y_data[idx-1], y_data[idx]

            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (x_pos - x0) / (x1 - x0)
        
        return None

    def update_plots(self):
        """Actualiza los gráficos de ECG con los datos actuales"""
        if len(self.data_manager.display_data['timestamp']) == 0:
            return

        timestamps = self.data_manager.display_data['timestamp']
        analog_raw = self.data_manager.display_data['analog']
        
        # Obtener los límites de la región seleccionada para filtrar datos
        min_x, max_x = self.roi.getRegion()


        # Asegurar que siempre sea lista
        subkeys = self.active_subkey if isinstance(self.active_subkey, list) else [self.active_subkey]
        # Si no hay subclaves activas, no hay nada que mostrar
        if not subkeys:
            return
            
        # Primero ocultar todas las curvas y etiquetas
        for gpio_name, curve in self.ecg_curves.items():
            curve.setVisible(False)
            if gpio_name in self.channel_labels:
                self.channel_labels[gpio_name].setVisible(False)
            
        num_channels = len(subkeys)
        channel_spacing = 3000  # mV entre canales

        # Luego actualizar y mostrar solo las curvas activas
        for idx, subkey in enumerate(subkeys):
            if subkey in self.ecg_curves:
                # Aplicar offset vertical
                offset = idx * channel_spacing

                y_values = []
                for a in analog_raw:
                    if isinstance(a, dict) and subkey in a:
                        # Convertir el valor raw a mV
                        raw_value = a[subkey]
                        mv_value = self.convert_raw_to_mv(raw_value)
                        y_values.append(mv_value + offset)
                    else:
                        y_values.append(offset)

                # Normalizar los datos antes de filtrar
                y_values_normalized = [y/1000.0 for y in y_values]  # Convertir a valores más pequeños
                y_values_filter = self.filtro.filtrar(y_values_normalized)
                y_values_filter = y_values_filter * 1000.0  # Volver a escalar después del filtrado

                #print(y_values)
                y_values_filter = self.filtro.filtrar(y_values)
                print(f"Tipo de y_values_filter: {type(y_values_filter)}")
                print(f"Primeros 5 valores originales: {y_values[:5]}")
                print(f"Primeros 5 valores filtrados: {y_values_filter[:5]}")

                # Asegúrate de que y_values_filter sea una lista o array numpy
                if not isinstance(y_values_filter, (list, np.ndarray)):
                    y_values_filter = np.array(y_values_filter)
                #y_values_filter = y_values
                #print(y_values)

                # Actualizar curva con todos los datos
                self.ecg_curves[subkey].setData(x=timestamps, y=y_values_filter)
                self.ecg_curves[subkey].setVisible(True)
                
                # Actualizar etiqueta al final
                if len(timestamps) > 0 and len(y_values_filter) > 0 and subkey in self.channel_labels:
                    # Buscar el último punto visible dentro del ROI
                    last_visible_idx = -1
                    for i in range(len(timestamps)-1, -1, -1):
                        if min_x <= timestamps[i] <= max_x:
                            last_visible_idx = i
                            break
                    
                    # Si hay punto visible, mostrar etiqueta
                    if last_visible_idx >= 0:
                        self.channel_labels[subkey].setPos(timestamps[last_visible_idx], y_values_filter[last_visible_idx])
                        self.channel_labels[subkey].setVisible(True)
        
        self.update_view_range()

    


        # ------- GRAFICAR EN rhythm_plot (solo primera curva, sin offset) --------
        if subkeys:  # Si hay al menos una subclave activa
            first_subkey = subkeys[0]
            y_values_rhythm = []
            
            for a in analog_raw:
                if isinstance(a, dict) and first_subkey in a:
                    y_values_rhythm.append(a[first_subkey])
                else:
                    y_values_rhythm.append(0)  # Valor predeterminado si no hay dato
                    
            self.rhythm_curve.setData(x=timestamps, y=y_values_rhythm)
        
        # Mantener el rango X fijo según el ROI
        self.ecg_plot.setXRange(min_x, max_x, padding=0)
        
        # Actualizar etiquetas si aplica
        self.update_interval_info()
        
        # Actualizar etiqueta del eje Y
        if len(subkeys) == 1:
            label = subkeys[0].replace('_', ' ')
        else:
            label = "Multicanal ECG"
            
        self.ecg_plot.setLabel('left', label, 'mV')



    def set_active_subkeys(self, subkeys):
        """
        Establece qué subclaves de 'analog' se mostrarán en el gráfico principal
        
        Args:
            subkeys (list): Lista de subclaves a mostrar (por ejemplo, ['gpio2', 'gpio4'])
        """
        if isinstance(subkeys, list) and len(subkeys) > 0:
            self.active_subkey = subkeys
        elif isinstance(subkeys, str):
            self.active_subkey = [subkeys]
        else:
            print("Error: se requiere al menos una subclave activa")
            return
            
        # Actualizar los gráficos con las nuevas subclaves activas
        self.update_plots()

    
        # Ajustar el rango de visualización para los canales activos
        self.update_view_range()

    def set_leads(self, lead_names):
        """
        Configura las derivaciones disponibles
        
        Args:
            lead_names (list): Lista de nombres de derivaciones
        """
        # Verificar que exista al menos una derivación
        if not lead_names:
            return
            
        # Actualizar gestor de datos con las nuevas derivaciones
        old_data_types = list(self.data_manager.data.keys())
        new_data_types = ['timestamp'] + lead_names
        
        # Crear nuevo gestor de datos con las derivaciones especificadas
        new_data_manager = DataManager(new_data_types)
        
        # Copiar datos existentes si es posible
        for key in old_data_types:
            if key in new_data_types:
                new_data_manager.data[key] = self.data_manager.data[key].copy()
                new_data_manager.display_data[key] = self.data_manager.display_data[key].copy()
        
        # Copiar metadatos
        new_data_manager.metadata = self.data_manager.metadata.copy()
        new_data_manager.initial_time = self.data_manager.initial_time
        new_data_manager.record = self.data_manager.record
        
        # Reemplazar el gestor de datos
        self.data_manager = new_data_manager
        
        # Actualizar lista de derivaciones
        self.leads = lead_names
        
        # Asignar colores
        default_colors = ['r', 'g', 'b', 'c', 'm', 'y']
        self.lead_colors = default_colors[:len(lead_names)]
        
        # Establecer la primera derivación como activa
        self.set_active_lead(lead_names[0])
        
    def set_active_lead(self, lead_name):
        """
        Cambia la derivación activa que se muestra en el gráfico principal
        
        Args:
            lead_name (str): Nombre de la derivación
        """
        if lead_name in self.leads and lead_name in self.data_manager.display_data:
            self.active_lead = lead_name
            self.update_plots()
            
            # Actualizar etiqueta del eje Y
            self.ecg_plot.setLabel('left', lead_name.replace('_', ' '), 'mV')

    def reset_markers(self):
        """Restablecer los marcadores a su posición inicial"""
        self.qrs_line1.setValue(0)
        self.qrs_line2.setValue(1)
        self.baseline.setValue(0)
        self.qrs_label.setText('')
        self.hr_label.setText('Heart Rate: -- bpm')
        
        # Restablecer ROI
        if hasattr(self, 'roi'):
            # Establecer ROI al inicio pero manteniendo su tamaño
            self.roi.blockSignals(True)
            self.roi.setRegion([0, self.roi_size])
            self.roi.blockSignals(False)
            self.update_roi()