from django.db import models

# Create your models here.
from django.conf import settings


##
# @brief This table is for Room data, how many rooms are there, including 
#        their id (unique), construction name ("farm" or "building"),
#        their size (length and width) which is used for rendering heatmap.
#
class Room(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.IntegerField(null=False, unique=True, db_column="room_id",)   #!< BigAutoField make the field keep increaing value and unique.
    construction_name = models.TextField(db_column="construction_name")
    x_length = models.SmallIntegerField(db_column="x_length")
    y_length = models.SmallIntegerField(db_column="y_length")
    information = models.TextField(null=False, db_column="information")

##
# @brief This table is for storing node data, including how many node are being emplemented,
#        the id of the room where it is being emplemented, and their mac address.
#
class Registration(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    x_axis = models.IntegerField(null=False, db_column="x_axis",)
    y_axis = models.IntegerField(null=False, db_column="y_axis",)
    function = models.TextField(null=False, db_column="function",)
    mac = models.TextField(null=False, db_column="mac",)
    status = models.TextField(null=False, db_column="status",)
    time = models.BigIntegerField(null=False, db_column="time",)



##
# @brief This table is for storing sensor node data.
#
class RawSensorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    co2 = models.SmallIntegerField(null=True,db_column="co2",)
    temp = models.FloatField(null=True, db_column="temp",)
    hum  = models.FloatField(null=True, db_column="hum",)
    light = models.FloatField(null=True, db_column="light",)
    dust = models.FloatField(null=True, db_column="dust",)
    sound = models.FloatField(null=True, db_column="sound",)
    red = models.SmallIntegerField(null=True, db_column="red",)
    green = models.SmallIntegerField(null=True, db_column="green",)
    blue = models.SmallIntegerField(null=True, db_column="blue",)
    tvoc = models.SmallIntegerField(null=True, db_column="tvoc",)
    motion = models.SmallIntegerField(null=True, db_column="motion",)
    time = models.BigIntegerField(null=False, db_column="time",)
    def __str__(self):
        return self.time

class SensorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    co2 = models.SmallIntegerField(null=True,db_column="co2",)
    temp = models.FloatField(null=True, db_column="temp",)
    hum  = models.FloatField(null=True, db_column="hum",)
    light = models.FloatField(null=True, db_column="light",)
    dust = models.FloatField(null=True, db_column="dust",)
    sound = models.FloatField(null=True, db_column="sound",)
    red = models.SmallIntegerField(null=True, db_column="red",)
    green = models.SmallIntegerField(null=True, db_column="green",)
    blue = models.SmallIntegerField(null=True, db_column="blue",)
    tvoc = models.SmallIntegerField(null=True, db_column="tvoc",)
    motion = models.SmallIntegerField(null=True, db_column="motion",)
    time = models.BigIntegerField(null=False, db_column="time",)
    def __str__(self):
        return self.time

class RawActuatorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    speed = models.SmallIntegerField(db_column="speed")
    state = models.SmallIntegerField(db_column="state")
    time = models.BigIntegerField(db_column="time")
    def __str__(self):
        return self.time
   
class ActuatorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    speed = models.SmallIntegerField(db_column="speed")
    state = models.SmallIntegerField(db_column="state")
    time = models.BigIntegerField(db_column="time")
    def __str__(self):
        return self.time

class ControlSetpoint(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room,
                                verbose_name=("Refering to room that this is trying to set value for"),
                                on_delete=models.CASCADE,
                                null=False,     
                                db_column="room_id",                        
                                )
    node_id = models.IntegerField(null=True, db_column="node_id",)
    option = models.TextField(db_column="option")
    aim = models.TextField(db_column="aim")
    value = models.FloatField(db_column="value")
    time = models.BigIntegerField(db_column="time")
    def __str__(self):
        return self.time
    
class SetTimerHistory(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room,
                                verbose_name=("Refering to room that this is trying to set timer value for"),
                                on_delete=models.CASCADE,
                                null=False,     
                                db_column="room_id",                        
                                )
    time = models.BigIntegerField(db_column="time")
    timer = models.IntegerField(null=False, db_column="timer",)
    temperature = models.IntegerField(null=False, db_column="temperature",)
    status = models.IntegerField(null=False, db_column="status",) #1 or 0

class NodeConfigBuffer(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    action = models.IntegerField(null=False, db_column="action")
    mac = models.TextField(null=False, db_column="mac", unique=True)
    room_id = models.IntegerField(null=False, db_column="room_id")
    time = models.BigIntegerField(null=False, db_column="time")
    
    
class AqiRef(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    aqi = models.IntegerField(null=True, db_column="aqi")
    pm25 = models.IntegerField(null = True, db_column="pm25") #pm2.5
    pm10 = models.IntegerField(null = True, db_column="pm10") #pm10
    o3 = models.IntegerField(null = True, db_column="o3")       
    no2 = models.IntegerField(null = True, db_column="no2")
    so2 = models.IntegerField(null = True, db_column="so2")
    co = models.IntegerField(null = True, db_column="co")
    t = models.IntegerField(null = True, db_column="t") #temperature
    p = models.IntegerField(null = True, db_column="p") #pressure
    h = models.IntegerField(null = True, db_column="h") #humidity
    w = models.IntegerField(null = True, db_column="w") #wind
    time = models.BigIntegerField(null = True, db_column="time")    #time
    dew = models.IntegerField(null = True, db_column="dew")
    wg = models.IntegerField(null = True, db_column="wg")
    
    
    
    
    
    


