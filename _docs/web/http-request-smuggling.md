---
title: HTTP Request Smuggling
category: Web
order: 26
---

HTTP request smuggling is a technique for interfering with the way a web site processes sequences of HTTP requests that are received from one or more users. Request smuggling vulnerabilities are often critical in nature, allowing an attacker to bypass security controls, gain unauthorized access to sensitive data, and directly compromise other application users. 

[HTTP Request Smuggling](/hackingnotes/images/smuggling.png)

Request smuggling is primarily associated with **HTTP/1 requests**.

Most HTTP request smuggling vulnerabilities arise because the `HTTP/1` specification provides two different ways to specify where a request ends: the `Content-Length` header and the `Transfer-Encoding` header. 

* **Content-Length**: It specifies the length of the message body in bytes.

```
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

* **Trasnfer-Encoding**: It specifies thatthe message body uses chunked encoding. This means that the message body contains one or more chunks of data. Each chunk consists of the chunk size in bytes expressed in **hexadecimal**, followed by a new line, followed by the chunk contents and it's terminated with a size zero.

```
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked

b
q=smuggling
0
```

Since HTTP/1 has two differents methods for specifyng the length of HTTP message, it is possible for a single message to use both methods at once.

* **CL.TE**: The front-end server uses the `Content-Lenght` header and the back-end server uses the `Transfer-Encoding` header.
* **TE.CL**: The front-end server uses the `Transfer-Encoding` header and the back-end server uses the `Content-Length` header.
* **TE.TE**: Both servers support the `Transfer-Encoding` header, but one of the servers can be induced not to process it by obfuscating the header in some way.


[HTTP Request Smuggling](/hackingnotes/images/smuggling2.png)


# Burpuiste Setup for smuggling attacks

At first we need to download `` burp extension may be we can use it.

We should do this on every request on the repeater tab.

1. Downgrade the protocol to HTTP/1.1.

[HTTP Request Smuggling](/hackingnotes/images/smuggling-downgrade.png)

2. Disable `Update Content-Length`

[HTTP Request Smuggling](/hackingnotes/images/smuggling-update.png)

3. Turn on `Non printable characters`

[HTTP Request Smuggling](/hackingnotes/images/smuggling-linebreak.png)

# CL.TE

Here, the front-end server uses the `Content-Length` header and the back-end server uses the `Transfer-Encoding` header. We can perform a simple HTTP request smuggling attack as follows: 

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

[HTTP Request Smuggling](/hackingnotes/images/smuggling-clte.png)

# TE.CL