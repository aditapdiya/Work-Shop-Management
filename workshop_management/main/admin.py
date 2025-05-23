from django.contrib import admin
from .models import Workshop, WorkshopRegistration , WorkshopFeedback
# Register your models here.
admin.site.register(Workshop)
admin.site.register(WorkshopRegistration)
admin.site.register(WorkshopFeedback)
