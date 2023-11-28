from .mqtt import Client
import datetime
import calendar
import json
import psycopg2
import time

broker = "27.71.227.1"
mqtt_topic = "farm/control"

backend_topic_dictionary = {"get_sensor_data": "farm/monitor/sensor",
                        "get_actuator_data": "farm/monitor/actuator",
                        "get_setpoint": "farm/control",
                        "room_sync_gateway_backend": "farm/sync_room",
                        "set_timer": "farm/set_timer",
                        "node_sync_backend_gateway": "farm/sync_node"}

client = Client(mqtt_topic,[backend_topic_dictionary["set_timer"]])
mqtt_broker = broker     
mqtt_port = 1883
client.connect(mqtt_broker, int(mqtt_port), 60)
client.loop_start()
print("Done setting up client...")


#This function is used by configurationNode view to send add,delete message to gateway
from api.models import Registration, NodeConfigBuffer
from api.serializers import RegistrationSerializer, NodeConfigBufferSerializer
def sendNodeConfigToGateway(client: Client, data: dict, command):  
    topic = backend_topic_dictionary["node_sync_backend_gateway"]
    result = 0
    while NodeConfigBuffer.objects.count() != 0:
        """
        If there is still data in buffer, get the first one out and send message with it's data to gateway
        if not successull, delete the latest data but in database registration and also delete the one in buffer
        if successfull, update the one in registration with new node_id and delete the one in buffer.
        """
        latest_data_waiting_in_buffer = NodeConfigBuffer.objects.filter(action=1).order_by("-time")[0] #!< this is for detele if needed
        print(latest_data_waiting_in_buffer["time"])
        latest_data_waiting_in_buffer_data = NodeConfigBufferSerializer(latest_data_waiting_in_buffer, 
                                                                   many=True).data[0]
        #this is for delete if needed, or update node id of this record if needed
        latest_data_waiting_in_registration = Registration.objects.filter(room_id=latest_data_waiting_in_buffer_data["room_id"],
                                                                          mac=latest_data_waiting_in_buffer_data["mac"])[0]
        print(latest_data_waiting_in_registration["time"])
        
        
        new_data = { 
                    "operator": "server_add", 
                    "info": 
                    { 
                        "room_id": latest_data_waiting_in_buffer_data["room_id"],
                        "node_function": latest_data_waiting_in_buffer_data["function"],     
                        "mac_address": latest_data_waiting_in_buffer_data["mac"],    
                        "time": int((datetime.datetime.now()).timestamp()) + 7*60*60,
                    } 
                }
        
        msg = json.dumps(new_data)
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print("Successfully send timer turn on air-conditioning message!!!")
        # print(f"Succesfully send '{msg}' to topic '{topic}'")
            pass
        else:
            raise Exception("Can't publish data to mqtt..........................!")

        
        curent_time = int((datetime.datetime.now()).timestamp())
        while(1):
            #if 10 seconds have passed, break out of loop and delete data in database
            if int((datetime.datetime.now()).timestamp()) - curent_time > 10: 
                
                break
            temp = client.msg_arrive()
            if temp != None:
                        print(f"RRRRRRRRRRRRRRRReceived `{temp}` from topic `{topic}`")
                        msg = json.loads(temp)
                        if msg["operator"] == "set_timer_ack":
                            if msg["info"]["status"] == 1:
                                result = 1
                                break
    return result
    


#this function is use by the view sending monitoring data to gateway
# param: data -> dict { 
#   "operator": " set_timer", 
#   "info": { 
#     "room_id": 0, 
#     "time": 1655396252, 
#   } 
# } 

def send_timer_to_gateway(client: Client, data: dict):
    topic = backend_topic_dictionary["set_timer"]
    date = int((datetime.datetime.now()).timestamp()) + 7*60*60         #time to save to database
    print(date)
    print(f"data in send_timer is {data}")
    new_data = { 
                "operator": "set_timer", 
                "info": 
                { 
                    "room_id": data["room_id"],         
                    "time": data["timer"],
                    "temperature": data["temperature"], 
                } 
            }
    
    msg = json.dumps(new_data)
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print("Successfully send timer turn on air-conditioning message!!!")
    # print(f"Succesfully send '{msg}' to topic '{topic}'")
        pass
    else:
        raise Exception("Can't publish data to mqtt..........................!")

    result = 0
    curent_time = int((datetime.datetime.now()).timestamp())
    while(1):
        if int((datetime.datetime.now()).timestamp()) - curent_time > 2: 
            break
        temp = client.msg_arrive()
        if temp != None:
                    print(f"RRRRRRRRRRRRRRRReceived `{temp}` from topic `{topic}`")
                    msg = json.loads(temp)
                    if msg["operator"] == "set_timer_ack":
                        if msg["info"]["status"] == 1:
                            result = 1
                            break
    return result

