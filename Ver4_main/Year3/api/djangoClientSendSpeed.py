from .mqtt import Client
import datetime
import calendar
import json
import psycopg2

broker = "27.71.227.1"
mqtt_topic = "farm/control"

client = Client(mqtt_topic)
mqtt_broker = broker     
mqtt_port = 1883
client.connect(mqtt_broker, int(mqtt_port), 60)
client.loop_start()
print("Done setting up client...")

def send_setpoint_to_mqtt(client: Client, data: dict):
    mqtt_topic = f"farm/control"
    date = datetime.datetime.utcnow()
    print(date)
    utc_time = calendar.timegm(date.utctimetuple())
    print(utc_time)
    print(f"data in send_speed_setpoint is {data}" )
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


#this function is use by the view sending monitoring data to gateway
# param: data -> dict { 
#                           "option": ...,
#                           "key": ..., 
#                     }
#                     key can be "co2" or "temp" or "speed"
def insert_to_table_ControlSetpoint(data,
                     __database='smart_construction', 
                     __user='quan', 
                     __password='1', 
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