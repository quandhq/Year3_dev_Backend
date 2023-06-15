import paho.mqtt.client as mqtt
import json
import random 
import time 
import calendar
import datetime

class RandomDataToMQTT:
   mqtt_broker = "desktop-rjl9d4n" #localhost      #this is default ip of our computer
   mqtt_port = 1883             #1883 is for TCP port
   topic = "farm/1/monitor/process"   # "farm/{farm_id}/{sensor_id}"

   client_id = f'python-mqtt-{random.randint(0,1000)}'
   # client_id = 'clientId-dhhSHVoTBA'

   def __init__(self, 
               __mqtt_broker = "desktop-rjl9d4n", 
               __mqtt_port = 1883, 
               __topic = "farm/1/sensor/1"):
      self.mqtt_broker = __mqtt_broker
      self.mqtt_port = __mqtt_port
      self.topic = __topic

   def connect_mqtt(self):
      def on_connect(client, userdata, flag, rc):
         if rc == 0:
            print("Connected to MQTT Brocker!")
         else:
            print(f"Failed to connect, return code {rc}")
         
      client = mqtt.Client(self.client_id)
      client.on_connect = on_connect
      client.connect(self.mqtt_broker, self.mqtt_port, 60)    #, self.mqtt_port, 60
      return client

   def publish(self, client):
      msg_count = 0
      while True:
         date = datetime.datetime.utcnow()
         print(date)
         utc_time = calendar.timegm(date.utctimetuple())
         print(utc_time)
         new_data = { 
                        "operator": "actuatorData", 
                        "status": 0, 
                        "info": 
                        { 
                            "state": round(random.uniform(0,1)), 
                            "speed": round(random.uniform(1, 100)), 
                            "time": utc_time 
                        } 
                    } 

         time.sleep(2)
         msg = json.dumps(new_data)
         result = client.publish(self.topic, msg)
         status = result[0]
         if status == 0:
            # print(f"Succesfully send '{msg}' to topic '{topic}'")
            pass
         else:
            raise Exception("Can't publish data to mqtt..........................!")
         msg_count += 1
         

   def run(self):
      client = self.connect_mqtt()
      try:
      # client.loop_start()
         self.publish(client)
      except Exception as e:
         print(str(e))
      finally:
         client.disconnect()

if __name__ == "__main__":
   new_client = RandomDataToMQTT()
   new_client.run()

