import base64
import requests

class AuthService():
    def __init__(self):
        self.cluster = None
        self.auth_token = None
        self.headers = {}

    def auth_user(self, cluster: str, username: str, password: str) -> bool:
        auth_token = base64.b64encode((username + ":" + password).encode("ascii")).decode()
        headers = {
                'Authorization': f'Basic {auth_token}',
                'Connection': 'keep-alive',
                'X-Dot-Client-App': 'SMv4',
                'X-Dot-Error-Arguments': 'true',
                'Content-Type': 'application/json'
        }
        login_response = requests.request("POST", f"https://{cluster}/security/login", verify=False, headers=headers)
        if login_response.status_code == 200:
            self.cluster = cluster
            self.auth_token = auth_token
            self.headers = headers
        else:
            raise PermissionError("Invalid credentials!")   