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
                        "get_setpoint": "farm/1/control",
                        "room_sync_gateway_backend": "",
                        "room_sync_ack_backend_gateway": "",
                        }

def insert_to_DB(topic,
                        data,
                        __database='smart_building', 
                        __user='quan', 
                        __password='1',
                        # __database='smartfarm', 
                        # __user='year3', 
                        # __password='year3', 
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
        query = f'''INSERT INTO api_rawsensormonitor (node_id, co2, temp, hum, time) 
                  VALUES (%s, %s, %s, %s ,%s)'''
        record = (1, data['info']['co2'], data['info']['temp'], data['info']['hum'], data['info']['time'])
        cursor.execute(query, record)
        print("Successfully insert SENSORRR to PostgreSQL")
        print(data['info']['time'])
        cursor.close()
        conn.close()
    elif topic == backend_topic_dictionary["send_actuator_data"]:
        query = f'''INSERT INTO api_rawactuatormonitor (node_id, speed, state, time) 
                  VALUES (%s, %s, %s, %s)'''
        record = (1, data['info']['speed'], data['info']['state'], data['info']['time'])
        cursor.execute(query, record)
        print("Successfully insert ACTUATORRR to PostgreSQL")
        print(data['info']['time'])
        cursor.close()
        conn.close()
    elif topic == backend_topic_dictionary["room_sync_gateway_backend"]:
        from psycopg2.extras import DictCursor
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = f"""SELECT * FROM api_registration WHERE room_id = {1}"""
        cursor.execute(query)
        all_nodes_in_room_list:list =cursor.fetchall()
        current_node_id_list = [i["id"] for i in all_nodes_in_room_list]   #!< get all current ids of nodes
        new_node_data:list = []  #!< this contains all the new nodes whichs will be inserted into database
        for node in data["info"]["node_list"]:  #!< get all the new nodes which is not present in database
            if node["node_id"] not in current_node_id_list:
                new_node_data.append(node)
            else:
                continue
        for new_node in new_node_data:
            this_query = '''INSERT INTO api_registration (id, room_id, x_axis, y_axis, function) 
                        VALUES (%s, %s, %s, %s, %s)'''
            this_record = (new_node["id"], data["info"]["room_id"], new_node["x_axis"], new_node["y_axis"], new_node["function"])
            cursor.execute(this_query, this_record)
        cursor.close()
        conn.close()
    

def run(topic):
    client = mqtt.Client(topic) 
    client.connect(broker, int(1883), 60)           #<! this will automatically subscribe to the topic
    # client.subscribe("farm/1/control")
    # client.subscribe(topic)

    client.loop_start()
    ##
    # @brief if topic == `backend_topic_dictionary["room_sync_gateway_backend"]`
    #        This "if block" is to handle sync message from gateway when a new node is added to gateway,
    #        it will add all new nodes to database and then send back a ack-message to topic "....." 
    #
    if topic == backend_topic_dictionary["room_sync_gateway_backend"]:
        while(1):
            temp = client.msg_arrive()
            if temp != None:
                print(f"RRRRRRRRRRRRRRRReceived `{temp}` from topic `{topic}`")
                msg = json.loads(temp)
                if msg["operator"] == "sync_room":
                    insert_to_DB(topic,
                                msg,
                                # 'smartfarm', 
                                # 'year3', 
                                # 'year3',
                                'smart_construction',
                                'quan',
                                '1',
                                'localhost', 
                                '5432')
                else:
                    continue
                msg_response = msg
                msg_response["operator"] = "ack_sync_room"
                client.publish(backend_topic_dictionary["room_sync_ack_backend_gateway"], json.dumps(msg_response))
    else:
        while(1):
            temp = client.msg_arrive()
            if temp != None:
                print(f"RRRRRRRRRRRRRRRReceived `{temp}` from topic `{topic}`")
                msg = json.loads(temp)
                insert_to_DB(topic,
                            msg,
                            # 'smartfarm', 
                            # 'year3', 
                            # 'year3',
                            'smart_construction',
                            'quan',
                            '1',
                            'localhost', 
                            '5432')
        

if __name__ == "__main__":
    process_list = []
    # process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["room_sync_gateway_backend"])))
    process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["send_sensor_data"],)))
    process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["send_actuator_data"],)))
    for i in process_list:
        i.start()
    for i in process_list:
        i.join()