---
title: Non-Jailborken iOS
category: Movil
order: 2
---

# Non-jailbroken iOS Hacking

On a jailbroken device, you can run `frida-server`, which handles injection for you, even in encrypted apps. However, on a non-jailbroken device, we have to prepare the application manually. There are two approaches we can take:

* Install a debug version of the application and inject during application launch
* Repackage the application to include the Frida Gadget

## Debug Version

Frist we need to create our signing certificate and the provisioning profile in xcode. After create that we can Sign our IPA without with the flag `get-task-allow` in `iOS App Signer`.

![iOS App Signer](/hackingnotes/images/ios-app-signer.jpg)

* https://github.com/DanTheMan827/ios-app-signer

> **Note**: It's important to **unmark** the `No get-task-allow` flag.

Once signed we can install it on our device with:

```
ideviceinstaller install resigned.ipa
ideviceintaller list
```

Once installed we need to store the frida gadget lib into our macOS.

```
wget https://github.com/frida/frida/releases/download/16.7.19/frida-gadget-16.7.19-ios-universal.dylib.gz
gzip -d frida-gadget-16.7.19-ios-universal.dylib.gz
mv frida-gadget-16.7.19-ios-universal.dylib /Users/USER/.cache/frida/gadget-ios.dylib
```

Finally use objection as usually does:

```
objection -g com.example explore
```

![Objection](/hackingnotes/images/objection-non-jailbroken.jpg)


If we get a timeout and get a blackscreen we need to configure frida in order to resume the app at startup.

```
nano /Users/USER/.cache/frida/gadget-ios.config

{
  "interaction": {
    "type": "listen",
    "address": "127.0.0.1",
    "port": 27042,
    "on_load": "resume"
  }
}
```