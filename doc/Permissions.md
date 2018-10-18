# Halibot Permissions
This document outlines information regarding how authentication and permissions work in Halibot.

## Permissions
Halibot can be configured to allow and prevent certain users from allowing halibot to perform certain actions. Halibot can also be configured to allow different permissions for the same user based on the source of a request. For instance, a user may have rights to perform certain actions from one IRC channel, but not another. If authentication is enabled, halibot will reject all requests by default.

## Enabling authentication
To enable authentication in halibot, add the `use-auth` boolean parameter to the `config.json` file. The default value is set to `true` (authentication enabled). Example:
```
{
  ...
  use-auth: true
}
```
When authentication is enabled, halibot will use the permissions file for permissions checking.

## Permissions file
The permissions file should consist of a JSON array of tuples, each tuple representing a permission. Each tuple should be of the following form:
'''
(ri, user, permissions)
'''
- `ri`: A string containing the identifier for the resource that made the request.
- `user`: A string containing a unique identifier for the user who is requesting a specific action.
- `permissions`: A string containing a single permission for this user.

The location of this file can be specified in your `config.json` via the `auth-path` string parameter. The default path is set to `permissions.json`, which is located at the top level of your halibot project. If you have not manually created a permissions file and have not initialized halibot already, running the following will create a permissions file in the default location.
```
halibot init
```
_Note: A permissions file with an empty JSON array grants all permissions to every user. The default permissions file is instantiated this way._

## Defining permissions in a Halibot module
To add permissions to a certain action within a halibot module, add the '@hasPermission' annotation to the respective function in your module. Each parameter of the annotation should be a string representing a permission. Defining permissions is up to the discretion of the developer. Example:
```
@hasPermission( "PERM_1", "PERM_2" ) 
```


