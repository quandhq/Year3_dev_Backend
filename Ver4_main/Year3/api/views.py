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
from api.serializers import RawSensorMonitorSerializer ,RawActuatorMonitorSerializer, SetTimerHistorySerializer
import pandas as pd
import math
import time

print("Setting views.py")





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
    max_len_of_array_in_total_list = max([len(i) for i in total_list])
    print(min_len_of_array_in_total_list)
    print(max_len_of_array_in_total_list)
    # total_list = [i[-min_len_of_array_in_total_list:] for i in total_list]
    for i in total_list:
        print(len(i))

    for i in total_list:
        if len(i) < max_len_of_array_in_total_list:
            for j in range(0, max_len_of_array_in_total_list - len(i)):
                i.insert(0, {i: -1 for i in parameter_key_list})

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
                if j != "time" and each_element_in_total_list[i][j] >= 0:
                    buffer[j]["value"] = buffer[j]["value"] +  each_element_in_total_list[i][j]
                    buffer[j]["number"] = buffer[j]["number"] +  1
                elif j == "time" and each_element_in_total_list[i][j] >= 0:
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

			
from .djangoClient import insert_to_table_ControlSetpoint
from .djangoClient import send_setpoint_to_mqtt
from .djangoClient import client as setpoint_client            

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


###############################################################
# @brief: View for set timer for actuator from Frontend, send it to gateway,
#           ,save the record to database.
# @paras:
#       url: "http://${host}/api/room/set_timer?room_id=${room_id}"
#       data:   
#           {
#               'method':'POST',
#                'headers': {
#                    'Content-Type':'application/json',
#                    },
#                "body": {
#                           "timer": [time],
#                        },
#           }
# @return: 
#       {"Result": "Successful set timer"}
###############################################################
from .djangoClient import send_timer_to_gateway, client
@api_view(["POST"])
def setTimerActuator(request, *args, **kwargs):
    room_id = request.GET.get("room_id")
    timer = json.loads(request.body)
    print(timer)
    result = send_timer_to_gateway(client, {"timer": timer["time"], "room_id": room_id})
    #send data to gateway and wait for return
    new_data = {"room_id": room_id, 
                "time": int((datetime.datetime.now()).timestamp()) + 7*60*60,
                "timer": timer["time"],
                "status": result,
                }
    new_data_serializer = SetTimerHistorySerializer(data=new_data)
    if new_data_serializer.is_valid():
        new_data_serializer.save()
        if result == 1:
            return Response({"Response": "Successful"}, status=status.HTTP_200_OK)
        if result == 0:
            return Response({"Response": "Unsuccessfully set timer"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Response": "Can not save record to database"}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    #save to database 
    


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

    
    k = Kriging(10, 10, default_value, default_X, default_Y, room_size["x_length"], room_size["y_length"])
    test = k.interpolation()
    response = {'data': test[2], 'resolutionX': k.resolutionX, 'resolutionY': k.resolutionY}

    return Response(response, status=status.HTTP_200_OK)     









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
                average_data_to_return[i] = -1
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
        df = df.replace(-1, np.nan)
        average_df = df.mean(numeric_only = True,)   #!< calculate average value of all column existing in dataframe
        for para in parameter_key_list:
            if para in average_df:
                if para not in average_data_to_return:
                    average_data_to_return[para] = []
                    average_data_to_return[para].append(int(average_df[para]) if str(average_df[para]) != "nan" else -1)
                else:
                    average_data_to_return[para].append(int(average_df[para]) if str(average_df[para]) != "nan" else -1)
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



##
# @brief: This view is for fetching all data of room for room table in configuration page
#
# @params: 
#       urls: "api/configuration/room/all"
# @return:
#   if there is any data:
#       [
#     {
#         "id": 1,
#         "room_id": 1,
#         "construction_name": "building",
#         "x_length": 18,
#         "y_length": 18,
#         "information": "C1B 401"
#     }
#   ]
#      if there is none:
#       []
@api_view(["GET"])
@authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
@permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def getConfigurationRoomAll(request, *args, **kwargs):
    if Room.objects.count() > 0:
        all_room_data = RoomSerializer(Room.objects.all(), many=True).data  #!< have to add many=True
        return Response(all_room_data, status=status.HTTP_200_OK)
    else:
        return Response([], status=status.HTTP_200_OK) 

##
# @brief: This view is for creating new room record, deleting room record or configuring record
#         Notice: if you use postman to test create, the data in JSON form should be exactly like this
#            {
#                 "room_id": "2",
#                 "construction_name": "building",
#                 "x_length": "12",
#                 "y_length": "25",
#                 "information": "TETIONSG"
#             }
#
# @params: 
#       urls: "api/configuration/room/create"
# @return:
#   if successful
#       status: 200
#       data:
#       {"Resposne": "Successful"}
#      if not:
#       status: 
#       {"Resposne": "Unsuccessful"}
@api_view(["POST", "DELETE", "PUT"])
@authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
@permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def configurationRoom(request, *args, **kwargs):
    if request.method == "POST":
        new_room = json.loads(request.body)

        print(f"new room data {new_room}")
        print(">???????????????????,,,,,,,,")
        if Room.objects.filter(room_id=new_room["room_id"]).count() > 0:
            return Response({"Response": "This room already existed!"}, status=status.HTTP_400_BAD_REQUEST)

        new_data_serializer = RoomSerializer(data=new_room)
        if new_data_serializer.is_valid():
            new_data_serializer.save()
            print("Successfully save new room to database!")
            return Response({"Response": "Successful!"}, status=status.HTTP_200_OK)
        else:
            print("Failed to save new room to database!")
            return Response({"Response": "Can not save record to database!"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        id = json.loads(request.body)["id"]
        record = Room.objects.filter(id=id)[0]
        print(record)
        record.delete()
        return Response({"Response": "Successfully delete room!"}, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        new_setting = json.loads(request.body)
        record = Room.objects.filter(id=new_setting["id"])[0]
        record.construction_name = new_setting["construction_name"]
        record.x_length = new_setting["x_length"]
        record.y_length = new_setting["y_length"]
        record.information = new_setting["information"]
        try:
            record.save()
        except:
            return Response({"Response": "Can not update new room data!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"Response": "Successfully update new room data"}, status=status.HTTP_200_OK)
    







