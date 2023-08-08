from pwinput import pwinput
import requests
import warnings
from pick import pick
import json
from services.auth_service import AuthService
from services.role_service import RoleService
from services.account_service import AccountService
from time import sleep
warnings.filterwarnings(action="ignore")

# Inject AuthService
auth_service = AuthService()

# Authenticate user
logged_in = False
while not logged_in:
    cluster = input("Cluster (FQDN): ")
    username = input("Username: ")
    password = pwinput(prompt="Password: ", mask="*")
    try:
        auth_service.auth_user(cluster, username, password)
        print("Login successful." + '\n')
        logged_in = True
    except PermissionError as e:
        print(str(e) + '\n')
    except requests.exceptions.ConnectionError as e:
        print("Connection error: Please connect to the VPN to continue\n")

# TODO: have role and account services retrieve creds within class rather than as params
role_service = RoleService(auth_service.cluster, auth_service.auth_token)
account_service = AccountService(auth_service.cluster, auth_service.auth_token)

while True:
    # Have user select whether they want to create an account and/or role
    title = "Pick one or more of the following (right arrow to select/deselect)"
    options = ["Create role from template", "Create account", "Modify existing role", "Delete account", "Delete role", "Exit"]
    selected = pick(options, title, indicator="=>", multiselect=True, min_selection_count=1)

    # Handle control flow based on user choice
    
    # Create account will an optional role (if role was previously created)

    if ('Create role from template', 0) in selected:
        print("Create role from template selected.")

        # Show user available role templates to use
        title = "Select a minimum privilege role template to use for this role:"
        # TODO: Automate generation of template names from role_templates folder
        options = ["Harvest 2", "Exit"]
        selection = pick(options, title, indicator="=>", multiselect=False, min_selection_count=1)

        if selection[0] == "Exit":
            print("Selection menu exited.")
            exit()

        role_name = selection[0]
        print("Role " + role_name + " selected.")

        # Try to create role based on json specification
        try:
            role_name = role_service.create_role(role_name)
            print("Role " + role_service.role_name + " created." + '\n')
            sleep(1)
        except Exception as e:
            print(str(e) + '\n')
            sleep(1)
            continue
    
    if ('Create account', 1) in selected:
        print("Create account selected.")

        if role_service.role_name:
            title = "The most recent role created was: " + role_service.role_name + ".\nDo you want use this role for the new account?"
            options = ["Yes", "No"]
            selection = pick(options, title, "=>", min_selection_count=1)

        try:
            if role_service.role_name and selection[0] == 'Yes':
                account_service.create_account(role_service.role_name)
            # TODO: allow user to create account with pre-existing role
            else:
                account_service.create_account()
            print("Account successfully created.\n")
            sleep(1)
        except:
            print("Could not create account.\n")
            sleep(1)
            continue
                   
    if ('Modify existing role', 2) in selected:
        roles = role_service.get_roles()
        if len(roles) == 0:
            print("No current roles to modify.")
            sleep(1)
            continue

        print('Modify existing role selected.')

        # Create paginated menu for user to select role to modify
        page_size = 5
        page_num = 0
        made_selection = False
        selection = []
        while not made_selection:
            # Calculate which roles will be shown on what page
            start = page_num * page_size
            end = min(page_size * (page_num + 1), len(roles))
            title = "Select which role you wish to modify:"
            # If menu page is last page, don't show next option, otherwise show next option
            if end == len(roles):
                options = roles[start:end] + ["BACK"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-1)
            elif start == 0:
                options = roles[start:end] + ["NEXT"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-1)
            else:
                options = roles[start:end] + ["NEXT", "BACK"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-2)
            if selection[0] == "NEXT":
                page_num += 1
            elif selection[0] == "BACK":
                page_num -= 1
            else:
                made_selection = True

        role_name = selection[0]

        print(f"Role {role_name} selected.")

        role_service.modify_role(role_name)

        sleep(1)
        continue

    elif ('Delete account', 3) in selected:
        print("Delete account selected.")
        accounts_objs = account_service.get_accounts()
        if len(accounts_objs) == 0:
            print("No current accounts to delete.")
            sleep(1)
            continue

        accounts = [x["name"] for x in accounts_objs]

        account = None
        page_size = 5
        page_num = 0
        confirmed = False
        selection = []
        while not confirmed:
            # Calculate which accounts will be shown on what page
            start = page_num * page_size
            end = min(page_size * (page_num + 1), len(accounts))
            title = "Select which account you wish to delete:"
            # If menu page is last page, don't show next option, otherwise show next option
            if end == len(accounts):
                options = accounts[start:end] + ["BACK"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-1)
            elif start == 0:
                options = accounts[start:end] + ["NEXT"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-1)
            else:
                options = accounts[start:end] + ["NEXT", "BACK"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-2)
            if selection[0] == "NEXT":
                page_num += 1
            elif selection[0] == "BACK":
                page_num -= 1
            else:
                account = selection[0]

                title = "Are you sure you wish to delete " + account + "?"
                options = ["Yes", "No"]
                selection = pick(options, title, min_selection_count=1)
                if selection[0] == "Yes":
                    confirmed = True

        try:
            # Called to set owner_uuid field for account service
            account_service.get_accounts()
            account_service.delete_account(account)
            print("Account successfully deleted.\n")
            sleep(1)
            continue
        except Exception as e:
            print(e)
       
    elif ('Delete role', 4) in selected:
        roles = role_service.get_roles()
        if len(roles) == 0:
            print("No current roles to delete.")
            sleep(1)
            continue

        print('Delete role selected.')

        # Create paginated menu for user to select role to modify
        page_size = 5
        page_num = 0
        confirmed = False
        role_name = None
        selection = []
        while not confirmed:
            # Calculate which roles will be shown on what page
            start = page_num * page_size
            end = min(page_size * (page_num + 1), len(roles))
            title = "Select which role you wish to delete:"
            # If menu page is last page, don't show next option, otherwise show next option
            if end == len(roles):
                options = roles[start:end] + ["BACK"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-1)
            elif start == 0:
                options = roles[start:end] + ["NEXT"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-1)
            else:
                options = roles[start:end] + ["NEXT", "BACK"]
                selection = pick(options, title, indicator="=>", default_index=len(options)-2)
            if selection[0] == "NEXT":
                page_num += 1
            elif selection[0] == "BACK":
                page_num -= 1
            else:

                role_name = selection[0]

                title = "Are you sure you wish to delete " + role_name + "?"
                options = ["Yes", "No"]
                selection = pick(options, title, min_selection_count=1)
                if selection[0] == "Yes":
                    confirmed = True

        role_service.delete_role(role_name)

        print(f"Role {role_name} removed successfully.\n")
        sleep(1)
        continue

    elif ('Exit', 5) in selected:
        print("Selection menu exited.")
        exit()
    
    
        

        






