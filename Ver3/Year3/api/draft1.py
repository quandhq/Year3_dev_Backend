##
# @brief Draft file
#       Trying to test mqtt
#
import mqtt 
import time
import json
broker = "27.71.227.1"
client = mqtt.Client("testtopic")
client.connect(broker, int(1883), 60)
client.loop_start()
while True:
    temp = client.msg_arrive()
    if temp != None:
        print("receive message!")
        print(json.loads(temp))
    client.publish("testtopic", json.dumps({"test": "TESTING FROM DRAF1"}))
    print("Done sending message")
    time.sleep(1)