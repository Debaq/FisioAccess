#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <WiFi.h>
#include <esp_now.h>
#include <ArduinoJson.h>
#include <Adafruit_ADS1X15.h>
#include <Update.h>
#include <EEPROM.h>
#include "esp_wifi.h"
#include "esp_log.h"

// Versión del firmware
#define FIRMWARE_VERSION "1.0.0"

// Tamaño del buffer JSON
#define JSON_BUFFER_SIZE 2048

// Intervalo de muestreo por defecto (ms)
#define DEFAULT_SAMPLE_INTERVAL 100

// Tamaño EEPROM
#define EEPROM_SIZE 512

// Estructura para configuración guardada en EEPROM
struct DeviceConfig {
  char deviceName[32];
  char wifiSSID[32];
  char wifiPassword[64];
  uint16_t sampleInterval;
  bool streamingEnabled;
  uint8_t activeSensors;
};

// Estructura para ESP-NOW peers
struct PeerInfo {
  uint8_t mac[6];
  char name[32];
  int8_t rssi;
};

// Objetos globales
Adafruit_ADS1115 ads;  // Objeto para ADS1115

// Variables globales
unsigned long startTime = 0;
unsigned long lastSampleTime = 0;
bool streamingEnabled = false;
uint16_t sampleInterval = DEFAULT_SAMPLE_INTERVAL;
bool adsConnected = false;
bool wifiConnected = false;
bool apActive = false;
bool espNowActive = false;
DeviceConfig config;
char deviceID[13]; // MAC address como ID
PeerInfo peers[20]; // Máximo 20 peers ESP-NOW
int peerCount = 0;

// Buffers para mensajes
char jsonBuffer[JSON_BUFFER_SIZE];
StaticJsonDocument<JSON_BUFFER_SIZE> jsonDoc;
StaticJsonDocument<512> cmdDoc;
char respBuffer[512];

// Función para inicializar hardware
void initHardware() {
  Serial.begin(115200);
  delay(500);
  
  // Inicializar I2C
  Wire.begin();
  
  // Inicializar SPI
  SPI.begin();
  
  // Generar ID desde la dirección MAC
  uint8_t mac[6];
  WiFi.macAddress(mac);
  sprintf(deviceID, "%02X%02X%02X%02X%02X%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  
  // Cargar configuración de EEPROM
  EEPROM.begin(EEPROM_SIZE);
  EEPROM.get(0, config);
  
  // Si la configuración no es válida, establecer valores por defecto
  if (String(config.deviceName).length() == 0 || String(config.deviceName).length() > 31) {
    sprintf(config.deviceName, "ESP32_%s", &deviceID[6]); // Últimos 6 caracteres del MAC
    strcpy(config.wifiSSID, "");
    strcpy(config.wifiPassword, "");
    config.sampleInterval = DEFAULT_SAMPLE_INTERVAL;
    config.streamingEnabled = false;
    config.activeSensors = 0xFF; // Todos activos por defecto
    EEPROM.put(0, config);
    EEPROM.commit();
  }
  
  sampleInterval = config.sampleInterval;
  streamingEnabled = config.streamingEnabled;
  
  // Imprimir info de inicio
  Serial.println("\n\n-----------------------------------------");
  Serial.printf("ESP32-C3 SuperMini Multisensor v%s\n", FIRMWARE_VERSION);
  Serial.printf("Device ID: %s\n", deviceID);
  Serial.printf("Device Name: %s\n", config.deviceName);
  Serial.println("-----------------------------------------\n");
}

// Convertir código de razón de reinicio a cadena descriptiva
const char* getResetReasonString(esp_reset_reason_t reason) {
  switch (reason) {
    case ESP_RST_UNKNOWN:
      return "Desconocida";
    case ESP_RST_POWERON:
      return "Encendido";
    case ESP_RST_EXT:
      return "Reset externo";
    case ESP_RST_SW:
      return "Reset por software";
    case ESP_RST_PANIC:
      return "Excepción/Pánico";
    case ESP_RST_INT_WDT:
      return "Watchdog interno";
    case ESP_RST_TASK_WDT:
      return "Watchdog de tarea";
    case ESP_RST_WDT:
      return "Watchdog";
    case ESP_RST_DEEPSLEEP:
      return "Despertar de sueño profundo";
    case ESP_RST_BROWNOUT:
      return "Brownout";
    case ESP_RST_SDIO:
      return "Reset SDIO";
    default:
      return "Otro";
  }
}

// Función para detectar dispositivos I2C
void scanI2C() {
  Serial.println("Scanning I2C bus...");
  adsConnected = false;
  
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    
    if (error == 0) {
      Serial.printf("I2C device found at address 0x%02X\n", address);
      
      // Detectar ADS1115 (dirección típica 0x48)
      if (address == 0x48) {
        if (ads.begin()) {
          adsConnected = true;
          Serial.println("ADS1115 initialized successfully");
        } else {
          Serial.println("Failed to initialize ADS1115");
        }
      }
    }
  }
  
  if (!adsConnected) {
    Serial.println("ADS1115 not found");
  }
}

