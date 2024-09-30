import math
import random
import numpy as np

class ECG_Simulator:
    def __init__(self, heart_rate=60, use_pacemaker=False, p_wave=0.25,
                 qrs_complex=1.0, t_wave=0.35, noise_level=0.05,
                 noise_amplitude=0.005):
        self.set_heart_rate(heart_rate)
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

        # Pre-calcular valores para mejorar el rendimiento
        self.t = 0
        self.pre_calc_size = 10000
        self.pre_calc_t = np.linspace(0, self.interval, self.pre_calc_size)
        self.pre_calc_p = self._generate_p_wave(self.pre_calc_t)
        self.pre_calc_qrs = self._generate_qrs_complex(self.pre_calc_t)
        self.pre_calc_t_wave = self._generate_t_wave(self.pre_calc_t)

        # Configuración de ruido
        self.noise_level = noise_level
        self.noise_amplitude = noise_amplitude

    def set_heart_rate(self, bpm):
        self.heart_rate = bpm
        self.interval = 60.0 / bpm
        self.frequency = 1 / self.interval

    def _generate_p_wave(self, t):
        return (self.p_wave * np.exp(-((t - 0.1 * self.interval) ** 2) / (0.002 * self.interval ** 2)))

    def _generate_qrs_complex(self, t):
        t_shift = (self.pr_interval + 0.04) * self.interval
        return (self.qrs_complex * np.exp(-((t - t_shift) ** 2) / (0.0002 * self.interval ** 2)))

    def _generate_t_wave(self, t):
        t_shift = (self.pr_interval + self.st_segment + 0.2) * self.interval
        return (self.t_wave * np.exp(-((t - t_shift) ** 2) / (0.006 * self.interval ** 2)))

    def generate_noise(self):
        return np.random.normal(0, self.noise_amplitude)

    def get_next_value(self):
        t_relative = (self.t % self.interval) / self.interval
        index = int(t_relative * self.pre_calc_size)

        value = (self.pre_calc_p[index] + 
                 self.pre_calc_qrs[index] + 
                 self.pre_calc_t_wave[index])

        if self.use_pacemaker:
            if self.t - self.last_pacemaker_pulse >= self.interval:
                pacemaker_pulse = self.pacemaker_amplitude * np.exp(
                    -((t_relative - 0.05) ** 2) / 0.00001
                )
                value += pacemaker_pulse
                self.last_pacemaker_pulse = self.t

        value += self.generate_noise()

        self.t += 0.01
        return value