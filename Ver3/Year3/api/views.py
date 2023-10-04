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
import math
import time

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
# @brief: view for sending secondly data for chart on front-
# @paras: 
#        url:  "http://127.0.0.1:8000/api/v1.1/monitor/data?room_id=1&filter=1&node_id={node_id}"
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
    room_id = int(request.GET.get("room_id"))   #!< the query parameter is in string form
    filter = int(request.GET.get("filter"))
    node_id = int(request.GET.get("node_id"))
    print(node_id)
    print(filter)
    dict_filter = {"1D": 1, "1W": 2, "1M": 3, "6M": 4, "1Y": 5}
    #Notice that: the timestamp in database is the utc timestamp + 7hour
    #Our local time stamp is faster than than the utc timestamp 7 hour
    ctime = int((datetime.datetime.now()).timestamp()) + (7*60*60) #!< convert to our local timestamp
    print(ctime)
    filter_time = 0 
    if filter == 1:
        filter_time = ctime - ctime%(24*60*60)
    elif filter == 2:
        filter_time = ctime - ctime%(24*60*60) - 24*60*60*7
    elif filter == 3:
        filter_time = ctime - ctime%(24*60*60) - 24*60*60*31
    elif filter == 4:
        filter_time = ctime - ctime%(24*60*60) - 24*60*60*31*6
    elif filter == 5:
        filter_time = ctime - ctime%(24*60*60) - 24*60*60*31*12
    else:
        filter_time = ctime - ctime%(24*60*60) - 24*60*60*31*12
         
    parameter_key_list = ["co2", "temp", "hum", "light", 
                            "dust", "sound", "red", "green", 
                            "blue", "tvoc", "motion", "time"]
    
    #Get all the node_id that is now presented in room
    sensor_node_id_list = [i["node_id"] for i in RegistrationSerializer(models.Registration.objects.filter(room_id=room_id, function="sensor"), many=True).data] #!< have to add many=True
    #Get all 100 record for each node_id and put all in an list
    total_list = []
    if node_id == 0:
        print(filter_time)
        for each_node_id in sensor_node_id_list:
            if models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=each_node_id).count() > 0:
                data = RawSensorMonitorSerializer(models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=each_node_id).order_by("-time"), many=True).data #!< have to add many=True
                data.reverse()
                total_list.append(data)
    else:
        if models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=node_id).count() > 0:
            data = RawSensorMonitorSerializer(models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=node_id).order_by("-time"), many=True).data #!< have to add many=True
            data.reverse()
            total_list.append(data) 
         


    if len(total_list) == 0:
        return_data = {}
        for i in parameter_key_list:
            return_data[i] = []
        return Response(return_data, status=status.HTTP_204_NO_CONTENT) 
    #!< Get an average data of each group of records id (ignore the 0 value) and the time of one record (latest) and add them to return data 

    for i in total_list:
        print(len(i))
    print("////....")
    min_len_of_array_in_total_list = min([len(i) for i in total_list])
    print(min_len_of_array_in_total_list)
    total_list = [i[-min_len_of_array_in_total_list:] for i in total_list]
    for i in total_list:
        print(len(i))

    
    return_data = {}
    buffer = {}
    for i in parameter_key_list:
        return_data[i] = []
        if i != "time":
            buffer[i] = {"value": 0, "number": 0}
        else:
            buffer[i] = []    #!< is used to get the max value of time
    print(len(total_list[0]))
    for i in range(len(total_list[0])):
        for each_element_in_total_list in total_list:
            for j in  parameter_key_list:
                if j != "time" and each_element_in_total_list[i][j] != 0:
                    buffer[j]["value"] = buffer[j]["value"] +  each_element_in_total_list[i][j]
                    buffer[j]["number"] = buffer[j]["number"] +  1
                elif j == "time" and each_element_in_total_list[i][j] != 0:
                    buffer[j].append(each_element_in_total_list[i][j])
                else:
                    continue
        for j in parameter_key_list:
            if j == "time":
                return_data[j].append(max(buffer[j])) 
                buffer[j] = []  #!< reset value
            else:
                if buffer[j]["number"] != 0:
                    return_data[j].append(round(buffer[j]["value"]/(buffer[j]["number"]),2 ))	
                else:
                    return_data[j].append(0)
                buffer[j]["value"] = 0
                buffer[j]["number"] = 0
    return Response(return_data, status=status.HTTP_200_OK)


	  

#___________________________________________________________________end__________________________________________________________________

			
from .djangoClientSendSpeed import insert_to_table_ControlSetpoint
from .djangoClientSendSpeed import send_setpoint_to_mqtt
from .djangoClientSendSpeed import client as setpoint_client            

###############################################################
# @brief: View for get set point value from Frontend, process
#         it, save it in database, and send it to gateway.
# @paras:
#       url: "http://${host}/api/v1.1/control/fans"
#       data:   
#           {
#               'method':'POST',
#                'headers': {
#                    'Content-Type':'application/json',
#                    },
#                "body": {
#                            "option": "manual",
#                            "speed": speed,
#                            "room_id": {room_id},
#                        },
#           }
# @return: 
#       {"Result": "Successful send setpoint"}
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
# @api_view(["POST","GET"])
# def set_level(request, *args, **kwargs):
#    param = kwargs["level"]
#    print("the level is " + str(param))
#    response = {"result": "successful", "level": str(param)}
#    return JsonResponse(response)


