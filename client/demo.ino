#include <WiFi.h>
#include "DHT.h"
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <LiquidCrystal_I2C.h>

/** DHT11 sensor Settings ***/
#define DHTPIN  25
#define DHTTYPE DHT22     
DHT dht(DHTPIN, DHTTYPE);

/** MQ-3 Sensor Settings ***/
const int MQ3PIN = 35;  // Set MQ-3 sensor pin as GPIO35

/** Fan, Heater, and LED Pin Settings ***/
const int coolingFanPin = 4;   // GPIO pin for cooling fan
const int heaterLampPin = 23;   // GPIO pin for heater lamp
const int exhaustFanPin = 5;   // GPIO pin for exhaust fan
const int humidityLEDPin = 18;  // GPIO pin for humidity LED
const int led = 15;

int lcdColumns = 16;
int lcdRows = 2;
LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows); 


/** WiFi Connection Details ***/
const char* ssid = "plastid";
const char* password = "plastid@123";

/*** MQTT Broker Connection Details ***/
const char* mqtt_server = "e6356bea60684fedadf26e979ecd631f.s1.eu.hivemq.cloud";
const char* mqtt_username = "admin";
const char* mqtt_password = "5m@rtP0ultry2024";
const int mqtt_port = 8883;

/** Secure WiFi Connectivity Initialisation ***/
WiFiClientSecure espClient;

/** MQTT Client Initialisation Using WiFi Connection ***/
PubSubClient client(espClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];

/** root certificate ***/
static const char *root_ca PROGMEM = R"EOF(
 -----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)EOF";

// Global variables for threshold values
float temperatureThresholdHigh;
float temperatureThresholdLow;
float humidityThresholdHigh;
float humidityThresholdLow;
int gasThreshold;

/** Function to Set Threshold Values **/
void setThresholds(float tempHigh, float tempLow, float humHigh, float humLow, int gasThresh) {
  temperatureThresholdHigh = tempHigh;
  temperatureThresholdLow = tempLow;
  humidityThresholdHigh = humHigh;
  humidityThresholdLow = humLow;
  gasThreshold = gasThresh;
}

/** Function to Get Threshold Values **/
void getThresholds(float &tempHigh, float &tempLow, float &humHigh, float &humLow, int &gasThresh) {
  tempHigh = temperatureThresholdHigh;
  tempLow = temperatureThresholdLow;
  humHigh = humidityThresholdHigh;
  humLow = humidityThresholdLow;
  gasThresh = gasThreshold;
}

/***** Connect to WiFi *****/
void setup_wifi() {
  delay(10);
  Serial.print("\nConnecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("\nWiFi connected\nIP address: ");
  Serial.println(WiFi.localIP());
}

/***** Connect to MQTT Broker *****/
/***** Connect to MQTT Broker *****/
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("led_state");
      client.subscribe("threshold_data"); // Subscribe to the new threshold_data topic
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String incomingMessage = "";
  for (int i = 0; i < length; i++) {
    incomingMessage += (char)payload[i];
  }

  // Check if the topic is "led_state" and act accordingly
  if (strcmp(topic, "led_state") == 0) {
    if (incomingMessage.equals("1")) digitalWrite(led, HIGH);   // Turn the LED on
    else digitalWrite(led, LOW);  // Turn the LED off
  }

  // Check if the topic is "threshold_data"
  if (strcmp(topic, "threshold_data") == 0) {
    // Parse the JSON payload
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, incomingMessage);
    
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    // Extract threshold values from the JSON payload
    float tempHigh = doc["temperature_max"];
    float tempLow = doc["temperature_min"];
    float humHigh = doc["humidity_max"];
    float humLow = doc["humidity_min"];
    int gasThresh = doc["ammonia_max"];

    // Call the setThresholds() function with the received values
    setThresholds(tempHigh, tempLow, humHigh, humLow, gasThresh);

    // Print the new threshold values for debugging
    Serial.println("Thresholds updated:");
    Serial.print("Temperature High: "); Serial.println(tempHigh);
    Serial.print("Temperature Low: "); Serial.println(tempLow);
    Serial.print("Humidity High: "); Serial.println(humHigh);
    Serial.print("Humidity Low: "); Serial.println(humLow);
    Serial.print("Gas Threshold: "); Serial.println(gasThresh);
  }
}

/** Method for Publishing MQTT Messages ****/
void publishMessage(const char* topic, String payload, boolean retained) {
  if (client.publish(topic, payload.c_str(), retained))
    Serial.println("Message published [" + String(topic) + "]: " + payload);
}

