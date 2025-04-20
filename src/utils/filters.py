import numpy as np
from scipy import signal
from scipy.ndimage import median_filter
from collections import deque
from abc import ABC, abstractmethod

# Clase base que define la interfaz común para todos los filtros
class Filter(ABC):
    @abstractmethod
    def configure(self, **kwargs):
        """Configura los parámetros del filtro"""
        pass
    
    @abstractmethod
    def process(self, data):
        """Procesa los datos utilizando el filtro"""
        pass
    
    @abstractmethod
    def process_sample(self, sample):
        """Procesa una muestra individual"""
        pass
    
    # Métodos de utilidad para las subclases que usan coeficientes IIR
    def _safe_process_iir(self, data, b, a, zi):
        """Método seguro para procesar datos con filtros IIR"""
        try:
            # Verificar si zi está en un rango razonable
            if np.any(np.abs(zi) > 1e6):
                # Reiniciar zi si se ha vuelto muy grande
                zi = signal.lfilter_zi(b, a)
            
            # Usar un factor de escala pequeño y seguro
            filtered_data, new_zi = signal.lfilter(b, a, data, zi=zi * 0.1)
            return filtered_data, new_zi
        except Exception as e:
            # En caso de fallo, reiniciar el estado y procesar sin estado inicial
            print(f"Error en filtro IIR: {e}, reiniciando estado")
            zi = signal.lfilter_zi(b, a)
            filtered_data = signal.lfilter(b, a, data)
            return filtered_data, zi
    
    def _safe_process_sample_iir(self, sample, b, a, zi):
        """Método seguro para procesar una muestra con filtros IIR"""
        try:
            # Verificar si zi está en un rango razonable
            if np.any(np.abs(zi) > 1e6):
                # Reiniciar zi si se ha vuelto muy grande
                zi = signal.lfilter_zi(b, a)
            
            # Procesar una única muestra
            filtered_sample, new_zi = signal.lfilter(b, a, [sample], zi=zi)
            return filtered_sample[0], new_zi
        except Exception as e:
            # En caso de fallo, reiniciar el estado y procesar sin estado inicial
            print(f"Error en filtro IIR (muestra): {e}, reiniciando estado")
            zi = signal.lfilter_zi(b, a)
            filtered_sample = signal.lfilter(b, a, [sample])
            return filtered_sample[0], zi

# Implementación de filtros específicos
class HighPassFilter(Filter):
    def __init__(self):
        self.cutoff = 0.5  # Valor predeterminado
        self.order = 4     # Valor predeterminado
        self.fs = 1000     # Frecuencia de muestreo predeterminada
        self.b = None
        self.a = None
        self.zi = None     # Estado interno del filtro
    
    def configure(self, **kwargs):
        self.cutoff = kwargs.get('cutoff', self.cutoff)
        self.order = kwargs.get('order', self.order)
        self.fs = kwargs.get('fs', self.fs)
        
        # Diseñar el filtro
        self.b, self.a = signal.butter(self.order, self.cutoff/(self.fs/2), 'high')
        self.zi = signal.lfilter_zi(self.b, self.a)
    
    def process(self, data):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_data, self.zi = self._safe_process_iir(data, self.b, self.a, self.zi)
        return filtered_data
    
    def process_sample(self, sample):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_sample, self.zi = self._safe_process_sample_iir(sample, self.b, self.a, self.zi)
        return filtered_sample

class LowPassFilter(Filter):
    def __init__(self):
        self.cutoff = 100.0  # Valor predeterminado
        self.order = 4        # Valor predeterminado
        self.fs = 1000        # Frecuencia de muestreo predeterminada
        self.b = None
        self.a = None
        self.zi = None        # Estado interno del filtro
    
    def configure(self, **kwargs):
        self.cutoff = kwargs.get('cutoff', self.cutoff)
        self.order = kwargs.get('order', self.order)
        self.fs = kwargs.get('fs', self.fs)
        
        # Diseñar el filtro
        self.b, self.a = signal.butter(self.order, self.cutoff/(self.fs/2), 'low')
        self.zi = signal.lfilter_zi(self.b, self.a)
    
    def process(self, data):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_data, self.zi = self._safe_process_iir(data, self.b, self.a, self.zi)
        return filtered_data
    
    def process_sample(self, sample):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_sample, self.zi = self._safe_process_sample_iir(sample, self.b, self.a, self.zi)
        return filtered_sample

