from urllib import request
from django.shortcuts import render,redirect
from django import http
from api import models
from api import serializers
from django.http import HttpResponse
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status as RestFrameworkStatus
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.response import Response as RestFrameworkResponse
from django.http import JsonResponse
import numpy as np
from .kriging import Kriging
from .SetPoint import SetPoint
from rest_framework import authentication, permissions
from rest_framework_simplejwt import authentication as jwtauthentication
import json
import psycopg2
import multiprocessing
import datetime
import calendar

print("This is in view.py")

# Create your views here.

@api_view(["POST", "GET"])
# @permission_classes([permissions.IsAuthenticated])
# @authentication_classes([authentication.TokenAuthentication])
def getAuthenticationSensorSecondlyData(request , *args, **kwargs):
   print(request.GET.get("farm_id"))
   print("This is in API secondly data")
   query_sample = models.SensorMonitor.objects.filter(node_id_id=1).order_by('-time')[:15]
   new_query = {"co2":[], "temp":[],"hum":[], "time":[]}
   for i in query_sample:
      new_query["co2"].append(i.co2)
      new_query["temp"].append(i.temp)
      new_query["hum"].append(i.hum)
      new_query["time"].append(i.time)
   #reverse all array in new_query
   for i in new_query:
      new_query[i].reverse()
   print(query_sample[0].time)
   print(args, kwargs)
   # return self.list(request, *args, **kwargs)
   return RestFrameworkResponse(new_query, status=RestFrameworkStatus.HTTP_200_OK)      

#brief: view for sending secondly data for chart on front-end
@api_view(["POST", "GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])
# @permission_classes([permissions.IsAuthenticated])
def getSensorSecondlyData(request , *args, **kwargs):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   print(request.GET.get("farm_id"))
   print("This is in API secondly data")
   query_sample = models.SensorMonitor.objects.filter(node_id_id=1).order_by('-time')[:15]
   new_query = {"co2":[], "temp":[],"hum":[], "time":[]}
   for i in query_sample:
      new_query["co2"].append(i.co2)
      new_query["temp"].append(i.temp)
      new_query["hum"].append(i.hum)
      new_query["time"].append(i.time)
   #reverse all array in new_query
   for i in new_query:
      new_query[i].reverse()
   print(query_sample[0].time)
   print(args, kwargs)
   return RestFrameworkResponse(new_query, status=RestFrameworkStatus.HTTP_200_OK)      
      

#___________________________________________________________________end__________________________________________________________________

            
from .djangoClientSendSpeed import insert_to_table_ControlSetpoint
from .djangoClientSendSpeed import send_setpoint_to_mqtt
from .djangoClientSendSpeed import client as setpoint_client            

@api_view(["POST"])
def send_setpoint(request, *arg, **kwargs):
   print(request.GET)
   farm_id = request.GET.get("farm_id")
   print(farm_id)
   monitor_data = json.loads(request.body)
   print(monitor_data)
   insert_to_table_ControlSetpoint(monitor_data)
   send_setpoint_to_mqtt(setpoint_client, monitor_data, farm_id)
   return RestFrameworkResponse({"Result": "Successful send setpoint"}, status=RestFrameworkStatus.HTTP_200_OK)      
   
#*brief: this function was used to test sending setpoint to sensor but not working, 
#        __________________CURRENLY NOT USING THIS_____________________
@api_view(["POST","GET"])
def set_level(request, *args, **kwargs):
   param = kwargs["level"]
   print("the level is " + str(param))
   response = {"result": "successful", "level": str(param)}
   return JsonResponse(response)


#*brief: view for sending data to generate heatmap on front-end
@api_view(["POST","GET"])           
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
   response = {'data': test[2], 'resolutionX': k.resolutionX, 'resolutionY': k.resolutionY}
   return RestFrameworkResponse(response, status=RestFrameworkStatus.HTTP_200_OK)     


from .processDataChart import getOptionDayData, getOptionMonthData, getOptionYearData
@api_view(["POST", "GET"])
def historyChart(request, *args, **kwargs):
   if("option" in request.GET):
      option = request.GET.get("option")
      farm_id = request.GET.get("farm_id")
      time_start = int(request.GET.get("time_start"))
      time_end = int(request.GET.get("time_end"))
      print(option, farm_id, time_start, time_end)
      result_data = None
      if(option == "day"): 
         result_data = getOptionDayData(time_start)
         return RestFrameworkResponse(result_data, status=RestFrameworkStatus.HTTP_200_OK)      
      elif(option == "month"):
         result_data = getOptionMonthData(time_start, time_end)
         return RestFrameworkResponse(result_data, status=RestFrameworkStatus.HTTP_200_OK)       
      elif(option == "year"):
         result_data = getOptionYearData(time_start, time_end)
         return RestFrameworkResponse(result_data, status=RestFrameworkStatus.HTTP_200_OK)       
      else:
         return RestFrameworkResponse({"Response": "Option provided is NOT valid"}, status=RestFrameworkStatus.HTTP_400_BAD_REQUEST)
   else:
      return RestFrameworkResponse({"Response": "Option is not provided"}, status=RestFrameworkStatus.HTTP_400_BAD_REQUEST)

@api_view(["POST", "GET"])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def getAuthentaicationSensorSecondlyData(request , *args, **kwargs):   
   dict = kwargs
   print(dict['id'])
   query_sample = models.SensorMonitor.objects.filter(id=dict['id']).order_by('-time')[:15]
   new_query = {"temp":[],"hum":[],"co2":[], "time":[]}
   for i in query_sample:
      new_query["temp"].append(i.temperature)
      new_query["hum"].append(i.humidity)
      new_query["co2"].append(i.co2)
      new_query["time"].append(i.time)
   for i in new_query:
      new_query[i].reverse()
   print(query_sample[0].time)
   print(args, kwargs)
   return JsonResponse(new_query)      
