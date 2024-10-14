from django.contrib import admin
from django.urls import path
from launches import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.SatellitesPage, name='main_url'),
    path('launch/<int:id>', views.LaunchesCreator, name='launch_url'),
    path('satellite/<int:id>', views.GetSat, name='sat_url'),
    path('launch/delete/<int:id>/', views.DeleteLaunch, name='delete_url'),
    path('satellite/add/<int:launch_id>/', views.AddSatellite, name='add_url'),
]