from django.db import models

class Workshop(models.Model):
    LOCATION_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    duration = models.CharField(max_length=50)
    speaker = models.CharField(max_length=100)
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES, default='offline')
    meeting_link = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    capacity = models.PositiveIntegerField()
    registration_deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.title

class WorkshopRegistration(models.Model):
    PARTICIPANT_TYPE_CHOICES = [
        ('student', 'Student'),
        ('employee', 'Employee'),
    ]
    workshop = models.ForeignKey('Workshop', on_delete=models.CASCADE)
    participant_type = models.CharField(max_length=10, choices=PARTICIPANT_TYPE_CHOICES)
    # Common Fields
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    # Student Fields
    college = models.CharField(max_length=150, blank=True)
    course = models.CharField(max_length=100, blank=True)
    year_of_study = models.CharField(max_length=20, choices=[
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year'),
        ('other', 'Other'),
    ], blank=True)
    # Employee Fields
    company_name = models.CharField(max_length=150, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.workshop.title}"

