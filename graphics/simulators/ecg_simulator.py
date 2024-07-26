import math
import random

class ECG_Simulator:
    def __init__(self, heart_rate=60, use_pacemaker=False, p_wave=0.25, qrs_complex=1.0, t_wave=0.35):
        self.t = 0
        self.set_heart_rate(heart_rate)
        self.amplitude = 1.0
        self.noise_level = 0.05
        self.use_pacemaker = use_pacemaker
        self.pacemaker_amplitude = 2.0
        self.last_pacemaker_pulse = -self.interval

        # Componentes de la onda
        self.p_wave = p_wave
        self.qrs_complex = qrs_complex
        self.t_wave = t_wave
        
        # Intervalos y segmentos (en proporción del ciclo cardíaco)
        self.pr_interval = 0.16
        self.st_segment = 0.1

    def set_heart_rate(self, bpm):
        self.heart_rate = bpm
        self.interval = 60.0 / bpm
        self.frequency = 1 / self.interval

    def get_next_value(self):
        t_relative = (self.t % self.interval) / self.interval

        # Onda P
        p = self.p_wave * self.amplitude * math.exp(-((t_relative - 0.1) ** 2) / 0.002)
        
        # Complejo QRS
        qrs = self.qrs_complex * self.amplitude * math.exp(-((t_relative - (self.pr_interval + 0.04)) ** 2) / 0.0002)
        
        # Onda T
        t = self.t_wave * self.amplitude * math.exp(-((t_relative - (self.pr_interval + self.st_segment + 0.2)) ** 2) / 0.006)
        
        value = p + qrs + t

        # Simular marcapasos si está activado
        if self.use_pacemaker:
            if self.t - self.last_pacemaker_pulse >= self.interval:
                # Generar pulso del marcapasos
                value += self.pacemaker_amplitude * math.exp(-((t_relative - 0.05) ** 2) / 0.00001)
                self.last_pacemaker_pulse = self.t

        # Añadir ruido
        noise = random.uniform(-self.noise_level, self.noise_level)
        value += noise

        # Incrementar el tiempo
        self.t += 0.01

        return value