from random import random
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .minio import *
from .serializers import *
from .models import Satellite, AuthUser, Launch, LaunchSatellite
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import datetime

def user():
    try:
        user1 = AuthUser.objects.get(id=1)
    except:
        user1 = AuthUser(id=1, first_name="Иван", last_name="Серик", password=1234, username="user1", is_superuser=True, is_staff=True, is_active=True)
        user1.save()
    return user1


class SatList(APIView):
    model = Satellite
    serializer = SatSerializer

    def get(self, request, format=None):
        searchText = request.query_params.get('SatelliteTitle', '')
        searchResult = Satellite.objects.filter(title__icontains=searchText)
        user1 = user()
        draftLaunch= user1.launch_creator.filter(status='draft').first()
        if draftLaunch:
            SatCount = LaunchSatellite.objects.filter(launch_id=draftLaunch).count()
            LaunchID = draftLaunch.launch_id
        else:
            SatCount = 0
            LaunchID = ''
        serial_data = self.serializer(searchResult, many=True)
        return Response({'satellites': serial_data.data, 'LaunchID': LaunchID,
                         'SatCount': SatCount})

    def post(self, request, format=None):
        serializer = self.serializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SatDetail(APIView):
    model = Satellite
    serializer = SatSerializer

    def get(self, request, satellite_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id)
        serializer = self.serializer(satellite)
        return Response(serializer.data)

    def put(self, request, satellite_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id)
        serializer = self.serializer(satellite, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, satellite_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id)
        result = del_pic(satellite)
        if 'error' in result.data:
            return result
        LaunchSat = LaunchSatellite.objects.filter(satellite_id=satellite)
        LaunchSat.delete()
        satellite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, satellite_id, format=None):
        user1 = user()
        draft = user1.launch_creator.filter(status='draft').first()
        satellite = get_object_or_404(self.model, satellite_id=satellite_id)
        if not draft and not (
        LaunchSatellite.objects.filter(launch_id=draft, satellite_id=satellite.satellite_id).exists()):
            draft = Launch(creator=user1, created_at=timezone.now())
            draft.save()
        if not (
        LaunchSatellite.objects.filter(launch_id=draft.launch_id, satellite_id=satellite.satellite_id).exists()):
            newPos = LaunchSatellite(launch_id=draft.launch_id, satellite_id=satellite.satellite_id)
            newPos.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_208_ALREADY_REPORTED)


@api_view(['Post'])
def SatImgUpload(request, satellite_id, format=None):
    satellite = get_object_or_404(Satellite, satellite_id=satellite_id)
    pic = request.FILES.get('image_url')
    result = add_pic(satellite, pic)
    if 'error' in result.data:
        return result
    return Response({'Success': 'image uploaded.'}, status=status.HTTP_200_OK)

class LaunchesList(APIView):
    model = Launch
    serializer = LaunchesSerializer

    def get(self, request, format=None):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status = request.query_params.get('status')

        launches = self.model.objects.exclude(status='deleted').exclude(status='draft')

        if start_date and end_date:
            launches = launches.filter(formed_at__range=[start_date, end_date])

        if status:
            launches = launches.filter(status=status)

        serialized_requests = self.serializer(launches, many=True)
        return Response(serialized_requests.data)


class LaunchDetail(APIView):
    model = Launch
    serializer_class = LaunchDetailSerializer

    def get(self, request, launch_id, format=None):
        launch = get_object_or_404(self.model, launch_id=launch_id)
        serializer = self.serializer_class(launch)
        return Response(serializer.data)

    def put(self, request, launch_id, format=None):
        launch = get_object_or_404(self.model, launch_id=launch_id)
        serializer = self.serializer_class(launch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, launch_id, format=None):
        launch = get_object_or_404(self.model, launch_id=launch_id)
        launch.status = 'deleted'
        launch.save()
        return Response(self.serializer_class(launch).data)


