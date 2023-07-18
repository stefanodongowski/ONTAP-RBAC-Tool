import json
from pwinput import pwinput
import requests

def create_account(cluster: str, auth_token: str, role_name):
    headers = {
            'Authorization': f'Basic {auth_token}',
            'Connection': 'keep-alive',
            'X-Dot-Client-App': 'SMv4',
            'X-Dot-Error-Arguments': 'true',
            'Content-Type': 'application/json'
    }
    # Try to create user account with role
    with(open("account.json")) as f:
        account_url = f"{cluster}/api/security/accounts"

        account = json.loads(f.read())

        valid_account = False
        while not valid_account:
            # Get new account info from user
            account["name"] = input("Enter new account username (3 - 24 characters ): ")

            account["password"] = pwinput(prompt="Enter new account password (must be alphanumeric): ", mask='*')

            if role_name:
                account["role"] = {
                    "name": role_name
                }

            account_payload = json.dumps(account)

            # Make request to create new role. If status code 201 (Resource Created) is not returned, throw error


            # Make request to create new account with role. If status code 201 (Resource Created) is not returned, throw error
            account_response = requests.request("POST", account_url, headers=headers, data=account_payload, verify=False)

            if str(account_response.status_code) != "201":
                print("ERROR: " + account_response.json()["error"]["message"])
            else:
                valid_account = True
                print("Account created.")