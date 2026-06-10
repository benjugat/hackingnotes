---
title: Web
description: Web application attacks and methodologies: OWASP Top 10, logic flaws, smuggling, deserialization, SSRF, JWT and more.
---

# Web

Web application attacks and methodologies: OWASP Top 10, logic flaws, smuggling, deserialization, SSRF, JWT and more.

## Contents

<div class="grid cards" markdown>

-   **[Access Control](access-control.md)**

    ---

    Access control is the application of constraints on who or what is authorized to perform actions or access resources. In the context of web applications, access control is dependent on authentication and session managem…

-   **[API Testing](api-testing.md)**

    ---

    APIs are usually documented so that developers know how to use and integrate with them.

-   **[Authentication Vulnerabilities](broken-authentication.md)**

    ---

    Authentication vulnerabilities are usually critical beacuse of the clear relationship between authentication and security.

-   **[Clickjacking](clickjacking.md)**

    ---

    Clickjacking is an interface-based attack in which a user is tricked into clicking on actionable content on a hidden website by clicking on some other content in a decoy website.

-   **[Command Injection](command-injection.md)**

    ---

    OS command injection is also known as shell injection. It allows an attacker to execute operating system (OS) commands on the server that is running an application, and typically fully compromise the application and its…

-   **[Cross-Origin Resource Sharing (CORS)](cors.md)**

    ---

    Cross-origin resource sharing (CORS) is a browser mechanism which enables controlled access to resources located outside of a given domain. It extends and adds flexibility to the same-origin policy (SOP). However, it al…

-   **[Cross Site Request Forgery (CSRF)](csrf.md)**

    ---

    Cross-site request forgery (also known as CSRF) is a web security vulnerability that allows an attacker to induce users to perform actions that they do not intend to perform. It allows an attacker to partly circumvent t…

-   **[DOM Based](dom.md)**

    ---

    The Document Object Model (DOM) is a web browser's hierarchical representation of the elements on the page. Websites can use JavaScript to manipulate the nodes and objects of the DOM, as well as their properties. DOM ma…

-   **[File Inclusion](file-inclusion.md)**

    ---

    File Inclusion refers to an inclusion attack through which an attacker can trick the web application into including files on the web server.

-   **[File Upload](file-upload.md)**

    ---

    File upload vulnerabilities are when a web server allows users to upload files to its filesystem without sufficiently validating things like their name, type, contents, or size. Failing to properly enforce restrictions…

-   **[Graphql](graphql.md)**

    ---

    ------ title: GraphQL category: Web order: 24 ---

-   **[HTTP Host header attacks](http-host-header-attacks.md)**

    ---

    The HTTP Host header is a mandatory request header as of HTTP/1.1. It specifies the domain name that the client wants to access.

-   **[HTTP Request Smuggling](http-request-smuggling.md)**

    ---

    HTTP request smuggling is a technique for interfering with the way a web site processes sequences of HTTP requests that are received from one or more users. Request smuggling vulnerabilities are often critical in nature…

-   **[Insecure Deserialization](insecure-deserialization.md)**

    ---

    Serialization is the process of converting complex data structures, such as objects and their fields, into a "flatter" format that can be sent and received as a sequential stream of bytes. Deserialization is the process…

-   **[JWT Attacks](jwt-attacks.md)**

    ---

    JSON web tokens (JWTs) are a standardized format for sending cryptographically signed JSON data between systems. They can theoretically contain any kind of data, but are most commonly used to send information ("claims")…

-   **[Bussiness Logic Flaws](logic-flaws.md)**

    ---

    Business logic vulnerabilities are flaws in the design and implementation of an application that allow an attacker to elicit unintended behavior. This potentially enables attackers to manipulate legitimate functionality…

-   **[NoSQL Injection (NoSQLi)](nosqli.md)**

    ---

    NoSQL injection attacks can be especially dangerous because code

-   **[OAuth 2.0 Bypass](oauth-2.0-bypass.md)**

    ---

    OAuth is a commonly used authorization framework that enables websites and web applications to request limited access to a user's account on another application. Crucially, OAuth allows the user to grant this access wit…

-   **[Prototype Pollution](prototype-pollution.md)**

    ---

    Prototype pollution is a JavaScript vulnerability that enables an attacker to add arbitrary properties to global object prototypes, which may then be inherited by user-defined objects.

-   **[Race Conditions](race-conditions.md)**

    ---

    Race conditions are a common type of vulnerability closely related to business logic flaws. They occur when websites process requests concurrently without adequate safeguards. This can lead to multiple distinct threads…

-   **[SQL Injection (SQLi)](sqli.md)**

    ---

    SQLi is a common web application vulnerability that is caused by unsanitized user input being inserted into SQL queries.

-   **[Server-Side Request Forgery (SSRF)](ssrf.md)**

    ---

    Server-side request forgery is a web security vulnerability that allows an attacker to cause the server-side application to make requests to an unintended location.

-   **[Server Side Templates Injections (SSTI)](templates-injections.md)**

    ---

    SSTI (Server Side Templates Injections) occurs when an attacker is able to use native template syntax to inject a malicious payload into a template, which is then executed server-side.

-   **[Unrestricted File Upload](unrestricted-file-upload.md)**

    ---

    Different ways to upload files and get RCE.

-   **[Web cache deception](web-cache-deception.md)**

    ---

    Web cache deception is a vulnerability that enables an attacker to trick a web cache into storing sensitive, dynamic content. It's caused by discrepancies between how the cache server and origin server handle requests.

-   **[Web cache poisoning](web-cache-poisoning.md)**

    ---

    Web cache poisoning is an advanced technique whereby an attacker exploits the behavior of a web server and cache so that a harmful HTTP response is served to other users.

-   **[Web Llm](web-llm.md)**

    ---

    ------ title: Web LLM Attacks category: Web order: 23 ---

-   **[XSS](xss.md)**

    ---

    Cross-site scripting (XSS) allows an attacker to compromise the interactions that users have with a vulnerable application.

-   **[XXE Injection](xxe.md)**

    ---

    XML External Entity injection as known as XXE is a vulnerability that allowss an attacker to interfere with an application's processing of XML data. It often allows an attacker to view files on the application server an…

</div>
