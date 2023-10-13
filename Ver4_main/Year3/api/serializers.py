from rest_framework import serializers
from api.models import Room, Registration, RawSensorMonitor, SensorMonitor
from api.models import RawActuatorMonitor, ActuatorMonitor, ControlSetpoint, SetTimerHistory


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