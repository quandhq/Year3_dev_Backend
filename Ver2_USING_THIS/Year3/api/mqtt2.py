import paho.mqtt.client as mqtt
import json

from paho.mqtt.client import _OnMessage


class Client(mqtt.Client):
    def __init__(self):
        super().__init__()
    # this function is call whenever a successful connection is fulfiled
    def on_connect(self, client, userdata, flag, rc):
        if rc == 0:
            print("Successfully connect to MQTT Broker!!!")
        else:
            print("Connection to MQTT Broker failed!!!")
    def on_message(self):
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
               print("INSERT SUCCESSFULLY!!!!!!!!")
               print(msg_json['info']['time'])