class NotchFilter(Filter):
    def __init__(self):
        self.frequency = 50.0  # Valor predeterminado (Hz)
        self.q_factor = 30.0   # Valor predeterminado
        self.fs = 1000         # Frecuencia de muestreo predeterminada
        self.b = None
        self.a = None
        self.zi = None         # Estado interno del filtro
    
    def configure(self, **kwargs):
        self.frequency = kwargs.get('frequency', self.frequency)
        self.q_factor = kwargs.get('q_factor', self.q_factor)
        self.fs = kwargs.get('fs', self.fs)
        
        # Diseñar el filtro notch
        w0 = self.frequency / (self.fs/2)
        self.b, self.a = signal.iirnotch(w0, self.q_factor)
        self.zi = signal.lfilter_zi(self.b, self.a)
    
    def process(self, data):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_data, self.zi = self._safe_process_iir(data, self.b, self.a, self.zi)
        return filtered_data
    
    def process_sample(self, sample):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_sample, self.zi = self._safe_process_sample_iir(sample, self.b, self.a, self.zi)
        return filtered_sample

class BandPassFilter(Filter):
    def __init__(self):
        self.low_cutoff = 1.0    # Valor predeterminado (Hz)
        self.high_cutoff = 40.0  # Valor predeterminado (Hz)
        self.order = 4           # Valor predeterminado
        self.fs = 1000           # Frecuencia de muestreo predeterminada
        self.b = None
        self.a = None
        self.zi = None           # Estado interno del filtro
    
    def configure(self, **kwargs):
        self.low_cutoff = kwargs.get('low_cutoff', self.low_cutoff)
        self.high_cutoff = kwargs.get('high_cutoff', self.high_cutoff)
        self.order = kwargs.get('order', self.order)
        self.fs = kwargs.get('fs', self.fs)
        
        # Verificar que los valores son válidos
        if self.high_cutoff <= self.low_cutoff:
            raise ValueError("La frecuencia de corte superior debe ser mayor que la inferior")
        
        # Diseñar el filtro
        nyq = 0.5 * self.fs
        low = self.low_cutoff / nyq
        high = self.high_cutoff / nyq
        self.b, self.a = signal.butter(self.order, [low, high], btype='band')
        self.zi = signal.lfilter_zi(self.b, self.a)
    
    def process(self, data):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_data, self.zi = self._safe_process_iir(data, self.b, self.a, self.zi)
        return filtered_data
    
    def process_sample(self, sample):
        if self.b is None or self.a is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        # Usar el método seguro de la clase base
        filtered_sample, self.zi = self._safe_process_sample_iir(sample, self.b, self.a, self.zi)
        return filtered_sample

class MedianFilter(Filter):
    def __init__(self):
        self.window_size = 5  # Valor predeterminado (muestras)
        self.buffer = None
    
    def configure(self, **kwargs):
        self.window_size = kwargs.get('window_size', self.window_size)
        
        # Verificar que el tamaño de ventana es válido
        if self.window_size < 1 or self.window_size % 2 == 0:
            raise ValueError("El tamaño de ventana debe ser un número impar y positivo")
        
        # Para process_sample necesitamos mantener un buffer circular
        self.buffer = deque(maxlen=self.window_size)
        
    def process(self, data):
        if self.window_size is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        try:
            # Usar la función median_filter de scipy para procesamiento por lotes
            filtered_data = median_filter(data, size=self.window_size)
            
            # Actualizar el buffer con las últimas muestras para mantener continuidad
            if len(data) >= self.window_size:
                self.buffer = deque(data[-self.window_size:], maxlen=self.window_size)
            else:
                # Si los datos son muy cortos, solo tomamos lo que podamos
                self.buffer.clear()
                for sample in data:
                    self.buffer.append(sample)
            
            return filtered_data
            
        except Exception as e:
            print(f"Error en filtro de mediana: {e}")
            # En caso de error, devolver los datos originales
            self.buffer = deque(maxlen=self.window_size)
            return data
    
    def process_sample(self, sample):
        if self.buffer is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        try:
            # Añadir la nueva muestra al buffer
            self.buffer.append(sample)
            
            # Si el buffer no está lleno, devolvemos la muestra original
            if len(self.buffer) < self.window_size:
                return sample
            
            # Calcular la mediana del buffer actual
            return np.median(list(self.buffer))
            
        except Exception as e:
            print(f"Error en filtro de mediana (muestra): {e}")
            # En caso de error, reiniciar buffer y devolver la muestra original
            self.buffer = deque(maxlen=self.window_size)
            self.buffer.append(sample)
            return sample

