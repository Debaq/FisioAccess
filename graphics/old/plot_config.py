import matplotlib.pyplot as plt

class PlotConfig:
    def __init__(self, data_type):
        self.data_type = data_type

    def apply_config(self, ax):
        if self.data_type == 'EEG':
            self.configure_eeg(ax)
        elif self.data_type == 'ECG':
            self.configure_ecg(ax)
        elif self.data_type == 'EMG':
            self.configure_emg(ax)
        else:
            self.configure_default(ax)

    def configure_eeg(self, ax):
        # Configuración específica para EEG (modificar según las características de los datos reales)
        ax.set_title('EEG Data')
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Time (s)')
        ax.axhline(0, color='black', linewidth=0.5)  # Línea horizontal en y=0
        ax.set_ylim(-1, 1)  # Rango del eje y

    def configure_ecg(self, ax):
        # Configuración específica para ECG (modificar según las características de los datos reales)
        ax.set_title('ECG Data')
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Time (s)')
        ax.axhline(0, color='black', linewidth=0.5)  # Línea horizontal en y=0
        ax.set_ylim(-1.5, 1.5)  # Rango del eje y

    def configure_emg(self, ax):
        # Configuración específica para EMG (modificar según las características de los datos reales)
        ax.set_title('EMG Data')
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Time (s)')
        ax.axhline(0, color='black', linewidth=0.5)  # Línea horizontal en y=0
        ax.set_ylim(-1, 1)  # Rango del eje y

    def configure_default(self, ax):
        ax.set_title('Random Data')
        ax.set_ylabel('Value')
        ax.set_xlabel('Sample')
        ax.axhline(0, color='black', linewidth=0.5)  # Línea horizontal en y=0
        ax.set_ylim(-1, 1)  # Rango del eje y

    def get_window_size(self):
        if self.data_type == 'EEG':
            return 10  # Ajustar según las necesidades
        elif self.data_type == 'ECG':
            return 200  # 200 segundos para ECG
        elif self.data_type == 'EMG':
            return 10  # Ajustar según las necesidades
        else:
            return 10  # Valor por defecto
