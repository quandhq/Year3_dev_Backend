import random
import paho.mqtt.client as mqtt
import psycopg2
import json
import multiprocessing
import threading
import time

from psycopg2.extras import DictCursor
conn = psycopg2.connect(
            database = "smart_construction",
            user = "quan",
            password = "1",
            host = "localhost",
            port = '5432',
         )

data = {
    "operator": "sync_room",
    "info": 
    {
        "room_id": 1,
        "construction_name": "farm",
        "node_list":
        [
            {
                "node_id": 1,
                "function": "sensor",
                "x_axis": 6,
                "y_axis": 6,
            },
            {
                "node_id": 25,
                "function": "sensor",
                "x_axis": 6,
                "y_axis": 6,
            },
        ]
    }
}
conn.autocommit = True
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