##
# @brief clone mqtt receiver
#       
#

backend_topic_dictionary = {"get_sensor_data": "farm/monitor/sensor",
                        "get_actuator_data": "farm/monitor/actuator",
                        "get_setpoint": "farm/control",
                        "room_sync_gateway_backend": "farm/sync_room",
                        "set_timer": "farm/set_timer",}

import mqtt 
import time
import json
broker = "27.71.227.1"
client = mqtt.Client("testtopic", _topic_array=[backend_topic_dictionary["set_timer"]])
client.connect(broker, int(1883), 60)
client.loop_start()
while(1):
    temp = client.msg_arrive()
    if temp != None:
        print("receive message!")
        data = json.loads(temp)
        print(json.loads(temp))
        if data["operator"] == "set_timer":
            client.publish(backend_topic_dictionary["set_timer"], json.dumps({
                "operator": "set_timer_ack",
                "info": {
                    "status": 1,
                }
            }))