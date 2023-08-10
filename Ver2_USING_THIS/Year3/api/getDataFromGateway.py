import mqtt
import multiprocessing
import json
import psycopg2

broker = "27.71.227.1"

thing_topic_dictionary = {"get_register": "farm/1/register",
                        "send_register_ack": "farm/1/register",
                        "get_alive_status": "farm/1/alive",
                        "get_sensor_data": "farm/1/sensor",
                        "get_actuator_data": "farm/1/actuator",
                        "send_setpoint": "farm/1/actuator",
                        "send_setpoint_ack": "farm/1/actuator",}

backend_topic_dictionary = {"send_sensor_data": "farm/1/monitor",
                        "send_actuator_data": "farm/1/monitor/process",
                        "get_setpoint": "farm/1/control",}

def insert_to_DB(topic,
                        data,
                        __database='smartfarm', 
                        __user='year3', 
                        __password='year3', 
                        __host='localhost', 
                        __port='5432') -> None:
    conn = psycopg2.connect(
            database = __database,
            user = __user,
            password = __password,
            host = __host,
            port = __port,
        )

    conn.autocommit = True
    cursor = conn.cursor()
    # with self.lock:
    if topic == backend_topic_dictionary["send_sensor_data"]:
        query = f'''INSERT INTO api_sensormonitor (node_id_id, co2, temp, hum, time) 
                VALUES (%s, %s, %s, %s ,%s)'''
        record = (1, data['info']['co2'], data['info']['temp'], data['info']['hum'], data['info']['time'])
        cursor.execute(query, record)
        print("Successfully insert SENSORRR to PostgreSQL")
        print(data['info']['time'])
        cursor.close()
        conn.close()
    elif topic == backend_topic_dictionary["send_actuator_data"]:
        query = f'''INSERT INTO api_actuatormonitor (node_id_id, speed, state, time) 
                VALUES (%s, %s, %s, %s)'''
        record = (1, data['info']['speed'], data['info']['state'], data['info']['time'])
        cursor.execute(query, record)
        print("Successfully insert ACTUATORRR to PostgreSQL")
        print(data['info']['time'])
        cursor.close()
        conn.close()
    

def run(topic):
    client = mqtt.Client(topic)
    client.connect(broker, int(1883), 60)

    client.loop_start()

    
    while(1):
        temp = client.msg_arrive()
        if temp != None:
            print(f"RRRRRRRRRRRRRRRReceived `{temp}` from topic `{topic}`")
            msg = json.loads(temp)
            insert_to_DB(topic,
                        msg,
                        'smartfarm', 
                        'year3', 
                        'year3', 
                        'localhost', 
                        '5432')

if __name__ == "__main__":
    process_list = []
    process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["send_sensor_data"],)))
    process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["send_actuator_data"],)))
    for i in process_list:
        i.start()
    for i in process_list:
        i.join()