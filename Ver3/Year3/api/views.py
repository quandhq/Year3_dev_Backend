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
import pandas as pd

print("This is in view.py")

# Create your views here.


#______________________________________view_for_testing_authentication______________________________________________
#_______________________________________CURRENLTY NOT USING THIS__________________________________________
@api_view(["POST", "GET"])
# @permission_classes([permissions.IsAuthenticated])
# @authentication_classes([authentication.TokenAuthentication])
def getAuthenticationSensorSecondlyData(request , *args, **kwargs):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   print(request.GET.get("farm_id"))
   print("This is in API secondly data")
   query_sample = models.RawSensorMonitor.objects.filter(node_id=1).order_by('-time')[:15]
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


###############################################################
# @brief: view for sending secondly data for chart on front-end
# @return: The json-formatted data that is returned to front-end
#           will have a for like this:
#           {"green":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "hum":[91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0],
#              "tvoc":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "sound":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "red":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "light":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "co2":[6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666],
#              "blue":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "motion":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "time":[20,20,20,20,20,20,20,20,20,20,20,20,20,20,20],
#              "temp":[32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0],
#              "dust":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null]}
###############################################################
@api_view(["POST", "GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])
# @permission_classes([permissions.IsAuthenticated])
def getSensorSecondlyData(request , *args, **kwargs):    
   room_id = request.GET.get("room_id")
   print(room_id)
   print("This is in API secondly data")
   parameter_key_list = ["co2", "temp", "hum", "light", 
                         "dust", "sound", "red", "green", 
                         "blue", "tvoc", "motion", "time"]
   if models.RawSensorMonitor.objects.filter(room_id=room_id).count() > 15:
      query_sample = models.RawSensorMonitor.objects.filter(room_id=room_id).order_by('-time')[:15]
      data_serializer = RawSensorMonitorSerializer(query_sample, many=True,).data #!< have to add many=True
      print(data_serializer)
      data_serializer.reverse()
      data_return = {}
      for i in parameter_key_list:
         data_return[i] = []
      for i in data_serializer:  #!< iterate through 15 elements
         for j in data_return: #!< iterate through all keys of data_return
            if j in i:          #!< if i contain the key "j"
               data_return[j].append(i[j])
            else:
               data_return[j].append(0)
      return Response(data_return, status=status.HTTP_200_OK)    
   else:
      result_return = {i:[] for i in parameter_key_list}
      return Response(result_return, status=status.HTTP_200_OK)
      

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
   monitor_data = json.loads(request.body)
   print(monitor_data)
   # print(request.data)
   insert_to_table_ControlSetpoint(monitor_data)
   send_setpoint_to_mqtt(setpoint_client, monitor_data)
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
      option = request.GET.get("option")  #!< query parameter inside an URL is a string not a integer
      room_id = request.GET.get("room_id")   #!< query parameter inside an URL is a string not a integer
      node_id = request.GET.get("node_id")   #!< query parameter inside an URL is a string not a integer
      time_start = request.GET.get("time_start")   #!< query parameter inside an URL is a string not a integer
      time_end = request.GET.get("time_end") #!< query parameter inside an URL is a string not a integer
      print(str(option), int(room_id), int(node_id), int(time_start), int(time_end))
      result_data = None
      if(option == "day"): 
         result_data = getOptionDayData(int(time_start), int(room_id), int(node_id))
         return Response(result_data, status=status.HTTP_200_OK)      
      elif(option == "month"):
         result_data = getOptionMonthData(int(time_start), int(time_end), int(room_id), int(node_id))
         return Response(result_data, status=status.HTTP_200_OK)       
      elif(option == "year"):
         result_data = getOptionYearData(int(time_start), int(time_end), int(room_id), int(node_id))
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
         node_data_in_room_element = Registration.objects.filter(room_id=element["room_id"])
         #!v create one more field "node_array" in this element
         element["node_array"] = RegistrationSerializer(node_data_in_room_element, many=True).data #!< HAVE TO ADD "many=True"
         response_dict["farm"].append(element)
      elif element["construction_name"] == "building":
         #!v get all node data that is in this room
         node_data_in_room_element = Registration.objects.filter(room_id=element["room_id"])
         #!v create one more field "node_array" int this element
         element["node_array"] = RegistrationSerializer(node_data_in_room_element, many=True).data #!< HAVE TO ADD "many=True"
         response_dict["building"].append(element)
   return Response(response_dict, status=status.HTTP_200_OK)
   
#######################################################################
# @brief This view is for get data for InformationTag component in 
#        frontend.
# @return Example:
               # {
               #    "time": 1076,
               #    "co2": [
               #       12344
               #    ],
               #    "temp": [
               #       34
               #    ],
               #    "hum": [
               #       93
               #    ]
               # }
#           
#######################################################################
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
@api_view(["GET"])
def getRoomInformationTag(request, *args, **kwargs):
   room_id = request.GET["room_id"]
   print(room_id)
   if RawSensorMonitor.objects.count() != 0:
      # 1.Get all node_id s that belong to this room
      if Registration.objects.filter(room_id=room_id, function="sensor").count() == 0:
         parameter_key_list = {"co2", "temp", "hum", "light", "dust", "sound", "red", "green", "blue", "tvoc", "motion"}
         average_data_to_return = {}
         for i in parameter_key_list:
            average_data_to_return[i] = 0
            average_data_to_return["time"] = 0
            return Response(average_data_to_return, status=status.HTTP_200_OK)
      all_node_id_of_this_room_id = Registration.objects.filter(room_id=room_id, function="sensor")
      RegistrationSerializer_instance = RegistrationSerializer(all_node_id_of_this_room_id, many=True)   #!< Have to add many=True
      all_node_id_of_this_room_id_list = [ i["node_id"] for i in RegistrationSerializer_instance.data]
      print(all_node_id_of_this_room_id_list)
      # 2.get the latest data for each node_id
      latest_data_of_each_node_id_in_this_room = []
      for each_node_id in all_node_id_of_this_room_id_list:
         if RawSensorMonitor.objects.filter(room_id=room_id, node_id=each_node_id).exists():   #!< if records of this node_id exist ...
            data_of_this_node_id = RawSensorMonitor.objects.filter(room_id=room_id, node_id=each_node_id).order_by('-time')[0]  #!< get the latest record of this node_id
            latest_data_of_each_node_id_in_this_room.append(RawSensorMonitorSerializer(data_of_this_node_id).data)
         else:
            continue
      # 3. get the average data of them
      parameter_key_list = {"co2", "temp", "hum", "light", "dust", "sound", "red", "green", "blue", "tvoc", "motion"}
      average_data_to_return = {}
      # for element in latest_data_of_each_node_id_in_this_room:
      df = pd.DataFrame(latest_data_of_each_node_id_in_this_room)
      df.sort_values(by="time", ascending=False, inplace=True, )
      average_data_to_return["time"] = df.iloc[0]["time"]   #!< get the time of the latest record
      average_df = df.mean(numeric_only = True,)   #!< calculate average value of all column existing in dataframe
      for para in parameter_key_list:
         if para in average_df:
            if para not in average_data_to_return:
               average_data_to_return[para] = []
               average_data_to_return[para].append(int(average_df[para]))
            else:
               average_data_to_return[para].append(int(average_df[para]))
         else:
            continue
      # 5. Get nodes information
      sensor_node_information_in_this_room_list = RegistrationSerializer(Registration.objects.filter(room_id=room_id, function="sensor"), many=True).data #!< have to add many=True
      actuator_node_information_in_this_room_list = RegistrationSerializer(Registration.objects.filter(room_id=room_id, function="actuator"), many=True).data  #!< have to add many=True
      average_data_to_return["node_info"] = {"sensor": sensor_node_information_in_this_room_list,
                                             "actuator": actuator_node_information_in_this_room_list}
      # 6. Get room size 
      room_size_data = RoomSerializer(Room.objects.filter(room_id=room_id), many=True).data #!< have to include many=True
      average_data_to_return["room_size"]

      return Response(average_data_to_return, status=status.HTTP_200_OK)
      data = RawSensorMonitor.objects.order_by('-time')[0]     #!< get the latest record in model according to timeline
      RawSensorMonitorSerializer_instance = RawSensorMonitorSerializer(data)
      return Response(RawSensorMonitorSerializer_instance.data, status=status.HTTP_200_OK)
   else:
      return Response({"message": "No content!"}, status=status.HTTP_200_OK)