class MovingAverageFilter(Filter):
    def __init__(self):
        self.window_size = 5  # Valor predeterminado (muestras)
        self.buffer = None
        self.sum = 0
    
    def configure(self, **kwargs):
        self.window_size = kwargs.get('window_size', self.window_size)
        
        # Verificar que el tamaño de ventana es válido
        if self.window_size < 1:
            raise ValueError("El tamaño de ventana debe ser positivo")
        
        # Para process_sample necesitamos mantener un buffer circular
        self.buffer = deque(maxlen=self.window_size)
        self.sum = 0
    
    def process(self, data):
        if self.buffer is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        try:
            # Para procesar un lote completo, usamos convolución con núcleo uniforme
            kernel = np.ones(self.window_size) / self.window_size
            filtered_data = np.convolve(data, kernel, mode='same')
            
            # Actualizar el buffer con las últimas muestras para mantener continuidad
            if len(data) >= self.window_size:
                self.buffer = deque(data[-self.window_size:], maxlen=self.window_size)
                self.sum = sum(self.buffer)
            else:
                # Si los datos son muy cortos, solo tomamos lo que podamos
                self.buffer.clear()
                self.sum = 0
                for sample in data:
                    self.buffer.append(sample)
                    self.sum += sample
            
            return filtered_data
            
        except Exception as e:
            print(f"Error en filtro de media móvil: {e}")
            # En caso de error, intentar un enfoque más simple
            self.buffer.clear()
            self.sum = 0
            # Devolver los datos originales
            return data
    
    def process_sample(self, sample):
        if self.buffer is None:
            raise ValueError("El filtro debe ser configurado antes de procesar datos")
        
        try:
            # Si el buffer está lleno, restamos el valor que sale
            if len(self.buffer) == self.window_size:
                self.sum -= self.buffer[0]
            
            # Añadir la nueva muestra al buffer y a la suma
            self.buffer.append(sample)
            self.sum += sample
            
            # Calcular el promedio
            return self.sum / len(self.buffer)
            
        except Exception as e:
            print(f"Error en filtro de media móvil (muestra): {e}")
            # En caso de error, reiniciar buffer y devolver la muestra original
            self.buffer.clear()
            self.sum = 0
            self.buffer.append(sample)
            self.sum = sample
            return sample

# Clase gestora de filtros
class FILTERS:
    def __init__(self, fs=1000):
        self.fs = fs  # Frecuencia de muestreo
        self.filter_mapping = {
            'highpass': HighPassFilter(),
            'lowpass': LowPassFilter(),
            'notch50': NotchFilter(),
            'notch60': NotchFilter(),
            'bandpass': BandPassFilter(),
            'median': MedianFilter(),
            'movingaverage': MovingAverageFilter()
        }
        self.active_filters = []  # Lista para mantener el orden de los filtros
    
    def set_param(self, configuracion):
        """Configura los filtros según el diccionario proporcionado"""
        self.active_filters = []  # Reiniciar filtros activos
        
        # Configurar cada filtro especificado
        for filter_name, params in configuracion.items():
            if filter_name in self.filter_mapping:
                # Caso especial para notch60
                if filter_name == 'notch60' and 'frequency' not in params:
                    params['frequency'] = 60.0
                
                # Agregar frecuencia de muestreo a los parámetros
                params['fs'] = self.fs
                
                # Configurar el filtro
                filtro = self.filter_mapping[filter_name]
                filtro.configure(**params)
                
                # Añadir a la lista de filtros activos
                self.active_filters.append(filtro)
    
    def filtrar(self, datos_raw):
        """Aplica todos los filtros activos a los datos en orden"""
        datos = np.array(datos_raw)  # Convertir a numpy array si no lo es
        
        # Aplicar cada filtro en secuencia
        for filtro in self.active_filters:
            datos = filtro.process(datos)
        
        return datos
    
    def filtrar_muestra(self, muestra):
        """Aplica todos los filtros activos a una única muestra"""
        dato = muestra
        
        # Aplicar cada filtro en secuencia
        for filtro in self.active_filters:
            dato = filtro.process_sample(dato)
        
        return dato

# Ejemplo de uso
if __name__ == "__main__":
    # Crear datos de prueba (simulación de una señal ECG)
    fs = 1000  # Frecuencia de muestreo de 1000 Hz
    t = np.arange(0, 10, 1.0/fs)  # 10 segundos de datos
    # Señal base (simulación simplificada de ECG)
    data = np.sin(2 * np.pi * 1.0 * t)  # Componente de 1 Hz
    # Agregar ruido
    noise_50hz = 0.5 * np.sin(2 * np.pi * 50.0 * t)  # Ruido de 50 Hz (línea eléctrica)
    noise_highfreq = 0.2 * np.random.randn(len(t))   # Ruido de alta frecuencia
    data_raw = data + noise_50hz + noise_highfreq
    
    # Crear gestor de filtros
    filtro = FILTERS(fs=fs)
    
    # Configurar filtros
    configuracion = {
        "highpass": {"cutoff": 0.5, "order": 2},
        "notch50": {"frequency": 50.0, "q_factor": 30},
        "bandpass": {"low_cutoff": 1.0, "high_cutoff": 40.0, "order": 4},
        "median": {"window_size": 5},
        "movingaverage": {"window_size": 9}
    }
    
    # Aplicar configuración
    filtro.set_param(configuracion)
    
    # Filtrar datos
    datos_filtrados = filtro.filtrar(data_raw)
    
    print(f"Forma de los datos originales: {data_raw.shape}")
    print(f"Forma de los datos filtrados: {datos_filtrados.shape}")
    print("Filtros aplicados:", [type(f).__name__ for f in filtro.active_filters])