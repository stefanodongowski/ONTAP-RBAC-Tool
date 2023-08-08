import json
from pwinput import pwinput
import requests
from pick import pick

class AccountService():
    def __init__(self, cluster: str, auth_token: str):
        self.cluster = cluster
        self.auth_token = auth_token
        self.owner_uuid = None
        self.headers = {
                'Authorization': f'Basic {self.auth_token}',
                'Connection': 'keep-alive',
                'X-Dot-Client-App': 'SMv4',
                'X-Dot-Error-Arguments': 'true',
                'Content-Type': 'application/json'
        }

    def create_account(self, role_name: str = None):
        # Try to create user account with role
        with(open("account.json")) as f:
            account = json.loads(f.read())
            account_url = f"https://{self.cluster}/api/security/accounts"
            
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

                # Make request to create new account with role. If status code 201 (Resource Created) is not returned, throw error
                account_response = requests.request("POST", account_url, headers=self.headers, data=account_payload, verify=False)

                if str(account_response.status_code) != "201":
                    raise Exception(account_response.json()["error"]["message"])
                else:
                    valid_account = True

    def delete_account(self, account_name: str):
        if not self.owner_uuid:
            accounts = self.get_accounts()
            self.owner_uuid = accounts["owner"]["uuid"]

        url = f"https://{self.cluster}/api/security/accounts/{self.owner_uuid}/{account_name}"
        response = requests.request("DELETE", url, headers=self.headers, verify=False)

        if response.status_code != 200:
            raise Exception("ERROR: Could not delete account!")

    def get_accounts(self):
        owner_name = self.cluster.split(".")[0]

        url = f"https://{self.cluster}/api/security/accounts?owner.name={owner_name}"
        response = requests.request("GET", url, headers=self.headers, verify=False)
        accounts = json.loads(response.text)["records"]

        self.owner_uuid = accounts[0]["owner"]["uuid"]
        return accounts