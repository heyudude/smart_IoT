# Smart BMS IoT Project Documentation

## 1. Introduction
The Smart BMS IoT Project aims to automate climate control in Brew Management Systems to ensure a healthy and optimal environment for the birds. Using a combination of temperature, humidity, and ammonia sensors, the system automatically adjusts the farm's conditions. The Django server enables farmers to monitor and control these parameters remotely.

## 2. Problem Statement
read sensors in a remote location via

## 3. System Overview
The system comprises hardware and software components that work together to monitor and control the environment of a BMS. Farmers interact with the system through a web interface where they can monitor live data and set thresholds.

### Main Features:
- Temperature control through fans and heaters.
- Humidity control through humidifiers and exhaust fans.
- Ammonia level monitoring and control through exhaust fans.

## 4. System Architecture

### 4.1 Hardware Components:
- **ESP32 Controller:** The central unit that reads sensor data and controls devices.
- **DHT22 Sensor:** Measures temperature and humidity.
- **MQ3 Gas Sensor:** Monitors ammonia levels in the air.
- **60W Bulb (Heater):** Provides heat when the temperature is too low.
- **5V DC Cooling and Exhaust Fans:** Used for cooling and air circulation.
- **2-Channel 5V Relays:** Switches for controlling fans, heater, and humidifier.

### 4.2 Software Components:
- **Django Framework:** Backend server to handle requests, data storage, and user authentication.
- **Arduino IDE:** Used to program the ESP32 controller.
- **MQTT (HiveMQ):** Protocol for communication between the ESP32 and the Django server.
- **HiveMQ:** MQTT broker for device-server communication.

## 5. Key Functionalities

### 5.1 Temperature Control:
- Users can set temperature thresholds on the web interface.
- If the temperature exceeds the higher threshold, the cooling fan turns on.
- If the temperature drops below the lower threshold, the heater (bulb) is activated.

### 5.2 Humidity Control:
- Users can set humidity thresholds.
- If the humidity exceeds the upper threshold, the exhaust fan turns on.
- If the humidity drops below the lower threshold, the humidifier is activated.

### 5.3 Ammonia Control:
- Ammonia levels are monitored using the MQ3 sensor.
- If ammonia levels exceed the threshold, the exhaust fan is turned on for ventilation.

## 6. Data Flow and Communication

### 6.1 Data Publishing (ESP32):
The ESP32 controller collects temperature, humidity, and ammonia data from the sensors and publishes the data to an MQTT topic in JSON format.

```cpp
doc["deviceId"] = "ESP32";
doc["siteId"] = "My Demo Lab";
doc["humidity"] = humidity;
doc["temperature"] = temperature;
doc["mq3Value"] = mq3Value;

serializeJson(doc, mqtt_message, sizeof(mqtt_message));
publishMessage("esp32_data", mqtt_message, true);
```
### 6.2 Data Processing (Django):
A Python script running on the Django server subscribes to the MQTT topic and stores the sensor data in a database.

```python
class SensorData(models.Model):
    device = models.ForeignKey(DeviceData, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()
    gas_sensor = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
```
    
### 6.3 Threshold Setting:
Farmers can set the desired thresholds for temperature, humidity, and ammonia levels via a web form. These values are published to MQTT and processed by the ESP32.

```python
payload = json.dumps({
    'deviceId': threshold_data.device.tag,
    'temperature_max': threshold_data.highest_temperature_level,
    'temperature_min': threshold_data.lowest_temperature_level,
    'humidity_max': threshold_data.highest_humidity_level,
    'humidity_min': threshold_data.lowest_humidity_level,
    'ammonia_max': threshold_data.highest_ammonia_level,
})
client.publish(MQTT_THRESHOLD_TOPIC, payload)
```
