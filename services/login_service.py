import base64
import requests

def login(cluster: str, username: str, password: str) -> bool:
    authorization = base64.b64encode((username + ":" + password).encode("ascii"))
    headers = {
            'Authorization': f'Basic {authorization.decode()}',
            'Connection': 'keep-alive',
            'X-Dot-Client-App': 'SMv4',
            'X-Dot-Error-Arguments': 'true',
            'Content-Type': 'application/json'
    }
    login_response = requests.request("POST", f"{cluster}/security/login", verify=False, headers=headers)
    if login_response.status_code == 200:
        return authorization.decode()
    else:
        raise PermissionError("Invalid credentials!")   