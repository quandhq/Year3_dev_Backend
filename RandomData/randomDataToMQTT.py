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

def publish(client):
   msg_count = 0
   while True:
      date = datetime.datetime.utcnow()
      print(date)
      utc_time = calendar.timegm(date.utctimetuple())
      print(utc_time)
      new_data = {
                     'operator':'senData',
                     'infor':{
                        # 'id':random.randint(1,8),
                        'id':1,
                        'time':utc_time,
                        'red':random.randint(0,3000),
                        'green':random.randint(0,3000),
                        'blue':random.randint(0,3000),
                        'clear':random.randint(0,3000),
                        'light':random.randint(0,3000),
                        'co2':random.randint(0,3000),
                        'dust':round(random.uniform(1, 100),2),
                        "tvoc":0,
                        "motion":random.randint(0,1),
                        "sound":round(random.uniform(1, 1000),2),
                        "temperature":round(random.uniform(1, 100),2),
                        "humidity":round(random.uniform(1, 100),2),
                        "status":0
                     }
                  }

      time.sleep(2)
      msg = json.dumps(new_data)
      result = client.publish(topic, msg)
      status = result[0]
      if status == 0:
         # print(f"Succesfully send '{msg}' to topic '{topic}'")
         pass
      else:
         # print(f"Fail to send '{msg}' to topic '{topic}'")
         pass
      msg_count += 1

def run():
   client = connect_mqtt()
   client.loop_start()
   publish(client)

if __name__ == "__main__":
   run()

