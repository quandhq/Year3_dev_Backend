from urllib import request
from django.shortcuts import render,redirect
from django import http
from api import models
from api import serializers
from django.http import HttpResponse
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.response import Response 
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
from api.models import Room, Registration, RawSensorMonitor
from api.serializers import RoomSerializer, RegistrationSerializer
from api.serializers import RawSensorMonitorSerializer ,RawActuatorMonitorSerializer 

print("This is in view.py")

# Create your views here.


#______________________________________view_for_testing_authentication______________________________________________

@api_view(["POST", "GET"])
# @permission_classes([permissions.IsAuthenticated])
# @authentication_classes([authentication.TokenAuthentication])
def getAuthenticationSensorSecondlyData(request , *args, **kwargs):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   print(request.GET.get("farm_id"))
   print("This is in API secondly data")
   query_sample = models.RawSensorMonitor.objects.filter(node_id_id=1).order_by('-time')[:15]
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
   return Response(new_query, status=status.HTTP_200_OK)      
   
   

#_________________________________________________end_______________________________________________________________

#____________________________________________________________________test for return data with function-base-view__________________________

###############################################################
# @brief: view for sending secondly data for chart on front-end
###############################################################
@api_view(["POST", "GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])
# @permission_classes([permissions.IsAuthenticated])
def getSensorSecondlyData(request , *args, **kwargs):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   print(request.GET.get("farm_id"))
   print("This is in API secondly data")
   query_sample = None
   if models.RawSensorMonitor.objects.all().count() > 15:
      query_sample = models.RawSensorMonitor.objects.filter(node_id_id=1).order_by('-time')[:15]
   else:
      return JsonResponse({"co2":[], "temp":[],"hum":[], "time":[]})
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
   # return Response(new_query, status=status.HTTP_200_OK)  
   return JsonResponse(new_query)    
      

#___________________________________________________________________end__________________________________________________________________

            
from .djangoClientSendSpeed import insert_to_table_ControlSetpoint
from .djangoClientSendSpeed import send_setpoint_to_mqtt
from .djangoClientSendSpeed import client as setpoint_client            

###############################################################
# @brief: View for get set point value from Frontend, process
#         it, save it in database, and send it to gateway.
###############################################################
@api_view(["POST"])
def send_setpoint(request, *arg, **kwargs):
   print(request.GET)
   farm_id = request.GET.get("farm_id")
   print(farm_id)
   monitor_data = json.loads(request.body)
   print(monitor_data)
   # print(request.data)
   insert_to_table_ControlSetpoint(monitor_data)
   send_setpoint_to_mqtt(setpoint_client, monitor_data, farm_id)
   return Response({"Result": "Successful send setpoint"}, status=status.HTTP_200_OK)      

# #*brief: view sending setPoint to sensors
# #*param: request
# #        kwargs - contain "param" which is set point to be sent to sensors
# #*ouput: NULL
# @api_view(["POST"])
# def send_set_point(request, *args, **kwargs):
#    # new_set_point = SetPoint()
#    # setPoint = kwargs["param"]
#    # new_set_point.run(setPoint)
#    # run(setPoint)
#    data = json.loads(request.body)  #get the data that attached with reqeust from front-end
#    print("RECEIVE data from MONITORING FRONT_END")
#    print(data)
#    # insert_to_table_ControlSetpoint(data)
#    send_speed_setpoint()
#    return JsonResponse({'data': 'Get setpoint successfully'})
   
#*brief: this function was used to test sending setpoint to sensor but not working, 
#        __________________CURRENLY NOT USING THIS_____________________
@api_view(["POST","GET"])
def set_level(request, *args, **kwargs):
   param = kwargs["level"]
   print("the level is " + str(param))
   response = {"result": "successful", "level": str(param)}
   return JsonResponse(response)


###############################################################
# @brief: View for send heatmap data to frontend, using kriging 
#         algorithm.
###############################################################
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
   return Response(response, status=status.HTTP_200_OK)     


# def index(request):
#    mydata = models.Sensor.objects.all().values()
#    print(mydata[0])
#    context = {
#     'insert_me': mydata,
#    }		
#    #CÁI INSERT_ME CHÍNH LÀ CÁI VARIABLE Ở TRONG CÁI FILE INDEX.HTML TRÊN KIA

#    return render(request, "api\main.html", context=context)

###############################################################
#@brief: This view is used to test sending a html template with 
#        data embedded in it to front-end, currently not using, 
#        don't mind this. 
###############################################################
def index(request):
   mydata = models.RawSensorMonitor.objects.all().values()
   # print(mydata[0])
   context = {
    'insert_me': mydata,
   }	
   #CÁI INSERT_ME CHÍNH LÀ CÁI VARIABLE Ở TRONG CÁI FILE INDEX.HTML TRÊN KIA
   send_setpoint_to_mqtt(setpoint_client, {"data": "test"})
   # return Response()
   return render(request, "api/main.html", context=context)



#_____________________________testing API_____________________________________
"""
*brief: this one is for testing "redirect" function
"""
@api_view(["GET", "POST"])
def test_redirect(request,*args, **kwargs):
   print(request.GET)
   print("_______________________________________________")
   return redirect("_get_index")

###############################################################
#@brief: TEST VIEW/This view is for testing url dispatching.
###############################################################
@api_view(["POST"])
def test_url_dispatching(request, *arg, **kwargs):
   print(request.GET)
   farm_id = request.GET.get("farm_id")
   print(farm_id)
   monitor_data = json.loads(request.body)
   print(monitor_data)
   # print(request.data)
   insert_to_table_ControlSetpoint(monitor_data)
   send_setpoint_to_mqtt(setpoint_client, monitor_data, farm_id)
   
   return JsonResponse({"Result": "Successful"})


###############################################################
#@brief: This view is for send history chart data to frontend.
###############################################################
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
         return Response(result_data, status=status.HTTP_200_OK)      
      elif(option == "month"):
         result_data = getOptionMonthData(time_start, time_end)
         return Response(result_data, status=status.HTTP_200_OK)       
      elif(option == "year"):
         result_data = getOptionYearData(time_start, time_end)
         return Response(result_data, status=status.HTTP_200_OK)       
      else:
         return Response({"Response": "Option provided is NOT valid"}, status=status.HTTP_400_BAD_REQUEST)
   else:
      return Response({"Response": "Option is not provided"}, status=status.HTTP_400_BAD_REQUEST)


#_____________________view for websocket________________________
"""
Here we will create a login page for the frontend part and from 
there we will make a post request with username and password 
then the backend view will validate whether the user is there or not, 
if the user is there then the token will be sent from the backend 
in the response and we will create a socket connection from there. 
For this, we will need a views.py which will have will handle login 
and send the token. 

The uses of different modules are described below:

1. Response: This is the response object which is sent from the API view
2. api_view: It converts the normal Django view to the API view.
3. authenticate: This will return the user, based on the username and password.
"""

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
 
 
@api_view(["POST"])
def loginWebsocket(request, *args, **kwargs):
   data = json.loads(request.body)
   username = data["username"]
   print(username)
   password = data["password"]
   print(password)
   try:
         user = authenticate(username=username, password=password)
   except:
         user = None
   if not user:
      print("No such User")
      return Response({
         "user_not_found": "There is no user with this username and password !"
               }, status=status.HTTP_400_BAD_REQUEST)
   token = Token.objects.get(user=user)
   return Response({
                     "token": token.key,
                  }, status=status.HTTP_200_OK)
#_____________________________END view for websocket__________________________________


#######################################################################
#@brief: This view is for get room data for Landing page in
#        frontend.
#@return: example:
         # {
         #    "farm": [
         #       {
         #             "id": 1,
         #             "construction_name": "farm",
         #             "x_length": 18,
         #             "y_length": 8,
         #             "node_array": [
         #                {
         #                   "id": 10,
         #                   "mac_address": "ZX:CV:BN:MN",
         #                   "function": "actuator",
         #                   "room_id": 1
         #                },
         #                {
         #                   "id": 1,
         #                   "mac_address": "AB:CD:EF:GH",
         #                   "function": "sensor",
         #                   "room_id": 1
         #                }
         #             ]
         #       },
         #       {
         #             "id": 2,
         #             "construction_name": "farm",
         #             "x_length": 18,
         #             "y_length": 8,
         #             "node_array": [
         #                {
         #                   "id": 100,
         #                   "mac_address": "PO:IU:YT:RE",
         #                   "function": "senor",
         #                   "room_id": 2
         #                }
         #             ]
         #       }
         #    ],
         #    "building": []
         # }
#######################################################################
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
@api_view(["GET"])
def getRoomData(request, *args, **kwargs):
   Room_all_data = Room.objects.all()  #!< get all records in Room table
   RoomSerializer_instance = RoomSerializer(Room_all_data, many=True)   #!< HAVE TO ADD "many=True"
   # RegistrationSerializer_inst
   response_dict = {"farm": [], "building": []}
   for element in RoomSerializer_instance.data:
      if element["construction_name"] == "farm":
         #!v get all node data that is in this room
         node_data_in_room_element = Registration.objects.filter(room_id=element["id"])
         #!v create one more field "node_array" int this element
         element["node_array"] = RegistrationSerializer(node_data_in_room_element, many=True).data #!< HAVE TO ADD "many=True"
         response_dict["farm"].append(element)
      elif element["construction_name"] == "building":
         #!v get all node data that is in this room
         node_data_in_room_element = Registration.objects.filter(room_id=element["id"])
         #!v create one more field "node_array" int this element
         element["node_array"] = RegistrationSerializer(node_data_in_room_element, many=True).data #!< HAVE TO ADD "many=True"
         response_dict["building"].append(element)
   return Response(response_dict, status=status.HTTP_200_OK)
   
#######################################################################
# @brief This view is for get data for InformationTag component in 
#        frontend.
# @return Example:
#
#######################################################################
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
@api_view(["GET"])
def getRoomInformationTag(request, *args, **kwargs):
   room_id = request.GET["room_id"]
   print(room_id)
   if RawSensorMonitor.objects.count() != 0:
      data = RawSensorMonitor.objects.order_by('-time')[0]     #!< get the latest record in model according to timeline
      RawSensorMonitorSerializer_instance = RawSensorMonitorSerializer(data)
      return Response(RawSensorMonitorSerializer_instance.data, status=status.HTTP_200_OK)
   else:
      return Response({"message": "No content!"}, status=status.HTTP_200_OK)