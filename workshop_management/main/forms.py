from django import forms
from .models import Workshop

class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = [
            'title', 'description', 'date', 'time', 'duration',
            'speaker', 'location', 'meeting_link', 'address',
            'capacity', 'registration_deadline', 'is_active'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'registration_deadline': forms.DateInput(attrs={'type': 'date'}),
        }
