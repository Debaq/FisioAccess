from PySide6.QtCore import QObject, Signal, Slot
import json

class SerialDataHandler(QObject):
    # Señal para datos JSON procesados
    new_data_json = Signal(dict)
    # Señal para respuestas a comandos
    command_response = Signal(dict)
    # Señal para errores y mensajes no JSON
    error_message = Signal(str)
    
    def __init__(self):
        super().__init__()
    
    @Slot(str)
    def analisis_input_serial(self, data_string):
        """Analizar datos recibidos del puerto serial"""
        try:
            # Limpiar el string
            data_string = data_string.strip()
            
            # Intentar parsear como JSON
            try:
                json_data = json.loads(data_string)
            except json.JSONDecodeError:
                # Si no es JSON, emitir como error
                self.error_message.emit(f"Formato inválido (no es JSON): {data_string}")
                return
            
            # Verificar si es una respuesta a comando (tiene cmd_received)
            if 'cmd_received' in json_data:
                print(f"entro un comando {json_data}")
                
                self.command_response.emit(json_data)
                return
            
            # Verificar si es una lectura de datos (tiene timestamp)
            if 'timestamp' in json_data:
                self.new_data_json.emit(json_data)
                return
                
            # Si llegamos aquí, es un JSON que no reconocemos
            self.error_message.emit(f"JSON con formato desconocido: {data_string}")
            
        except Exception as e:
            # Si hay error en el procesamiento
            self.error_message.emit(f"Error procesando: {data_string}, {str(e)}")
    
    def send_command(self, command_dict):
        """
        Prepara un comando para enviar al dispositivo
        
        Args:
            command_dict (dict): Diccionario con el comando a enviar
            
        Returns:
            str: Comando en formato JSON con salto de línea
        """
        try:
            # Convertir diccionario a JSON
            command_json = json.dumps(command_dict)
            # Añadir salto de línea requerido por el dispositivo
            return command_json + "\n"
        except Exception as e:
            self.error_message.emit(f"Error preparando comando: {str(e)}")
            return None