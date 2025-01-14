from django.db import models
from django.utils import timezone

class DeviceData(models.Model):
    device_name = models.CharField(max_length=100)  # Device name
    location = models.CharField(max_length=255)     # Location of the device
    owners_name = models.CharField(max_length=100)
    flock_size = models.IntegerField()              # Size of the flock (for BMS context)
    tag = models.CharField(max_length=50, unique=True)  # Unique device tag

    def __str__(self):
        return f"{self.device_name} - {self.location}"
class SensorData(models.Model):
    device = models.ForeignKey(DeviceData, on_delete=models.CASCADE, related_name='sensor_data')
    temperature = models.FloatField()  # Temperature in ºC
    humidity = models.FloatField()     # Humidity in %
    gas_sensor = models.FloatField()   # Gas sensor reading in ppm
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically sets the current time

    def __str__(self):
        return f"Temperature: {self.temperature} ºC, Humidity: {self.humidity} %, Gas Sensor: {self.gas_sensor} ppm"


class ClimateControlData(models.Model):
    device = models.ForeignKey(DeviceData, on_delete=models.CASCADE, related_name='climate_control_data')
    heater = models.BooleanField(default=False)
    cooling_fan = models.BooleanField(default=False)
    humidifier = models.BooleanField(default=False)
    exhaust_fan = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the record is created
    updated_at = models.DateTimeField(auto_now=True)      # Timestamp when the record is last updated

    def __str__(self):
        return f"Climate control for {self.device.device_name}"


class ThresholdData(models.Model):
    device = models.ForeignKey(DeviceData, on_delete=models.CASCADE, related_name='threshold_data')
    highest_temperature_level = models.FloatField()
    lowest_temperature_level = models.FloatField()
    highest_humidity_level = models.FloatField()
    lowest_humidity_level = models.FloatField()
    highest_ammonia_level = models.FloatField()
    lowest_ammonia_level = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the record is created
    updated_at = models.DateTimeField(auto_now=True)      # Timestamp when the record is last updated

    def __str__(self):
        return f"Temperature range: {self.lowest_temperature_level} - {self.highest_temperature_level} ºC, " \
               f"Humidity range: {self.lowest_humidity_level} - {self.highest_humidity_level} %, " \
               f"Ammonia range: {self.lowest_ammonia_level} - {self.highest_ammonia_level} ppm"
