from django.db import models

# Create your models here.
from pyexpat import model
from unittest.util import _MAX_LENGTH
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL     #auth.User        #trying to presnet user name to Sensor model

# Create your models here.

#>>>>>>>>>>>>>>>>>>>>>>>>can not migrate table to postgresql<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# class User(models.Model):
#    user_id = models.IntegerField(primary_key = True)
#    user_name = models.CharField(max_length=50)
#    email = models.CharField(max_length=255)

class Sensor(models.Model):
   user = models.ForeignKey(User, default = 1, null = True, on_delete = models.SET_NULL)
   i = models.BigAutoField(primary_key = True)
   time = models.BigIntegerField()
   temperature = models.FloatField()
   humidity  = models.FloatField()
   light = models.FloatField()
   dust = models.FloatField()
   sound = models.FloatField()
   red = models.SmallIntegerField()
   green = models.SmallIntegerField()
   blue = models.SmallIntegerField()
   co2 = models.SmallIntegerField()
   tvoc = models.SmallIntegerField()
   motion = models.SmallIntegerField()
   id = models.SmallIntegerField()


