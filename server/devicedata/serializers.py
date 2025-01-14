from rest_framework import serializers
from .models import DeviceData, SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['temperature', 'humidity', 'gas_sensor', 'timestamp']

class DeviceDataSerializer(serializers.ModelSerializer):
    sensor_data = SensorDataSerializer(many=True, read_only=True)  # Include related sensor data

    class Meta:
        model = DeviceData
        fields = ['device_name', 'location', 'owners_name', 'flock_size', 'tag', 'sensor_data']