def send_actuator_command_to_gateway(client: Client, data: dict):
    
    
    #CONTINUE FINISHING THIS
    result = 1
    # topic = backend_topic_dictionary["set_timer"]
    # date = int((datetime.datetime.now()).timestamp()) + 7*60*60         #time to save to database
    # print(date)
    # print(f"data in send_timer is {data}")
    # new_data = { 
    #             "operator": "set_timer", 
    #             "info": 
    #             { 
    #                 "room_id": data["room_id"],         
    #                 "time": data["timer"],
    #                 "temperature": data["temperature"], 
    #             } 
    #         }
    
    # msg = json.dumps(new_data)
    # result = client.publish(topic, msg)
    # status = result[0]
    # if status == 0:
    #     print("Successfully send timer turn on air-conditioning message!!!")
    # # print(f"Succesfully send '{msg}' to topic '{topic}'")
    #     pass
    # else:
    #     raise Exception("Can't publish data to mqtt..........................!")

    # result = 0
    # curent_time = int((datetime.datetime.now()).timestamp())
    # while(1):
    #     if int((datetime.datetime.now()).timestamp()) - curent_time > 2: 
    #         break
    #     temp = client.msg_arrive()
    #     if temp != None:
    #                 print(f"RRRRRRRRRRRRRRRReceived `{temp}` from topic `{topic}`")
    #                 msg = json.loads(temp)
    #                 if msg["operator"] == "set_timer_ack":
    #                     if msg["info"]["status"] == 1:
    #                         result = 1
    #                         break
    return result
    



#this function is use by the view sending monitoring data to gateway
# param: data -> dict { 
#                           "option": ...,
#                           "key": ..., 
#                     }
#                     key can be "co2" or "temp" or "speed"
def send_setpoint_to_mqtt(client: Client, data: dict):
    mqtt_topic = f"farm/control"
    date = datetime.datetime.utcnow()
    print(date)
    utc_time = calendar.timegm(date.utctimetuple())
    print(utc_time)
    print(f"data in send_speed_setpoint is {data}")
    key = ""
    option = ""
    if "temp" in data:
        key = "temp"
        option = "auto"
    elif "co2" in data:
        key = "co2"
        option = "auto"
    else:
        key = "speed"
        option = "manual"
    new_data = { 
                "operator": "sendSetPoint", 
                "option": option, 
                "info": 
                { 
                    "room_id": data["room_id"],         
                    "node_id": 0,
                    key: data[key],
                    # "key": 123,
                    "time": utc_time, 
                } 
            }
    
    msg = json.dumps(new_data)
    result = client.publish(mqtt_topic, msg)
    status = result[0]
    if status == 0:
        print("Successfully send speed message!!!")
    # print(f"Succesfully send '{msg}' to topic '{topic}'")
        pass
    else:
        raise Exception("Can't publish data to mqtt..........................!") 


def insert_to_table_ControlSetpoint(data,
                     __database='smartfarm', 
                     __user='year3', 
                     __password='year3', 
                     __host='localhost', 
                     __port='5432') -> None:
      conn = psycopg2.connect(
            database = __database,
            user = __user,
            password = __password,
            host = __host,
            port = __port,
         )
      # lock = 
      conn.autocommit = True
      cursor = conn.cursor()
      # with self.lock:
      record = ()
      if data['option'] == "manual":
         query = f'''INSERT INTO api_controlsetpoint (room_id, node_id, option, aim, value, time) 
               VALUES (%s, %s, %s, %s, %s ,%s)'''
         mqtt_topic = "farm/control"
         date = datetime.datetime.utcnow()
         print(date)
         utc_time = calendar.timegm(date.utctimetuple())
         record = (data['room_id'], 10, "manual", "speed", data['speed'], utc_time)
         cursor.execute(query, record)
         print("Successfully insert SET POINT SPEED DATA to PostgreSQL TIME: " + str(utc_time))
         cursor.close()
         conn.close()
      elif data["option"] == "auto":
         query = f'''INSERT INTO api_controlsetpoint (room_id, option, aim, value, time) 
               VALUES (%s, %s, %s, %s, %s ,%s)'''
         key = ""
         if "temp" in data:
            key = "temp"
         elif "co2" in data:
            key = "co2"
         date = datetime.datetime.utcnow()
         print(date)
         utc_time = calendar.timegm(date.utctimetuple())
         record = (1, "auto", key, data[key], utc_time)
         cursor.execute(query, record)
         print(f"Successfully insert SET POINT DATA {key} to PostgreSQL TIME: " + str(utc_time))
         cursor.close()
         conn.close()