# FisioAccess - ESP32-C3 SuperMini Multisensor

## Descripción General

FisioAccess es un sistema de adquisición de datos basado en el ESP32-C3 SuperMini que permite la lectura y transmisión de múltiples sensores. Diseñado para aplicaciones de monitoreo biomédico y fisioterapia, el dispositivo facilita la captura de señales analógicas y digitales a través de diversos protocolos de comunicación.

## Características Principales

- **Múltiples Interfaces**: Soporta conexiones analógicas directas, I2C, SPI y seriales
- **Conectividad Inalámbrica**: WiFi y ESP-NOW para transmisión de datos
- **Streaming de Datos**: Envío continuo de lecturas a intervalos configurables
- **Control por Comandos JSON**: Interfaz de control simple mediante comandos JSON a través del puerto serial
- **Configuración Persistente**: Guarda la configuración en memoria EEPROM
- **Soporte para ADS1115**: Conversor analógico-digital de precisión integrado

## Requisitos de Hardware

- ESP32-C3 SuperMini (o compatible)
- Convertidor ADS1115 (opcional para mayor precisión en lecturas analógicas)
- Sensores compatibles con interfaces analógicas, I2C o SPI según necesidad
- Conexión USB para alimentación y comunicación inicial

## Instalación y Configuración

1. Carga el firmware en el ESP32-C3 utilizando el IDE de Arduino o PlatformIO
2. Conecta el dispositivo a tu computadora mediante USB
3. Abre un monitor serial a 115200 baudios
4. Envía comandos JSON para configurar el dispositivo según tus necesidades

## Comandos Principales

Todos los comandos deben enviarse en formato JSON seguidos de un salto de línea (`\n`). El dispositivo responderá con otro objeto JSON.

### Comandos Básicos

```json
{"cmd": "single_read"}             // Solicita una lectura única de todos los sensores
{"cmd": "start_stream"}            // Inicia el streaming continuo de datos
{"cmd": "stop_stream"}             // Detiene el streaming
{"cmd": "set_sample_rate", "interval": 100}  // Configura el intervalo de muestreo (en ms)
```

### Configuración WiFi

```json
{"cmd": "wifi_connect", "ssid": "nombre_red", "password": "clave_wifi"}  // Conecta a una red WiFi
{"cmd": "wifi_disconnect"}         // Desconecta de la red WiFi
{"cmd": "wifi_ap_start"}           // Inicia modo punto de acceso
{"cmd": "wifi_ap_stop"}            // Detiene modo punto de acceso
```

### Comandos de Sistema

```json
{"cmd": "scan_i2c"}                // Escanea dispositivos I2C conectados
{"cmd": "get_status"}              // Obtiene información del estado del sistema
{"cmd": "set_name", "name": "mi_sensor_ecg"}  // Cambia el nombre del dispositivo
{"cmd": "reset"}                   // Reinicia el dispositivo
```

### Comunicación ESP-NOW (dispositivo a dispositivo)

```json
{"cmd": "espnow_init"}             // Inicializa ESP-NOW
{"cmd": "espnow_pair", "mac": "AA:BB:CC:DD:EE:FF"}  // Empareja con otro dispositivo
{"cmd": "espnow_send", "mac": "AA:BB:CC:DD:EE:FF", "data": "mensaje"}  // Envía datos
```

## Formato de Datos

Al solicitar una lectura o durante el streaming, el dispositivo envía un objeto JSON completo con todos los datos disponibles, similar a:

```json
{
  "timestamp": 12345,
  "analog": {
    "gpio2": 2048,
    "gpio3": 1024,
    "gpio4": 3072
  },
  "i2c": {
    "ads1115": {
      "a0": 12345,
      "a1": 23456,
      "a2": 34567,
      "a3": 45678
    }
  },
  "spi": {
    "device1": {
      "register1": 123,
      "register2": 456
    }
  },
  "wifi": {
    "status": "connected",
    "ssid": "Red_Actual",
    "ip": "192.168.1.100",
    "rssi": -65
  },
  "status": {
    "device_id": "AABBCCDDEEFF",
    "device_name": "ESP32_EEFF",
    "uptime": 3600,
    "firmware": "1.0.0",
    "free_memory": 230000,
    "cpu_freq": 160,
    "temperature": 42.5
  }
}
```

## Casos de Uso Comunes

### Adquisición de Datos Biomédicos
1. Conecta sensores analógicos al ESP32 o al ADS1115
2. Configura el intervalo de muestreo según la señal a capturar
3. Inicia el streaming de datos
4. Procesa los datos recibidos en tu aplicación

### Monitoreo Remoto
1. Configura la conexión WiFi del dispositivo
2. Establece la comunicación entre el dispositivo y tu servidor
3. Utiliza el streaming continuo para monitorear en tiempo real

### Red de Sensores
1. Configura varios dispositivos FisioAccess
2. Utiliza ESP-NOW para comunicación directa entre ellos
3. Establece un dispositivo como coordinador para recopilar datos

## Solución de Problemas

- **El dispositivo no responde**: Verifica la conexión USB y que estés utilizando 115200 baudios
- **Error en comandos**: Asegúrate de enviar JSON válido terminado con `\n`
- **No se detectan sensores I2C**: Ejecuta `{"cmd": "scan_i2c"}` para verificar conexiones
- **Fallo en conexión WiFi**: Verifica las credenciales y la disponibilidad de la red

## Desarrollo Avanzado

El firmware está desarrollado en Arduino y puede ser modificado para:
- Añadir soporte para sensores adicionales
- Implementar protocolos de comunicación personalizados
- Optimizar el consumo energético para aplicaciones portátiles
- Integrar algoritmos de procesamiento de señales en el dispositivo

## Licencia

Este proyecto se distribuye bajo licencia de código abierto. Consulta el archivo LICENSE para más detalles.

---

Para más información y documentación detallada, consulta la [documentación de comandos completa](Fisioaccess-commands-docs.md).
