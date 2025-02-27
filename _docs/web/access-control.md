---
title: Access Control
category: Web
order: 13
---

Access control is the application of constraints on who or what is authorized to perform actions or access resources. In the context of web applications, access control is dependent on authentication and session management:

Broken access controls are common and often present a critical security vulnerability. Design and management of access controls is a complex and dynamic problem that applies business, organizational, and legal constraints to a technical implementation. Access control design decisions have to be made by humans so the potential for errors is high. 


# Vertical Access Controls

Vertical access controls are mechanisms that restrict access to sensitive functionality to specific types of users. 

With vertical access controls, different types of users have access to different application functions. For example, an administrator might be able to modify or delete any user's account, while an ordinary user has no access to these actions. Vertical access controls can be more fine-grained implementations of security models designed to enforce business policies such as separation of duties and least privilege. 

## Unprotected functionality

At its most basic, vertical privielege escalation arises where an application does not enforce any protttection for sensitive functionalities such as admin panels.

For example, a website might host:

```
https://hackingnotes.com/admin
```

The vulnerability arises when is accesible by any user, not only administrative users who have a link to the functionality in ther user interface. Those panels often appears on files such as `sitemap.xml` or `robots.txt`. It can also be found by doing fuzzing.

It can be also found on javascript files or html. **Make a look**.

## Parameter-based access control methods

Some applications determine the user's access rights or role at login, and then store this information in a user-controllable location. This could be: 

* A hidden field.
* A cookie.
* A preset query string parameter.

The application makes access control decisions based on the submitted value. For example: 

```
https://hackingnotes.com/login/home.jsp?admin=true
https://hackingnotes.com/login/home.jsp?role=1
```

## Broken access control resulting from platform misconfiguration

Some applications enforce access controls at the platform layer. they do this by restricting access to specific URLs and HTTP methods based on the user's role. For example, an application might configure a rule as follows: 

```
DENY: POST, /admin, managers
```
This rule denies access to the `POST` method on the URL `/admin`, for users in the managers group. Various things can go wrong in this situation, leading to access control bypasses. 

### URL-based access control

Some application frameworks support various non-standard HTTP headers that can be used to override the URL in the original request, such as `X-Original-URL` and `X-Rewrite-URL`. If a website uses rigorous front-end controls to restrict access based on the URL, but the application allows the URL to be overridden via a request header, then it might be possible to bypass the access controls using a request like the following: 

```
GET /?username=benjugat HTTP/1.1
X-Original-URL: /admin
...
X-Rewrite-URL: /admin
```

### Method-based access control

We can find and enpoint that blocks us `POST` request, we can try to do it in `GET`.


## Broken access control resulting from URL-matching discrepancies

Websites can vary in how strictly they match the path of an incoming request to a defined endpoint. 

There are different ways to bypass that type of restrictions:

* Using capital letters: `/ADMIN/DELETEUSER`
* Adding a suffix: `/admin/deleteUser.anything`
* Adding a slash: `/admin/deleteUser/`


## Broken access control in multi-step processes

Many websites implement important functions over a series of steps, sometimes the website will implement rigorous access controls over some of these steps, but ignore others. Check all steps.

## Referer-based access control

Some websites base access controls on the `Referer` http header.

For example, an application robustly enforces access control over the main administrative page at `/admin`, but for sub-pages such as `/admin/deleteUser` only inspects the `Referer` header. If the Referer header contains the main /admin URL, then the request is allowed. 

```
GET /admin/deleteUser?username=benjugat
Referer: /admin
```

# Horizontal access controls

Horizontal access controls are mechanisms that restrict access to resources to specific users.

With horizontal access controls, different users have access to a subset of resources of the same type. For example, a banking application will allow a user to view transactions and make payments from their own accounts, but not the accounts of any other user. 

## Insecure Direct Object Reference (IDOR)

Horizontal privilege escalation attacks may use similar types of exploit methods to vertical privilege escalation. For example, a user might access their own account page using the following URL: 

```
https://hackingnotes.com/myaccount?id=123
```

If an attacker modifies the `id` parameter value to that of another user, they might gain access to another user's account page, and the associated data and functions. 


# Context-dependent access controls

Context-dependent access controls restrict access to functionality and resources based upon the state of the application or the user's interaction with it.

Context-dependent access controls prevent a user performing actions in the wrong order. For example, a retail website might prevent users from modifying the contents of their shopping cart after they have made payment. 


