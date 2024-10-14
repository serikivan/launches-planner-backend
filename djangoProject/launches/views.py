from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date
from .models import Satellite, Launch, LaunchSatellite
import psycopg2

conn = psycopg2.connect(dbname="launches", host="localhost", user="postgres", password="123", port="5432")

cursor = conn.cursor()

user_id = 1

def SatellitesPage(request):
    search_query = request.GET.get('satname', '')
    satellites = Satellite.objects.filter(title__icontains=search_query) if search_query else Satellite.objects.filter(status=True)

    launch = Launch.objects.filter(creator=user_id,status='draft').first()
    launches_size = LaunchSatellite.objects.filter(launch=launch).count() if launch else 0

    return render(request, 'satellites.html', {'data': {
        'search': search_query,
        'satellites': satellites,
        'launchesSize': launches_size,
        'launch_id': launch.launch_id if launch else None
    }})

def LaunchesCreator(request, id):
    launch = Launch.objects.filter(pk=id).first()

    if launch.status == 'deleted':
        return HttpResponse(status=404)

    satellites_with_order = [
        (ls.satellite, ls.order) for ls in LaunchSatellite.objects.filter(launch=launch).order_by('order')]

    return render(request, 'launch.html', {'data': {
        'launch': launch,
        'satellites_with_order': satellites_with_order
    }})

def GetSat(request, id):
    satellite = Satellite.objects.filter(pk=id).first()

    return render(request, 'satellite.html', {'data': {
            'satellite': satellite
        }})


def DeleteLaunch(request, id):
    cursor.execute("UPDATE launches SET status = 'deleted' WHERE launch_id = %s", (id,))
    conn.commit()

    new_launch = Launch.objects.create(

        creator=request.user,
        rocket='',
        status='draft'
    )

    return redirect('main_url')

def AddSatellite(request, launch_id):
    if request.method == 'POST':
        satellite_id = request.POST.get('satellite_id')
        launch = Launch.objects.filter(pk=launch_id).first()
        satellite = Satellite.objects.filter(pk=satellite_id).first()

        if not LaunchSatellite.objects.filter(launch=launch, satellite=satellite).exists():
            LaunchSatellite.objects.create(launch=launch, satellite=satellite)
            messages.success(request, 'Спутник успешно добавлен в запуск.')
        else:
            messages.warning(request, 'Этот спутник уже добавлен в запуск.')

    return redirect('main_url')