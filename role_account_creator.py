import requests
import json
from pwinput import pwinput
import warnings
from pick import pick
from services.login_service import login
from services.role_service import create_role
from services.account_service import create_account
warnings.filterwarnings(action="ignore")

# Authenticate user
logged_in = False
authorization = ""
cluster = ""
while not logged_in:
    cluster = input("Cluster (FQDN): ")
    username = input("Username: ")
    password = pwinput(prompt="Password: ", mask="*")
    try:
        authorization = login(cluster, username, password)
        logged_in = True
        print("Login successful.")
    except PermissionError:
        print("Invalid credentials.")

# Have user select whether they want to create an account, role, or both

title = "Pick one or more of the following (right arrow to select/deselect)"
options = ["Create account", "Create role", "Exit"]
selected = []
role_name = ""
selected = pick(options, title, multiselect=True, min_selection_count=1)

# Handle control flow based on user choice

if ('Create role', 1) in selected:
    print("Create role selected.")
    # Show user available role templates to use
    title = "Pick a minimum privilege role template to use for this role:"
    options = ["Harvest 2"]
    role_selected = []
    valid_pick = False
    while not valid_pick:
        try:
            role_selected = pick(options, title, multiselect=False, min_selection_count=1)
            valid_pick = True
            print("Role " + role_selected[0] + " selected.")
        except:
            continue
    # Try to create role based on json specification
    try:
        role_name = create_role(cluster, role_selected[0], authorization)
    except Exception as e:
        print(e)

if ('Create account', 0) in selected:
    print("Create account selected.")
    create_account(cluster, authorization, role_name)

if ('Exit', 0) in selected:
    print("Selection menu exited.")
    exit()

    

    