// Inicializar WiFi en modo estación
bool initWiFi() {
  if (strlen(config.wifiSSID) == 0) {
    Serial.println("WiFi credentials not configured");
    return false;
  }
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(config.wifiSSID, config.wifiPassword);
  
  Serial.printf("Connecting to WiFi %s", config.wifiSSID);
  
  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected with IP: ");
    Serial.println(WiFi.localIP());
    wifiConnected = true;
    return true;
  } else {
    Serial.println("Failed to connect to WiFi");
    WiFi.disconnect();
    wifiConnected = false;
    return false;
  }
}

// Inicializar WiFi en modo AP
bool startAP() {
  WiFi.mode(WIFI_AP);
  bool result = WiFi.softAP(config.deviceName);
  
  if (result) {
    Serial.print("AP started with IP: ");
    Serial.println(WiFi.softAPIP());
    apActive = true;
  } else {
    Serial.println("Failed to start AP");
    apActive = false;
  }
  
  return result;
}

// Callback cuando se recibe un mensaje ESP-NOW
void onEspNowReceive(const esp_now_recv_info_t *esp_now_info, const uint8_t *data, int len) {
  const uint8_t *mac = esp_now_info->src_addr;
  char macStr[18];
  sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  
  Serial.printf("ESP-NOW message received from %s, %d bytes\n", macStr, len);
  
  // Buscar si el peer ya está registrado
  int peerIndex = -1;
  for (int i = 0; i < peerCount; i++) {
    if (memcmp(peers[i].mac, mac, 6) == 0) {
      peerIndex = i;
      break;
    }
  }
  
  // Si es un nuevo peer, añadirlo
  if (peerIndex < 0 && peerCount < 20) {
    peerIndex = peerCount;
    memcpy(peers[peerCount].mac, mac, 6);
    strcpy(peers[peerCount].name, "Unknown");
    peers[peerCount].rssi = 0;
    peerCount++;
  }
  
  // Registrar el último mensaje recibido
  if (peerIndex >= 0) {
    // Actualizar RSSI (ejemplo, en realidad requerirá implementación adicional)
    peers[peerIndex].rssi = -50; // Valor de ejemplo
  }
  
  // Aquí se procesaría el mensaje recibido
  // ...
}

// Inicializar ESP-NOW
bool initEspNow() {
  if (WiFi.getMode() == WIFI_OFF) {
    WiFi.mode(WIFI_STA);
  }
  
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    espNowActive = false;
    return false;
  }
  
  esp_now_register_recv_cb(onEspNowReceive);
  Serial.println("ESP-NOW initialized");
  espNowActive = true;
  return true;
}

// Función para añadir un peer ESP-NOW
bool addEspNowPeer(const uint8_t *mac) {
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, mac, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add ESP-NOW peer");
    return false;
  }
  
  return true;
}

// Función para enviar un mensaje ESP-NOW
bool sendEspNowMessage(const uint8_t *mac, const char *message) {
  esp_err_t result = esp_now_send(mac, (const uint8_t *)message, strlen(message));
  if (result != ESP_OK) {
    Serial.println("Error sending ESP-NOW message");
    return false;
  }
  return true;
}

// Leer valores analógicos directos
void readAnalogValues(JsonObject &analog) {
  analog["gpio2"] = analogRead(2);
  analog["gpio3"] = analogRead(3);
  analog["gpio4"] = analogRead(4);
}

// Leer valores del ADS1115
void readADSValues(JsonObject &i2c) {
  if (adsConnected) {
    JsonObject ads1115 = i2c.createNestedObject("ads1115");
    ads1115["a0"] = ads.readADC_SingleEnded(0);
    ads1115["a1"] = ads.readADC_SingleEnded(1);
    ads1115["a2"] = ads.readADC_SingleEnded(2);
    ads1115["a3"] = ads.readADC_SingleEnded(3);
  } else {
    i2c["ads1115"] = nullptr;
  }
}

