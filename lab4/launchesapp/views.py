import datetime
import uuid
from random import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .minio import *
from .models import *
from .serializers import *
from .permissions import *
from .getUser import getUserBySession
import redis

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def user():
    try:
        user1 = CustomUser.objects.get(id=1)
    except:
        user1 = CustomUser(id=1, password=1234, email="email1", is_superuser=True, is_staff=True)
        user1.save()
    return user1

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
def login_view(request):
    username = request.data["email"]
    password = request.data["password"]
    user = authenticate(request, email=username, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)

        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")

def logout_view(request):
    logout(request._request)
    return Response({'status': 'Success'})

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request):
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            user = getUserBySession(self.request)
            if user == AnonymousUser():
                return Response({"detail": "Authentication required."}, status=401)
            else:
                try:
                    self.check_permissions(self.request)
                except Exception as e:
                    return Response({"detail": "You do not have permission to perform this action."}, status=403)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

class SatList(APIView):
    model = Satellite
    serializer = SatSerializer

    @swagger_auto_schema(
        operation_summary="Get satellite list",
        responses={200: SatSerializer(many=True)}
    )
    @method_permission_classes((IsAuth,))
    def get(self, request, format=None):
        searchText = request.query_params.get('SatelliteTitle', '')
        searchResult = Satellite.objects.filter(title__icontains=searchText)
        user1 = getUserBySession(request)
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

    @swagger_auto_schema(
        operation_summary="Create Satellite",
        request_body= SatSerializer,
        responses={201: SatSerializer(),
                   400: "Bad Request"}
    )
    @method_permission_classes((IsAdmin,))
    def post(self, request, format=None):
        serializer = self.serializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SatDetail(APIView):
    model = Satellite
    serializer = SatSerializer

    @swagger_auto_schema(
        operation_summary="Get satellite details",
        responses={200: serializer()}
    )
    @method_permission_classes((IsAuth,))
    def get(self, request, satellite_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id)
        serializer = self.serializer(satellite)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Satellite details update",
        request_body=serializer,
        responses={200: serializer()}
    )
    @method_permission_classes((IsAdmin,))
    def put(self, request, satellite_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id)
        serializer = self.serializer(satellite, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete Satellite",
        responses={
            204: openapi.Response(description="Satellite deleted"),
            404: openapi.Response(description="Satellite not found")
        }
    )
    @method_permission_classes((IsAdmin,))
    def delete(self, request, satellite_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id)
        result = del_pic(satellite)
        if 'error' in result.data:
            return result
        LaunchSat = LaunchSatellite.objects.filter(satellite_id=satellite)
        LaunchSat.delete()
        satellite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="Add Satellite to launch",
        request_body=serializer,
        responses={200: serializer()}
    )
    @method_permission_classes((IsAuth,))
    def post(self, request, satellite_id, format=None):
        user1 = getUserBySession(request)
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

@swagger_auto_schema(
        method="post",
        request_body=SatSerializer,
        operation_summary='Update Satellite Image',
        responses={
            200: SatSerializer(many=False),
            400: "Bad Request",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Get launches list",
        responses={200: serializer(many=True)}
    )
    @method_permission_classes((IsAuth,))
    def get(self, request, format=None):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status = request.query_params.get('status')

        launches = self.model.objects.exclude(status='deleted').exclude(status='draft')
        ##launches = launches.filter(creator_id=getUserBySession(request))

        if start_date and end_date:
            launches = launches.filter(formed_at__range=[start_date, end_date])

        if status:
            launches = launches.filter(status=status)

        serialized_requests = self.serializer(launches, many=True)
        return Response(serialized_requests.data)


class LaunchDetail(APIView):
    model = Launch
    serializer = LaunchDetailSerializer

    @swagger_auto_schema(
        operation_summary="Get launch details",
        responses={200: serializer()}
    )
    @method_permission_classes((IsAuth,))
    def get(self, request, launch_id, format=None):
        launch = get_object_or_404(self.model, launch_id=launch_id)
        serializer = self.serializer(launch)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Launch details update",
        request_body=serializer,
        responses={200: serializer()}
    )
    @method_permission_classes((IsAdmin,))
    def put(self, request, launch_id, format=None):
        launch = get_object_or_404(self.model, launch_id=launch_id)
        serializer = self.serializer(launch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete launch",
        responses={
            204: openapi.Response(description="Launch status set to deleted"),
            404: openapi.Response(description="Launch not found")
        }
    )
    @method_permission_classes((IsAdmin,))
    def delete(self, request, launch_id, format=None):
        launch = get_object_or_404(self.model, launch_id=launch_id)
        launch.status = 'deleted'
        launch.save()
        return Response(self.serializer(launch).data)


class CreatorSave(APIView):
    model = Launch
    serializer = LaunchDetailSerializer

    @swagger_auto_schema(
        operation_summary="Form drafted launch",
        request_body= serializer,
        responses={
            200: serializer(),
            400: openapi.Response(description="Wrong data"),
            404: openapi.Response(description="Launch not found")
        }
    )
    @method_permission_classes((IsManager,))
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
    serializer = LaunchDetailSerializer

    @swagger_auto_schema(
        operation_summary="Moderator accept form",
        request_body=serializer,
        responses={
            200: serializer(),
            400: openapi.Response(description="Wrong data"),
            403: openapi.Response(description="Access denied"),
            404: openapi.Response(description="Launch not found")
        }
    )
    @method_permission_classes((IsManager,))
    def put(self, request, launch_id, format = None):
        try:
            launch = Launch.objects.get(launch_id=launch_id)
        except Launch.DoesNotExist:
            return Response({'ERROR': 'Launch does not exist'}, status=status.HTTP_404_NOT_FOUND)

        update = request.data.get('new_status')
        if (update not in ['completed', 'rejected']) or (launch.status != 'formed'):
            return Response({'ERROR': f'Cannot change to {update} from {launch.status}'}, status=status.HTTP_400_BAD_REQUEST)

        moderator = getUserBySession(request)
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
    serializer = SatLaunchSerializer

    @swagger_auto_schema(
        operation_summary="Remove satellite from draft",
        responses={
            204: openapi.Response(description="Satellite removed"),
            404: openapi.Response(description="Provided satellite launch pair not found")
        }
    )
    @method_permission_classes((IsAuth,))
    def delete(self, request, satellite_id, launch_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id, launch_id=launch_id)
        satellite.delete()
        satellites = self.model.objects.filter(launch_id=launch_id)
        return Response(self.serializer(satellites, many=True).data)

    @swagger_auto_schema(
        operation_summary="Link details update",
        request_body=serializer,
        responses={
            202: serializer(),
            400: openapi.Response(description="Wrong data"),
            404: openapi.Response(description="Provided satellite launch pair not found")
        }
    )
    @method_permission_classes((IsAuth,))
    def put(self, request, satellite_id, launch_id, format=None):
        satellite = get_object_or_404(self.model, satellite_id=satellite_id, launch_id=launch_id)
        serializer = self.serializer(satellite, data=request.data)
        if serializer.is_valid():
            serializer.save()
            satellites = self.model.objects.filter(launch_id=launch_id)
            return Response(self.serializer(satellites, many=True).data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    model = get_user_model()
    serializer = AuthUserSerializer

    def post(self, request, format=None):
        serializer = self.serializer(data=request.data)
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
        serializer = self.serializer(user, data=request.query_params, partial=True)
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