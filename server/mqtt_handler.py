import os
import django
import paho.mqtt.client as mqtt
import json
import time
import threading

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_iot.settings")
django.setup()

from devicedata.models import DeviceData, SensorData, ThresholdData  # Import your models

# MQTT settings
MQTT_BROKER = "192.168.2.6"
MQTT_PORT = 8883
MQTT_TOPIC = "smart_iot"
MQTT_THRESHOLD_TOPIC = "threshold_data"
MQTT_USERNAME = "iot"
MQTT_PASSWORD = "iotiot2020"

# SSL certificate for secure connection (store securely)
MQTT_TLS_CERT = """
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
"""

# The callback function when a message is received
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        print(f"Message received on topic {message.topic}: {payload}")
        
        # Parse the JSON data
        data = json.loads(payload)
        print(f"Parsed data: {data}")

        device_tag = data.get('deviceId')  # Assuming 'deviceId' matches 'tag' in DeviceData model
        temperature = round(data.get('temperature'), 1)
        humidity = round(data.get('humidity'),1)
        gas_sensor = data.get('mq3Value')

        # Fetch the device by tag
        device = DeviceData.objects.get(tag=device_tag)
        
        # Create and save the SensorData
        SensorData.objects.create(
            device=device,
            temperature=temperature,
            humidity=humidity,
            gas_sensor=gas_sensor
        )
        print(f"Sensor data saved successfully for device: {device_tag}")

    except DeviceData.DoesNotExist:
        print(f"Device with tag {device_tag} does not exist.")
    except json.JSONDecodeError:
        print("Received message is not in JSON format.")
    except Exception as e:
        print(f"Error while saving data: {e}")

# Function to send threshold data to the MQTT broker
def send_threshold_to_mqtt():
    try:
        client = mqtt.Client()

        # Set username and password for the broker
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # Set the SSL certificate
        client.tls_set(certfile=None, keyfile=None, cert_reqs=mqtt.ssl.CERT_REQUIRED, tls_version=mqtt.ssl.PROTOCOL_TLS)
        client.tls_insecure_set(False)

        # Connect to the broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        while True:
            # Fetch threshold data
            threshold_data = ThresholdData.objects.latest('created_at') # Modify this to query your threshold data
            if threshold_data:
                # Convert threshold data to JSON and publish to the MQTT topic
                payload = json.dumps({
                    'deviceId': threshold_data.device.tag,
                    'temperature_max': threshold_data.highest_temperature_level,
                    'temperature_min': threshold_data.lowest_temperature_level,
                    'humidity_max': threshold_data.highest_humidity_level,
                    'humidity_min': threshold_data.lowest_humidity_level,
                    'ammonia_max': threshold_data.highest_ammonia_level,
                    'ammonia_min': threshold_data.lowest_ammonia_level,
                })
                client.publish(MQTT_THRESHOLD_TOPIC, payload)
                print("Threshold data sent to MQTT.")
            
            time.sleep(5)  # Adjust the sleep time to control how frequently threshold data is sent

        client.disconnect()

    except Exception as e:
        print(f"Error sending threshold data to MQTT: {e}")
# The callback function for connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

# Setting up the MQTT client
def setup_mqtt():
    client = mqtt.Client()

    # Set username and password for the broker
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Set the SSL certificate
    client.tls_set(certfile=None, keyfile=None, cert_reqs=mqtt.ssl.CERT_REQUIRED, tls_version=mqtt.ssl.PROTOCOL_TLS)
    client.tls_insecure_set(False)

    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the broker
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    return client

# Function to run both MQTT loop and threshold sender in parallel
def run_mqtt_and_threshold():
    # Start the MQTT client
    mqtt_client = setup_mqtt()

    # Start the MQTT loop in a separate thread
    mqtt_thread = threading.Thread(target=mqtt_client.loop_forever)
    mqtt_thread.start()

    # Run the threshold data sender in the main thread
    send_threshold_to_mqtt()

if __name__ == "__main__":
    # Run both MQTT sensor data receiver and threshold sender in parallel
    run_mqtt_and_threshold()

