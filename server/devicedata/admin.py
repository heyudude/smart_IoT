from django.contrib import admin
from .models import *

# Register the DeviceData model
@admin.register(DeviceData)
class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ['device_name', 'location', 'flock_size', 'tag']
    search_fields = ['device_name', 'location', 'tag']

# Register the SensorData model
@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['device', 'temperature', 'humidity', 'gas_sensor', 'timestamp']
    list_filter = ['device', 'timestamp']
    search_fields = ['device__device_name', 'device__tag']

@admin.register(ClimateControlData)
class ClimateControlDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'heater', 'cooling_fan', 'humidifier', 'exhaust_fan','created_at')

@admin.register(ThresholdData)
class ThresholdDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'highest_temperature_level', 'lowest_temperature_level', 'highest_humidity_level', 
                    'lowest_humidity_level', 'highest_ammonia_level', 'lowest_ammonia_level','created_at')