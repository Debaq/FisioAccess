import numpy as np

class ABR_Simulator:
    def __init__(self, sample_rate=20000, duration=12):
        self.sample_rate = sample_rate
        self.duration = duration  # en milisegundos
        self.time = np.linspace(0, duration / 1000, int(duration * sample_rate / 1000))
        
        # Parámetros de las ondas I-V (amplitudes en nV)
        self.wave_params = [
            {'latency': 1.5, 'amplitude': 150},  # Onda I
            {'latency': 2.5, 'amplitude': 100},  # Onda II
            {'latency': 3.5, 'amplitude': 200},  # Onda III
            {'latency': 4.5, 'amplitude': 150},  # Onda IV
            {'latency': 5.5, 'amplitude': 300},  # Onda V
        ]
        
        self.noise_level = 50  # nV de ruido

    def generate_single_response(self):
        waveform = np.zeros_like(self.time)
        for wave in self.wave_params:
            waveform += wave['amplitude'] * np.exp(-((self.time - wave['latency'] / 1000) ** 2) / (0.0002 ** 2))
        
        # Añadir ruido
        noise = np.random.normal(0, self.noise_level, len(self.time))
        return waveform + noise

    def generate_averaged_response(self, num_averages=2000):
        averaged_response = np.zeros_like(self.time)
        for _ in range(num_averages):
            averaged_response += self.generate_single_response()
        return averaged_response / num_averages