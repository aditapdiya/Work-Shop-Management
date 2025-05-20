from django import forms
from .models import Workshop, WorkshopRegistration
from datetime import date

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

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get('location')
        meeting_link = cleaned_data.get('meeting_link')
        address = cleaned_data.get('address')
        workshop_date = cleaned_data.get('date')
        registration_deadline = cleaned_data.get('registration_deadline')

        if workshop_date and workshop_date < date.today():
            self.add_error('date', "Workshop date cannot be in the past.")

        if registration_deadline and workshop_date:
            if registration_deadline > workshop_date:
                self.add_error('registration_deadline', "Deadline must be before the workshop date.")

        if location == 'online' and not meeting_link:
            self.add_error('meeting_link', "Meeting link is required for online workshops.")

        if location == 'offline' and not address:
            self.add_error('address', "Address is required for offline workshops.")



class WorkshopRegistrationForm(forms.ModelForm):
    PARTICIPANT_CHOICES = [
        ('student', 'Student'),
        ('employee', 'Employee'),
    ]

    participant_type = forms.ChoiceField(
        choices=PARTICIPANT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_participant_type'})
    )

    class Meta:
        model = WorkshopRegistration
        fields = [
            'participant_type', 'name', 'email', 'phone',
            'college', 'course', 'year_of_study',
            'company_name', 'designation'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_phone'}),
            'college': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_college'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_course'}),
            'year_of_study': forms.Select(attrs={'class': 'form-select', 'id': 'id_year_of_study'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_company_name'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_designation'}),
        }
