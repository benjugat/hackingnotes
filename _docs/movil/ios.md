---
title: iOS
category: Movil
order: 1
---

Setup of the environment

More info in:

* [https://ios.cfw.guide](https://ios.cfw.guide)

# Jailbreaks

## Jailbreak iOS 14 with Checkra1n

Jailbreak is needed to make an audit of an iOS application. Checkra1n allows us to get our iphone jailbroke.

```
sudo checkra1n 
```

![Checkra1n](/hackingnotes/images/checkra1n_01.png)


In order to get support on iOS 14.2 we need to skip the A11 BPR checks.

![Skip A11 BPR checks](/hackingnotes/images/checkra1n_02.png)

Once properly configured we can jailbreak our iphone.

![Checkra1n](/hackingnotes/images/checkra1n_03.png)

## Jailbreak iOS 15 with Palera1n (rootless)

Passcode should be deleted previously. You can download palera1n from the following link:

* [https://github.com/palera1n/palera1n/releases/tag/v2.0.0-beta.7](https://github.com/palera1n/palera1n/releases/tag/v2.0.0-beta.7)

Open a terminal and **keep the tab open**.
```
sudo systemctl stop usbmuxd
sudo usbmuxd -f -p
```

First step is to run palera1n without root permissions (rootless).

```
./palera1n-linux-x86_64 -l
```

Once on DFU mode open close the palera1n and execute palera1n another time with root permissions and follow the instructions.

```
sudo ./palera1n-linux-x86_64
```

With a newer version of palera1n its possible to do it with one step.

```
sudo /bin/sh -c "$(curl -fsSL https://static.palera.in/scripts/install.sh)"
```

```
sudo palera1n -l
```

### Troubleshooting

* **Phone stucked in DFU mode**:

If fails and the phone gets stucked on DFU or recovery mode execute the following command: 

```
sudo ./palera1n --exit-recovery
```

* **Wifi not working**:

If wifi does not work afeter jailbreak, try to execute palera1n in safe mode.

```
sudo ./palera1n -s
```

* **Timeout Error**:

If an error like this `<Error>: Timed out waiting for download mode (error code: -status_exploit_timeout_error)` appears, try to unplug and plug again the device without closing palerain.


* **Loader Palera1n not installed**:

Remember to not set passcode or touchID during the hard reset.

# Installing Burp certificate

Once the proxy has been configured on the device, open the browser and search for the url `http://burp`. Download the profile.

![Downloaded Profile](/hackingnotes/images/ios_burp.png)

Then go to settins and a new tabb will appear with the downloaded profiles.

![Downloaded Profile](/hackingnotes/images/ios_profile.png)

Install the profile.

![Install Profile](/hackingnotes/images/ios_install.png)

Finally, we just need to enable and trust with the certificate. Search on settings `trust certificates` and enable PortSwigger CA certificate.

![Burp Certificate](/hackingnotes/images/ios_certi.png)

# Setup openssh server

Root password should be changed before ssh usage. Execute the following commands to change the password from **NewTerm** software on the iOS device.

```
iPhone:~ mobile% sudo passwd root
[sudo] password for mobile: [enter password setup during Palera1n install]
Changing password for root.
Old Password: [alpine]
New Password: [alpine]
Retype New Password: [alpine]
```

# Installing packages

## on Zebra 

In order to make and audit some software is needed:

* **Filza File Manager**: File manager to install ipa files. -> `http://apt.thebigboss.org/`
* **Openssh server** -> `https://apt.procurs.us/`
* **Frida Server**: Hooking software. Repo -> `https://build.frida.re`.
* **Newterm**: Terminal. -> `https://repo.chariz.com`
* **Shadow**: Jailbreak bypass. Repo -> `https://ios.jjolano.me` or `https://ellekit.space`
* **Newterm**: Terminal
* **SSL Kill Switch 3**: SSL pinning bypass. Repo -> `https://repo.misty.moe/apt`.

## on Kali

* **Frida Client**:

It's important that the frida server (iphone) version match with frida client (pc).

Frida client installation:

```
pip3 install frida
pip3 install frida-tools
```

Useful commands:

```
frida-ls-devices	# list devices
frida-ps -Uia		# running processes
frida upload <local> <remote>
frida download <remote> <local>

frida-trace -U "app" -i "*log*"		# functions called

frida-ios-dump

frida -U -p 1234 -l test_script.js
```

* **Objection**:

Objection is an awesome tool that uses frida to hook functions and make bypasses such as ssl pinning or jailbreak detection.

```
pip3 install objection
```

Usage:

```
frida-ps -Uai
objection --gadget com.example.app explore
```

If an error like that occur, try to downgrade from frida 17 to frida 16.

```
frida.core.RPCException: ReferenceError: 'ObjC' is not defined
```

On the kali try to install:

```
pip3 install frida==16.5.2
```

And execute the following commands on the ios via ssh.

```
# contains plist
cd /var/jb/Library/LaunchDaemons/

# move plist to root
mv re.frida.server.plist ~
cd ~

#unload frida service
launchctl unload re.frida.server.plist
mv re.frida.server.plist /var/jb/Library/LaunchDaemons
mv /var/jb/Library/LaunchDaemons/re.frida.server.plist /var/jb/Library/LaunchDaemons/re.frida.server.backup

# fetch FRIDA
wget -O /tmp/frida_16.5.2_iphoneos-arm64.deb https://github.com/frida/frida/releases/download/16.5.2/frida_16.5.2_iphoneos-arm64.deb

# update server, agent and plist
dpkg -i /tmp/frida_16.5.2_iphoneos-arm64.deb

# restore plist
mv /var/jb/Library/LaunchDaemons/re.frida.server.backup /var/jb/Library/LaunchDaemons/re.frida.server.plist

# launch service using new plist
launchctl load /Library/LaunchDaemons/re.frida.server.plist
```


# IPA extractor

We can extract the IPA from an installed application from APP Store.

* [https://github.com/AloneMonkey/frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump)

Modify the code in order to put the IP and Port of the iOS ssh server.

```
DUMP_JS = os.path.join(script_dir, 'dump.js')

User = 'root'
Password = 'alpine'
Host = 'IP'
Port = 22
KeyFileName = None
```

```
python3 ./dump.py com.example.app
```

It is also possible to zip the bundle app and download it by ssh.

# Evasion techniques

## SSL Pinning

* **With Objection**:

Objection can be used with the default scripts.

```
objection --gadget com.example.app
com.example.app on (iPhone: 16.7.9) [usb] # ios sslpinning disable
```
* **With SSL Kill Switch 3**:

With the package SSL Kill Switch 3 we can bypass ssl pinning. It can be installed from any package manager.
Repo: `https://repo.misty.moe/apt`.

## Jailbreak Detection

* **With Shadow**:

With shadow some jailbreak detections can be bypassed.
Repo: `https://ios.jjolano.shadow`.


# Hooking 

## With Objection

Sometimes we can't bypass the defenses with default templates, so should find the method that make the check and hook it properly.

```
env
ios bundles list_bundles
ios bundles list_frameworks

ios keychain dump
ios info binary
ios nsurlcredentialstorage dump
ios nsuserdefaults get
ios cookie get

ios jailbreak disable
ios sslpinning disable

ios hooking list classes
ios hooking search classes <search>
ios hooking list class_methods <class_name>
ios hooking watch class <class_name>		# hook a class
ios hooking watch method "-[<class_name> <method_name>]" --dump-args --dump-return --dump-backtrace 		# hook single method
ios hooking set return_value "-[<class_name> <method_name>]" false 		# change boolean return
ios hooking generate simple <class_name> 		# generate a hooking template
```
## With frida

```
frida -l script.js -f com.example.app 		# basic hook
frida -U --no-pause -l script.js -f com.example.app 	# hook before starting the app
```

* **Python script**:

```
import frida, sys

jscode = open(sys.argv[0]).read()
process = frida.get_usb_device().attach('infosecadventures.fridademo')
script = process.create_script(jscode)
print('[ * ] Running Frida Demo application')
script.load()
sys.stdin.read()
```

# Installing a not signed ipa

We can only install ipas which are signed by a developer certificate. These certificates are expensive and there is a way to autosign it with a **validation of 7 days**.

* [https://sideloadly.io/](https://sideloadly.io/)

With `SideLoadly` we can sign with our icloud account the ipa and install it on our device while it's plugged via USB.

![sideloadly](/hackingnotes/images/sideloadly.png)

Once installed the following message will appear, because our developer account is not trusted.

![Developer not trusted](/hackingnotes/images/desarrollador_no_fiable.png)

Go to `Settings -> General -> VPN and device management`, click on the developer name and trust him.

* [https://support.apple.com/es-es/118254](https://support.apple.com/es-es/118254)

![Developer verification](/hackingnotes/images/developer_verification.png)


# Bypassing Flutter apps

## Jailbreak detection

We can use a frida script.

```
frida -l flutter-jb-bypass-ios.js -f com.example.app -U
```

* [https://github.com/CyberCX-STA/flutter-jailbreak-root-detection-bypass/blob/main/flutter-jb-bypass-ios.js](https://github.com/CyberCX-STA/flutter-jailbreak-root-detection-bypass/blob/main/flutter-jb-bypass-ios.js)


```js
Interceptor.attach(Module.findExportByName("IOSSecuritySuite", "$s16IOSSecuritySuiteAAC13amIJailbrokenSbyFZ"), {
  onEnter: function(args) {
    // Print out the function name and arguments
    console.log("$s16IOSSecuritySuiteAAC13amIJailbrokenSbyFZ has been called with arguments:");
    console.log("arg0: " + args[0] + " (context)");

    // Print out the call stack
    console.log("$s16IOSSecuritySuiteAAC13amIJailbrokenSbyFZ called from:\n" +
      Thread.backtrace(this.context, Backtracer.ACCURATE)
      .map(DebugSymbol.fromAddress).join("\n") + "\n");
  },
  onLeave: function(retval) {
    // Print out the return value
    console.log("$s16IOSSecuritySuiteAAC13amIJailbrokenSbyFZ returned: " + retval);
    console.log("Setting JB check results to False");
    // Set the return value to 0x0 (False)
    retval.replace(0x0);
  }
});
```

## SSL pinning detection

Since Flutter uses DART and is not using system proxy, we need to route our traffic to our burp with the help of a vpn.

Frist we need to install openvpn on our kali and create a profile

```
sudo wget https://git.io/vpn -O openvpn-install.sh
sudo sed -i "$(($(grep -ni "debian is too old" openvpn-install.sh | cut  -d : -f 1)+1))d" ./openvpn-install.sh
sudo chmod +x openvpn-install.sh
sudo ./openvpn-install.sh
````

```
Which IPv4 address should be used?  
> Select option of your system IP. i.e. 192.168.1.118
    
Public IPv4 address / hostname []:
> Provide your system IP i.e. 192.168.1.118
    
Protocol [1]: 1
Port [1194]: 1194
DNS server [1]: 1
Name [client]: flutter_pentest
```

The `fullter_pentest.ovpn` will be created on the actual folder, we just need to send it to our iphone via ssh or http.

Install `OpenVpn` client on iPhone and import the configuration file.

We also need to redirect the traffic from `tun0` to burp.

```
sudo iptables -t nat -A PREROUTING -i tun0 -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i tun0 -p tcp --dport 443 -j REDIRECT --to-port 8080
sudo iptables -t nat -A POSTROUTING -s 192.168.1.101/24 -o eth0 -j MASQUERADE
```

> **Note**: On the last command `192.168.1.101` is the iPhone IP.

Finally configure burp to bind on all interfaces or the tun0 interface and especify invisible proxying.

```
Proxy -> Proxy settings -> Edit -> Request handling -> Support invisible proxying (enable only if needed)
```

At that moment we can see HTTP traffic on burp, but we need to bypass ssl pinning.

We can use a modified version of this frida script.

* [https://github.com/NVISOsecurity/disable-flutter-tls-verification/blob/main/disable-flutter-tls.js](https://github.com/NVISOsecurity/disable-flutter-tls-verification/blob/main/disable-flutter-tls.js)

```js
var config = {
    "ios":{
        "modulename": "Flutter",
        "patterns":{
            "arm64": [
                // First pattern is actually for macos
                "FF 83 01 D1 FA 67 01 A9 F8 5F 02 A9 F6 57 03 A9 F4 4F 04 A9 FD 7B 05 A9 FD 43 01 91 F4 03 00 AA 68 31 00 F0 08 01 40 F9 08 01 40 F9 E8 07 00 F9",
                "FF 83 01 D1 FA 67 01 A9 F8 5F 02 A9 F6 57 03 A9 F4 4F 04 A9 FD 7B 05 A9 FD 43 01 91 F? 03 00 AA ?? 0? 40 F? ?8 ?? 40 F9 ?? ?? 4? F9 ?? 00 00",
                "FF 43 01 D1 F8 5F 01 A9 F6 57 02 A9 F4 4F 03 A9 FD 7B 04 A9 FD 03 01 91 F3 03 00 AA 14 00 40 F9 88 1A 40 F9 15 E9 40 F9 B5 00 00 B4 B6 46 40 F9"

            ],
        },
    }
};
console.log("[+] Pattern version: May 19 2025")
console.log("[+] Arch:", Process.arch)
console.log("[+] Platform: ", Process.platform)
// Flag to check if TLS validation has already been disabled
var TLSValidationDisabled = false;
var flutterLibraryFound = false;
var tries = 0;
var maxTries = 5;
var timeout = 1000;
var androidBypass = false;
disableTLSValidation();


// Main function to disable TLS validation for Flutter
function disableTLSValidation() {

    // Stop if ready
    if (TLSValidationDisabled) return;

    tries ++;
    if(tries > maxTries && !androidBypass){
        console.warn(`\n`)
        console.warn('[!] Flutter library not found. Possible reasons:');
        console.warn('[!] - The application does not use Flutter');
        console.warn('[!] - The application has not loaded the Flutter library yet');
        console.warn('[!] - You are using an emulator + gadget (https://github.com/NVISOsecurity/disable-flutter-tls-verification/issues/43)');
        console.warn('[!] The script will continue, but is likely to fail');
        console.warn(`\n`)
        androidBypass = true;
    }else{
        // No module found yet
        if(m == null){
            if(androidBypass){
                // But we are in bypass mode and are looking for the ssl_verify_peer_certy anyway
                console.log(`[ ] Locating ssl_verify_peer_cert (${tries}/${maxTries})`)
            }
            else{
                // Still looking for flutter lib
                console.log(`[ ] Locating Flutter library ${tries}/${maxTries}`);
            }
        }
        else
        {
            // Module has been located
            console.log(`[ ] Locating ssl_verify_peer_cert (${tries}/${maxTries})`)
        }
    }
    
    var platformConfig = {}
    platformConfig = config["ios"]

    var m = Process.findModuleByName(platformConfig["modulename"]);

    if (m === null && !androidBypass) {
        setTimeout(disableTLSValidation, timeout);
        return;
    }
    else{
        if(!androidBypass){
            console.log(`[+] Flutter library located`)
        }
        // reset counter so that searching for ssl_verify_peer_cert also gets x attempts
        if(flutterLibraryFound == false){
            flutterLibraryFound = true;
            tries = 0;
        }
    }

    if (Process.arch in platformConfig["patterns"])
    {
        var ranges;
        if(Java.available){
            // On Android, getting ranges from the loaded module is buggy, so we revert to Process.enumerateRanges
            ranges = Process.enumerateRanges({protection: 'r-x'}).filter(isFlutterRange)
        }else{
            // On iOS, there's no issue
            ranges = m.enumerateRanges('r-x')
        }

        findAndPatch(ranges, platformConfig["patterns"][Process.arch], Java.available && Process.arch == "arm" ? 1 : 0);
    }
    else
    {
        console.log('[!] Processor architecture not supported: ', Process.arch);
    }

    if (!TLSValidationDisabled)
    {        
        if (tries == maxTries)
        {
            if(androidBypass){
                console.warn(`\n`)
                console.warn(`[!] No function matching ssl_verify_peer_cert could be found.`)
                console.warn(`[!] If you are sure that the application is using Flutter, please open an issue:`)
                console.warn(`[!] https://github.com/NVISOsecurity/disable-flutter-tls-verification/issues`)
                console.warn(`\n`)
            }else{
                console.warn(`\n`)
                console.error(`[!] libFlutter was found, but ssl_verify_peer_cert could not be located`)
                console.error(`Please open an issue at https://github.com/NVISOsecurity/disable-flutter-tls-verification/issues`);
                console.warn(`\n`)
            }
            // Not really, but we give up
            TLSValidationDisabled = true
        }
    }
}

// Find and patch the method in memory to disable TLS validation
function findAndPatch(ranges, patterns, thumb) {
   
    ranges.forEach(range => {
        patterns.forEach(pattern => {
            var matches = Memory.scanSync(range.base, range.size, pattern);
            matches.forEach(match => {
                var info = DebugSymbol.fromAddress(match.address)
                if(info.name){
                    console.log(`[+] ssl_verify_peer_cert found at offset: ${info.name || match.address}`);
                }else{

                    console.log(`[+] ssl_verify_peer_cert found at location: ${match.address}`);
                }
                TLSValidationDisabled = true;
                hook_ssl_verify_peer_cert(match.address.add(thumb));
                console.log('[+] ssl_verify_peer_cert has been patched')
    
            });
            if(matches.length > 1){
                console.log('[!] Multiple matches detected. This can have a negative impact and may crash the app. Please open a ticket')
            }
        });
        
    });
    
    // Try again. disableTLSValidation will not do anything if TLSValidationDisabled = true
    setTimeout(disableTLSValidation, timeout);
}

function isFlutterRange(range){
    if(androidBypass) return true;

    var address = range.base
    var info = DebugSymbol.fromAddress(address)
    if(info.moduleName != null){
        if(info.moduleName.toLowerCase().includes("flutter")){
            return true;
        }
    }
    return false;
}

// Replace the target function's implementation to effectively disable the TLS check
function hook_ssl_verify_peer_cert(address) {
    Interceptor.replace(address, new NativeCallback((pathPtr, flags) => {
        return 0;
    }, 'int', ['pointer', 'int']));
}
````

# Static Analysis

## Binary Analysis

First, we need to download the ipa to our computer and install `llvm`.

* **Position Independent Executable (PIE)**: Output must have PIE.

```
$ llvm-otool-19 -h -v  Runner | grep PIE          
MH_MAGIC_64   ARM64        ALL  0x00     EXECUTE    81       9088   NOUNDEFS DYLDLINK TWOLEVEL BINDS_TO_WEAK PIE
```

* **Stack Smashing Protections**: Output must have `stack_chk_fail` and `stack_chk_guard`.

```
$ llvm-otool-19 -I -v  Runner | grep stack        
0x00000001000bafc4   265 ___stack_chk_fail
0x00000001000fc198   266 ___stack_chk_guard
```

* **Automatic Reference Counting (ARC)**: Output must have:

```
_objc_retain
_objc_release
_objc_storeStrong
_objc_releaseReturnValue
_objc_autoreleaseReturnValue
_objc_retainAutoreleaseReturnValue
```

```
$ llvm-otool-19 -I -v  Runner | grep _objc_           
0x00000001000bb21c   362 _objc_alloc
0x00000001000bb228   363 _objc_allocWithZone
0x00000001000bb234   364 _objc_alloc_init
0x00000001000bb240   365 _objc_autorelease
0x00000001000bb24c   366 _objc_autoreleasePool
```


# References:

* [https://medium.com/@shivayadav2820/unlocking-ios-a-comprehensive-guide-to-penetration-testing-on-apple-devices-2-5df8f4d72930](https://medium.com/@shivayadav2820/unlocking-ios-a-comprehensive-guide-to-penetration-testing-on-apple-devices-2-5df8f4d72930)
