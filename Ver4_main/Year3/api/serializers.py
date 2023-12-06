from rest_framework import serializers
from api.models import Room, Registration, RawSensorMonitor, SensorMonitor
from api.models import RawActuatorMonitor, ActuatorMonitor, ControlSetpoint, SetTimerHistory, NodeConfigBuffer
from api.models import AqiRef
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
   class Meta:
        model = User
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class RegistrationSerializer(serializers.ModelSerializer):
   class Meta:
      model = Registration
      fields = "__all__"

class RawSensorMonitorSerializer(serializers.ModelSerializer):
   class Meta:
      model = RawSensorMonitor
      fields = "__all__"

class RawActuatorMonitorSerializer(serializers.ModelSerializer):
   class Meta:
      model = RawActuatorMonitor
      fields = "__all__"

class SetTimerHistorySerializer(serializers.ModelSerializer):
    class Meta:
       model = SetTimerHistory
       fields = "__all__"

class NodeConfigBufferSerializer(serializers.ModelSerializer):
    class Meta:
       model = NodeConfigBuffer
       fields = "__all__"

class AqiRefSerializer(serializers.ModelSerializer):
   class Meta:
      model = AqiRef
      fields = "__all__"


##
# @brief Override the TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
       data = super(MyTokenObtainPairSerializer, self).validate(attrs)
       data["is_superuser"] = '1' if self.user.is_superuser else '0'
       return data