/*** Application Initialisation Function ****/
void setup() {
  dht.begin(); // Set up DHT11 sensor
  pinMode(led, OUTPUT);            // Set up LED
  pinMode(MQ3PIN, INPUT);          // Set up MQ-3 sensor
  pinMode(coolingFanPin, OUTPUT);  // Set up cooling fan
  pinMode(heaterLampPin, OUTPUT);  // Set up heater lamp
  pinMode(exhaustFanPin, OUTPUT);  // Set up exhaust fan
  pinMode(humidityLEDPin, OUTPUT); // Set up LED for humidity control

  Serial.begin(115200);
  setup_wifi();

  espClient.setCACert(root_ca);  // Use root certificate for SSL

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Set initial threshold values
  setThresholds(22.0, 20.0, 85.0, 70.0, 800);
  // initialize LCD
  lcd.init();
  // turn on LCD backlight                      
  lcd.backlight();
}

/*** Main Function ***/
unsigned long lastSensorRead = 0;  // Stores the last time the sensor was read
const long interval = 5000;        // Interval between sensor readings (in milliseconds)

void loop() {
  if (!client.connected()) reconnect(); // Check if client is connected
  client.loop();

  unsigned long now = millis(); // Get the current time

  // Check if it's time to read the sensors and publish data
  if (now - lastSensorRead >= interval) {
    lastSensorRead = now;

    // Read thresholds
    float tempHigh, tempLow;
    float humHigh, humLow;
    int gasThresh;
    getThresholds(tempHigh, tempLow, humHigh, humLow, gasThresh);

    // Add a small delay before reading the sensor
    delay(100);

    // Read DHT11 temperature and humidity reading
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    // Round temperature and humidity to one decimal place
    temperature = round(temperature * 10) / 10.0;
    humidity = (round(humidity * 10) / 10.0)*0.9;

    // Read MQ-3 Alcohol Gas Sensor reading
    int mq3Value = 26 ;//(analogRead(MQ3PIN)/100);

    //Control Cooling Fan and Heater Lamp based on temperature thresholds
    if (temperature > tempHigh) {
      digitalWrite(coolingFanPin, HIGH);  // Start cooling fan
      digitalWrite(heaterLampPin, LOW);   // Turn off heater lamp
      Serial.println("Cooling fan On,heater off");
      lcd.setCursor(0, 0);
      lcd.print("Cooler on.");
      lcd.setCursor(0, 1);
      lcd.print("Heater off");
      delay(1000);
      lcd.clear();
    } else if (temperature < tempLow) {
      digitalWrite(coolingFanPin, LOW);   // Turn off cooling fan
      digitalWrite(heaterLampPin, HIGH);  // Start heater lamp
      Serial.println("Heater on.cooling fan off");
      lcd.setCursor(0, 0);
      lcd.print("Heater on.");
      lcd.setCursor(0, 1);
      lcd.print("Cooler off");
      delay(1000);
      lcd.clear();
    } else {
      digitalWrite(coolingFanPin, LOW);   // Ensure cooling fan is off
      digitalWrite(heaterLampPin, LOW);   // Ensure heater lamp is off
    }


    if (humidity < humLow) {
      digitalWrite(humidityLEDPin, HIGH); // Turn on humidity LED
      Serial.println("humidifier on");
      // lcd.clear();
      // lcd.setCursor(0, 0);
      // lcd.print("Humidifier on.");
      // lcd.setCursor(0, 1);
      // lcd.print("Exhaust off");
    } else {
      digitalWrite(humidityLEDPin, LOW);  // Ensure humidity LED is off
      Serial.println("humidifier off");
    }

    // Control Exhaust Fan based on MQ-3 sensor value
    if ((mq3Value > gasThresh) || (humidity > humHigh)) {
      digitalWrite(exhaustFanPin, HIGH);  // Start exhaust fan for gas level
      Serial.println("Exhaust fan on");
      // lcd.clear();
      // lcd.setCursor(0, 0);
      // lcd.print("Exhaust on.");
    } else {
      digitalWrite(exhaustFanPin, LOW);   // Turn off exhaust fan if gas is under control
      Serial.println("exhaust fan off.");
      // lcd.clear();
      // lcd.setCursor(0, 0);
      // lcd.print("Exhaust off.");
    }

    // digitalWrite(exhaustFanPin, LOW);
    // digitalWrite(coolingFanPin, LOW);
    // delay(10000);
    // digitalWrite(exhaustFanPin, HIGH);
    // digitalWrite(coolingFanPin, HIGH);
    // delay(10000);

    DynamicJsonDocument doc(1024);

    // Limit precision in the JSON serialization
    doc["deviceId"] = "ESP32";
    doc["siteId"] = "My Demo Lab";
    doc["humidity"] = humidity;
    doc["temperature"] = temperature;
    doc["mq3Value"] = mq3Value;

    // Set float precision to 1 decimal place
    char mqtt_message[128];
    serializeJson(doc, mqtt_message, sizeof(mqtt_message));
    
    // Publish the message
    publishMessage("esp32_data", mqtt_message, true);
  }
}

