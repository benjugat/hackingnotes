---
title: Bussiness Logic Flaws
category: Web
order: 11
---

Business logic vulnerabilities are flaws in the design and implementation of an application that allow an attacker to elicit unintended behavior. This potentially enables attackers to manipulate legitimate functionality to achieve a malicious goal. These flaws are generally the result of failing to anticipate unusual application states that may occur and, consequently, failing to handle them safely. 

# Excessive trust in client-side controls

A fundamentally flawed assumption is that users will only interact with the application via the provided web interface. This is especially dangerous because it leads to the further assumption that client-side validation will prevent users from supplying malicious input. 

Check if the price is sent by the client to the server and try to put different values such as `0` or `1`.

![](/hackingnotes/images/logic-flaw-1.png)

# Failing to handle unconventional input

One aim of the application logic is to restrict user input to values that adhere to the business rules. For example, the application may be designed to accept arbitrary values of a certain data type, but the logic determines whether or not this value is acceptable from the perspective of the business. Many applications incorporate numeric limits into their logic. This might include limits designed to manage inventory, apply budgetary restrictions, trigger phases of the supply chain, and so on.

In particular, try input in ranges that legitimate users are unlikely to ever enter. This includes exceptionally high or exceptionally low numeric inputs or negative ones `-1000eur` and abnormally long strings for text-based fields. You can even try unexpected data types. By observing the application's response, you should try and answer the following questions:

* Are there any limits that are imposed on the data?
* What happens when you reach those limits?
* Is any transformation or normalization being performed on your input?

# Making flawed assumptions about user behavior

One of the most common root causes of logic vulnerabilities is making flawed assumptions about user behavior. This can lead to a wide range of issues where developers have not considered potentially dangerous scenarios that violate these assumptions.

## Trusted users won't always remain trustworthy

Applications may appear to be secure because they implement seemingly robust measures to enforce the business rules. Unfortunately, some applications make the mistake of assuming that, having passed these strict controls initially, the user and their data can be trusted indefinitely. This can result in relatively lax enforcement of the same controls from that point on. 

If business rules and security measures are not applied consistently throughout the application, this can lead to potentially dangerous loopholes that may be exploited by an attacker. 

## Users won't always supply mandatory input

One misconception is that users will always supply values for mandatory input fields. Browsers may prevent ordinary users from submitting a form without a required input, but as we know, attackers can tamper with parameters in transit. This even extends to removing parameters entirely.

This is a particular issue in cases where multiple functions are implemented within the same server-side script. In this case, the presence or absence of a particular parameter may determine which code is executed. Removing parameter values may allow an attacker to access code paths that are supposed to be out of reach.

When probing for logic flaws, you should try removing each parameter in turn and observing what effect this has on the response. You should make sure to:

* Only remove one parameter at a time to ensure all relevant code paths are reached.
* Try deleting the name of the parameter as well as the value. The server will typically handle both cases differently.
* Follow multi-stage processes through to completion. Sometimes tampering with a parameter in one step will have an effect on another step further along in the workflow.

## Users won't always follow the intended sequence

Many transactions rely on predefined workflows consisting of a sequence of steps. The web interface will typically guide users through this process, taking them to the next step of the workflow each time they complete the current one. However, attackers won't necessarily adhere to this intended sequence. Failing to account for this possibility can lead to dangerous flaws that may be relatively simple to exploit. 

For example, many websites that implement two-factor authentication (2FA) require users to log in on one page before entering a verification code on a separate page. Assuming that users will always follow this process through to completion and, as a result, not verifying that they do, may allow attackers to bypass the 2FA step entirely.

Note that this kind of testing will often cause exceptions because expected variables have null or uninitialized values. Arriving at a location in a partly defined or inconsistent state is also likely to cause the application to complain. In this case, be sure to pay close attention to any error messages or debug information that you encounter. These can be a valuable source of information disclosure, which can help you fine-tune your attack and understand key details about the back-end behavior. 

> **Note**: Try to drop some request to see if some default values are setted.

# Domain-specific flaws

The discounting functionality of online shops is a classic attack surface when hunting for logic flaws. This can be a potential gold mine for an attacker, with all kinds of basic logic flaws occurring in the way discounts are applied. 

For example, consider an online shop that offers a 10% discount on orders over $1000. This could be vulnerable to abuse if the business logic fails to check whether the order was changed after the discount is applied. In this case, an attacker could simply add items to their cart until they hit the $1000 threshold, then remove the items they don't want before placing the order. They would then receive the discount on their order even though it no longer satisfies the intended criteria.

Another example is when we can use a discount to a gift card, we can generate a macro in order to get an infinite money loop. We can create a macro to execute it automatically every time a request is made.

To do that we just need to create a **Session handling rule** on `Settings tab -> Sessions -> Session handling rules`.

![](/hackingnotes/images/logic-flaw-2.png)

On `Scope -> URL Scope` tab we need to select `Include all URLS`.

![](/hackingnotes/images/logic-flaw-3.png)

On `Details` tab Add a new macro. The `Macro Recorder` windows should be open.

![](/hackingnotes/images/logic-flaw-4.png)

Select the requests needed to do the infinite cycle.

![](/hackingnotes/images/logic-flaw-5.png)

We can configure dynamic parameters, in that case the coupon voucher will be retrieved from `/cart/order-confirmation` request. To do that we need to specify a `custom parameter locations in response`. We can select on the request the text and the regex will be generated automatically.

> **Note**: Use the same name of the parameter.

![](/hackingnotes/images/logic-flaw-6.png)

On the request where we want to specify the custom paramter select the option `Derive from prior response` and select the response where the coupon was retrieved.

![](/hackingnotes/images/logic-flaw-7.png)

Finally test the macro and if it works try to use repeater or intruder to see if it is executed.

# Providing an encryption oracle

Dangerous scenarios can occur when user-controllable input is encrypted and the resulting ciphertext is then made available to the user in some way. This kind of input is sometimes known as an "encryption oracle". An attacker can use this input to encrypt arbitrary data using the correct algorithm and asymmetric key.
