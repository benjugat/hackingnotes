---
title: JWT Attacks
category: Web
order: 23
---

JSON web tokens (JWTs) are a standardized format for sending cryptographically signed JSON data between systems. They can theoretically contain any kind of data, but are most commonly used to send information ("claims") about users as part of authentication, session handling, and access control mechanisms. 

A JWT consists of 3 parts: a header, a payload, and a signature. These are each separated by a dot, as shown in the following example: 

![JWT](/hackingnotes/images/jwt.png)

* [https://jwt.io/](https://jwt.io/)

The server that issues the token typically generates the signature by hashing the header and payload. In some cases, they also encrypt the resulting hash. Either way, this process involves a secret signing key. This mechanism provides a way for servers to verify that none of the data within the token has been tampered.

The JWT specification is actually very limited. It only defines a format for representing information ("claims") as a JSON object that can be transferred between two parties. In practice, JWTs aren't really used as a standalone entity. The JWT spec is extended by both the JSON Web Signature (JWS) and JSON Web Encryption (JWE) specifications, which define concrete ways of actually implementing JWTs.

![JWS - JWE](/hackingnotes/images/jwe.png)

In other words, a JWT is usually either a JWS or JWE token. When people use the term "JWT", they almost always mean a JWS token. JWEs are very similar, except that the actual contents of the token are encrypted rather than just encoded. 

With Bupsuite we can modify, sign and attack JWT. Check for more info the following link:

* [https://portswigger.net/burp/documentation/desktop/testing-workflow/session-management/jwts](https://portswigger.net/burp/documentation/desktop/testing-workflow/session-management/jwts)

# Exploiting flawed JWT signature verification

By design, servers don't usually store any information about the JWTs that they issue. Instead, each token is an entirely self-contained entity. So if we can modify the claims and bypass the signature verification we can modify our rights.

## Accepting arbitrary signatures

JWT libraries typically provide one method for verifying tokens and another that just decodes them. For example, the Node.js library `jsonwebtoken` has `verify()` and `decode()`.

Occasionally, developers confuse these two methods and only pass incoming tokens to the decode() method. This effectively means that the application doesn't verify the signature at all.

So we can change the claims without a valid signature.

![JWT with arbitrary signature](/hackingnotes/images/jwt-nosignature.png)

## Accepting tokens with no signature

Among other things, the JWT header contains an `alg` parameter. This tells the server which algorithm was used to sign the token and, therefore, which algorithm it needs to use when verifying the signature. 

```
{
    "alg": "HS256",
    "typ": "JWT"
}
```

This is inherently flawed because the server has no option but to implicitly trust user-controllable input from the token which, at this point, hasn't been verified at all. In other words, an attacker can directly influence how the server checks whether the token is trustworthy. 

JWTs can be signed using a range of different algorithms, but can also be left unsigned. In this case, the `alg` parameter is set to `none`, which indicates a so-called "unsecured JWT".

```
{
    "alg": "none",
    "typ": "JWT"
}
```

![JWT with arbitrary signature](/hackingnotes/images/jwt-none.png)

# Brute-forcing secret keys

Some signing algorithms, such as HS256 (HMAC + SHA-256), use an arbitrary, standalone string as the secret key. Just like a password, it's crucial that this secret can't be easily guessed or brute-forced by an attacker. 

There are a wordlist of well-known secrets:

* [https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list)

It can be cracked with `hashcat`:

```
hashcat -a 0 -m 16500 <jwt> <wordlist>
```

Once cracked we should add the key on JWT Editor burp extension as a symmetric key.

![JWT Key](/hackingnotes/images/jwt-key.png)


# JWT header parameter injections

According to the JWS specification, only the alg header parameter is mandatory. In practice, however, JWT headers (also known as JOSE headers) often contain several other parameters. The following ones are of particular interest to attackers. 

* `jwk` (JSON Web Key) - Provides an embedded JSON object representing the key. 
* `jku` (JSON Web Key Set URL) - Provides a URL from which servers can fetch a set of keys containing the correct key.
* `kid` (Key ID) - Provides an ID that servers can use to identify the correct key in cases where there are multiple keys to choose from. Depending on the format of the key, this may have a matching kid parameter.

These user-controllable parameters each tell the recipient server which key to use when verifying the signature. The idea is to trick the server to use our injected key instead of the server one.

## Injecting self-signed JWTs via the jwk parameter

The JSON Web Signature (JWS) specification describes an optional `jwk` header parameter, which servers can use to embed their public key directly within the token itself in JWK format. 

```
{
    "kid": "28ce00f8-57b8-4fde-ae75-ec6a16d5231d",
    "typ": "JWT",
    "alg": "RS256",
    "jwk": {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "28ce00f8-57b8-4fde-ae75-ec6a16d5231d",
        "n": "roJMZ8RJz1gJC0aULEGrxP0jqM2ySlvnZFE3PCPQSeZsm-uHUlQr0r2EfXBEIrExSktUtge7qutfcdRXv28euJLv26shATMVN5lazCV6I8JeN75GicIhNlsk5-3ZNhWFKqFg2rPojDDQ8SsIo1l2dir9tvAnM9DRre20n3ypVB0pk_cC_zpr4Eh2-2Ji-BsO3BV922p_w-2_kTbe6hfmE698m2YqW4LWrg0YHcE8x00fZ6jGkupiS50jARHezvqPfp4UDhu0Pio2NZvW1Er7qBJA_Z9F_9SlB_eqTcLGaBYRMvJkZ-xb606xKFXsM4yfIHUEOUGO5OZR1kOlRwUGhQ"
    }
}
```

Ideally, servers should only use a limited whitelist of public keys to verify JWT signatures. However, misconfigured servers sometimes use any key that's embedded in the `jwk` parameter.

You can exploit this behavior by signing a modified JWT using your own RSA private key, then embedding the matching public key in the `jwk` header.

Follow the steps in order to exploit it using the `JWT Editor` burp extension.

1. Generate a new RSA key on the `JWT Editor Keys` tab.

![JWK RSA Key](/hackingnotes/images/jwk-rsa.png)

2. Send a request containing a JWT to Repeater.
3. In the message editor, switch to the extension-generated JSON Web Token tab and modify the token's payload.
4. Click `Attack` then select `Embedded JWK`. Whem prompted, select your newly generated RSA key.

![Embedded JWK](/hackingnotes/images/jwk-embedded.png)

5. Send the request.


## Injecting self-signed JWTs via the jku parameter

Instead of embedding public keys directly using the `jwk` header parameter, some servers let you use the `jku` (JWK Set URL) header parameter to reference a JWK Set containing the key. When verifying the signature, the server fetches the relevant key from this URL. 

```
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
            "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
        },
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA",
            "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ_cb33HocCuJolwDqmk6GPM4Y_qTVX67WhsN3JvaFYw-dfg6DH-asAScw"
        }
    ]
}
```

JWK Sets like this are sometimes exposed publicly via a standard endpoint, such as `/.well-known/jwks.json`.

Follow the steps in order to exploit it using the `JWT Editor` burp extension. Also a exploit server is needed to host the keys.

1. Generate a new RSA key on the `JWT Editor Keys` tab.

![JWK RSA Key](/hackingnotes/images/jwk-rsa.png)

2. Send a request containing a JWT to Repeater.
3. In the message editor, switch to the extension-generated JSON Web Token tab and modify the token's payload.
4. Click `Attack` then select `Embed Collaborator payload`. Whem prompted, select `jku`.
5. Host the key on a exploit server. `Content-Type: application/json`.

```
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
            "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
        }
    ]
}
```
6. Change the `jku` URL to our exploit server: `"jku:"httpps://exploit-server.com/jwks.json"`.
7. Sign the request with the RSA key. Important, select the option `Update/generate "alg", "typ" and "kid" parameters`.

![JKU Sign](/hackingnotes/images/jku-sign.png)

8. Send the request.

## Injecting self-signed JWTs via the kid parameter

Servers may use several cryptographic keys for signing different kinds of data, not just JWTs. For this reason, the header of a JWT may contain a `kid` (Key ID) parameter, which helps the server identify which key to use when verifying the signature. 

Verification keys are often stored as a JWK Set. In this case, the server may simply look for the JWK with the same `kid` as the token. However, the JWS specification doesn't define a concrete structure for this ID - it's just an arbitrary string of the developer's choosing. For example, they might use the `kid` parameter to point to a particular entry in a database, or even the name of a file. 

If this parameter is also vulnerable to directory traversal, an attacker could potentially force the server to use an arbitrary file from its filesystem as the verification key.

You could theoretically do this with any file, but one of the simplest methods is to use `/dev/null`, which is present on most Linux systems. As this is an empty file, reading it returns an empty string. Therefore, signing the token with a empty string will result in a valid signature. 

```
{
    "kid": "../../dev/null",
    "typ": "JWT",
    "alg": "HS256",
    "k": "asGsADas3421-dfh9DGN-AFDFDbasfd8-anfjkvc"
}
```

If the server stores its verification keys in a database, the kid header parameter is also a potential vector for SQL injection attacks. 

### Kid header path traversal

Follow the steps in order to exploit it using the `JWT Editor` burp extension.

1. Generate a new symmetric key in blank on the `JWT Editor Keys` tab.
![KID key](/hackingnotes/images/kid-key.png)

2. Send a request containing a JWT to Repeater.
3. In the message editor, switch to the extension-generated JSON Web Token tab and modify the token's payload.
4. Modify the `kid` header with a ppath traversal pointing to `/dev/null` file.

![KID modified](/hackingnotes/images/kid-modified.png)

5. Sign the request with the new key generated
6. Send the request.