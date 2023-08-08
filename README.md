# Minimum-Privilege Role Account Creator

## Table of Contents
- [Functionality](#functionality)
  - [Input](#input)
  - [APIs](#apis)
- [Current Limitations](#current-limitations)
  - [User authentication](#user-authentication)
- [Next Steps](#next-steps)
  - [Menu of Presets for Roles](#menu-of-presets-for-roles)
  - [User Authorization](#user-authorization)
  - [SVM Users and Roles](#svm-users-and-roles)
  - [Interactive UI](#interactive-ui)

## Functionality

The purpose of the Minimum-Privileges User Roles Creator is to create cluster level roles for various use cases that provide the user with the starting foundation of privileges required for any roles with additional necessary privileges. Within this tool, the user is also afforded the ability to modify and delete roles, in addition to creating and deletin existing accounts.

### APIs

All APIs used in this tool use the documented APIs available through the ONTAP REST API Online Reference.

**Creating Roles: /api/security/roles**

This endpoint is called to create a new cluster level role. While this endpoint supports the creation of roles for all SVM, the current implementation of this tool is restricted to cluster level roles for the time being. This API is public part of the documented API available through the ONTAP REST API Online Reference.

**Creating Accounts: /api/security/accounts**

This endpoint is called to create a new cluster level user account. Like the endpoint for role creation, while able to create accounts for specific SVMs, the current implementation of this tool focuses on cluster level account creation only. This endpoint is public and available thorugh the ONTAP REST API Online Reference.

**Deleting Roles: /api/security/roles/{owner uuid}/{role name}**

This endpoint is called to delete an existing cluster level role. To ensure the role exists, the user is presented with a menu of existing roles to choose from to delete. If the owner uuid does not already exist within the Role Service, the get_roles service method will be called to retrieve the cluster svm's uuid.

**Deleting Accounts: /api/security/accounts/{owner uuid}/{account name}**

This endpoint is called to delete an existing cluster level account. To ensure the account exists, the user is presented with a menu of existing accounts to choose from to delete. If the owner uuid does not already exist within the Account Service, the get_accounts service method will be called to retrieve the cluster svm's uuid.

**Modifying Roles: /api/security/roles/{owner uuid}/{role name}/privileges/{privilege name}**
This endpoint is called to modify an existing cluster level role. The user is presented with the ability to either remove a privilege from or add a privilege to the existing role. The inputs for privilege name are not regulated, and as such, if they receive an invalid input, wil throw an error and the user will be reprompted for a privilege name. If the owner uuid does not already exist within the Account Service, the get_accounts service method will be called to retrieve the cluster svm's uuid.

### Input

To create the role with it's corresponding privileges and define each privilege's access, a json object of the following format is consumed by the /api/security/roles:

    {
        "name": <role name here>,
        "privileges": 
            [
                {
                    "path": <command name>,
                    "access": <access level (e.g. all, readonly, etc.)>
                },
                ...
            ]
    }

Each command can have its access individually defined, making necessary command access modifications in the case of edge cases such as linked command sets. By defining a single linked command with a given access level, all subsequent linked commands that are automatically added to the role are given the same access. This prevents linked commands from unintentionally being added that provide functionality beyond the intended scope of the role.

To create an account with the previously created role, a json object of the following format is consumed by the endpoint /api/security/accounts:

    {
        "name": <account name>,
        "applications": [
            {
                "application": "ontapi",
                "authentication_methods": [ 
                    "password"
                ]
            },
            {
                "application": "http",
                "authentication_methods": [
                    "password"
                ]
            }
            ...
        ],
        "password": <password>,
        "role": {
            "name": <role name>
        }
    }
