from django.urls import path, include
from . import views  # Import your views

urlpatterns = [
    path('', views.home, name='home'),  # Example path, adjust as needed
    path('api/devices/', views.get_all_devices, name='get_all_devices'),
    path('api/devices/<str:tag>/', views.get_device_by_tag, name='get_device_by_tag'),
    path('sensor-data/', views.sensor_data_view, name='sensor_data'),
    path('api/latest-data/', views.latest_data, name='latest-data'),
    path('latest-data-view/', views.latest_data_view, name='latest_data_view'),
    path('set-threshold/', views.set_threshold_data, name='set_threshold_data'),
    path('api-auth/', include('rest_framework.urls')),
]
