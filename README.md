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

The purpose of the Minimum-Privileges User Roles Creator is to create cluster level roles for various use cases that provide the user with the starting foundation of privileges required for any roles with additional necessary privileges.

### APIs

**/api/svms/{cluster SVM name}/admin/roles**

This endpoint is called to create a new cluster level role. While this endpoint supports the creation of roles for all SVM, the current implementation of this tool is restricted to cluster level roles for the time being. This API is also private and not part of the documented API available through the ONTAP REST API Online Reference.

**/api/security/accounts**

This endpoint is called to create a new cluster level user account. Like the endpoint for role creation, while able to create accounts for specific SVMs, the current implementation of this tool focuses on cluster level account creation only. This endpoint is public and available thorugh the ONTAP REST API Online Reference.

### Input

To create the role with it's corresponding privileges and define each privilege's access, a json object of the following format is consumed by the /api/svms/{cluster SVM name}/admin/roles:

    {
        "role": <role name here>,
        "entries": 
            [
                {
                "cmddirname": <command name>,
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

## Limitations and Next Steps

### Menu of Presets for Roles

Currently the application requires a hardcoded reference to a file containing the json for the role to be created. This can be improved upon once a collection of json files for various pre-defined roles have been created. A menu will show the user the available roles to create and allow them to select a given role, while still allowing them to change the role name if they wish.

### User Authorization

To authorize users, unique tokens must be passed in the headers of each request made to the system. The current mode of authorization is a static token that is stored in the payload of each request. While this works for testing purposes, this is not a secure way to approach user authorization.

Because of this, a next step for this project is having the user sign in when using the Role Account Creator as a means of authorization.

### SVM Users and Roles

Another area in which progress can be made is expanding support from exclusively cluster level roles to providing functionality to allow the creation of roles and accounts on any SVM the user has access to.

### Interactive UI

While it is important to prioritize the early development on creating functional features, ensuring that this tool can be integrated into an environment where it will be used it essential. While where and how this will be done is to be discussed, it is an important area within the scope of this project that must be considered.