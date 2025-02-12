---
title: Race Conditions
category: Web
order: 10
---

Race conditions are a common type of vulnerability closely related to business logic flaws. They occur when websites process requests concurrently without adequate safeguards. This can lead to multiple distinct threads interacting with the same data at the same time, resulting in a "collision" that causes unintended behavior in the application. A race condition attack uses carefully timed requests to cause intentional collisions and exploit this unintended behavior for malicious purposes.

![](/hackingnotes/images/race-condition-1.png)

The period of time during which a collision is known as the `race window`. This could be the fraction of a second between two interactions with the database.

![](/hackingnotes/images/race-condition-2.png)

There are many variations of this kind of attack:

* Redeeming a gift card multiple times.
* Rating a product multiple times.
* Withdrawing or transfering chash in excess of your account balance.
* Reusing a single CAPTCHA solution.
* Bypassing an anti-force rate limit.

# Detecting and exploiting limit overrun race conditions

The challange is timming the requests in order to line up at least two race windows, causing a collision. Even if we sent multiple requests at the same time, there are various uncontrollable and unpredictable external factors that affect the server processes each request and in which order.

![](/hackingnotes/images/race-condition-3.png)

* **HTTP/1**: Last-byte synchronization technique.
* **HTTP/2**: Single-packet attack technique.

This `single-packet` technique enables you to completely neutralize the interference from network jitter by using a single TCP packet to complete 20-30 requests simultaneously.

![](/hackingnotes/images/race-condition-4.png)

## With Burp Repeater

There are multiple techniques to allign the the race windows, that are added in `Burp Repeater: Sending requests in parallel`, more info in:

* [https://portswigger.net/burp/documentation/desktop/tools/repeater/send-group#sending-requests-in-parallel](https://portswigger.net/burp/documentation/desktop/tools/repeater/send-group#sending-requests-in-parallel)

We just need to agrupate the requests on repeater, and change to `Send group (parallel)`.

![](/hackingnotes/images/race-condition-repeater.png)

## With Turbo Intruder

It is also added native support to single-packet attack in turbo intruder. To use single-packet attack in turbo intruder:

1. Ensure that the target support HTTP/2. Incompatible with HTTP/1.
2. Set the `engine=Engine.BURP2` and `concurrentConnections=1` configuration options for the request engine.
3. When queueing the requests, group them by assigning them to a named gate using the `gate` argument for the `engine.queue()` method.
4. To send all the requests in a given group, open the gate with `engine.openGate()`.

```py
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                            concurrentConnections=1,
                            engine=Engine.BURP2
                            )
    
    # queue 20 requests in gate '1'
    for i in range(20):
        engine.queue(target.req, gate='1')
    
    # send all requests in gate '1' in parallel
    engine.openGate('1')
```