---
title: Web cache deception
category: Web
order: 12
---

Web cache deception is a vulnerability that enables an attacker to trick a web cache into storing sensitive, dynamic content. It's caused by discrepancies between how the cache server and origin server handle requests.

In a web cache deception attack, an attacker persuades a victim to visit a malicious URL, inducing the victim's browser to make an ambiguous request for sensitive content. The cache misinterprets this as a request for a static resource and stores the response. The attacker can then request the same URL to access the cached response, gaining unauthorized access to private information.

![](/hackingnotes/images/web-cache-deception.png)

The difference between web cache deception and web cache poisoning, while both exploit caching mechanism:

* Web cache deception exploits cache rules to trick the cache into storing sensitive or private content, which the attacker can then access
* Web cache poisoning manipulates cache keys to inject malicious content into a cached response, which is then served to other users.

# Web caches

A web cache is a system that sits between the origin server and the user. When a client requests a static resource, the request is first directed to the cache. If the cache doesn't contain a copy of the resource (known as a cache miss), the request is forwarded to the origin server, which processes and responds to the request. The response is then sent to the cache before being sent to the user. The cache uses a preconfigured set of rules to determine whether to store the response. 

When a request for the same static resource is made in the future, the cache serves the stored copy of the response directly to the user (known as a cache hit). 

![](/hackingnotes/images/web-cache-deception-2.png)

## Cache keys

When the cache receives an HTTP request, it must decide whether there is a cached response that it can serve directly, or whether it has to forward the request to the origin server. The cache makes this decision by generating a `cache key` from elements of the HTTP request. Typically, this includes the URL path and query parameters, but it can also include a variety of other elements like headers and content type.

If the incoming request's cache key matches that of a previous request, the cache considers them to be equivalent and serves a copy of the cached response. 

## Cache rules

Cache rules determine what can be cached and for how long. Cache rules are often set up to store static resources, which generally don't change frequently and are reused across multiple pages. Dynamic content is not cached as it's more likely to contain sensitive information, ensuring users get the latest data directly from the server.

Web cache deception attacks exploit how cache rules are applied, so it's important to know about some different types of rules, particularly those based on defined strings in the URL path of the request. For example: 

* **Static file extension rules**: Those rules that match the file extension of the requested resource, for example `.css` or `.js`.
* **Static directory rules**: These rules match all urls paths that start with a specifix prefix for example `/static` or `/assets`.
* **File name rules**: These rules match specific file names to target files that are universally required for web operations and change rarely such as `robots.txt` and `favicon.ico`.


# Construting an attack

A basic web cache deception attack involves the following steps:

1. Identify a target endpoint that returns a dynamic response containing sensitive information. Focus on endpoints that support the `GET`, `HEAD` or `OPTIONS` methods as requests that alter the origin server's state are generally not cached.
2. Identify discrepancy in how the cache and origin server parse the URL path. Discrepancies in `Map URLs to resources`, `Process delimiter characters` and `Normalize paths`.
3. Craft a malicious URL that uses the discrepancy to trick the cache into storing a dynamic response. When te victim accesses the URL, their response will be stored in the cache. The attacker can send a request to the same URL to fetch the cached response containing the victim's data.

> **Note**: Avoid doing this directly in the browser as some applications redirect users without a session or invalidate local data, which could hide a vulnerability.

## Cache buster

While testing discrepancies and crafting a web cache deception exploit, make sure that each request has a different cache key. As both URL path and any query parameteres are typically included in the cache key, you can change the key by adding a query string to the path and changing it each time you send a request.

This can be done with `Param miner`. Click on `Param miner -> Settings` menu and select `Add dynamic cachebuster`.

![](/hackingnotes/images/web-cache-deception-3.png)

## Detecting cached responses

During testing, it's crucial to detect cached responses. Various response headers may indicate that it is cached:

* `X-Cache`: Provides information about whether a reponse was served from the cache. Typical values: `hit` the response was served form the cache, `miss` cache did not contain a response for the request's key, in most cases the response is then cached, `dynamic` the origin server dynamically generated the content, which means the response is not suitable for caching, and `refresh` the cached content was outdated and needed to be refreshed or revalidated.
* `Cache-Control`: May include a directive that indicates caching, like `public` with a `max-age` higher than `0`. This only suggest that the resource is cacheable. It isn't always indicative of caching, as the cache may sometimes override this header.

