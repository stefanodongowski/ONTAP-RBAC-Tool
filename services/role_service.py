import json
import requests

def create_role(cluster: str, role_selection: str, authorization: str) -> None:
    with(open(f"role_templates/{role_selection.lower().replace(' ', '')}_role.json")) as f:
        role = json.loads(f.read())

        role_name = input("Enter new role name: ")

        # Get new role name
        role["role"] = role_name

        role_payload = json.dumps(role)

        role_url = f"{cluster}/api/svms/rtp-sa-select02/admin/roles"
        headers = {
            'Authorization': f'Basic {authorization}',
            'Connection': 'keep-alive',
            'X-Dot-Client-App': 'SMv4',
            'X-Dot-Error-Arguments': 'true',
            'Content-Type': 'application/json'
        }
        role_response = requests.request("POST", role_url, headers=headers, data=role_payload, verify=False)

        if str(role_response.status_code) != "201":
            print("ERROR: ", end="")
            raise Exception(role_response.json()["error"]["message"])
        print('Role created.')
        return role_name