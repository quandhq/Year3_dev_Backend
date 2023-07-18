from .models import SensorMonitor
import pandas as pd
import datetime

def getOptionDayData(day):
    # http://localhost:8000/api/v1.1/monitor/data/history?farm_id=1&time_start=1684765622&time_end=1684765622&option=day
    print(datetime.datetime.fromtimestamp(day).day)
    sensorMonitorList= SensorMonitor.objects.filter(time__gt=day)
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
    table = table[table['day'] == (datetime.datetime.fromtimestamp(day).day)]
    table1 = table.groupby(['hour'], as_index=False).mean()
    table1['co2'] = round(table1['co2'],0)
    table1['temp'] = round(table1['temp'],0)
    table1['hum'] = round(table1['hum'],0)
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
    # print(extra_data.keys().tolist())
    for hour in listHours:
        for key in extra_data:
            if str(key) == "hour":
                extra_data[key].append(hour)
            else: 
                extra_data[key].append(0)
    extra_df = pd.DataFrame(extra_data)
    table1 = pd.concat([table1, extra_df], ignore_index=True)
    table_result = table1.sort_values(by='hour')
    # print(table_result)
    #____________________________________________________________
    # print(extra_data)
    # newList = []
    # for j in listDays:
    #     newList.append([j, 0])
    # dfCo2 = pd.DataFrame(newList, columns=['hour', "co2"])
    # table1 = pd.concat([table1, dfCo2], ignore_index=True)
    # dfHum = pd.DataFrame(newList, columns=['hour', "hum"])
    # table1 = pd.concat([table1, dfHum], ignore_index=True)
    # dfTemp = pd.DataFrame(newList, columns=['hour', "temp"])
    # table1 = pd.concat([table1, dfTemp], ignore_index=True)
    # table1.sort_values(by='hour', inplace=True)
    listTime = []    
    for i in table_result['hour'].tolist():
        listTime.append(int(float(str(i))))
    listCo2 = table_result['co2'].tolist()
    listTemp = table_result['hum'].tolist()
    listHum = table_result['temp'].tolist()
    print(table_result)
    return {"time": listTime, "co2": listCo2, "temp": listTemp, "hum": listHum}
    # print(newList)
    # print(df)
    # print(table1)
    # print(df)
    # print(listTime)
    # print(listCo2)
    # print("inside getOPtiondaydata")