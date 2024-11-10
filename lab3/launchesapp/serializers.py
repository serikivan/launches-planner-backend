from .models import Satellite, Launch, LaunchSatellite, AuthUser
from rest_framework import serializers

class SatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = '__all__'

class FullSatSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Satellite
        fields = ["satellite_id", "title", "description", "status", "image_url", "weight", "orbit", "expected_date", "user"]

class UserSerializer(serializers.ModelSerializer):
    sat_set = SatSerializer(many=True, read_only=True)
    class Meta:
        model = AuthUser
        fields = ["id", "first_name", "last_name", "sat_set"]

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'

class SatLaunchSerializer(serializers.ModelSerializer):
    Sat = SatSerializer(source = 'satellites', read_only=True)
    class Meta:
        model = LaunchSatellite
        fields = ["satellite_id", "Sat", "order"]

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