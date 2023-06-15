from urllib import request
from django.shortcuts import render,redirect
from django import http
from rest_framework import mixins
from rest_framework import generics
from api import models
from api import serializers
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from django.http import JsonResponse
import numpy as np
from .kriging import Kriging
from .SetPoint import SetPoint
from rest_framework import authentication, permissions
import json
import psycopg2
import multiprocessing
import datetime
import calendar

print("This is in view.py")

# Create your views here.


# # _______________________implementation for view publishing setpoint data to mqtt___________________
# import paho.mqtt.client as mqtt
# import json
# import random 
# import time 
# import calendar
# import datetime


# mqtt_broker = "broker.hivemq.com"
# mqtt_port = 1883
# topic = "Year3"

# client_id = f'python-mqtt-{random.randint(0,1000)}'
# # client_id = 'clientId-dhhSHVoTBA'

# def connect_mqtt():
#    def on_connect(client, userdata, flag, rc):
#       if rc == 0:
#          print("Connected to MQTT Brocker!")
#       else:
#          print(f"Failed to connect, return code {rc}")
      
#    client = mqtt.Client(client_id)
#    client.on_connect = on_connect
#    client.connect(mqtt_broker, mqtt_port, 60)
#    return client

# def publish(client, setPoint):
#    date = datetime.datetime.utcnow()
#    utc_time = calendar.timegm(date.utctimetuple())

#    new_data = {
#                   'operator':'sendSetPoint',
#                   'infor':{
#                      'time':utc_time,
#                      "status":setPoint,
#                   }
#                }

#    time.sleep(2)
#    msg = json.dumps(new_data)
#    result = client.publish(topic, msg)
#    status = result[0]
#    if status == 0:
#       print(f"Succesfully send '{msg}' to topic '{topic}' PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
#    else:
#       print(f"Fail to send '{msg}' to topic '{topic}' PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")

# def run(setPoint):
#    client = connect_mqtt()
#    client.loop_start()
#    publish(client, setPoint)
#    client.disconnect()
# # ____________________________________________________end____________________________________________________




#______________________________________view_for_testing_authentication______________________________________________

@api_view(["POST", "GET"])
# @permission_classes([permissions.IsAuthenticated])
# @authentication_classes([authentication.TokenAuthentication])
def getAuthentaicationSensorSecondlyData(request , *args, **kwargs):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   query_sample = models.SensorMonitor.objects.order_by('-time')[:15]
   new_query = {"temperature":[],"humidity":[],"co2":[],"dust":[],"sound":[],"light":[],"time":[]}
   for i in query_sample:
      new_query["temperature"].append(i.temperature)
      new_query["humidity"].append(i.humidity)
      new_query["co2"].append(i.co2)
      new_query["dust"].append(i.dust)
      new_query["sound"].append(i.sound)
      new_query["light"].append(i.light)
      new_query["time"].append(i.time)
   #reverse all array in new_query
   for i in new_query:
      new_query[i].reverse()
   print(query_sample[0].time)
   print(args, kwargs)
   # return self.list(request, *args, **kwargs)
   return JsonResponse(new_query)      
   
   

#_________________________________________________end_______________________________________________________________

#____________________________________________________________________test for return data with function-base-view__________________________

#brief: view for sending secondly data for chart on front-end
@api_view(["POST", "GET"])
# @authentication_classes([authentication.TokenAuthentication])
def getSensorSecondlyData(request , *args, **kwargs):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   dict = kwargs
   print(dict['id'])
   query_sample = models.SensorMonitor.objects.filter(node_id_id=dict['id']).order_by('-time')[:15]
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
   return JsonResponse(new_query)      

#___________________________________________________________________end__________________________________________________________________



#__________________________________________________________________view for returning secondly data__________________________________________
# #brief: view for sending secondly data for chart on front-end
# class SensorSecondlyData(mixins.ListModelMixin,
#                         generics.GenericAPIView):     #have to inherit this too
#    # queryset = models.Sensor.objects.all()
#    # queryset = models.Sensor.objects.order_by('-time')[:15]
#    serializer_class = serializers.SensorSerializer
#    def get(self, request , *args, **kwargs):
#       dict = kwargs
#       print(dict['id'])
#       self.queryset = models.Sensor.objects.filter(id=dict['id']).order_by('-time')[:15]
#       query_sample = self.queryset
#       new_query = {"temperature":[],"humidity":[],"co2":[],"dust":[],"sound":[],"light":[],"time":[]}
#       for i in query_sample:
#          new_query["temperature"].append(i.temperature)
#          new_query["humidity"].append(i.humidity)
#          new_query["co2"].append(i.co2)
#          new_query["dust"].append(i.dust)
#          new_query["sound"].append(i.sound)
#          new_query["light"].append(i.light)
#          new_query["time"].append(i.time)
#       #reverse all array in new_query
#       for i in new_query:
#          new_query[i].reverse()
#       print(self.queryset[0].time)
#       print(args, kwargs)
#       print(self.list(request, *args, **kwargs))
#       # return self.list(request, *args, **kwargs)
#       return JsonResponse(new_query)      
#_______________________________________________________________end_______________________________________________________________



