# FisioAccess - Documentación de Comandos

## Introducción

Este documento detalla todos los comandos disponibles para controlar el ESP32-C3 SuperMini Multisensor. El dispositivo utiliza un sistema de comandos basado en JSON a través del puerto serial, lo que permite una configuración y control flexibles.

Todos los comandos deben enviarse en formato JSON terminados con un salto de línea (`\n`). El dispositivo responderá con otro objeto JSON que incluirá el resultado o los datos solicitados.

## Formato de Comandos

```json
{
  "cmd": "nombre_del_comando",
  "param1": "valor1",
  "param2": "valor2"
}
```

## Obtención de Datos

### Lectura Única

**Comando:**
```json
{"cmd": "single_read"}
```

**Descripción:** Realiza una única lectura de todos los sensores conectados y devuelve un objeto JSON completo con todos los datos.

**Respuesta:** Un objeto JSON que contiene datos de todos los sensores disponibles, estado del sistema, configuración WiFi, etc.

### Streaming de Datos

**Comando para iniciar:**
```json
{"cmd": "start_stream"}
```

**Descripción:** Inicia el envío continuo de datos JSON a intervalos regulares.

**Comando para detener:**
```json
{"cmd": "stop_stream"}
```

**Descripción:** Detiene el envío continuo de datos.

**Configuración del intervalo:**
```json
{"cmd": "set_sample_rate", "interval": 100}
```

**Descripción:** Configura el intervalo de muestreo en milisegundos para el streaming de datos.
**Parámetros:**
- `interval`: Intervalo en milisegundos entre cada envío de datos (ej. 100ms)

## Escaneo de Hardware

### Escaneo I2C

**Comando:**
```json
{"cmd": "scan_i2c"}
```

**Descripción:** Escanea el bus I2C para detectar dispositivos conectados.

**Respuesta:**
```json
{
  "cmd_received": true,
  "cmd": "scan_i2c",
  "result": "I2C scan completed",
  "ads1115_found": true
}
```

## Configuración WiFi

### Conectar a una Red WiFi

**Comando:**
```json
{"cmd": "wifi_connect", "ssid": "nombre_red", "password": "clave_wifi"}
```

**Descripción:** Conecta el ESP32 a una red WiFi específica.
**Parámetros:**
- `ssid`: Nombre de la red WiFi
- `password`: Contraseña de la red WiFi

**Respuesta:**
```json
{
  "cmd_received": true,
  "cmd": "wifi_connect",
  "result": "Connected to WiFi",
  "ip": "192.168.1.100"
}
```

### Desconectar WiFi

**Comando:**
```json
{"cmd": "wifi_disconnect"}
```

**Descripción:** Desconecta el ESP32 de la red WiFi actual.

### Iniciar Punto de Acceso

**Comando:**
```json
{"cmd": "wifi_ap_start"}
```

**Descripción:** Inicia el modo punto de acceso WiFi.

**Respuesta:**
```json
{
  "cmd_received": true,
  "cmd": "wifi_ap_start",
  "result": "AP started",
  "ip": "192.168.4.1"
}
```

### Detener Punto de Acceso

**Comando:**
```json
{"cmd": "wifi_ap_stop"}
```

**Descripción:** Detiene el modo punto de acceso WiFi.

## Configuración ESP-NOW

### Inicializar ESP-NOW

**Comando:**
```json
{"cmd": "espnow_init"}
```

**Descripción:** Inicializa la funcionalidad ESP-NOW para comunicación de bajo consumo entre dispositivos ESP32.

### Emparejar Dispositivo ESP-NOW

**Comando:**
```json
{"cmd": "espnow_pair", "mac": "AA:BB:CC:DD:EE:FF"}
```

**Descripción:** Añade un dispositivo para comunicación ESP-NOW.
**Parámetros:**
- `mac`: Dirección MAC del dispositivo a emparejar en formato XX:XX:XX:XX:XX:XX

### Enviar Mensaje ESP-NOW

**Comando:**
```json
{"cmd": "espnow_send", "mac": "AA:BB:CC:DD:EE:FF", "data": "mensaje"}
```

**Descripción:** Envía datos a un dispositivo ESP-NOW emparejado.
**Parámetros:**
- `mac`: Dirección MAC del dispositivo destino
- `data`: Mensaje a enviar (máximo 250 bytes)

## Comandos de Sistema

### Obtener Estado

**Comando:**
```json
{"cmd": "get_status"}
```

**Descripción:** Obtiene información detallada sobre el estado del sistema.

**Respuesta:**
```json
{
  "cmd_received": true,
  "cmd": "get_status",
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

### Cambiar Nombre del Dispositivo

**Comando:**
```json
{"cmd": "set_name", "name": "mi_sensor_ecg"}
```

**Descripción:** Cambia el nombre del dispositivo.
**Parámetros:**
- `name`: Nuevo nombre para el dispositivo (máximo 31 caracteres)

### Reiniciar Dispositivo

**Comando:**
```json
{"cmd": "reset"}
```

**Descripción:** Reinicia el ESP32 completamente.

## Formato de Respuesta JSON

El dispositivo responde a todos los comandos (excepto `single_read`) con un objeto JSON que incluye al menos:

```json
{
  "cmd_received": true,
  "cmd": "nombre_del_comando",
  "result": "resultado_de_la_operación"
}
```

En caso de error:

```json
{
  "cmd_received": true,
  "error": "descripción_del_error"
}
```

## Estructura JSON de Datos Completa

Cuando se solicita una lectura de datos (mediante `single_read` o durante el streaming), se recibe un objeto JSON con la siguiente estructura:

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
  "serial": {
    "data": "valor recibido por serial",
    "port": "UART1"
  },
  "wifi": {
    "status": "connected",
    "ssid": "Red_Actual",
    "ip": "192.168.1.100",
    "rssi": -65
  },
  "espnow": {
    "status": "active",
    "peers": [
      {"mac": "AA:BB:CC:DD:EE:FF", "name": "sensor2", "rssi": -60}
    ]
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

Si algún sensor o interfaz no está disponible, su valor correspondiente será `null`.
