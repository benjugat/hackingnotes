---
title: Network
description: Network and service attacks: per-service notes (FTP, SSH, SMB, HTTP, DNS, etc.) and WiFi penetration testing (WEP, WPA/WPA2 PSK, WPA/WPA2 Enterprise).
---

# Network

Notes on attacking the network layer: per-service enumeration and
exploitation, plus WiFi-specific testing methodologies.

## Services

<div class="grid cards" markdown>

-   **[PORT 21/tcp - FTP](services/ftp.md)**

    ---

    File Transfer Protocol: anonymous logins, bounce attacks, brute force.

-   **[PORT 22/tcp - SSH](services/ssh.md)**

    ---

    Secure Shell: key-based auth, weak ciphers, libssh vulnerabilities.

-   **[PORT 25/tcp - SMTP](services/smtp.md)**

    ---

    Mail servers: user enumeration, open relay, spoofing.

-   **[PORT 53/tcp - DNS](services/dns.md)**

    ---

    DNS zone transfers, sub-domain brute force, cache poisoning.

-   **[PORT 80/tcp, 443/tcp - HTTP Server](services/http.md)**

    ---

    Web servers: virtual host enumeration, default credentials, known CVEs.

-   **[PORT 111/tcp - RPCBind](services/rpcbind.md)**

    ---

    RPC portmapper: NFS enumeration, RPC service discovery.

-   **[PORT 139/tcp, 445/tcp - SMB](services/smb.md)**

    ---

    SMB shares: null sessions, enum4linux, psexec, EternalBlue.

-   **[PORT 143/tcp, 993/tcp - IMAP](services/imap.md)**

    ---

    IMAP mail retrieval: brute force, pass-the-hash.

-   **[PORT 161/udp - SNMP](services/snmp.md)**

    ---

    SNMP community strings: public/private, info disclosure.

-   **[PORT 1100/tcp - Java RMI](services/java-rmi.md)**

    ---

    Java Remote Method Invocation: deserialization attacks.

-   **[PORT 1433/tcp - Microsoft SQL Server](services/sql-server.md)**

    ---

    MSSQL: authentication, xp_cmdshell, NTLM relay.

-   **[PORT 2049/tcp - NFS](services/nfs.md)**

    ---

    NFS shares: no_root_squash, file owner manipulation.

-   **[PORT 3306/tcp - MySQL Server](services/mysql.md)**

    ---

    MySQL: UDF, load_file, secure_file_priv bypass.

-   **[PORT 3389/tcp - RDP](services/rdp.md)**

    ---

    Remote Desktop: BlueKeep, NLA bypass, credential reuse.

</div>

## WiFi

<div class="grid cards" markdown>

-   **[Theory](hacking-wifi/theory.md)**

    ---

    WiFi fundamentals: 802.11 frames, encryption types, authentication modes.

-   **[WEP](hacking-wifi/wep.md)**

    ---

    Wired Equivalent Privacy: IV weakness, packet injection.

-   **[WPA/WPA2 PSK](hacking-wifi/wpa-wpa2-psk.md)**

    ---

    Pre-Shared Key: handshake capture, offline cracking, WPS attacks.

-   **[WPA/WPA2 Enterprise (PEAP)](hacking-wifi/wpa-wpa2-peap-enterprise.md)**

    ---

    Enterprise authentication: evil twin, credential harvesting.

</div>
