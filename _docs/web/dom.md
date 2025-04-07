---
title: DOM Based
category: Web
order: 20
---

The Document Object Model (DOM) is a web browser's hierarchical representation of the elements on the page. Websites can use JavaScript to manipulate the nodes and objects of the DOM, as well as their properties. DOM manipulation in itself is not a problem. In fact, it is an integral part of how modern websites work. However, JavaScript that handles data insecurely can enable various attacks. DOM-based vulnerabilities arise when a website contains JavaScript that takes an attacker-controllable value, known as a source, and passes it into a dangerous function, known as a sink.

# DOM-based open redirect

DOM-based open-redirection vulnerabilities arise when a script writes attacker-controllable data into a sink that can trigger cross-domain navigation.

The following are some of the main sinks can lead to DOM-based open-redirection vulnerabilities: 

```js
location
location.host
location.hostname
location.href
location.pathname
location.search
location.protocol
location.assign()
location.replace()
open()
element.srcdoc
XMLHttpRequest.open()
XMLHttpRequest.send()
jQuery.ajax()
$.ajax()
```

# DOM-based cookie manipulation

Some DOM-based vulnerabilities allow attackers to manipulate data that they do not typically control. This transforms normally-safe data types, such as cookies, into potential sources. DOM-based cookie-manipulation vulnerabilities arise when a script writes attacker-controllable data into the value of a cookie. 

```
document.cookie = 'cookieName='+location.hash.slice(1);
```

So we can deliver a the following exploit to the victim:

```html
<iframe src="https://example.com/product?productId=1&test'><script>print()</script>" onload="if(!window.x)this.src='https://example.com';window.x=1;">
```

# DOM-based web message vulnerabilities

If a page handles incoming web messages in an unsafe way, for example, by not verifying the origin of incoming messages correctly in the event listener, properties and functions that are called by the event listener can potentially become sinks.

For example, an attacker could host a malicious `iframe` and use the `postMessage()` method to pass web message data to the vulnerable event listener, which then sends the payload to a sink on the parent page. This behavior means that you can use web messages as the source for propagating malicious data to any of those sinks. 

Consider the following code:

```html
<script>
window.addEventListener('message', function(e) {
  eval(e.data);
});
</script>
```

This is vulnerable because an attacker could inject a JavaScript payload by constructing the following `iframe`: 

```html
<iframe src="https://vulnerable-website" onload="this.contentWindow.postMessage('<img src=x onerror=print()>','*')">
```

## Origin verification

Even if an event listener does include some form of origin verification, this verification step can sometimes be fundamentally flawed. For example, consider the following code: 

```js
window.addEventListener('message', function(e) {
    if (e.origin.indexOf('normal-website.com') > -1) {
        eval(e.data);
    }
});
```

Note that `indexOf` method is used to verify that the origin of the incoming message is `normal-website.com` domain, however it only verifies that contains the string so an attacker could use `http://normal-website.com.evil.com`

The same flaw applies to verification check that rely on `startWith()` or `endsWith()` methods.

* StartWith: `normal-website.comevil.com`
* EndsWith: `evil-normal-website.com`
