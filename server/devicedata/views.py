from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.utils import timezone 
def home(request):
    return render(request, 'meter.html')

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import DeviceDataSerializer

@api_view(['GET'])
def get_all_devices(request):
    devices = DeviceData.objects.prefetch_related('sensor_data').all()  # Fetch devices with sensor data
    serializer = DeviceDataSerializer(devices, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_device_by_tag(request, tag):
    try:
        device = DeviceData.objects.prefetch_related('sensor_data').get(tag=tag)
        serializer = DeviceDataSerializer(device)
        return Response(serializer.data)
    except DeviceData.DoesNotExist:
        return Response({'error': 'Device not found'}, status=404)


def sensor_data_view(request):
    sensor_data = SensorData.objects.all().order_by('timestamp')
    
    # Prepare data for the chart
    context = {
        'timestamps': [
            timezone.localtime(data.timestamp).strftime("%Y-%m-%d %H:%M:%S") for data in sensor_data
        ],
        'temperature': [round(data.temperature, 2) for data in sensor_data],
        'humidity': [data.humidity for data in sensor_data],
        'gas_sensor': [data.gas_sensor for data in sensor_data]
    }
    
    return render(request, 'graphs.html', context)


@api_view(['GET'])
def latest_data(request):
    try:
        # Fetch the latest threshold and sensor data
        threshold_data = ThresholdData.objects.latest('created_at')
        sensor_data = SensorData.objects.latest('timestamp')

        # Initialize climate control settings
        climate_control = ClimateControlData(
            device=sensor_data.device,
            heater=False,
            cooling_fan=False,
            humidifier=False,
            exhaust_fan=False
        )

        # Debugging: Print the sensor and threshold data
        print(f"Sensor Data - Temperature: {sensor_data.temperature}, Humidity: {sensor_data.humidity}, Gas Sensor: {sensor_data.gas_sensor}")
        print(f"Threshold Data - Temp Max: {threshold_data.highest_temperature_level}, Temp Min: {threshold_data.lowest_temperature_level}")
        print(f"Threshold Data - Humidity Max: {threshold_data.highest_humidity_level}, Humidity Min: {threshold_data.lowest_humidity_level}")
        print(f"Threshold Data - Ammonia Max: {threshold_data.highest_ammonia_level}")

        # Compare SensorData with ThresholdData to adjust climate controls
        if sensor_data.temperature > threshold_data.highest_temperature_level:
            climate_control.cooling_fan = True
            print("Cooling fan activated.")
        
        if sensor_data.temperature < threshold_data.lowest_temperature_level:
            climate_control.heater = True
            print("Heater activated.")

        if sensor_data.humidity < threshold_data.lowest_humidity_level:
            climate_control.humidifier = True
            print("Humidifier activated.")
        
        if sensor_data.humidity > threshold_data.highest_humidity_level:
            climate_control.exhaust_fan = True
            print("Exhaust fan activated due to high humidity.")

        if sensor_data.gas_sensor > threshold_data.highest_ammonia_level:
            climate_control.exhaust_fan = True
            print("Exhaust fan activated due to high ammonia.")

        # Save the climate control data
        climate_control.save()

        # Create response data
        climate_data_dict = {
            'heater': climate_control.heater,
            'cooling_fan': climate_control.cooling_fan,
            'humidifier': climate_control.humidifier,
            'exhaust_fan': climate_control.exhaust_fan,
            'created_at': climate_control.created_at
        }

        threshold_data_dict = {
            'highest_temperature_level': threshold_data.highest_temperature_level,
            'lowest_temperature_level': threshold_data.lowest_temperature_level,
            'highest_humidity_level': threshold_data.highest_humidity_level,
            'lowest_humidity_level': threshold_data.lowest_humidity_level,
            'highest_ammonia_level': threshold_data.highest_ammonia_level,
            'lowest_ammonia_level': threshold_data.lowest_ammonia_level,
            'created_at': threshold_data.created_at
        }

        # Return the response with climate control and threshold data
        return Response({
            'climate_data': climate_data_dict,
            'threshold_data': threshold_data_dict
        })

    except Exception as e:
        print(f"Error: {e}")
        return Response({'error': str(e)}, status=500)



def latest_data_view(request):
    return render(request, 'meter2.html')


from .forms import ThresholdDataForm

def set_threshold_data(request):
    if request.method == 'POST':
        form = ThresholdDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('latest_data_view')  # Redirect to the latest data page after submission
    else:
        form = ThresholdDataForm()

    return render(request, 'set_threshold_data.html', {'form': form})