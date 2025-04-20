from PySide6.QtWidgets import QMainWindow, QPushButton
from PySide6.QtCore import QTimer, Slot
import serial.tools.list_ports
from .main_window import Ui_Main
from utils.serial_comm.serial_handler import SerialHandler  
from utils.serial_comm.SerialDataHandler import SerialDataHandler
#from utils.GraphHandler import GraphHandler
from utils.FileHandler import FileHandler

from utils.SpirometryGraphManager import SpirometryGraphManager
from utils.ECGGraphManager import ECGGraphManager
from utils.FilterManager import FilterManager

import time

class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Iniciar metodos de guardado
        self.file_handler = FileHandler()
        # Inicializar el manejador serial
        self.serial_handler = SerialHandler()
        self.data_handler = SerialDataHandler()
        self.data_handler.new_data_json.connect(self.command_into)

        # Inicializar los gráficos
        self.graph = ECGGraphManager()
        self.graph.set_active_subkeys(['gpio2'])  # O cualquier subclave que quieras visualizar
        self.graph.window_limit_reached.connect(self.on_window_limit_reached)
        self.graph_layout.addWidget(self.graph)


        # Configurar el timer para actualizar la lista de puertos
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.update_port_list)
        self.port_timer.start(1000)  # Actualizar cada segundo
        
        # Lista para mantener track de los puertos disponibles
        self.available_ports = []
        
        # Conectar señales
        self.connect_signals()
        
        # Actualizar lista inicial de puertos
        self.update_port_list()

        for objeto in self.findChildren(QPushButton):
            if objeto.objectName().startswith("btn_test_"):
                objeto.clicked.connect(self.reconnect_graph)

        self.fs = 200
                # Crear y configurar el gestor de filtros
        self.filter_manager = FilterManager(self)
        
        # Conectar la señal configurationChanged a nuestro método
        self.filter_manager.configurationChanged.connect(self.on_filter_config_changed)
        
        self.spin_time_record.setValue(60)
        self.spin_time_record.valueChanged.connect(self.windows_time)
        
    @Slot(float)
    def on_window_limit_reached(self, time_value):
        """Maneja el evento cuando se recibe una actualización del tiempo del gráfico"""
        # Actualizar el reloj en formato MM:SS
        minutes = int(time_value) // 60
        seconds = int(time_value) % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.lbl_time_count.setText(time_str)
        
        # Verificar si se alcanzó el tiempo límite configurado
        max_time = self.spin_time_record.value()
        
        # Si el tiempo actual supera o iguala el tiempo máximo configurado, detener la adquisición
        if time_value >= max_time:
            try:
                # Detener la actualización del gráfico
                self.data_handler.new_data_json.disconnect(self.graph.update_data)
                self.statusbar.showMessage(f"Adquisición detenida automáticamente al alcanzar límite en t={time_value:.2f}s")
                
                # Cambiar el estado del botón si es necesario
                if self.btn_start.text() == "Detener":
                    self.btn_start.setText("Iniciar")
                    self.btn_start.clicked.disconnect(self.stop_read)
                    self.btn_start.clicked.connect(self.start_read)
            except Exception as e:
                print(f"Error al desconectar la señal: {str(e)}")

    def windows_time(self, value):
        self.graph.set_time_graph(value)

    
    def on_filter_config_changed(self, param):
        self.graph.set_filters(param=param)

    def reconnect_graph(self):
        button = self.sender()
        self.limpiar_layout(self.graph_layout)
        if button.objectName() == "btn_test_ecg":
            self.graph = ECGGraphManager()
            # Reconectar la señal de límite de ventana
            self.graph.window_limit_reached.connect(self.on_window_limit_reached)
            self.graph_layout.addWidget(self.graph)
        elif button.objectName() == "btn_test_spiro":
            self.graph = SpirometryGraphManager()
            # Verificar si SpirometryGraphManager también tiene esta señal
            if hasattr(self.graph, 'window_limit_reached'):
                self.graph.window_limit_reached.connect(self.on_window_limit_reached)
            self.graph_layout.addWidget(self.graph)

    def limpiar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)  # Quita el padre pero no destruye el widget

    def connect_signals(self):
        """Conectar todas las señales necesarias"""
        
        self.file_handler.save_status.connect(self.statusbar.showMessage)
        self.file_handler.error_occurred.connect(self.statusbar.showMessage)
        self.btn_save.clicked.connect(self.save_data)

        self.btn_clear.clicked.connect(self.clear_data)
        self.btn_reset.clicked.connect(self.reset_data)

        # Conectar el botón de abrir
        self.btn_open.clicked.connect(self.open_data)
        
        # Conectar la señal de datos cargados del file_handler
        self.file_handler.data_loaded.connect(self.load_data_to_graph)


        # Conectar el botón de conexión
        self.btn_connect.clicked.connect(self.handle_connection)
        
        # Conectar el cambio de selección del combo box
        self.serial_list.currentIndexChanged.connect(self.port_selected)

        # Verificar la conexión de señales del serial_handler
        try:
            # Desconectar primero para evitar conexiones duplicadas
            try:
                self.serial_handler.data_received_serial.disconnect(self.data_handler.analisis_input_serial)
            except:
                print("error al desconectar")
            
            # Reconectar la señal
            self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
        except Exception as e:
            print(f"Error al conectar serial_handler.data_received: {str(e)}")


        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.start_read)
        print("Señal de botón start conectada")

        print("Conexión de señales completada\n")

 
    @Slot()
    def command_into(self, value):
        status = value["status"]
        interval = status["sample_interval"]
        fs = 1000 / interval
        if self.fs != fs:
            self.fs = fs
            self.spin_fs.setValue(fs)

    @Slot()
    def start_read(self):
        self.btn_start.setText("Detener")
        self.btn_start.clicked.disconnect(self.start_read)
        self.btn_start.clicked.connect(self.stop_read)
        self.lbl_state.setText("Grabando")
        try:
            # Continuar desde el último tiempo guardado
            self.graph.data_manager.resume()
            self.data_handler.new_data_json.connect(self.graph.update_data)
            print("Adquisición reanudada - continuando desde tiempo anterior")
        except Exception as e:
            print(f"Error al conectar data_handler.new_data_json: {str(e)}")

    def start_read_serial(self):
        try:
            self.serial_handler.start_reading()

        except Exception as e:
            print(f"Error al iniciar lectura: {str(e)}")

    @Slot()
    def update_port_list(self):
        """Actualizar la lista de puertos seriales disponibles"""
        # Obtener puertos actuales
        ports = self.serial_handler.get_available_ports()
        
        # Si la lista es diferente a la anterior, actualizar el combo box
        if ports != self.available_ports:
            # Guardar el puerto seleccionado actualmente
            current_port = self.serial_list.currentText()
            
            # Actualizar la lista de puertos
            self.serial_list.clear()
            self.serial_list.addItems(ports)
            
            # Intentar mantener el puerto seleccionado si aún existe
            if current_port in ports:
                self.serial_list.setCurrentText(current_port)
            
            # Actualizar la lista de puertos disponibles
            self.available_ports = ports
            
            # Deshabilitar el botón de conexión si no hay puertos
            self.btn_connect.setEnabled(len(ports) > 0)
            
            # Si no hay puertos y estaba conectado, desconectar
            if not ports and self.btn_connect.isChecked():
                self.btn_connect.setChecked(False)
                self.handle_connection()
    

    @Slot()
    def handle_connection(self):
        """Manejar la conexión/desconexión del puerto serial"""
        if self.btn_connect.isChecked():
            try:
                port = self.serial_list.currentText()
                
                # Crear nueva instancia de SerialHandler
                self.serial_handler = SerialHandler(port=port)
                
                # Reconectar la señal data_received
                try:
                    self.serial_handler.data_received_serial.disconnect(self.data_handler.analisis_input_serial)
                except:
                    pass
                self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
                
                if self.serial_handler.open():

                    self.statusbar.showMessage(f"Conectado a {port}")
                    self.serial_list.setEnabled(False)
                    self.btn_connect.setText("Desconectar")
                    self.start_read_serial()
                    self.serial_handler.write_data(('{"cmd": "set_sample_rate", "interval": 1}'))
                    time.sleep(1)
                    self.serial_handler.write_data(('{"cmd": "start_stream"}'))

                    
                    self.btn_start.setEnabled(True)
                
                else:
                    raise Exception("No se pudo conectar al puerto")
                    
            except Exception as e:
                print(f"Error en conexión: {str(e)}")
                self.statusbar.showMessage(f"Error de conexión: {str(e)}")
                self.btn_connect.setChecked(False)
                self.serial_list.setEnabled(True)
        else:
            try:
                if self.serial_handler:
                    self.serial_handler.write_data(('{"cmd": "stop_stream"}'))
                    time.sleep(1)
                    self.serial_handler.close()
                self.statusbar.showMessage("Desconectado")
                # Habilitar combo box después de desconectar
                self.serial_list.setEnabled(True)
                self.btn_connect.setText("Conectar")

            except Exception as e:
                self.statusbar.showMessage(f"Error al desconectar: {str(e)}")


    @Slot()
    def open_data(self):
        """Abrir y cargar datos desde un archivo"""
        # Desconectar del puerto serial si está conectado
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()
        
        # Abrir archivo
        self.file_handler.open_data_file(self)

    @Slot(dict)
    def load_data_to_graph(self, data):
        """
        Cargar datos en el gráfico
        
        Args:
            data (dict): Diccionario con los datos cargados
        """
        try:
            # Limpiar datos actuales
            self.graph_handler.clear_data()
            
            # Actualizar los datos uno por uno para asegurar la actualización correcta del gráfico
            for i in range(len(data['t'])):
                new_data = {
                    't': data['t'][i],
                    'p': data['p'][i],
                    'f': data['f'][i],
                    'v': data['v'][i]
                }
                self.graph_handler.update_data(new_data)
            
            # Deshabilitar botones de control serial
            self.btn_start.setEnabled(False)
            self.btn_connect.setEnabled(False)
            self.serial_list.setEnabled(False)
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al cargar datos en el gráfico: {str(e)}")

    @Slot(int)
    def port_selected(self, index):
        """Manejar la selección de un puerto en el combo box"""
        # Si hay un puerto seleccionado, habilitar el botón de conexión
        self.btn_connect.setEnabled(index >= 0)
        
        # Si cambia el puerto y estaba conectado, desconectar
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()
    @Slot()
    def save_data(self):
        """Guardar datos actuales en CSV"""
        self.file_handler.save_data_to_csv(self, self.graph_handler.data)
 
    @Slot()
    def clear_data(self):
        """Limpiar el puerto serial"""
        self.serial_handler.write_data("v")

        """Limpiar los gráficos"""
        self.graph_handler.clear_data()
        
    @Slot()
    def stop_read(self):
        self.btn_start.setText("Iniciar")
        self.btn_start.clicked.disconnect(self.stop_read)
        self.btn_start.clicked.connect(self.start_read)
        self.lbl_state.setText("Detenido")

        try:
            self.data_handler.new_data_json.disconnect(self.graph.update_data)
            # Guardar el estado de tiempo actual para continuar después
            self.graph.data_manager.pause()
            print("Adquisición pausada - tiempo guardado para continuación")
        except Exception as e:
            print(f"Error al desconectar la señal: {str(e)}")
            


    @Slot()
    def reset_data(self):
        """resetear la placa"""
        self.serial_handler.write_data("r")

        """Limpiar los gráficos"""
        self.graph_handler.clear_data()
    

    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        # Detener el timer
        self.port_timer.stop()
        
        # Desconectar si es necesario
        if self.btn_connect.isChecked():
            self.serial_handler.stop_reading()
            self.serial_handler.close()
            
        # Aceptar el evento de cierre
        event.accept()
