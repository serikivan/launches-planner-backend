from collections import OrderedDict
from .models import Satellite, Launch, LaunchSatellite, CustomUser
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_staff', 'is_superuser']

class SatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = ["satellite_id", "title", "description", "status",
                  "image_url", "weight", "orbit", "expected_date", "user"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields


class ShortSatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = ["satellite_id", "title", "image_url", "weight"]

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class SatLaunchSerializer(serializers.ModelSerializer):
    Sat = ShortSatSerializer(source = 'satellite', read_only=True)
    class Meta:
        model = LaunchSatellite
        fields = ["Sat", "order"]

class LaunchesSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    moderator = serializers.StringRelatedField()

    class Meta:
        model = Launch
        fields = '__all__'

class LaunchDetailSerializer(serializers.ModelSerializer):
    satellites = SatLaunchSerializer(source = 'linked_launches',  many = True, read_only = True)
    creator = serializers.StringRelatedField()
    moderator = serializers.StringRelatedField()

    class Meta:
        model = Launch
        fields = ["launch_id", "rocket", "created_at", "formed_at",
                  "completed_at", "status", "creator", "moderator", "satellites"]