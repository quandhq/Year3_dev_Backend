import random
import paho.mqtt.client as mqtt
import psycopg2
import json

#-----------------------------THIS ONE IS CURRENTLY USED---------------------------------------

class Mqtt():
   #turn on emqx on laptop first "emqx start", be careful that this ip is random whenever we reconnect to the internet
   mqtt_broker = "172.19.200.236"         
   mqtt_port = 1883
   topic = "Year3/Gateway"
   # generate client ID with pub prefix randomly
   client_id = f'python-mqtt-{random.randint(0, 100)}'
   # username = 'emqx'
   # password = 'public'
   def __init__(self, 
               __mqtt_broker = "172.19.200.236", 
               __mqtt_port = 1883, 
               __topic = "Year3/Gateway"):
      self.mqtt_broker = __mqtt_broker
      self.mqtt_port = __mqtt_port
      self.topic = __topic


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

   def insert_to_DB(self,data):
      conn = psycopg2.connect(
            database = 'year3',
            user = 'quan',
            password = '1',
            host = 'localhost',
            port = '5432',
         )

      conn.autocommit = True
      cursor = conn.cursor()

      query = '''INSERT INTO api_sensor(time, temperature, humidity, light, dust, sound, red, green, blue, co2, tvoc, motion, id) 
      VALUES (%s, %s, %s, %s ,%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
      record = (data['infor']['time'], data['infor']['temperature'], data['infor']['humidity'], data['infor']['light'], data['infor']['dust'],
                  data['infor']['sound'], data['infor']['red'], data['infor']['green'], data['infor']['blue'], data['infor']['co2'], data['infor']['tvoc']
                  , data['infor']['motion'], data['infor']['id'])
      cursor.execute(query, record)

      conn.close()

   # def subscribe(self, client):
   #    def on_message(client, userdata, msg):
   #       print(f"RRRRRRRRRRRRRRRReceived `{msg.payload.decode()}` from `{msg.topic}` topic")
   #       msg_str = msg.payload.decode("UTF-8")
   #       msg_json = json.loads(msg_str)
   #       self.insert_to_DB(msg_json)
   #       print(msg_json['infor']['time'])

   #    client.subscribe(self.topic)
   #    client.on_message = on_message


   # def run(self):
   #    client = self.connect_mqtt()
   #    self.subscribe(client)
   #    client.loop_start()

#___________________try new code: try exception______________
   def subscribe(self, client):
         def on_message(client, userdata, msg):
            print(f"RRRRRRRRRRRRRRRReceived `{msg.payload.decode()}` from `{msg.topic}` topic")
            msg_str = msg.payload.decode("UTF-8")
            msg_json = json.loads(msg_str)
            if not msg_json:
               print("Did not receive anything!")
            else:
               self.insert_to_DB(msg_json)
               print("INSERT SUCCESSFULLY!!!!!!!!")
               print(msg_json['infor']['time'])
         client.subscribe(self.topic)
         client.on_message = on_message


   def run(self):
      client = self.connect_mqtt()
      self.subscribe(client)
      # client.loop_forever() #loop forever will trap the program in the loop forever
      client.loop_start()     #this will create a new thread that process the loop of mqtt which will not trap the program



# if __name__ == '__main__':
#    run()