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

backend_topic_dictionary = {"get_sensor_data": "farm/monitor/sensor",
                        "get_actuator_data": "farm/monitor/actuator",
                        "get_setpoint": "farm/control",
                        "room_sync_gateway_backend": "farm/sync_room",
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
    if topic == backend_topic_dictionary["get_sensor_data"]:
        query = f'''INSERT INTO api_rawsensormonitor (room_id, node_id, co2, temp, hum, light, 
                    dust, sound, red, green, blue, tvoc, motion, time) 
                  VALUES (%s, %s, %s, %s ,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        parameter_key_list = ["co2", "temp", "hum", "light", 
                         "dust", "sound", "red", "green", 
                         "blue", "tvoc", "motion", "time"]
        record = (data["info"]["room_id"], data["info"]["node_id"])
        for i in parameter_key_list:
            if i not in data["info"]:
                record = record + (0,)
            else:
                record = record + (data["info"][i], )   #!< create a tupble of one element "data["info"][i]" and concatenate it to record
        print(record)    
        
        # record = (data["info"]["room_id"], 
        #           data["info"]["node_id"], 
        #           data['info']['co2'], 
        #           data['info']['temp'], 
        #           data['info']['hum'], 
        #           data['info']['time'])
        cursor.execute(query, record)
        print("Successfully insert SENSORRR to PostgreSQL")
        print(data['info']['time'])
        cursor.close()
        conn.close()
    elif topic == backend_topic_dictionary["get_actuator_data"]:
        query = f'''INSERT INTO api_rawactuatormonitor (room_id, node_id, speed, state, time) 
                  VALUES (%s, %s, %s, %s, %s)'''
        record = (data["info"]["room_id"], data["info"]["node_id"], data['info']['speed'], data['info']['state'], data['info']['time'])
        cursor.execute(query, record)
        print("Successfully insert ACTUATORRR to PostgreSQL")
        print(data['info']['time'])
        cursor.close()
        conn.close()
    elif topic == backend_topic_dictionary["room_sync_gateway_backend"]:
        ##
        # @brief This block is for handling data from topic "room_sync"
        #        The data coming will be as followed
        #        {
                #     "operator": "room_sync",
                #     "status": `0: send all nodes | 1: add one new node | 2: delete nodes`,
                #     "info":
                #     {
                #         "room_id": {room_id},
                #         "x_length": `x_length`,
                #         "y_length": `y_length`,
                #         "contruction_name": `"farm" or "building"`,
                #         "node_list":
                #             [
                #             {"node_id": `node_id`, "function": `"sensor" or "actuator"`, "x_axis": `x_axis`, "y_axis": `y_axis`},
                #             ...
                #             ]
                #     }
                # }
        ######
        if data["status"] == 0:    #!< status = 0 means that gateway will send all nodes available to server
            from psycopg2.extras import DictCursor
            cursor = conn.cursor(cursor_factory=DictCursor)
            #First check if room is registered in database, if not add it to database
            query = f"""SELECT * FROM api_room"""
            cursor.execute(query)
            all_rooms_in_database_list = cursor.fetchall()  #!< a list that contains all room_id that available in database
            current_room_id_in_database_list = [i["room_id"] for i in all_rooms_in_database_list]
            if data["info"]["room_id"] not in current_room_id_in_database_list:
                print("This room is not in database status 0")
                #add new room_id to database
                this_query = f"""INSERT INTO api_room (room_id, construction_name, x_length, y_length)
                            VALUES (%s, %s, %s, %s)"""
                this_record = (data["info"]["room_id"], data["info"]["construction_name"], data["info"]["x_length"], data["info"]["y_length"])
                cursor.execute(this_query, this_record)
                print("Done add new room status 0")
            #Next check all nodes of this room and add them to database if they are not registered

            query = f"""SELECT * FROM api_registration WHERE room_id = {data["info"]["room_id"]}"""   #!< FIX: fix room_id 
            cursor.execute(query)
            all_nodes_in_room_list:list =cursor.fetchall()
            current_node_id_list = [i["node_id"] for i in all_nodes_in_room_list]   #!< get all current ids of nodes
            new_node_data:list = []  #!< this contains all the new nodes whichs will be inserted into database
            for node in data["info"]["node_list"]:  #!< get all the new nodes which is not present in database
                if node["node_id"] not in current_node_id_list:
                    new_node_data.append(node)
                else:
                    continue
            if(new_node_data.__len__() > 0):    #!< if there are new nodes needed to be inserted into database
                for new_node in new_node_data:
                    this_query = '''INSERT INTO api_registration (room_id, node_id ,x_axis, y_axis, function) 
                                VALUES (%s, %s, %s, %s, %s)'''
                    this_record = (data["info"]["room_id"], new_node["node_id"], new_node["x_axis"], new_node["y_axis"], new_node["function"])
                    cursor.execute(this_query, this_record)
                print("Done execute status 0")
            else:
                print("No need to done status 0")
            cursor.close()
            conn.close()
        elif data["status"] == 1: #!< status = 1 means that gateway will add one new node to server
            from psycopg2.extras import DictCursor
            cursor = conn.cursor(cursor_factory=DictCursor)
            query = f"""SELECT * FROM api_registration WHERE room_id = {data["info"]["room_id"]}"""
            cursor.execute(query)
            all_nodes_in_room_list:list =cursor.fetchall()
            current_node_id_list = [i["node_id"] for i in all_nodes_in_room_list]   #!< get all current ids of nodes
            new_node_data:list = []  #!< this contains all the new nodes whichs will be inserted into database
            for node in data["info"]["node_list"]:  #!< get all the new nodes which is not present in database
                if node["node_id"] not in current_node_id_list:
                    new_node_data.append(node)
                else:
                    continue
            for new_node in new_node_data:
                this_query = '''INSERT INTO api_registration (room_id, node_id, x_axis, y_axis, function) 
                            VALUES (%s, %s, %s, %s, %s)'''
                this_record = (data["info"]["room_id"], new_node["node_id"], new_node["x_axis"], new_node["y_axis"], new_node["function"])
                cursor.execute(this_query, this_record)
                print("Done execute status 1")
            cursor.close()
            conn.close()
        elif data["status"] == 2: #!< status = 2 means that gateway will send list of sensors need to be deleted from database
            from psycopg2.extras import DictCursor
            cursor = conn.cursor(cursor_factory=DictCursor)
            query = f"""SELECT * FROM api_registration WHERE room_id = {data["info"]["room_id"]}"""
            cursor.execute(query)
            all_nodes_in_room_list:list =cursor.fetchall()
            current_node_id_list = [i["node_id"] for i in all_nodes_in_room_list]   #!< get all current ids of nodes
            node_to_be_deleted_list:list = []  #!< this contains all the nodes whichs gateway wants server to delete
            for node in data["info"]["node_list"]:  #!< get all nodes which gateway wants server to delete
                if node["node_id"] in current_node_id_list: #!< if node to be deleted presents in database, add it to list
                    node_to_be_deleted_list.append(node)
                else:                           #!< if not, do not care
                    continue
            for each_node in node_to_be_deleted_list:
                this_query = f'''DELETE FROM api_registration WHERE node_id = {each_node["node_id"]}'''
                cursor.execute(this_query)
                print("Done execute status 2")
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
                if msg["operator"] == "room_sync":
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
                msg_response = {
                        "operator": "room_sync_ack",
                        "status": 0,
                        "info":
                        {
                        }
                    }
                msg_response["operator"] = "room_sync_ack"
                client.publish(backend_topic_dictionary["room_sync_gateway_backend"], json.dumps(msg_response))
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
    process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["room_sync_gateway_backend"],))) #!< must have ',' in the finishing of set args
    process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["get_sensor_data"],)))          #!< must have ',' in the finishing of set args
    process_list.append(multiprocessing.Process(target=run, args=(backend_topic_dictionary["get_actuator_data"],)))        #!< must have ',' in the finishing of set args
    for i in process_list:
        i.start()
    for i in process_list:
        i.join()