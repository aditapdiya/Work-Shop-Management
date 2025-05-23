# main/forms.py
from django import forms
from .models import Workshop, WorkshopRegistration, WorkshopFeedback
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

    def __init__(self, *args, **kwargs):
        self.workshop = kwargs.pop('workshop', None)  # Get the workshop passed from the view
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        if self.workshop:
            if email and WorkshopRegistration.objects.filter(workshop=self.workshop, email__iexact=email).exists():
                raise forms.ValidationError("This email is already registered for this workshop.")
            if phone and WorkshopRegistration.objects.filter(workshop=self.workshop, phone=phone).exists():
                raise forms.ValidationError("This phone number is already registered for this workshop.")

        return cleaned_data

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


class WorkshopFeedbackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.workshop = kwargs.pop('workshop', None)  # Accept the workshop instance
        super().__init__(*args, **kwargs)

    class Meta:
        model = WorkshopFeedback
        fields = ['name', 'email', 'rating', 'most_helpful_part', 'suggestions']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'most_helpful_part': forms.Textarea(attrs={'rows': 3}),
            'suggestions': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_email(self):
        # print("Validating email for workshop:", self.workshop)
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError("Email is required.")

        if not email.endswith('.com'):
            raise forms.ValidationError("Email must be a valid .com address.")
        if self.workshop:
            is_registered = WorkshopRegistration.objects.filter(
                workshop=self.workshop, email__iexact=email
            ).exists()
            if not is_registered:
                raise forms.ValidationError("This email is not registered for the workshop.")
        return email

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

    def clean_most_helpful_part(self):
        most_helpful = self.cleaned_data.get('most_helpful_part')
        if not most_helpful or len(most_helpful.strip()) < 10:
            raise forms.ValidationError("Please provide more detailed feedback (at least 10 characters).")
        return most_helpful

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if name and not name.strip():
            self.add_error('name', "Name cannot be empty or only spaces.")

        return cleaned_data
