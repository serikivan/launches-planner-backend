from django.contrib import admin
from .models import Satellite, Launch, LaunchSatellite

admin.site.register(Satellite)
admin.site.register(Launch)
admin.site.register(LaunchSatellite)