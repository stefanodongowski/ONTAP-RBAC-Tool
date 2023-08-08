import json
import requests
from pick import pick

class RoleService():
    def __init__(self, cluster: str, auth_token: str):
        self.cluster = cluster
        self.owner_uuid = None
        self.auth_token = auth_token
        self.role_name = None
        self.headers = {
                'Authorization': f'Basic {self.auth_token}',
                'Connection': 'keep-alive',
                'X-Dot-Client-App': 'SMv4',
                'X-Dot-Error-Arguments': 'true',
                'Content-Type': 'application/json'
        }

    def get_role(self, role_name):
        url = f"https://{self.cluster}/api/security/roles?name={role_name}&fields=privileges.path,privileges.access&return_records=true&return_timeout=15"
        response = requests.request("GET", url, headers=self.headers, verify=False)
    
        try:
            role = json.loads(response.text)["records"][0]
            return role
        except Exception as e:
            print(e)

    def get_roles(self):
        url = f"https://{self.cluster}/api/security/roles"
        response = requests.request("GET", url, headers=self.headers, verify=False)
        roles = []
        for role in json.loads(response.text)["records"]:
            name = role["name"]
            roles.append(name)
        return roles

    def create_role(self, role_name: str) -> None:
        with(open(f"role_templates/{role_name.lower().replace(' ', '')}_role.json")) as f:
            role = json.loads(f.read())
            role_name = input("Enter new role name: ")

            # Update role name in json
            role["name"] = role_name
            role_payload = json.dumps(role)


            # Send request to create role
            role_url = f"https://{self.cluster}/api/security/roles"
            role_response = requests.request("POST", role_url, headers=self.headers, data=role_payload, verify=False)

            if str(role_response.status_code) != "201":
                raise Exception("Role already exists.")
            self.role_name = role_name
        
    def modify_role(self, role_name: str):
        valid_role = False
        while not valid_role:
            title = "Select an action:"
            options = ["Add a privilege", "Remove a privilege", "Exit"]
            action_selected = pick(options, title, multiselect=False, min_selection_count=1)
            
            if action_selected[0] == "Add a privilege":
                print("Action " + action_selected[0].lower() + " selected.")
                
                privilege = input("Enter privilege command name: ")

                title = "Select an access level:"
                options = ["none", "readonly", "all", "Exit"]
                access = pick(options, title, multiselect=False, min_selection_count=1)

                if access == "Exit":
                    print("Selection menu exited.\n")
                    exit()
                try:
                    self.add_privilege(role_name, privilege, access[0])
                    valid_role = True
                except Exception as e:
                    print("ERROR: privilege is either invalid or already added to role!\n")

            elif action_selected[0] == "Remove a privilege":
                print("Action " + action_selected[0].lower() + " selected.")
                
                privilege = input("Enter privilege command name: ")

                try:
                    self.remove_privilege(role_name, privilege)
                    print(f"Successfully removed {privilege} as a privilege from {role_name}.\n" )
                    valid_role = True
                except Exception as e:
                    print(e)

            elif action_selected[0] == "Exit":
                print("Selection menu exited.")
                exit()
    
    def delete_role(self, role_name):
        if not self.owner_uuid:
            old_role = self.get_role(role_name)
            self.owner_uuid = old_role["owner"]["uuid"]

        url = f"https://{self.cluster}/api/security/roles/{self.owner_uuid}/{role_name}"
        response = requests.request("DELETE", url, headers=self.headers, verify=False)
        if response.status_code != 200:
            raise Exception("ERROR: Could not delete role!")
        
        
    def add_privilege(self, role_name, priv_name, access):
        if not self.owner_uuid:
            role = self.get_role(role_name)
            self.owner_uuid = role["owner"]["uuid"]

        payload = json.dumps({
            "access": f"{access}",
            "path": f"{priv_name}"
        })
        role_url = f"https://{self.cluster}/api/security/roles/{self.owner_uuid}/{role_name}/privileges"
        role_response = requests.request("POST", role_url, headers=self.headers, data=payload, verify=False)
        
        if role_response.status_code != 201:
            raise Exception("ERROR: Privilege already exists!\n")
        
        print(f"Added privilege {priv_name} to {role_name}.\n")

    def remove_privilege(self, role_name, priv_name):
        if not self.owner_uuid:
            role = self.get_role(role_name)
            self.owner_uuid = role["owner"]["uuid"]

        role_url = f"https://{self.cluster}/api/security/roles/{self.owner_uuid}/{role_name}/privileges/{priv_name}"
        role_response = requests.request("DELETE", role_url, headers=self.headers, verify=False)
        
        if role_response.status_code != 200:
            raise Exception("ERROR: Privilege does not exist in role!\n")
        