###############################################################
# @brief: View for send heatmap data to frontend, using kriging 
#         algorithm.
#         the heatmap that is used in frontend has points arranged
#         in the x_axis from left to right and y_axis from top to bot
#         but the points we generate here is from bot to top and left to right
#         so we have to re-arrange them.
# @paras: 
#           url:    "http://127.0.0.1:8000/api/room/kriging?room_id={room_id}"
# @return: 
#       data in json format:
#           {"data":[-11.57,-0.29,9.6,18.04,24.99,30.41,34.37,37.12,39.01,40.45,-12.07,-0.88,8.92,17.25,23.94,
#                   28.85,31.98,33.61,34.21,34.28,-12.46,-1.32,8.5,16.89,23.57,28.14,30.44,30.86,30.1,28.78,-12.91,
#                   ...],
#           "resolutionX":10,
#           "resolutionY":10}
###############################################################
from .kriging import Kriging
@api_view(["POST","GET"])           
def kriging(request, *args, **kwargs):
    room_id = request.GET.get("room_id")
    default_X = []          #default axis x of id 3,4,5,6
    default_Y = []     #default axis y of id 3,4,5,6
    default_value = []    #this is default-type value of all known-points
    all_sensor_node_in_this_room = RegistrationSerializer(Registration.objects.filter(room_id=room_id, function="sensor"), 
                                                            many=True).data #!< have to add many=True
    room_size = RoomSerializer(Room.objects.filter(room_id=room_id), many=True).data[0] #!< have to add many=True
    for node in all_sensor_node_in_this_room:
        # 1. Get the x axis and y axis of all sensor nodes
        default_X.append(node["x_axis"])
        default_Y.append(node["y_axis"])
        # 2. Get all sensor nodes' values (in order according to the two above array of course)
        if RawSensorMonitor.objects.filter(node_id=node["node_id"]).count() >= 1:
            default_value.append((RawSensorMonitorSerializer(RawSensorMonitor.objects.filter(node_id=node["node_id"]).order_by('-time'),
                                                            many=True).data)[0]["temp"]) #!< have to add many=True
        else:
            # if len(default_X) >=1 and len(default_Y) >=1: 
            #    default_X.pop()
            #    default_Y.pop()
            default_value.append(0)

    # # 1. Get the x axis and y axis of all sensor nodes
    # default_X = [0,0,6.25,8.75]          #default axis x of id 3,4,5,6
    # default_Y = [0.25,2.25,1.25,0.25]     #default axis y of id 3,4,5,6
    # # 2. Get all sensor nodes' values (in order according to the two above array of course)
    # #--------------------------------value of all known-points------------------------------
    # Var = [34.43, 22.03, 28.76, 24.78]    #this is default-type value of all known-points
    # #---------------------------------------------------------------------------------------
    # id1 = models.Sensor.objects.filter(id=1).order_by('-time')[0]
    # id2 = models.Sensor.objects.filter(id=2).order_by('-time')[0]
    # id3 = models.Sensor.objects.filter(id=3).order_by('-time')[0]
    # id4 = models.Sensor.objects.filter(id=4).order_by('-time')[0]
    # new_var = [id1.temperature, id2.temperature, id3.temperature, id4.temperature]
    k = Kriging(10,10, default_value, default_X, default_Y, room_size["x_length"], room_size["y_length"])
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
#@paras:
#           url: "http://backend_host/api/v1.1/monitor/data/history?room_id=1&time_start=${unixTimestampStart}&time_end=${unixTimestampEnd}&option=${optionChartData}"
#           times_start: unixtimestamp 
#           times_end: unixtimestamp 
#           for example: "http://127.0.0.1:8000/api/v1.1/monitor/data/history?room_id=1&node_id=0&time_start=1694451600&time_end=1694451600&option=day"
#
#@return:
#           data in json format:
#               {"co2":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "temp":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "hum":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "light":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "dust":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "sound":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "red":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "green":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "blue":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "tvoc":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "motion":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "time":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]}
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





