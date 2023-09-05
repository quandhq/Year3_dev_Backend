from .models import RawSensorMonitor
import pandas as pd
import datetime

def getOptionDayData(day):
    # http://localhost:8000/api/v1.1/monitor/data/history?farm_id=1&time_start=1684765622&time_end=1684765622&option=day
    print("state time line")
    print(day)
    print(datetime.datetime.fromtimestamp(day+25200).day)
    sensorMonitorList= RawSensorMonitor.objects.filter(time__gt=day)   #time__gt = "time greater than"
    list_co2 = []
    list_temp = []
    list_hum  = []
    list_time = []
    data = {
        'timestamp': list_time,
        'co2': list_co2,
        'temp': list_temp,
        'hum': list_hum,

    }
    for sensorData in sensorMonitorList:
        data['timestamp'].append(sensorData.__dict__['time'])
        data['co2'].append(sensorData.__dict__['co2'])
        data['temp'].append(sensorData.__dict__['temp'])
        data['hum'].append(sensorData.__dict__['hum'])
    table = pd.DataFrame(data)
    table.sort_values(by='timestamp', inplace=True)
    table.drop_duplicates(subset='timestamp', inplace=True)
    table['timestamp'] += 3600*7
    table['datetime'] = pd.to_datetime(table['timestamp'], unit='s')
    table['day'] = table['datetime'].dt.day
    table['hour'] = table['datetime'].dt.hour
    print(table)
    table = table.loc[table['day'] == datetime.datetime.fromtimestamp(day+25200).day]
    table1 = table.groupby(['hour'], as_index=False).mean()
    table1['co2'] = round(table1['co2'],0)
    table1['temp'] = round(table1['temp'],0)
    table1['hum'] = round(table1['hum'],0)
    print(table1)
    listHours = [*range(1, 25)]
    for i in table1.index:
        if table1.loc[i, 'hour'] in listHours:
            listHours.remove(table1.loc[i, 'hour'])
    extra_data = {
        'hour': [],
        'co2': [],
        'temp': [],
        'hum': [],
    }
    for hour in listHours:
        for key in extra_data:
            if str(key) == "hour":
                extra_data[key].append(hour)
            else: 
                extra_data[key].append(0)
    extra_df = pd.DataFrame(extra_data)
    table1 = pd.concat([table1, extra_df], ignore_index=True)
    table_result = table1.sort_values(by='hour')
    listTime = []    
    for i in table_result['hour'].tolist():
        listTime.append(int(float(str(i))))
    listCo2 = table_result['co2'].tolist()
    listTemp = table_result['hum'].tolist()
    listHum = table_result['temp'].tolist()
    print(table_result)
    return {"time": listTime, "co2": listCo2, "temp": listTemp, "hum": listHum}


