
import calendar
import datetime
import random
import json
 
new_data = {
                     "operator":"senData",
                     "infor":{
                        "id":f"{random.randint(1,8)}",
                        "time":1,
                        "red":{str(random.randint(0,3000))},
                        "green":{str(random.randint(0,3000))},
                        "blue":{str(random.randint(0,3000))},
                        "clear":{str(random.randint(0,3000))},
                        "light":{str(random.randint(0,3000))},
                        "co2":{str(random.randint(0,3000))},
                        "dust":str(round(random.uniform(1, 100),2)),
                        "tvoc":"0",
                        "motion":str(random.randint(0,1)),
                        "sound":str(round(random.uniform(1, 1000),2)),
                        "temperature":str(round(random.uniform(1, 100),2)),
                        "humidity":str(round(random.uniform(1, 100),2)),
                        "status":"0"
                     }
                  }
json_ = json.dumps(list(new_data))
print(json_)
print(type(new_data))