#######################################################################
#@brief: This view is for get room data for Landing page in
#        frontend.
#@paras:
#           url: "http://127.0.0.1:8000/api/room"
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
#@paras
#           urls: "http://127.0.0.1:8000/api/room/information_tag?room_id=1"
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
        df = df.replace(0, pd.np.nan)
        average_df = df.mean(numeric_only = True,)   #!< calculate average value of all column existing in dataframe
        for para in parameter_key_list:
            if para in average_df:
                if para not in average_data_to_return:
                    average_data_to_return[para] = []
                    average_data_to_return[para].append(int(average_df[para]) if str(average_df[para]) != "nan" else 0)
                else:
                    average_data_to_return[para].append(int(average_df[para]) if str(average_df[para]) != "nan" else 0)
            else:
                continue
        # 5. Get nodes information
        sensor_node_information_in_this_room_list = RegistrationSerializer(Registration.objects.filter(room_id=room_id, function="sensor"), many=True).data #!< have to add many=True
        actuator_node_information_in_this_room_list = RegistrationSerializer(Registration.objects.filter(room_id=room_id, function="actuator"), many=True).data  #!< have to add many=True
        average_data_to_return["node_info"] = {"sensor": sensor_node_information_in_this_room_list,
                                                "actuator": actuator_node_information_in_this_room_list}
        # 6. Get room size 
        room_size_data = RoomSerializer(Room.objects.filter(room_id=room_id), many=True).data #!< have to include many=True
        average_data_to_return["room_size"] = {"x_length": room_size_data[0]["x_length"], "y_length": room_size_data[0]["y_length"]}
            
        return Response(average_data_to_return, status=status.HTTP_200_OK)
        # data = RawSensorMonitor.objects.order_by('-time')[0]     #!< get the latest record in model according to timeline
        # RawSensorMonitorSerializer_instance = RawSensorMonitorSerializer(data)
        # return Response(RawSensorMonitorSerializer_instance.data, status=status.HTTP_200_OK)
    else:
        return Response({"message": "No content!"}, status=status.HTTP_204_NO_CONTENT)



##
# @brief: This view calculate the hourly and daily AQIdust pm2.5 base on airnowtech 
#       Goto "https://forum.airnowtech.org/t/the-aqi-equation/169" for more informations
# @params: 
#       urls: "room/AQIdustpm2_5?room_id={room_id}"
# @return:
#       data in json format: 
#       {
#           "hourly": ...,
#           "daily": ...,
#       }
@api_view(["GET"])
def AQIdustpm2_5(request, *args, **kwargs):
    room_id = int(request.GET.get("room_id"))
    pm2_5_table = [
        {"conclo": 0.0, "conchi": 12.0, "aqilo": 0, "aqihi": 50,},
        {"conclo": 12.1, "conchi": 35.4, "aqilo": 51, "aqihi": 100,},
        {"conclo": 35.5, "conchi": 55.4, "aqilo": 101, "aqihi": 150,},
        {"conclo": 55.5, "conchi": 150.4, "aqilo": 151, "aqihi": 200,},
        {"conclo": 150.5, "conchi": 250.4, "aqilo": 201, "aqihi": 300,},
        {"conclo": 250.5, "conclo": 500.4, "aqilo": 301, "aqihi": 500,},
    ]
    hourly = 0
    daily = 0
    ctime = int((datetime.datetime.now()).timestamp()) + (7*60*60) #!< convert to our local timestamp
    print(ctime)
    #calculate hourly data
    filter_time = ctime - 12*60*60
    node_sensor_list = RegistrationSerializer(Registration.objects.filter(room_id=room_id),many=True)
    hourly_dust_data = RawSensorMonitorSerializer(RawSensorMonitor.objects.filter(room_id=room_id, time__gt=filter_time, dust__gt=0), many=True).data #!< have to add many=True
    if len(hourly_dust_data) != 0:
        df = pd.DataFrame(hourly_dust_data)
        df = df[["time", "id", "dust"]]
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df["hour"] = df["datetime"].dt.hour
        df = df.groupby(['hour'], as_index=False).mean()
        df.sort_values(by='hour', ascending=False, inplace=True)
        print(df)
        power_index = 0
        pre_row = None
        l = []
        first_record_flag = True
        for index, row in df.iterrows():
            if first_record_flag:
                pre_row = row["hour"]
                l.append({"value": row["dust"], "pow": power_index})
                first_record_flag = False
            else:
                dif = pre_row - row["hour"]
                pre_row = row["hour"]
                power_index = int(power_index + dif)
                l.append({"value": row["dust"], "pow": power_index})

        print(l)
        temp_list = [i["value"] for i in l]
        range = round(max(temp_list) - min(temp_list),1)
        scaled_rate_of_change = range/max(temp_list)
        weight_factor = 1 - scaled_rate_of_change
        weight_factor = 0.5 if weight_factor < 0.5 else round(weight_factor, 1)
        sum = 0
        sum_of_power = 0
        
        for i in l:
            sum = sum + i["value"]*pow(weight_factor, i["pow"])
            sum_of_power = sum_of_power + pow(weight_factor, i["pow"])
            
        hourly = round(sum/sum_of_power, 1)
        conclo = None
        conchi = None
        aqilo = None
        aqihi = None
        for i in pm2_5_table:
            if round(hourly) > 500:
                hourly = 500
                break
            if round(hourly) <= i["conchi"] and round(hourly) >= i["conclo"]:        
                conclo = i["conclo"]
                conchi = i["conchi"]
                aqilo = i["aqilo"]
                aqihi = i["aqihi"]
                hourly = round((aqihi - aqilo)*(hourly-conclo)/(conchi-conclo) + aqilo)
                break
        print(hourly)
            
    return Response({"hourly": hourly, "daily": 0}, status=200)









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