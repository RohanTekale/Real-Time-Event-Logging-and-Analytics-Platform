from rest_framework import serializers
from .models import Event, UserProfile, SystemMetrics,MLInsight
from django.contrib.auth.models import User
from datetime import datetime



class Userserializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserProfile.ROLES, write_only=True)

    class Meta:
        model = User  # Changed from Model to model
        fields = ('id', 'username', 'email', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user, role=role)
        return user

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class SystemMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetrics
        fields = '__all__'

class AnalyticsSerializer(serializers.Serializer):
    events_per_second = serializers.FloatField()
    active_users = serializers.IntegerField()
    error_rate = serializers.FloatField()
    timestamp = serializers.DateTimeField()


class MLInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLInsight
        fields = '__all__'