> **Note**: If you notice a big different in response time for the same request, this may algo indicate that the faster response is served from the cache.

# Exploiting static extension cache rules

Cache rules often target static resources by matching common file extensions like `.css` or `.js`. This is the default behavior in most CDNs. 

## Path mapping discrepancies

URL path mapping is the process of associating URL paths with resources on a server, such as files, scripts, or command executions. There are a range of different mapping styles used by different frameworks and technologies. Two common styles are traditional URL mapping and RESTful URL mapping. 

* **Traditional URL mapping**: `https://hackingnotes.com/path/resource.html`

`http://hackingnotes.com` points to the server.
`/path/` represents the directory path in the server's file system.
`resource.html` is the specific file.

* **REST URL mapping**: `https://hackingnotes.com/path/resource/param1/param2`

`http://hackingnotes.com` points to the server.
`/path/resource` in and enpoint representing a resource.
`param1` and `param2` are path parameteres used by the server to process the request.

Discrepancies is how the cache and origin server map the URL path to resources can result in web cache deception vulnerabilities. Consider the following example `https://hackingnotes.com/user/1/profile/wcd.css`.

An origin server using RESTful URL mapping may interpret this as a request for `/user/1/profile` ignorind `wcd.css` as a non-significant parameter.

A cache that uses traditional URL mapping may view this as a request for a file named `wcd.css` located in `/profile` directory under `/user/1`. It interprets the URL path as `/user/1/profile/wcd.css`. If the cache is configured to store responses for requests where the path ends in `.css`, it would cache and serve the profile information as if it were a CSS file.

### Explotaiton

To test how the origin server maps the URL path to resources, add an arbitrary path segment to the URL of your target endpoint. If the response still contains the same sensitive data as the base response, it indicates that the origin server abstracts the URL path and ignores the added segment.

For example, this is the case if modifying `/api/orders/1` to `/api/orders/1/foo` still returns order inofrmation.

To test how the cache maps the URL paths to resources, you'll need to modify the path to attempt to match a cache rule by adding a static extension. For example, update `/api/orders/1/foo` to `/api/orders/1/foo.js`. If the response is cached, this indicates that the cache interprets the full URL path with the static extension, and that there is a cache rule to store responses for requests ending in `.js`.

> **Note**: Try a range of extensions including `.css`, `.ico`, `.js`, `.exe` ...

## Delimiter discrepancies

Delimiters specify boundaries between different elements in URLs. The use of characters and strings as delimiters is generally standardized. For example, ? is generally used to separate the URL path from the query string. However, as the URI RFC is quite permissive, variations still occur between different frameworks or technologies. 

Discrepancies in how the cache and origin server use characters and strings as delimiters can result in web cache deception vulnerabilities. Consider the example `/profile;foo.css`:

* Java Spring framework uses `;` charater to add parameters known as matrix variables. It will interprete `;` as a delimeter and will truncate the path after `/profile`. and will return profile information.
* Other frameworks don't use `;` as a delimeter,  cache that doesn't use Java Spring is likely to interpret `;` and everything after it as part of the path. If the cache has a rule to store responses for requests ending in `.css`, it might cache and serve the profile information as if it were a CSS file. 

Encoded characters may algo sometimes be used as delimeters for example `/profile%00foo.js`.

### Exploitation

First we need to find characters that are used as delimiters by the origin server. Start by adding a random string to a legit endpoint such as `/my/endpoint/list` to `/my/endpoint/listaaaa`.

Next, add posible delimeteres between the original path and the random string such as `/my/endpoint/list;aaaa`.

> **Note**: If the response of `/my/endpoint/list;aaa` is identical to `/my/endpoint/list` indicates that the character `;` is a delimiter.

Once we've identified delimiters that are used by the origin server, test whether they're also used by the cache. To do this, add a static extension to the end of the path.

If the response is cached indicates that:

* The cache doesn't use the delimiter and interprets the full URL path with the satic extension.
* That there is a cache rule to store responses.

