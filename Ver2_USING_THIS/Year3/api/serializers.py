from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from api import models

class SensorSerializer(serializers.ModelSerializer):
   class Meta:
      pass
      # model = models.Sensor
      # # fields = ['time', 'temperature', 'humidity', 'light', 'dust', 'sound', 'red', 'green', 'blue', 'co2', 'tvoc', 'id']
      # fields = '__all__'