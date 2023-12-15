url = "https://api.waqi.info/feed/here/?token=08f2de731b94a1ff55e871514aa8f145e12ebafe"
import requests
data = requests.get(url)
data_json = data.json()
time_of_data = data_json["data"]["time"]["v"]
print(time_of_data)