Here we can find a web cache deception **delimiter list**:
```
!
"
#
$
%
&
'
(
)
*
+
,
-
.
/
:
;
<
=
>
?
@
[
\
]
^
_
`
{
|
}
~
%21
%22
%23
%24
%25
%26
%27
%28
%29
%2A
%2B
%2C
%2D
%2E
%2F
%3A
%3B
%3C
%3D
%3E
%3F
%40
%5B
%5C
%5D
%5E
%5F
%60
%7B
%7C
%7D
%7E
%00
%0A
%09
```
> **Note**: Some delimiters characters may be processed by the victim's browser before it forwards the request to cache. This means that some delimiters can't be used in an exploit. An example of this are `#`, `{`, `}`, `<` and `>`. If the cache or origin server decodes these characters, it may be possible to use and encoded version.

# Exploiting static directory cache rules

It's common practice for web servers to store static resources in specific directories such as `/static`, `/assets`, `/scripts` or `/images`. These rules can also be vulnerable to web cache deception.

## Normalization discrepancies

Normalization involves converting various representations of URL paths into a standardized format. Includes decoding and resolving dot-segments such as `/static..%2fprofile`.

* An origin server that decodes slash characters and resolves dot-segments would normalize the path to `/profile`. and return profile information.
* A cache that doesn't resolve dot-segments or decode slashes would interpret the path as `/static/..%2fprofiles`, and the cache stores responses for requests with `/static` prefix it would cache and serve the profile information.

> **Note**: Each dot-segment in the path traversal sequence needs to be encoded. Otherwise the victim's browser willl resolve it before forwarding the request to the cache.

### Detecting normalization by the origin server

To test how the origin server normalizes the URL path, **send a request to a non-cacheable resource** with a path traversal sequence.

For example if we want to check `/profile` try `/aaa/..%2fprofile`.

* If the response matches the base response and return the profile information, indicates that the path has been interpreted as `/profile`. **It will work.**
* If the response doesn't match the base response, returning a `404 Not Found` indicates that the path has been intrepreted as `/aaa/..%2fprofile`. **It won't work.**

> **Note**: Try to encode a dot instead of a slash, sometimes the server shows a different response.

If the origin server resolves encoded dot-segments, and the cache don't, we can attempt to exploit the discrepancy by constructing a payload such as:

```
/<static-directory-prefix>/..%2f<dynamic-path>
/assets/..%2fprofile
```

### Detecting normalization by the cache server

We can use different methods to test how the cache normalizes the path. We can start by identifying potential static directories. Focus on static resources.

We can choose a request with a cached response and resent the request with a path traversal sequence and an arbitrary directory at the start of the static path. For example `/aaa/..%2fassets/js/main.js`.

* If the response is no longer cached, this indicates that the cache isn't normalizing the path before mapping it to the endpoint. It shows that there is a cache rule based on the `/assets` prefix.
* If the response is still cached, this may indicate that the cache has normalized to `/assets/js/main.js`.

We can also try to add a dot-segment after que directory prefix such as `/assets/..%2f/js/main.js`.

* If the response is no longer cached, indicates that the cache decodes the payload and resolve the dot-segment interpreting the path as `/js/main.js`. Shows that there is a cache rule based on `/assets` prefix.
* If the response is still cached, this may indicate that the cache hasn't decoded the slash or resolved the dot-segment, interpreting the path as `/assets/..%2fjs/main.js`.

> **Note**: In both cases the response may be cached due to another cache rule such as one based on file extension. To confirm try `/assets/aaa`.

If the cache server resolves encoded dot-segments but the origin server doesn't, we can try to exploit discrepancies by constructing a payload such as:

```
/<dynamic-path>%2f%2e%2e%2f<static-directory-prefix>
/profile%2f%2e%2e%2fstatic
```

The origin server is likely to return an error `404` because will interpret `/profile%2f%2e%2e%2fstatic`. **Try to use a delimiter**

```
/profile;%2f%2e%2e%2fstatic
```

# Exploiting file name cache rules

Certain files such as `robots.txt`, `index.html` or `favicon.ico` are common files found on web servers. They're often cached due to their infrequent changes. Those files can be cached.

The exploitation is similar to static directory cache rules but specifying the file.

```
/profile;%2f%2e%2e%2findex.html
```