// Leer valores SPI (ejemplo con lectura simulada)
void readSPIValues(JsonObject &spi) {
  // Ejemplo básico - en la práctica habría que comunicarse con dispositivos SPI reales
  JsonObject device1 = spi.createNestedObject("device1");
  device1["register1"] = random(0, 1000); // Simulación
  device1["register2"] = random(0, 1000); // Simulación
}

// Leer valores del puerto serial secundario (si está disponible)
void readSerialValues(JsonObject &serial) {
  // En un ESP32-C3 real, podrías usar Serial1, Serial2, etc.
  // Este es solo un ejemplo
  serial["data"] = "No secondary serial data";
  serial["port"] = "UART0";
}

// Crear información de estado del sistema
void createStatusInfo(JsonObject &status) {
  // Información básica del dispositivo
  status["device_id"] = deviceID;
  status["device_name"] = config.deviceName;
  status["uptime"] = millis() / 1000;
  status["firmware"] = FIRMWARE_VERSION;
  
  // Información de memoria
  status["free_memory"] = ESP.getFreeHeap();
  status["min_free_memory"] = ESP.getMinFreeHeap();
  status["free_sketch_space"] = ESP.getFreeSketchSpace();
  status["sketch_size"] = ESP.getSketchSize();
  
  // Información de CPU y temperatura
  status["cpu_freq"] = ESP.getCpuFreqMHz();
  status["temperature"] = temperatureRead(); // Temperatura interna del ESP32
  
  // Información de energía y sistema
  esp_reset_reason_t resetReason = esp_reset_reason();
  status["reset_reason"] = (uint8_t)resetReason;
  status["reset_reason_str"] = getResetReasonString(resetReason);
  
  #ifdef CONFIG_FREERTOS_USE_STATS_FORMATTING_FUNCTIONS
  status["task_count"] = uxTaskGetNumberOfTasks();
  #endif
  
  // Variables de configuración
  status["sample_interval"] = sampleInterval;
  status["streaming_enabled"] = streamingEnabled;
  status["ads_connected"] = adsConnected;
  status["wifi_connected"] = wifiConnected;
  status["ap_active"] = apActive;
  status["espnow_active"] = espNowActive;
  status["active_sensors"] = config.activeSensors;
  
  // Información WiFi adicional
  if (wifiConnected || apActive) {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char macStr[18];
    sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    status["mac_address"] = macStr;
    status["wifi_channel"] = WiFi.channel();
    
    int8_t power;
    esp_err_t err = esp_wifi_get_max_tx_power(&power);

    float dbm = power * 0.25;

    status["tx_power"] = dbm;

  }
  
  // Información adicional sobre almacenamiento
  status["flash_size"] = ESP.getFlashChipSize() / 1024; // KB
  status["eeprom_size"] = EEPROM_SIZE;
  status["flash_speed"] = ESP.getFlashChipSpeed() / 1000000; // MHz
}

// Crear información de WiFi
void createWiFiInfo(JsonObject &wifi) {
  wifi["status"] = wifiConnected ? "connected" : (apActive ? "ap_active" : "disconnected");
  
  if (wifiConnected) {
    wifi["ssid"] = WiFi.SSID();
    wifi["ip"] = WiFi.localIP().toString();
    wifi["rssi"] = WiFi.RSSI();
  } else if (apActive) {
    wifi["ssid"] = config.deviceName;
    wifi["ip"] = WiFi.softAPIP().toString();
    JsonArray clients = wifi.createNestedArray("clients");
    // Si se necesita, implementar enumeración de clientes WiFi
  }
}

// Crear información de ESP-NOW
void createEspNowInfo(JsonObject &espnow) {
  espnow["status"] = espNowActive ? "active" : "inactive";
  
  if (espNowActive && peerCount > 0) {
    JsonArray peersArray = espnow.createNestedArray("peers");
    
    for (int i = 0; i < peerCount; i++) {
      JsonObject peer = peersArray.createNestedObject();
      char macStr[18];
      sprintf(macStr, "%02X:%02X:%02X:%02X:%02X:%02X", 
              peers[i].mac[0], peers[i].mac[1], peers[i].mac[2], 
              peers[i].mac[3], peers[i].mac[4], peers[i].mac[5]);
      peer["mac"] = macStr;
      peer["name"] = peers[i].name;
      peer["rssi"] = peers[i].rssi;
    }
  }
}

