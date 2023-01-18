from urllib import request
from django.shortcuts import render
from django import http
from rest_framework import mixins
from rest_framework import generics
from api import models
from api import serializers
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
import numpy as np
from .kriging import Kriging

# Create your views here.


# _______________________implementation for view publishing setpoint data to mqtt___________________
import paho.mqtt.client as mqtt
import json
import random 
import time 
import calendar
import datetime


mqtt_broker = "broker.hivemq.com"
mqtt_port = 1883
topic = "Year3"

client_id = f'python-mqtt-{random.randint(0,1000)}'
# client_id = 'clientId-dhhSHVoTBA'

def connect_mqtt():
   def on_connect(client, userdata, flag, rc):
      if rc == 0:
         print("Connected to MQTT Brocker!")
      else:
         print(f"Failed to connect, return code {rc}")
      
   client = mqtt.Client(client_id)
   client.on_connect = on_connect
   client.connect(mqtt_broker, mqtt_port, 60)
   return client

def publish(client, setPoint):
   date = datetime.datetime.utcnow()
   utc_time = calendar.timegm(date.utctimetuple())

   new_data = {
                  'operator':'sendSetPoint',
                  'infor':{
                     'time':utc_time,
                     "status":setPoint,
                  }
               }

   time.sleep(2)
   msg = json.dumps(new_data)
   result = client.publish(topic, msg)
   status = result[0]
   if status == 0:
      print(f"Succesfully send '{msg}' to topic '{topic}'")
   else:
      print(f"Fail to send '{msg}' to topic '{topic}'")

def run(setPoint):
   client = connect_mqtt()
   client.loop_start()
   publish(client, setPoint)
# ____________________________________________________end____________________________________________________









class SensorMixinView(mixins.ListModelMixin,
                        generics.GenericAPIView):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   serializer_class = serializers.SensorSerializer
   def get(self, request , *args, **kwargs):
      dict = kwargs
      print(dict['id'])
      self.queryset = models.Sensor.objects.filter(id=dict['id']).order_by('-time')[:15]
      print(self.queryset)
      print("YOLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
      print(args, kwargs)
      return self.list(request, *args, **kwargs)     
   
@api_view(["POST","GET"])
def set_level(request, *args, **kwargs):
   param = kwargs["level"]
   print("the level is " + str(param))
   response = {"result": "successful", "level": str(param)}
   return JsonResponse(response)



@api_view(["POST","GET"])           #view for sending data to heatmap on front-end
def kriging(request, *args, **kwargs):
   default_X = [0,0,6.25,8.75]          #default axis x of id 3,4,5,6
   default_Y = [0.25,2.25,1.25,0.25]     #default axis y of id 3,4,5,6
   #--------------------------------value of all known-points------------------------------
   Var = [34.43, 22.03, 28.76, 24.78]    #this is default-type value of all known-points
   #---------------------------------------------------------------------------------------
   id1 = models.Sensor.objects.filter(id=1).order_by('-time')[0]
   id2 = models.Sensor.objects.filter(id=2).order_by('-time')[0]
   id3 = models.Sensor.objects.filter(id=3).order_by('-time')[0]
   id4 = models.Sensor.objects.filter(id=4).order_by('-time')[0]
   new_var = [id1.temperature, id2.temperature, id3.temperature, id4.temperature]
   print("-------------------------------------------------")
   print(new_var)
   k = Kriging(100,80, new_var, default_X,default_Y)
   test = k.interpolation()
   response = {'data': test[2], 'resolutionX': test[0], 'resolutionY': test[1]}
   return JsonResponse(response)


# def index(request):
#    mydata = models.Sensor.objects.all().values()
#    print(mydata[0])
#    context = {
#     'insert_me': mydata,
#    }		
#    #CÁI INSERT_ME CHÍNH LÀ CÁI VARIABLE Ở TRONG CÁI FILE INDEX.HTML TRÊN KIA

#    return render(request, "api\main.html", context=context)

def index(request):
   mydata = models.Sensor.objects.all().values()
   print(mydata[0])
   context = {
    'insert_me': mydata,
   }		
   #CÁI INSERT_ME CHÍNH LÀ CÁI VARIABLE Ở TRONG CÁI FILE INDEX.HTML TRÊN KIA

   return render(request, "api/form.html", context=context)
 
#*brief: view sending setPoint to sensors
#*param: request
#        kwargs - contain "param" which is set point to be sent to sensors
#*ouput: NULL
def send_set_point(request, *args, **kwargs):
   setPoint = kwargs["param"]
   run(setPoint)
   return JsonResponse({'data': 'response successfully'})

