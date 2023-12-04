# """
# This file is for testing resgistration with gateway
# """

# import datetime

# import mqtt 
# import time
# import json
# import random
# import threading

# topic = "farm/sync_node"
# broker = "27.71.227.1"

# client = mqtt.Client(topic)
# client.connect(broker, int(1883), 60)
# client.loop_start()
# while True:
#     # client.subscribe(topic)
#     temp = client.msg_arrive()
#     if temp != None:
#         # client.unsubscribe(topic)
#         print("receive message!")
#         print(json.loads(temp))
#         # new_data = { 
#         #         "operator": "server_add_ack", 
#         #         "status": 1, 
#         #         "info": { 
#         #             "room_id": 1, 
#         #             "node_id": 100,
#         #             "mac_address": "TEST", 
#         #             "time": 1655396252,
#         #             } 
#         #         }
#         new_data = { 
#                 "operator": "server_delete_ack", 
#                 "status": 1, 
#                 "info": { 
#                     "room_id": 1, 
#                     "node_id": 100,
#                     "mac_address": "TEST", 
#                     "time": 1655396252,
#                     } 
#                 } 
#         client.publish("farm/sync_node", json.dumps(new_data))
#         print(f"Done sending message! {new_data}")
    
# def func1():
#     while(1):
#         print("func1")
#         time.sleep(2)    

# def func2():
#     while(1):
#         print("func2")
#         time.sleep(3)    
    
# def test():
#     t = threading.Thread(target=func1)
#     t1 = threading.Thread(target=func2)
#     t.start()
#     t.join()
#     t1.start()
#     t1.join()
#     return 

# test()

# cd Year3_dev_Backend\Ver4_main\Year3\api

import requests
# from api.serializers import RegistrationSerializer, NodeConfigBufferSerializer

from api.models import ActuatorMonitor

def getDataForAqiRef():
    url = "https://api.waqi.info/feed/here/?token=08f2de731b94a1ff55e871514aa8f145e12ebafe"
    while 1:    
        data = requests.get(url)
        if data.status_code == 200:
            data_json = data.json()
            print(data_json["data"]["time"]["v"])
        
getDataForAqiRef()