// Generar el JSON completo con todas las mediciones
void generateJSON() {
  jsonDoc.clear();
  
  jsonDoc["timestamp"] = millis() - startTime;
  
  // Lecturas analógicas
  JsonObject analog = jsonDoc.createNestedObject("analog");
  readAnalogValues(analog);
  
  // Dispositivos I2C
  JsonObject i2c = jsonDoc.createNestedObject("i2c");
  readADSValues(i2c);
  
  // Dispositivos SPI
  JsonObject spi = jsonDoc.createNestedObject("spi");
  readSPIValues(spi);
  
  // Lecturas seriales
  JsonObject serial = jsonDoc.createNestedObject("serial");
  readSerialValues(serial);
  
  // Información WiFi
  JsonObject wifi = jsonDoc.createNestedObject("wifi");
  createWiFiInfo(wifi);
  
  // Información ESP-NOW
  JsonObject espnow = jsonDoc.createNestedObject("espnow");
  createEspNowInfo(espnow);
  
  // Estado del sistema
  JsonObject status = jsonDoc.createNestedObject("status");
  createStatusInfo(status);
  
  // Serializar a JSON
  serializeJson(jsonDoc, jsonBuffer, JSON_BUFFER_SIZE);
}

// Procesar comandos recibidos
void processCommand(const char* command) {
  // Limpiar el buffer de respuesta
  memset(respBuffer, 0, sizeof(respBuffer));
  StaticJsonDocument<512> respDoc;
  respDoc["cmd_received"] = true;
  
  // Intentar parsear el comando JSON
  DeserializationError error = deserializeJson(cmdDoc, command);
  
  if (error) {
    respDoc["error"] = "Invalid JSON command";
    serializeJson(respDoc, respBuffer, sizeof(respBuffer));
    Serial.println(respBuffer);
    return;
  }
  
  // Extraer el comando
  const char* cmd = cmdDoc["cmd"];
  
  if (!cmd) {
    respDoc["error"] = "No command specified";
    serializeJson(respDoc, respBuffer, sizeof(respBuffer));
    Serial.println(respBuffer);
    return;
  }
  
  respDoc["cmd"] = cmd;
  
  // Procesar el comando
  if (strcmp(cmd, "scan_i2c") == 0) {
    scanI2C();
    respDoc["result"] = "I2C scan completed";
    respDoc["ads1115_found"] = adsConnected;
  }
  else if (strcmp(cmd, "wifi_connect") == 0) {
    if (cmdDoc.containsKey("ssid") && cmdDoc.containsKey("password")) {
      strlcpy(config.wifiSSID, cmdDoc["ssid"], sizeof(config.wifiSSID));
      strlcpy(config.wifiPassword, cmdDoc["password"], sizeof(config.wifiPassword));
      EEPROM.put(0, config);
      EEPROM.commit();
      
      bool connected = initWiFi();
      respDoc["result"] = connected ? "Connected to WiFi" : "Failed to connect";
      respDoc["ip"] = connected ? WiFi.localIP().toString() : "";
    } else {
      respDoc["error"] = "Missing SSID or password";
    }
  }
  else if (strcmp(cmd, "wifi_disconnect") == 0) {
    WiFi.disconnect();
    wifiConnected = false;
    respDoc["result"] = "WiFi disconnected";
  }
  else if (strcmp(cmd, "wifi_ap_start") == 0) {
    bool success = startAP();
    respDoc["result"] = success ? "AP started" : "Failed to start AP";
    if (success) {
      respDoc["ip"] = WiFi.softAPIP().toString();
    }
  }
  else if (strcmp(cmd, "wifi_ap_stop") == 0) {
    WiFi.softAPdisconnect(true);
    apActive = false;
    respDoc["result"] = "AP stopped";
  }
  else if (strcmp(cmd, "espnow_init") == 0) {
    bool success = initEspNow();
    respDoc["result"] = success ? "ESP-NOW initialized" : "Failed to initialize ESP-NOW";
  }
  else if (strcmp(cmd, "espnow_pair") == 0) {
    if (cmdDoc.containsKey("mac")) {
      const char* macStr = cmdDoc["mac"];
      uint8_t mac[6];
      sscanf(macStr, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx", 
             &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5]);
      
      bool success = addEspNowPeer(mac);
      respDoc["result"] = success ? "Peer added" : "Failed to add peer";
    } else {
      respDoc["error"] = "Missing MAC address";
    }
  }
  else if (strcmp(cmd, "espnow_send") == 0) {
    if (cmdDoc.containsKey("mac") && cmdDoc.containsKey("data")) {
      const char* macStr = cmdDoc["mac"];
      const char* data = cmdDoc["data"];
      uint8_t mac[6];
      sscanf(macStr, "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx", 
             &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5]);
      
      bool success = sendEspNowMessage(mac, data);
      respDoc["result"] = success ? "Message sent" : "Failed to send message";
    } else {
      respDoc["error"] = "Missing MAC address or data";
    }
  }
  else if (strcmp(cmd, "set_sample_rate") == 0) {
    if (cmdDoc.containsKey("interval")) {
      sampleInterval = cmdDoc["interval"];
      config.sampleInterval = sampleInterval;
      EEPROM.put(0, config);
      EEPROM.commit();
      respDoc["result"] = "Sample interval updated";
      respDoc["interval"] = sampleInterval;
    } else {
      respDoc["error"] = "Missing interval parameter";
    }
  }
  else if (strcmp(cmd, "start_stream") == 0) {
    streamingEnabled = true;
    config.streamingEnabled = true;
    EEPROM.put(0, config);
    EEPROM.commit();
    respDoc["result"] = "Streaming started";
  }
  else if (strcmp(cmd, "stop_stream") == 0) {
    streamingEnabled = false;
    config.streamingEnabled = false;
    EEPROM.put(0, config);
    EEPROM.commit();
    respDoc["result"] = "Streaming stopped";
  }
  else if (strcmp(cmd, "single_read") == 0) {
    generateJSON();
    Serial.println(jsonBuffer);
    return; // Ya enviamos el JSON completo, no enviamos respuesta adicional
  }
  else if (strcmp(cmd, "reset") == 0) {
    respDoc["result"] = "Resetting device...";
    serializeJson(respDoc, respBuffer, sizeof(respBuffer));
    Serial.println(respBuffer);
    delay(100);
    ESP.restart();
    return;
  }
  else if (strcmp(cmd, "get_status") == 0) {
    JsonObject status = respDoc.createNestedObject("status");
    createStatusInfo(status);
  }
  else if (strcmp(cmd, "set_name") == 0) {
    if (cmdDoc.containsKey("name")) {
      strlcpy(config.deviceName, cmdDoc["name"], sizeof(config.deviceName));
      EEPROM.put(0, config);
      EEPROM.commit();
      respDoc["result"] = "Device name updated";
      respDoc["name"] = config.deviceName;
    } else {
      respDoc["error"] = "Missing name parameter";
    }
  }
  else {
    respDoc["error"] = "Unknown command";
  }
  
  serializeJson(respDoc, respBuffer, sizeof(respBuffer));
  Serial.println(respBuffer);
}

