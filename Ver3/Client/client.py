#Example for testing token authentication
from getpass import getpass
import requests
# username = input("What is your username?: ")
# password = getpass("What is your password?: ")
# url = "http://127.0.0.1:8000/api/get/token_auth"
# token_test_reponse = requests.post(url, json={"username": username,"password": password})
# token = token_test_reponse.json()["token"]
# print(token)


# if token_test_reponse.status_code == 200:
#     url = "http://127.0.0.1:8000/api/get/test_authentication"
#     header = {"Authorization": f"Token {token}",}
#     data_with_token_authentication = requests.get(url=url, headers=header)
#     print(data_with_token_authentication.json())



# username = input("What is your name? ")
# password = getpass("What is your password? ")
# #url to get token
# url_to_get_token = "http://127.0.0.1:8000/api/get/token_auth"   
# token_response = requests.post(url=url_to_get_token, json={"username": username, "password": password})
# if token_response.status_code == 200:
#     token = token_response.json()["token"]
#     print(f"Token is: {token}")
#     url_to_get_data = "http://127.0.0.1:8000/api/get/test_authentication"
#     header = {"Authorization": f"Token {token}"}
#     data_when_being_permitted = requests.get(url=url_to_get_data, headers=header)
#     print(data_when_being_permitted.json())


url_dispatching = "http://127.0.0.1:8000/api/v1.1/control/fans?farm_id=1"
data = { 
    "time":"1682656256", 
    "co2": 400,
}
response = requests.post(url=url_dispatching, 
                        # data={"test": "1234"},
                        json=data, 
                        # headers={"Content-type": "Application/json"}
                        )
print(response)
