from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget

class FilterManager(QObject):
    """
    Controlador para manejar los parámetros de los filtros y generar
    el diccionario de configuración automáticamente al cambiar cualquier parámetro.
    """
    
    # Señal que se emite cuando cambia la configuración
    configurationChanged = Signal(dict)
    
    def __init__(self, parent_widget):
        """
        Inicializa el controlador.
        
        Args:
            parent_widget: El widget principal que contiene todos los controles de filtros
        """
        super().__init__()
        self.parent = parent_widget
        self.connect_all_signals()
        
    def connect_all_signals(self):
        """Conecta todas las señales de los widgets para actualización automática"""
        
        # Conectar checkboxes
        checkboxes = [
            self.parent.checkBoxHighPass,
            self.parent.checkBoxLowPass,
            self.parent.checkBoxNotch50,
            self.parent.checkBoxNotch60,
            self.parent.checkBoxBandPass,
            self.parent.checkBoxMedian,
            self.parent.checkBoxMovingAverage
        ]
        
        # Diccionario para mapear checkboxes con los widgets que deben activar/desactivar
        widget_groups = {
            self.parent.checkBoxHighPass: [
                self.parent.spinBoxHighPassCutoff,
                self.parent.spinBoxHighPassOrder
            ],
            self.parent.checkBoxLowPass: [
                self.parent.spinBoxLowPassCutoff,
                self.parent.spinBoxLowPassOrder
            ],
            self.parent.checkBoxNotch50: [
                self.parent.spinBoxNotch50Frequency,
                self.parent.spinBoxNotch50QFactor
            ],
            self.parent.checkBoxNotch60: [
                self.parent.spinBoxNotch60Frequency,
                self.parent.spinBoxNotch60QFactor
            ],
            self.parent.checkBoxBandPass: [
                self.parent.spinBoxBandPassLowCutoff,
                self.parent.spinBoxBandPassHighCutoff,
                self.parent.spinBoxBandPassOrder
            ],
            self.parent.checkBoxMedian: [
                self.parent.spinBoxMedianWindowSize
            ],
            self.parent.checkBoxMovingAverage: [
                self.parent.spinBoxMovingAverageWindowSize
            ]
        }
        
        # Conectar cada checkbox para habilitar/deshabilitar widgets y actualizar configuración
        for checkbox in checkboxes:
            checkbox.toggled.connect(lambda checked, cb=checkbox: self.handle_checkbox_change(cb, checked))
            # Inicializar el estado
            widgets_to_enable = widget_groups.get(checkbox, [])
            self.toggle_widgets_enabled(widgets_to_enable, checkbox.isChecked())
        
        # Conectar todos los spinboxes para que cuando cambien se actualice la configuración
        all_spinboxes = [
            self.parent.spinBoxHighPassCutoff,
            self.parent.spinBoxHighPassOrder,
            self.parent.spinBoxLowPassCutoff,
            self.parent.spinBoxLowPassOrder,
            self.parent.spinBoxNotch50Frequency,
            self.parent.spinBoxNotch50QFactor,
            self.parent.spinBoxNotch60Frequency,
            self.parent.spinBoxNotch60QFactor,
            self.parent.spinBoxBandPassLowCutoff,
            self.parent.spinBoxBandPassHighCutoff,
            self.parent.spinBoxBandPassOrder,
            self.parent.spinBoxMedianWindowSize,
            self.parent.spinBoxMovingAverageWindowSize,
            self.parent.spinBoxSamplingFrequency
        ]
        
        # Conectar todos los spinboxes
        for spinbox in all_spinboxes:
            if hasattr(spinbox, 'valueChanged'):
                spinbox.valueChanged.connect(self.update_configuration)
    
    def handle_checkbox_change(self, checkbox, checked):
        """
        Maneja los cambios en los checkboxes: habilita/deshabilita widgets y actualiza la configuración
        
        Args:
            checkbox: El checkbox que cambió
            checked: Nuevo estado del checkbox
        """
        # Habilitar/deshabilitar widgets relacionados
        widget_groups = {
            self.parent.checkBoxHighPass: [
                self.parent.spinBoxHighPassCutoff,
                self.parent.spinBoxHighPassOrder
            ],
            self.parent.checkBoxLowPass: [
                self.parent.spinBoxLowPassCutoff,
                self.parent.spinBoxLowPassOrder
            ],
            self.parent.checkBoxNotch50: [
                self.parent.spinBoxNotch50Frequency,
                self.parent.spinBoxNotch50QFactor
            ],
            self.parent.checkBoxNotch60: [
                self.parent.spinBoxNotch60Frequency,
                self.parent.spinBoxNotch60QFactor
            ],
            self.parent.checkBoxBandPass: [
                self.parent.spinBoxBandPassLowCutoff,
                self.parent.spinBoxBandPassHighCutoff,
                self.parent.spinBoxBandPassOrder
            ],
            self.parent.checkBoxMedian: [
                self.parent.spinBoxMedianWindowSize
            ],
            self.parent.checkBoxMovingAverage: [
                self.parent.spinBoxMovingAverageWindowSize
            ]
        }
        
        widgets_to_enable = widget_groups.get(checkbox, [])
        self.toggle_widgets_enabled(widgets_to_enable, checked)
        
        # Actualizar configuración
        self.update_configuration()
    
    def toggle_widgets_enabled(self, widgets, enabled):
        """
        Habilita o deshabilita una lista de widgets
        
        Args:
            widgets: Lista de widgets a modificar
            enabled: True para habilitar, False para deshabilitar
        """
        for widget in widgets:
            widget.setEnabled(enabled)
    
    def update_configuration(self):
        """
        Actualiza y emite la configuración basada en los valores actuales de los widgets.
        
        Returns:
            dict: Diccionario de configuración generado
        """
        config = {}
        fs = self.parent.spinBoxSamplingFrequency.value()
        
        # HighPass Filter
        if self.parent.checkBoxHighPass.isChecked():
            config["highpass"] = {
                "cutoff": self.parent.spinBoxHighPassCutoff.value(),
                "order": self.parent.spinBoxHighPassOrder.value()
            }
        
        # LowPass Filter
        if self.parent.checkBoxLowPass.isChecked():
            config["lowpass"] = {
                "cutoff": self.parent.spinBoxLowPassCutoff.value(),
                "order": self.parent.spinBoxLowPassOrder.value()
            }
        
        # Notch 50Hz Filter
        if self.parent.checkBoxNotch50.isChecked():
            config["notch50"] = {
                "frequency": self.parent.spinBoxNotch50Frequency.value(),
                "q_factor": self.parent.spinBoxNotch50QFactor.value()
            }
        
        # Notch 60Hz Filter
        if self.parent.checkBoxNotch60.isChecked():
            config["notch60"] = {
                "frequency": self.parent.spinBoxNotch60Frequency.value(),
                "q_factor": self.parent.spinBoxNotch60QFactor.value()
            }
        
        # BandPass Filter
        if self.parent.checkBoxBandPass.isChecked():
            config["bandpass"] = {
                "low_cutoff": self.parent.spinBoxBandPassLowCutoff.value(),
                "high_cutoff": self.parent.spinBoxBandPassHighCutoff.value(),
                "order": self.parent.spinBoxBandPassOrder.value()
            }
        
        # Median Filter
        if self.parent.checkBoxMedian.isChecked():
            config["median"] = {
                "window_size": self.parent.spinBoxMedianWindowSize.value()
            }
        
        # Moving Average Filter
        if self.parent.checkBoxMovingAverage.isChecked():
            config["movingaverage"] = {
                "window_size": self.parent.spinBoxMovingAverageWindowSize.value()
            }
        
        # Emitir la señal con la configuración actualizada
        self.configurationChanged.emit(config)
        
        # Aquí llamamos a la función filters_params para actualizar los filtros
        self.filters_params(config)
        
        return config
    
    def filters_params(self, config):
        """
        Procesa el diccionario de configuración para actualizar los filtros.
        Este método se llama automáticamente cada vez que cambia algún parámetro.
        
        Args:
            config: Diccionario de configuración de filtros
        """
        # Aquí implementa la lógica para procesar la configuración y actualizar los filtros
        #print("Actualización automática de filtros:")
        #print(config)
        
        # Ejemplo: actualizar la instancia de FILTERS si existe en el parent
        if hasattr(self.parent, 'filters'):
            fs = self.parent.spinBoxSamplingFrequency.value()
            self.parent.filters.set_param(config)
            # Si fs ha cambiado, actualizar también
            # self.parent.filters.fs = fs
    
    def set_configuration(self, config, fs=1000):
        """
        Establece la configuración de los widgets a partir de un diccionario.
        
        Args:
            config: Diccionario de configuración
            fs: Frecuencia de muestreo
        """
        # Desconectar temporalmente las señales para evitar actualizaciones durante la configuración
        self.disconnect_all_signals()
        
        # Establecer frecuencia de muestreo
        self.parent.spinBoxSamplingFrequency.setValue(fs)
        
        # Resetear todos los checkboxes primero
        checkboxes = [
            self.parent.checkBoxHighPass,
            self.parent.checkBoxLowPass,
            self.parent.checkBoxNotch50,
            self.parent.checkBoxNotch60,
            self.parent.checkBoxBandPass,
            self.parent.checkBoxMedian,
            self.parent.checkBoxMovingAverage
        ]
        
        for checkbox in checkboxes:
            checkbox.setChecked(False)
        
        # Configurar HighPass
        if "highpass" in config:
            self.parent.checkBoxHighPass.setChecked(True)
            self.parent.spinBoxHighPassCutoff.setValue(config["highpass"].get("cutoff", 0.5))
            self.parent.spinBoxHighPassOrder.setValue(config["highpass"].get("order", 4))
        
        # Configurar LowPass
        if "lowpass" in config:
            self.parent.checkBoxLowPass.setChecked(True)
            self.parent.spinBoxLowPassCutoff.setValue(config["lowpass"].get("cutoff", 100))
            self.parent.spinBoxLowPassOrder.setValue(config["lowpass"].get("order", 4))
        
        # Configurar Notch 50Hz
        if "notch50" in config:
            self.parent.checkBoxNotch50.setChecked(True)
            self.parent.spinBoxNotch50Frequency.setValue(config["notch50"].get("frequency", 50))
            self.parent.spinBoxNotch50QFactor.setValue(config["notch50"].get("q_factor", 30))
        
        # Configurar Notch 60Hz
        if "notch60" in config:
            self.parent.checkBoxNotch60.setChecked(True)
            self.parent.spinBoxNotch60Frequency.setValue(config["notch60"].get("frequency", 60))
            self.parent.spinBoxNotch60QFactor.setValue(config["notch60"].get("q_factor", 30))
        
        # Configurar BandPass
        if "bandpass" in config:
            self.parent.checkBoxBandPass.setChecked(True)
            self.parent.spinBoxBandPassLowCutoff.setValue(config["bandpass"].get("low_cutoff", 1))
            self.parent.spinBoxBandPassHighCutoff.setValue(config["bandpass"].get("high_cutoff", 40))
            self.parent.spinBoxBandPassOrder.setValue(config["bandpass"].get("order", 4))
        
        # Configurar Median
        if "median" in config:
            self.parent.checkBoxMedian.setChecked(True)
            self.parent.spinBoxMedianWindowSize.setValue(config["median"].get("window_size", 5))
        
        # Configurar MovingAverage
        if "movingaverage" in config:
            self.parent.checkBoxMovingAverage.setChecked(True)
            self.parent.spinBoxMovingAverageWindowSize.setValue(config["movingaverage"].get("window_size", 5))
        
        # Reconectar todas las señales
        self.connect_all_signals()
        
        # Actualizar la configuración después de establecer todos los valores
        self.update_configuration()
    
    def disconnect_all_signals(self):
        """Desconecta temporalmente todas las señales para evitar actualizaciones múltiples"""
        # Esta es una versión simplificada para Qt
        # En PySide6, puedes usar blockSignals para cada widget en lugar de desconectar
        
        # Lista de todos los widgets a bloquear
        all_widgets = [
            self.parent.checkBoxHighPass,
            self.parent.checkBoxLowPass,
            self.parent.checkBoxNotch50,
            self.parent.checkBoxNotch60,
            self.parent.checkBoxBandPass,
            self.parent.checkBoxMedian,
            self.parent.checkBoxMovingAverage,
            self.parent.spinBoxHighPassCutoff,
            self.parent.spinBoxHighPassOrder,
            self.parent.spinBoxLowPassCutoff,
            self.parent.spinBoxLowPassOrder,
            self.parent.spinBoxNotch50Frequency,
            self.parent.spinBoxNotch50QFactor,
            self.parent.spinBoxNotch60Frequency,
            self.parent.spinBoxNotch60QFactor,
            self.parent.spinBoxBandPassLowCutoff,
            self.parent.spinBoxBandPassHighCutoff,
            self.parent.spinBoxBandPassOrder,
            self.parent.spinBoxMedianWindowSize,
            self.parent.spinBoxMovingAverageWindowSize,
            self.parent.spinBoxSamplingFrequency
        ]
        
        # Bloquear señales de todos los widgets
        for widget in all_widgets:
            widget.blockSignals(True)