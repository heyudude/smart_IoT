from django import forms
from .models import ThresholdData

class ThresholdDataForm(forms.ModelForm):
    class Meta:
        model = ThresholdData
        fields = ['device', 'highest_temperature_level', 'lowest_temperature_level', 'highest_humidity_level', 'lowest_humidity_level', 'highest_ammonia_level', 'lowest_ammonia_level']
        widgets = {
            'device': forms.Select(attrs={'class': 'form-control'}),
            'highest_temperature_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'lowest_temperature_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'highest_humidity_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'lowest_humidity_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'highest_ammonia_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'lowest_ammonia_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }
