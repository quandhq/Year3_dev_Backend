##
# @brief Draft file
#       Trying to test mqtt
#
import mqtt 
import time
import json
broker = "27.71.227.1"
topic = "farm/monitor/sensor"
data = {
    "operator": "room_sync",
    "status": 0,
    "info": 
    {
        "room_id": 2,
        "construction_name": "farm",
        "x_length": 20,
    	"y_length": 20,
        "node_list":
        [
            {
                "node_id": 1,
                "function": "sensor",
                "x_axis": 10,
                "y_axis": 10,
            },
            {
                "node_id": 2,
                "function": "sensor",
                "x_axis": 11,
                "y_axis": 11,
            },
            {
                "node_id": 3,
                "function": "sensor",
                "x_axis": 12,
                "y_axis": 12,
            },
        ]
    }
}
data1 = { 
  "operator": "data_response", 
  "status": 1, 
  "info": { 
    "room_id": 1, 
    "node_id": 1, 
    "co2": 400, 
    "temp": 60.52, 
    "hum": 29.32, 
    "time": 1655396252 
  } 
} 


client = mqtt.Client(topic)
client.connect(broker, int(1883), 60)
client.loop_start()
while True:
    temp = client.msg_arrive()
    if temp != None:
        print("receive message!")
        print(json.loads(temp))
    client.publish(topic, json.dumps(data1))
    print("Done sending message")
    time.sleep(3)