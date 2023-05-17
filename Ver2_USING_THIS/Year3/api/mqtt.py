# import paho.mqtt.client as mqtt
# import json
# import psycopg2


# # mqtt_broker = "broker.mqttdashboard.com"
# mqtt_broker = "broker.hivemq.com"
# mqtt_port = 1883
# topic = "Year3"

# def on_connect(client, userdata, flags, rc):
#     print("Connected successfully from mqtt.py")
#     client.subscribe(topic)

# def insert_to_DB(data):
#     conn = psycopg2.connect(
#         database = 'year3',
#         user = 'quan',
#         password = '1',
#         host = 'localhost',
#         port = '5432',
#     )

#     conn.autocommit = True
#     cursor = conn.cursor()

#     query = '''INSERT INTO api_sensor(time, temperature, humidity, light, dust, sound, red, green, blue, co2, tvoc, motion, id) 
#     VALUES (%s, %s, %s, %s ,%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
#     record = (data['infor']['time'], data['infor']['temperature'], data['infor']['humidity'], data['infor']['light'], data['infor']['dust'],
#                 data['infor']['sound'], data['infor']['red'], data['infor']['green'], data['infor']['blue'], data['infor']['co2'], data['infor']['tvoc']
#                 , data['infor']['motion'], data['infor']['id'])
#     cursor.execute(query, record)

#     conn.close()

# def on_message(client, userdata, msg):
#     msg_str = msg.payload.decode("UTF-8")
#     msg_json = json.loads(msg_str)
#     insert_to_DB(msg_json)
#     print(msg_json['infor']['time'])


# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(mqtt_broker, mqtt_port, 60)