// Revisar y procesar entradas seriales
void checkSerial() {
  static String inputBuffer = "";
  static bool commandComplete = false;
  
  while (Serial.available()) {
    char c = Serial.read();
    
    if (c == '\n') {
      commandComplete = true;
    } else {
      inputBuffer += c;
    }
  }
  
  if (commandComplete) {
    processCommand(inputBuffer.c_str());
    inputBuffer = "";
    commandComplete = false;
  }
}

// Inicializar toda la configuración
void setup() {
  startTime = millis();
  
  // Inicializar hardware
  initHardware();
  
  // Escanear dispositivos I2C
  scanI2C();
  
  // Intentar conectar a WiFi si hay credenciales guardadas
  if (strlen(config.wifiSSID) > 0) {
    initWiFi();
  }
  
  // Si streaming estaba activo, iniciarlo
  streamingEnabled = config.streamingEnabled;
  sampleInterval = config.sampleInterval;
  
  Serial.println("Setup complete, ready to receive commands");
}

// Bucle principal
void loop() {
  // Comprobar comandos seriales
  checkSerial();
  
  // Si el streaming está activo y es tiempo de enviar datos
  if (streamingEnabled && (millis() - lastSampleTime >= sampleInterval)) {
    generateJSON();
    Serial.println(jsonBuffer);
    lastSampleTime = millis();
  }
  
  // Pequeña pausa para reducir uso de CPU
  delay(1);
}
