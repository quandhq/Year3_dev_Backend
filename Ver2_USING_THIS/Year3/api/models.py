from django.db import models

# Create your models here.
from pyexpat import model
from unittest.util import _MAX_LENGTH
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL     #auth.User    

# Create your models here.

# class User(models.Model):
#    user_id = models.IntegerField(primary_key = True)
#    user_name = models.CharField(max_length=50)
#    email = models.CharField(max_length=255)

# class Sensor(models.Model):
#    user = models.ForeignKey(User, default = 1, null = True, on_delete = models.SET_NULL)
#    i = models.BigAutoField(primary_key = True)
#    time = models.BigIntegerField()
#    temperature = models.FloatField()
#    humidity  = models.FloatField()
#    light = models.FloatField()
#    dust = models.FloatField()
#    sound = models.FloatField()
#    red = models.SmallIntegerField()
#    green = models.SmallIntegerField()
#    blue = models.SmallIntegerField()
#    co2 = models.SmallIntegerField()
#    tvoc = models.SmallIntegerField()
#    motion = models.SmallIntegerField()
#    id = models.SmallIntegerField()

class Registration(models.Model):
   id = models.IntegerField(primary_key=True, null=False)
   mac_address = models.TextField()

class SensorMonitor(models.Model):
   id = models.BigAutoField(primary_key=True,)
   node_id = models.ForeignKey(Registration, 
                     verbose_name=("refering to id of node registered in Registration table"), 
                     on_delete=models.CASCADE,
                     null=False,
                     )
   co2 = models.SmallIntegerField()
   temp = models.FloatField()
   hum  = models.FloatField()
   time = models.BigIntegerField()
   def __str__(self):
      return self.temp

class ActuatorMonitor(models.Model):
   id = models.BigAutoField(primary_key=True)
   node_id = models.ForeignKey(Registration, 
                     verbose_name=("refering to id of node registered in Registration table"), 
                     on_delete=models.CASCADE,
                     null=False,
                     )
   speed = models.SmallIntegerField()
   state = models.SmallIntegerField()
   time = models.BigIntegerField()
   def __str__(self):
      return self.speed

class ControlSetpoint(models.Model):
   id = models.BigAutoField(primary_key=True)
   node_id = models.ForeignKey(Registration,
                              verbose_name=("Refering to value that need to set for actuator"),
                              on_delete=models.CASCADE,
                              null=False,                               
                              )
   option = models.TextField()
   aim = models.TextField()
   value = models.FloatField()
   time = models.BigIntegerField()
   def __str__(self):
      return self.aim
   