class CreatorSave(APIView):
    model = Launch
    serializer_class = LaunchDetailSerializer

    def put(self, request, launch_id, format = None):
        Launch = get_object_or_404(self.model, launch_id=launch_id)
        if Launch.status != 'draft':
            return Response({'ERROR': 'Launch is not draft'}, status=status.HTTP_400_BAD_REQUEST)
        elif Launch.rocket is not None and Launch.date is not None:
            Launch.formed_at = datetime.date.today().isoformat()
            Launch.status = 'formed'
            Launch.save()
            return Response({'Status update': 'formed.'}, status = status.HTTP_200_OK)
        return Response({'ERROR': 'Check required fields: rocket, date.'}, status=status.HTTP_400_BAD_REQUEST)


class ModAccept(APIView):
    model = Launch
    serializer_class = LaunchDetailSerializer

    def put(self, request, launch_id, format = None):
        try:
            launch = Launch.objects.get(launch_id=launch_id)
        except Launch.DoesNotExist:
            return Response({'ERROR': 'Launch does not exist'}, status=status.HTTP_404_NOT_FOUND)

        update = request.data.get('new_status')
        if (update not in ['completed', 'rejected']) or (launch.status != 'formed'):
            return Response({'ERROR': f'Cannot change to {update} from {launch.status}'}, status=status.HTTP_400_BAD_REQUEST)

        moderator = user()
        if update == 'completed':
            launch.moderator = moderator
            launch.completed_at = timezone.now()

            satellites = LaunchSatellite.objects.filter(launch_id=launch)
            satorder = [sat.order for sat in satellites]

            launch.success = random() < 0.2

            if len(satorder) != len(set(satorder)):
                return Response({'ERROR': 'Order is not unique'}, status=status.HTTP_400_BAD_REQUEST)
            launch.status = 'completed'

        elif update == 'rejected':
            launch.moderator = moderator
            launch.completed_at = timezone.now()
            launch.status = 'rejected'
        launch.save()

        serializer = LaunchesSerializer(launch)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SatLaunch(APIView):
    model = LaunchSatellite
    serializer_class = SatLaunchSerializer

    def delete(self, request, satellite_id, launch_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id, launch_id=launch_id)
        satellite.delete()
        satellites = self.model.objects.filter(launch_id=launch_id)
        return Response(self.serializer_class(satellites, many=True).data)

    def put(self, request, satellite_id, launch_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id, launch_id=launch_id)
        serializer = self.serializer_class(satellite, data=request.data)
        if serializer.is_valid():
            serializer.save()
            satellites = self.model.objects.filter(launch_id=launch_id)
            return Response(self.serializer_class(satellites, many=True).data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    model = get_user_model()
    serializer_class = AuthUserSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_user = self.model.objects.create_user(
                username=serializer.validated_data.get('username'),
                password=serializer.validated_data.get('password'),
                is_superuser=serializer.validated_data.get('is_superuser'),
                is_staff=serializer.validated_data.get('is_staff'),
                email=serializer.validated_data.get('email'),
                first_name=serializer.validated_data.get('first_name'),
                last_name=serializer.validated_data.get('last_name'),
                date_joined=datetime.date.today().isoformat()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id, format = None):
        user = get_object_or_404(self.model, id=user_id)
        serializer = self.serializer_class(user, data=request.query_params, partial=True)
        if serializer.is_valid():
            current_password = request.data.get('current_password')
            if current_password:
                if not user.check_password(current_password):
                    return Response({"ERROR": f"Wrong pass."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            if 'password' in serializer.validated_data:
                user.set_password(serializer.validated_data.get('password'))
                user.save()
            return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    model = get_user_model()
    serializer = AuthUserSerializer

    def post(self, request, format=None):
        inp_password = request.query_params.get('password')
        inp_username = request.query_params.get('username')
        user = self.model.objects.get(username=inp_username)
        if user.check_password(inp_password):
            return Response({'authentification': 'success'}, status=status.HTTP_200_OK)
        return Response({'authentification': f'failed {user.username} {user.password} {inp_password}'}, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    model_class = get_user_model()
    serializer_class = AuthUserSerializer

    def post(self, request, format=None):
        return Response({'deauthorisation': 'complete'}, status=status.HTTP_401_UNAUTHORIZED)