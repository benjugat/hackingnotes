---
title: API Testing
category: Web
order: 9
---

# Discovering API Documentation

APIs are usually documented so that developers know how to use and integrate with them.

Documentation can be in both human-readable and machine-readable forms. Human-readable documentation is designed for developers to understand how to use the API.

Even if API documentation isn't openly available, you may still be able to access it by browsing applications that use the API.

Juicy endpoints:

```
/api
/swagger/index.html
/openapi.json
/api/openapi.json
/api/swagger/v1
/api/swagger
```

# Interacting with API endpoints

* **Suported HTTP Methods**:

```
GET
POST
PATCH
OPTIONS
PUT
DELETE
```

* **Content-Types**:

Usually APIs use XML or JSON

```
Content-Type: application/json
Content-Type: application/xml
```

# Mass Assigment Vulnerabilities

Mass assignment (also known as auto-binding) can inadvertently create hidden parameters. It occurs when software frameworks automatically bind request parameters to fields on an internal object. Mass assignment may therefore result in the application supporting parameters that were never intended to be processed by the developer.

To do that sometimes we need to find hidden parameters. These can be easily found on the GET request such as `GET /api/user/benjugat`.

```
GET /api/user/benjugat
...
200 OK

{
    "id": 1,
    "name": "Ben Jugat",
    "email": "benjugat@example.com",
    "isAdmin": "false"
}

```

After that Mass Assigment occurs when we can add a parameter on a `PATH` or `POST` request and it is not validated.

Example:

* Original PATCH request:

```
PATH /api/user/benjugat
Content-Type: application/json

{
	"name":"Ben Jugat",
	"email":"benjugat@example.com"
}
```

* Modified request:

```
PATH /api/user/benjugat
Content-Type: application/json

{
	"name":"Ben Jugat",
	"email":"benjugat@example.com",
	"isAdmin":"true"
}
```

# Server-side parameter pollution

Some systems contain internal APIs that aren't directly accessible from the internet. Server-side parameter pollution occurs when a website embeds user input in a server-side request to an internal API without adequate encoding. This means that an attacker may be able to manipulate or inject parameters, which may enable them to, for example: 

* Override existing parameters.
* Modify the application behavior.
* Access unauthorized data.

To test for server-side parameter pollution in the query string, place query syntax characters like `#`, `&`, and `=` in your input and observe how the application responds. 

Consider a vulnerable application that enables you to search a user:

```
GET /userSearch?name=benjugat&back=/home
```
The app ask to a API with the following query:

```
GET /user/search?name=benjugat&publicProfile=true
```

## Truncating query strings

We can trick the app to trucnate the final API request with `#` urlencoded:

```
GET /userSearch?name=benjugat%23foo&back=/home
```

The app will trigger:

```
GET /user/search?name=benjugat#foo&publicProfile=true
```

If the response return the user `benjugat`, the server-side query may have benn truncated, but if an error such as `invalid name` is received the application may treated `#foo` as a part of the username and it is not vulnerable.

## Injecting invalid parameters

We can url encode `&` character to attempt to add a second parameter to the server-side request.

```
GET /userSearch?name=benjugat%26foo=xyz&back=/home
```

This tricks the app to do the following request:

```
GET /users/search?name=benjugat&foo=xyz&publicProfile=true
```

Review the response for clues about how the additional parameter is parsed. For example, if the response is unchanged this may indicate that the parameter was successfully injected but ignored by the application.

## Injecting valid parameters

If we are able to modify the query string, we can attempt to add a second valid parameter to the server-side request.

```
GET /userSearch?name=benjugat%26email=foo&back=/home
```
This results to:

```
GET /users/search?name=benjugat&email=foo&publicProfile=true
```

## Overriding existing parameters

To confirm if the application is vulnerable to server-side parameter pollution, we can try to override the original parameter. We can inject a second parameter with the same name.

```
GET /userSearch?name=benjugat%26name=juan&back=/home
```

This results to:

```
GET /users/search?name=benjugat&name=juan&publicProfile=true
```

The internal API interprets two `name` parameters. This could affect different on some servers:

* **PHP** parses the second parameter, in that case `juan`.
* **ASP.NET** combines both parameters, this would result in a user search for `benjugat,juan` which might result in an `Invalid Username`.
* **Node.JS/Express** parses only the first parameter, this would result in `benjugat`.