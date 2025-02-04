---
title: Path Traversal
category: Web
order: 8
---

 Path traversal is also known as directory traversal. These vulnerabilities enable an attacker to read arbitrary files on the server that is running an application. This might include: 

* Application code and data.
* Credentials for back-end systems.
* Sensitive operating system files.


# Reading arbitrary files via path traversal

Imagin the following resource available on a webpage:

```
https://example.com/loadImage?filename=image.png
```
The `loadImage` URL takes a filename parameter and returns the contents of the specified file. The image files are stored on disk in the location `/var/www/images/`. To return an image, the application appends the requested filename to this base directory and uses a filesystem API to read the contents of the file. In other words, the application reads from the following file path `/var/www/images/image.png`.

If the application don't have implemenations of path traversal defenses we can append `../../../` and access to any file of the filesystem such as `/etc/passwd`.


```
https://example.com/loadImage?filename=../../../../../../etc/passwd
```

> **Note**: In windows `..\` and `../` are both valid in directory traversal sequences.


# Bypassing defenses

Many applications that place user input into file paths implement defenses against path traversal attacks. These can often be bypassed.

If an application strips or blocks directory traversal sequences from the user-supplied filename, it might be possible to bypass the defense using a variety of techniques.

* **Absolute paths**: Using absolute paths such as `filename=/etc/passwd` sometimes works.

* **Nested Sequences**: The use of nested sequences such as `...////` or `....\/`  will be revert to simple travesal sequences when the `../` is stripped.

* **URL Encode or doble URL Encode**: URL encode the `../` characters to `%2e%2e%2f` and `%252e%252e%252f` respectively. Some non estandards encodings such as `..%c0%af` or `..%ef%bc%8f` may work.

* **Expected folder**: The app may require the user-supplied filename to start with the expected base folder like `filename=/var/www/images/image.png` so `filename=/var/www/images/../../../../etc/passwd` could work.

* **Expected extension**: The app may require the user-supplied extension such as `filename=image.png` so we can use the null byte character `%00` to effectively terminate the string. `filename=/etc/passwd%0a.png`