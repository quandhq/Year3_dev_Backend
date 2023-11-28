"""
This file is for testing resgistration with gateway
"""

import datetime

import mqtt 
import time
import json
import random
import threading

# client = mqtt.Client(topic)
# client.connect(broker, int(1883), 60)
# client.loop_start()
# while True:
#     temp = client.msg_arrive()
#     if temp != None:
#         print("receive message!")
#         print(json.loads(temp))
#     random.seed(int((datetime.datetime.now()).timestamp()))
#     data1 = { 
#     "operator": "data_response", 
#     "status": 1, 
#     "info": { 
#         "room_id": 3, 
#         "node_id": random.randint(5,6),
#         # "node_id": 7, 
#         "co2": random.randint(100,400) + round(random.random(),2), 
#         "dust": random.randint(0,50) + round(random.random(),2),
#         "temp": random.randint(20,30) + round(random.random(),2), 
#         "hum": random.randint(70,80) + round(random.random(),2),
#         "time": int((datetime.datetime.now()).timestamp()) + (7*60*60), 
#     } 
#     } 
#     client.publish(topic, json.dumps(data1))
#     print("Done sending message")
#     time.sleep(20)
    
def func1():
    while(1):
        print("func1")
        time.sleep(2)    

def func2():
    while(1):
        print("func2")
        time.sleep(3)    
    
def test():
    t = threading.Thread(target=func1)
    t1 = threading.Thread(target=func2)
    t.start()
    t.join()
    t1.start()
    t1.join()
    return 

test()

# cd Year3_dev_Backend\Ver4_main\Year3\api
