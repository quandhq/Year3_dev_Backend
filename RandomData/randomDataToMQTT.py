import paho.mqtt.client as mqtt
import json
import random 
import time 
import calendar
import datetime

class RandomDataToMQTT:
   mqtt_broker = "broker.hivemq.com"
   mqtt_port = 1883
   topic = "Year3/Gateway"

   client_id = f'python-mqtt-{random.randint(0,1000)}'
   # client_id = 'clientId-dhhSHVoTBA'

   def connect_mqtt(self):
      def on_connect(client, userdata, flag, rc):
         if rc == 0:
            print("Connected to MQTT Brocker!")
         else:
            print(f"Failed to connect, return code {rc}")
         
      client = mqtt.Client(self.client_id)
      client.on_connect = on_connect
      client.connect(self.mqtt_broker, self.mqtt_port, 60)
      return client

   def publish(self, client):
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

