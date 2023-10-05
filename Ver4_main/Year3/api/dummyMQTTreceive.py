##
# @brief clone mqtt receiver
#       
#

import mqtt 
import time
import json
broker = "27.71.227.1"
client = mqtt.Client("testtopic")
client.connect(broker, int(1883), 60)
client.loop_start()
while(1):
    temp = client.msg_arrive()
    if temp != None:
        print("receive message!")
        print(json.loads(temp))