from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from api.models import Room, Registration, RawSensorMonitor, SensorMonitor
from api.models import RawActuatorMonitor, ActuatorMonitor, ControlSetpoint


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
