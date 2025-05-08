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