def getOptionMonthData(time_start, time_end):
    # http://localhost:8000/api/v1.1/monitor/data/history?farm_id=1&time_start=1684750364&time_end=1688966425&option=month
    print(datetime.datetime.fromtimestamp(time_start).month)
    print(datetime.datetime.fromtimestamp(time_start).year)
    filter_month = datetime.datetime.fromtimestamp(time_start).month
    filter_year = datetime.datetime.fromtimestamp(time_start).year
    if((time_end - time_start) > 3600*24*30):
        time_end = time_start + 3600*24*30
    sensorMonitorList= RawSensorMonitor.objects.filter(time__gt=time_start, time__lt=time_end) #time_gt = time greater than
    list_time = []
    list_co2 = []
    list_temp = []
    list_hum  = []
    data = {
        'timestamp': list_time,
        'co2': list_co2,
        'temp': list_temp,
        'hum': list_hum,

    }
    for sensorData in sensorMonitorList:
        data['timestamp'].append(sensorData.__dict__['time'])
        data['co2'].append(sensorData.__dict__['co2'])
        data['temp'].append(sensorData.__dict__['temp'])
        data['hum'].append(sensorData.__dict__['hum'])
    table = pd.DataFrame(data)
    table.sort_values(by='timestamp', inplace=True)
    table.drop_duplicates(subset='timestamp', inplace=True)
    table['timestamp'] += 3600*7
    table['datetime'] = pd.to_datetime(table['timestamp'], unit='s')
    table['year'] = table['datetime'].dt.year
    table['month'] = table['datetime'].dt.month
    table['day'] = table['datetime'].dt.day
    table['hour'] = table['datetime'].dt.hour
    table1 = table.groupby(['day'], as_index=False).mean(numeric_only=True)      #group all data by "day"
    table1['co2'] = round(table1['co2'],0)
    table1['temp'] = round(table1['temp'],0)
    table1['hum'] = round(table1['hum'],0)
    table1['hour'] = round(table1['hour'],0)
    table1 = table1.sort_values(by=['month', 'day'], ascending=[True, True])
    print(table1)
    listTime = []    
    for row in table1.itertuples(index=False):
        listTime.append(f"{str(int(float(str(row.day))))}/{str(int(float(str(row.month))))}/{str(int(float(str(row.year))))}")
    print(listTime)
    listCo2 = table1['co2'].tolist()
    listTemp = table1['hum'].tolist()
    listHum = table1['temp'].tolist()
    return {"time": listTime, "co2": listCo2, "temp": listTemp, "hum": listHum}

def getOptionYearData(time_start, time_end):
    # http://localhost:8000/api/v1.1/monitor/data/history?farm_id=1&time_start=1684750364&time_end=1688965929&option=year
    print(datetime.datetime.fromtimestamp(time_start).month)
    print(datetime.datetime.fromtimestamp(time_start).year)
    filter_month = datetime.datetime.fromtimestamp(time_start).month
    filter_year = datetime.datetime.fromtimestamp(time_start).year
    if((time_end - time_start) > 3600*24*30*12):
        time_end = time_start + 3600*24*30*12
    sensorMonitorList= RawSensorMonitor.objects.filter(time__gt=time_start, time__lt=time_end) #time_gt = time greater than
    list_time = []
    list_co2 = []
    list_temp = []
    list_hum  = []
    data = {
        'timestamp': list_time,
        'co2': list_co2,
        'temp': list_temp,
        'hum': list_hum,

    }
    for sensorData in sensorMonitorList:
        data['timestamp'].append(sensorData.__dict__['time'])
        data['co2'].append(sensorData.__dict__['co2'])
        data['temp'].append(sensorData.__dict__['temp'])
        data['hum'].append(sensorData.__dict__['hum'])
    table = pd.DataFrame(data)
    table.sort_values(by='timestamp', inplace=True)
    table.drop_duplicates(subset='timestamp', inplace=True)
    table['timestamp'] += 3600*7
    table['datetime'] = pd.to_datetime(table['timestamp'], unit='s')
    table['year'] = table['datetime'].dt.year
    table['month'] = table['datetime'].dt.month
    table['day'] = table['datetime'].dt.day
    table['hour'] = table['datetime'].dt.hour
    table1 = table.groupby(['month'], as_index=False).mean(numeric_only=True)      #group all data by "day"
    print(table1)
    table1['co2'] = round(table1['co2'],0)
    table1['temp'] = round(table1['temp'],0)
    table1['hum'] = round(table1['hum'],0)
    table1['hour'] = round(table1['hour'],0)
    table1 = table1.sort_values(by=['year', 'month'], ascending=[True, True])
    print(table1)
    listTime = []    
    for row in table1.itertuples(index=False):
        listTime.append(f"{str(int(float(str(row.month))))}/{str(int(float(str(row.year))))}")
    print(listTime)
    listCo2 = table1['co2'].tolist()
    listTemp = table1['hum'].tolist()
    listHum = table1['temp'].tolist()
    return {"time": listTime, "co2": listCo2, "temp": listTemp, "hum": listHum}