import random
import paho.mqtt.client as mqtt
import psycopg2
import json
import multiprocessing
import threading
import time

#-----------------------------THIS ONE IS CURRENTLY USED---------------------------------------

broker = "27.71.227.1"



class Mqtt():
   #turn on emqx on laptop first "emqx start", be careful that this ip is random whenever we reconnect to the internet
   mqtt_broker = "172.19.200.236"         
   mqtt_port = 1883
   topic = "Year3/Gateway"
   # generate client ID with pub prefix randomly
   client_id = f'python-mqtt-{random.randint(0, 100)}'
   # username = 'emqx'
   # password = 'public'
   table = None
   lock = None
   topic_list = {"sensor_topic": "farm/1/sensor/1", 
                      "actuator_topic": "farm/1/actuator/1",
                      "sensor_gateway_server": "farm/1/monitor",
                      "actuator_gateway_server": "farm/1/monitor/process",}
   def __init__(self,
               #  lock, 
               __mqtt_broker = "172.19.200.236", 
               __mqtt_port = 1883, 
               __topic = "farm/1/monitor",
               __table = 'api_sensormonitor'):
      # self.lock = lock
      self.mqtt_broker = __mqtt_broker
      self.mqtt_port = __mqtt_port
      self.topic = __topic
      self.table = __table


   def connect_mqtt(self):
      def on_connect(client, userdata, flags, rc):
         if rc == 0:
            print("Connected to MQTT Broker!")
         else:
            print("Failed to connect, return code %d\n", rc)

      client = mqtt.Client(self.client_id)
      #  client.username_pw_set(username, password)
      client.on_connect = on_connect
      client.connect(self.mqtt_broker, self.mqtt_port)
      return client

   def insert_to_DB(self,  data,
                     __database='farm', 
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

      conn.autocommit = True
      cursor = conn.cursor()
      # with self.lock:
      if self.topic == self.topic_list["sensor_gateway_server"]:
         query = f'''INSERT INTO api_sensormonitor (node_id_id, co2, temp, hum, time) 
                  VALUES (%s, %s, %s, %s ,%s)'''
         record = (1, data['info']['co2'], data['info']['temp'], data['info']['hum'], data['info']['time'])
         cursor.execute(query, record)
         print("Successfully insert SENSORRR to PostgreSQL")
         print(data['info']['time'])
         cursor.close()
         conn.close()
      elif self.topic == self.topic_list["actuator_gateway_server"]:
         query = f'''INSERT INTO api_actuatormonitor (node_id_id, speed, state, time) 
                  VALUES (%s, %s, %s, %s)'''
         record = (1, data['info']['speed'], data['info']['state'], data['info']['time'])
         cursor.execute(query, record)
         print("Successfully insert ACTUATORRR to PostgreSQL")
         print(data['info']['time'])
         cursor.close()
         conn.close()

   def subscribe(self, client):
         def on_message(client, userdata, msg):
            print(f"RRRRRRRRRRRRRRRReceived `{msg.payload.decode()}` from `{msg.topic}` topic")
            msg_str = msg.payload.decode("UTF-8")
            msg_json = json.loads(msg_str)
            if not msg_json:
               print("Did not receive anything!")
            else:
               self.insert_to_DB(msg_json,
                                 'farm',
                                 'quan', 
                                 '1', 
                                 'localhost', 
                                 '5432',)
         client.subscribe(self.topic)
         client.on_message = on_message


   def run(self, i):
      client = self.connect_mqtt()
      print(f"finish conecting {i}")
      self.subscribe(client)
      # client.loop_forever() #loop forever will trap the program in the loop forever
      client.loop_start()     #this will create a new thread that process the loop of mqtt which will not trap the program
      while True:
         continue




if __name__ == '__main__':
   process_list = []
   thread_list = []
   
   client_1 = Mqtt("27.71.227.1", 
                   1883, 
                   "farm/1/monitor",
                   'api_sensormonitor')
   print("Start client 1!!!")
   client_2 = Mqtt("27.71.227.1",
                   1883,
                   "farm/1/monitor/process",
                   'api_actuatormonitor')
   print("Start client 2!!!")
   process_list.append(multiprocessing.Process(target=client_1.run, args=(1,)))
   process_list.append(multiprocessing.Process(target=client_2.run, args=(2,)))
   
   thread_list.append(threading.Thread(target=client_1.run, args=(1,)))
   thread_list.append(threading.Thread(target=client_2.run, args=(2,)))

   for i in process_list:
      i.start()
   for i in process_list:
      i.join()


