import numpy as np

class DataSimulator:
    def __init__(self, data_type):
        self.data_type = data_type
        self.fs = 1000  # Frecuencia de muestreo (Hz)
        self.t = np.linspace(0, 1.5, int(self.fs * 1.5), endpoint=False)  # Tiempo para un ciclo completo a 40 bpm
        self.ecg_signal = self.generate_ecg_signal()

    def generate_data(self):
        if self.data_type == 'EEG':
            return self.generate_eeg_data()
        elif self.data_type == 'ECG':
            return self.generate_ecg_data()
        elif self.data_type == 'EMG':
            return self.generate_emg_data()
        else:
            return self.generate_random_data()

    def generate_eeg_data(self):
        # Simulación de datos EEG (modificar según las características de los datos reales)
        return np.random.randn(1)

    def generate_ecg_data(self):
        return np.random.choice(self.ecg_signal, 1)

    def generate_emg_data(self):
        # Simulación de datos EMG (modificar según las características de los datos reales)
        return np.random.randn(1)

    def generate_random_data(self):
        return np.random.random(1)

    def generate_ecg_signal(self):
        rr_interval = 60 / 40  # Intervalo RR para 40 bpm (1.5 segundos)
        t = self.t

        # Generar componentes de la señal ECG
        p_wave = 0.1 * np.sin(2 * np.pi * 5 * t) * (t > 0.1) * (t < 0.2)
        q_wave = -0.15 * np.sin(2 * np.pi * 50 * t) * (t > 0.2) * (t < 0.22)
        r_wave = 1.0 * np.sin(2 * np.pi * 100 * t) * (t > 0.22) * (t < 0.24)
        s_wave = -0.25 * np.sin(2 * np.pi * 50 * t) * (t > 0.24) * (t < 0.26)
        t_wave = 0.4 * np.sin(2 * np.pi * 5 * t) * (t > 0.3) * (t < 0.4)

        ecg_signal = p_wave + q_wave + r_wave + s_wave + t_wave
        return ecg_signal
