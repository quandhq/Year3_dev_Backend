"""
*brief: When we run this python script, firstly it will check if there
    is the file that contains the access-token and the refresh-token, if not
    it will perform the authentication process that require the username
    and password from user and store the access-token and refresh-token
    get back in a file for future-use. If there is, it will check if the
    access token if valid or not, if the access token is valid, the user is 
    authenticated to use API, if the accress token is not valid, it performs the
    refreshing access token process, if the refreshing access token process is fine 
    the user is given a new access token and be able to continue using API, if the
    refreshing access token provess is not fine which means the refreshing token is out of date,
    it will perform the authentication process again to give the user both new access token
    and new refreshing token
"""

import requests
from getpass import getpass
import pathlib 
import json

class JWTClient:
    """
    Use a dataclass decorator
    to simply the class construction
    """
    access:str = None
    refresh:str = None
    # ensure this matches your simplejwt config
    header_type: str = None
    # this assumesy ou have DRF running on localhost:8000
    base_endpoint: str = None
    # this file path is insecure
    cred_path: pathlib.Path = None

    def __init__(self, __access: str = None,
                  __refresh: str = None, 
                  __header_type: str = "Bearer",
                  __base_endpoint: str = "http://localhost:8000/api",
                  __cred_path: str = "creads.json"):
        print("Performing __init___")
        self.access = __access
        self.refersh = __refresh
        self.header_type = __header_type
        self.base_endpoint = __base_endpoint
        self.cred_path = pathlib.Path(__cred_path)
        self.__post_init__()

    def __post_init__(self):
        print("Performing __post_init__ ...")
        if self.cred_path.exists(): 
            print("THIS CRED FILE EXIST!!!!!!")
            """
            You have stored creds,
            let's verify them
            and refresh them.
            If that fails,
            restart login process.
            """
            try:
                data = json.loads(self.cred_path.read_text())
            except Exception:
                print("Assuming creds has been tampered with")
                data = None
            if data is None:
                """ 
                Clear stored creds and
                Run login process
                """
                self.clear_tokens()
                self.perform_auth()
            else:
                """
                `creds.json` was not tampered with
                Verify token -> if necessary, Refresh token -> if necessary, Run login process
                """
                self.access = data.get('access')
                self.refresh = data.get('refresh')
                token_verified = self.verify_token()
                if not token_verified:
                    """
                    This can mean the token has expired
                    or is invalid. Either way, attempt
                    a refresh.
                    """
                    print("invalid access token, perfoming refreshing access-token ...")
                    refreshed = self.perform_refresh()
                    if not refreshed:
                        """
                        This means the token refresh
                        also failed. Run login process
                        """
                        print("invalid refresh-token, login again.")
                        self.clear_tokens()
                        self.perform_auth()
        else:
            """
            Run login process
            """
            self.perform_auth()

    def get_headers(self, header_type=None) -> dict: 
        """
        Default headers for HTTP requests
        including the JWT token
        """
        _type = header_type or self.header_type
        token = self.access
        if not token:
            return {}
        return {
                "Authorization": f"{_type} {token}"
        }

    def perform_auth(self):
        """
        Simple way to perform authentication
        Without exposing password(s) during the
        collection process.
        """
        endpoint = f"{self.base_endpoint}/token" 
        username = input("What is your username?\n")
        password = getpass("What is your password?\n")
        r = requests.post(url=endpoint, json={'username': username, 'password': password}) 
        if r.status_code != 200:
            raise Exception(f"Access not granted: {r.text}")
        print('access granted')
        self.write_creds(r.json())

    def write_creds(self, data:dict):
        """
        >>Store credentials as a local file
        and update instance with correct
        data.
        >>This function works only when you provide this class 
        a file name for the the file being gonna be used to store
        tokens 
        """
        if self.cred_path is not None:
            self.access = data.get('access')
            self.refresh = data.get('refresh')
            if self.access and self.refresh:
                self.cred_path.write_text(json.dumps(data))

    def verify_token(self):
        """
        Simple method for verifying your
        token data. This method only verifies
        your `access` token. A 200 HTTP status
        means success, anything else means failure.
        """
        data = {
            "token": f"{self.access}"
        }
        endpoint = f"{self.base_endpoint}/token/verify" 
        r = requests.post(endpoint, json=data)
        return r.status_code == 200

    def clear_tokens(self):
        """
        Remove any/all JWT token data
        from instance as well as stored
        creds file.
        """
        self.access = None
        self.refresh = None
        if self.cred_path.exists():
            self.cred_path.unlink()

    def perform_refresh(self):
        """
        Refresh the access token by using the correct
        auth headers and the refresh token.
        """
        print("Refreshing token.")
        headers = self.get_headers()
        data = {
            "refresh": f"{self.refresh}"
        }
        endpoint = f"{self.base_endpoint}/token/refresh" 
        r = requests.post(endpoint, json=data)
        if r.status_code != 200:
            self.clear_tokens()
            return False
        refresh_data = r.json()
        if not ('access' in refresh_data):
            self.clear_tokens()
            return False
        stored_data = {
            'access': refresh_data.get('access'),
            'refresh': self.refresh
        }
        self.write_creds(stored_data)
        return True

    def list(self, endpoint=None):
        """
        Here is an actual api call to a DRF
        View that requires our simplejwt Authentication
        Working correctly.
        """
        headers = self.get_headers()
        if endpoint is None or self.base_endpoint not in str(endpoint):
            endpoint = f"{self.base_endpoint}/get/test_authentication" 
        r = requests.get(endpoint, headers=headers) 
        if r.status_code != 200:
            raise Exception(f"Request not complete {r.text}")
        data = r.json()
        return data


if __name__ == "__main__":
    """
    Here's Simple example of how to use our client above.
    """

    # this will either prompt a login process
    # or just run with current stored data
    client = JWTClient() 

    # simple instance method to perform an HTTP
    # request to our /api/products/ endpoint
    data = client.list()
    print(data)