#brief: view for sending daily data for chart on front-end, we will get all the datas 
#        that being in database for the last 10 days
#output: a json dictionary with average values of all measurements in 10 day each and 
#        corresponding one value of time stick to each day
#
@api_view(["GET", "POST"])    
def getSensorDailyData(request , *args, **kwargs):     #have to inherit this too
   # queryset = models.Sensor.objects.all()
   # queryset = models.Sensor.objects.order_by('-time')[:15]
   #________get the serializer of sensor model
   #________define the function that answer the request
   temp_queryset = models.SensorMonitor.objects.filter(node_id_id=1).order_by('-time')
   latest_time = temp_queryset[0].time
   print("LATEST TIME IS ________________________________ " + str(latest_time))
   # get the time of the latest object being at the latest 10 days of the array self.queryset
   second_limit = latest_time - latest_time%86400 - 9*86400 - 7*3600 #7*3600 is to suit up with the current our timezone, beacuse the current 
                                                                     #timeline is 7 hours faster 
   print("LIMITTTTTTTTTTTTTTTTTTTTTTTTTTTT___________ " + str(second_limit))
   # get the index of the last object being at the latest 10 days of the array self.queryset
   #default, index will be the length of temp_queryset
   index = len(temp_queryset)
   index_0 = -1 #this will be used to get the real index
   for ob in temp_queryset:
      index_0 += 1
      if ob.time < second_limit:
         index = index_0-1
         break
   #get all the data from the latest until index 
   temp_queryset = temp_queryset[:(index+1)]
   print("INDEX IS: " + str(index))
   #the query to be returned to front-end
   res_query = {"co2":[], "temp":[],"hum":[], "time":[]}

   #this is the array that contain all datas to compute the average values returned back to front-end
   #reverse all data in an increasing order to make it easier to compute
   new_query = {"co2":[], "temp":[],"hum":[], "time":[]}
   for i in temp_queryset:
      new_query["co2"].append(i.co2)
      new_query["temp"].append(i.temp)
      new_query["hum"].append(i.hum)
      new_query["time"].append(i.time)
   #reverse all array in new_query
   for i in new_query:
      new_query[i].reverse()
   # return JsonResponse(new_query)
   #get the second_limit and index_0 and initial values to compute the average value of all measurements
   second_limit = second_limit + 86400     #we will get all the datas which are below this second_limit and calculate the avarage of them
   print("THE FIRST LIMIT TIME TO PROCESS ... " + str(second_limit))
   initial_value = {"index_0": 0,
                     "temp": 0,
                     "hum": 0,   
                     "co2": 0,
                     "flag": 0, #the flag is to indicate that if the second_limit reach the last round}
                     "process": 0   #currently not using this field
                              }
   #reference dictionary. this is used to access properies of res_result dicionary more easily 
   key = ["co2", "temp", "hum"]

   #this scope is to get the sum of all values of all kinds of measurements in one day and then get the sum divided by the 
   #number of values we get to get the the average value of that day
   for i in range(len(new_query["time"])):
      if (new_query["time"][i] < second_limit or initial_value["flag"] == 1) and i < (len(new_query["time"])-1):
         initial_value["index_0"] += 1
         print("IN HERE:_____________" + "INDEX_0 is ______" + str(initial_value["index_0"]) + "time limit is _________ " + str(second_limit))
         for j in key:
            initial_value[j] += new_query[j][i]
            # temperature += new_query["temperature"][i]
            # humidity += new_query["humidity"][i]
            # co2 += new_query["co2"][i]
            # dust += new_query["dust"][i]z
            # sound += new_query["sound"][i]
            # light += new_query["light"][i]
      elif new_query["time"][i] >= second_limit and new_query["time"][-1] > (second_limit + 86400) and i < (len(new_query["time"])-1):
         print(f"CALCULATING AVERAGE VALUE : ---- i is {i}: " + "______________ " + str(initial_value["temperature"]) + " ____________________ " + str(initial_value["index_0"]) + "second limit is ____ " + str(second_limit))
         if initial_value["index_0"] == 0:
            for j in key:
               res_query[j].append(0)   #add new value to res_query
               initial_value[j] = new_query[j][i]  #reset value
            res_query["time"].append(second_limit-1)   #append value time for front-end to get the day
            print(">>>>>>>>>>>>>>>>>>>ADDED " + str(second_limit-1))
            initial_value["index_0"] = 1  #reset value
            second_limit += 86400
         else:
            for j in key:
               res_query[j].append(round(initial_value[j]/initial_value["index_0"]))   #add new value to res_query
               initial_value[j] = new_query[j][i]  #reset value
            res_query["time"].append(second_limit-1)   #append value time for front-end to get the day
            print(">>>>>>>>>>>>>>>>>>>ADDED " + str(second_limit-1))
            initial_value["index_0"] = 1  #reset value
            second_limit += 86400
               # res_query["temperature"].append()
      #this is for values of the last day
      elif new_query["time"][i] >= second_limit and new_query["time"][-1] < (second_limit + 86400) and initial_value["flag"] == 0:
         initial_value["flag"] = 1
         print("JUST SET FLAG TO 1")
         print(f"i is {i}: " + "______________ " + str(initial_value["temperature"]) + " ____________________ " + str(initial_value["index_0"]) + "second limit is ____ " + str(second_limit))
         if initial_value["index_0"] == 0:
            for j in key:
               res_query[j].append(0)   #add new value to res_query
               initial_value[j] = new_query[j][i]  #reset value
            res_query["time"].append(second_limit-1)   #append value time for front-end to get the day
            print(">>>>>>>>>>>>>>>>>>>>>>>ADDED " + str(second_limit-1))
            initial_value["index_0"] = 1  #reset value
         else:
            for j in key:
               res_query[j].append(round(initial_value[j]/initial_value["index_0"]))   #add new value to res_query
               initial_value[j] = new_query[j][i]  #reset value
            res_query["time"].append(second_limit-1)   #append value time for front-end to get the day
            print(">>>>>>>>>>>>>>>>>>>>>>>ADDED " + str(second_limit-1))
            initial_value["index_0"] = 1  #reset value
      #the last process for the last day
      if i == len(new_query["time"]) - 1:    #the last process
         print("THE LAST PROCESS:")
         print(f"CALCULATING THE LAST PROCESS: ------ i is {i}: " + "______________ " + str(initial_value["temperature"]) + " ____________________ " + str(initial_value["index_0"]) + "second limit is ____ " + str(second_limit))

         if initial_value["index_0"] == 0:
            for j in key:
               res_query[j].append(0)   #add new value to res_query
         else:
            for j in key:
               res_query[j].append(round(initial_value[j]/initial_value["index_0"]))   #add new value to res_query
         #append value time for front-end to get the day
         if (second_limit + 86400) < new_query["time"][-1]:
            res_query["time"].append(second_limit)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>ADDED LAST PROCESS SECONDLIMIT " + str(second_limit))
         else:
            res_query["time"].append(latest_time)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>ADDED LATESTTIME " + str(latest_time))   
   return JsonResponse(res_query)




            
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
   # print(request.data)
   insert_to_table_ControlSetpoint(monitor_data)
   send_setpoint_to_mqtt(setpoint_client, monitor_data, farm_id)
   
   return JsonResponse({"Result": "Successful"})

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
   return JsonResponse(response)


# def index(request):
#    mydata = models.Sensor.objects.all().values()
#    print(mydata[0])
#    context = {
#     'insert_me': mydata,
#    }		
#    #CÁI INSERT_ME CHÍNH LÀ CÁI VARIABLE Ở TRONG CÁI FILE INDEX.HTML TRÊN KIA

#    return render(request, "api\main.html", context=context)

#brief: this view is used to test sending a html template with data embedded in it to front-end, currently not using, don't mind this
def index(request):
   mydata = models.SensorMonitor.objects.all().values()
   # print(mydata[0])
   context = {
    'insert_me': mydata,
   }	
   #CÁI INSERT_ME CHÍNH LÀ CÁI VARIABLE Ở TRONG CÁI FILE INDEX.HTML TRÊN KIA
   send_setpoint_to_mqtt(setpoint_client, {"data": "test"})
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

#_______________________test url dispatching_____________________________
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

   