---
title: Active Directory
description: Active Directory attack and defense: enumeration, lateral movement, persistence, privilege escalation, cross-trust abuse and AD CS exploitation.
---

# Active Directory

Active Directory attack and defense: enumeration, lateral movement, persistence, privilege escalation, cross-trust abuse and AD CS exploitation.

## Contents

<div class="grid cards" markdown>

-   **[AD Attacks](ad-attacks.md)**

    ---

    Password spraying is an effective technique for discovering weak passwords that users are notorious for using. Patterns such as MonthYear (August2022), SeasonYear (Summer2022) and DayDate (Tuesday6) are very common.

-   **[Active Directory Certificate Services](ad-certificate-services.md)**

    ---

    Active Directory Certificate Services (AD CS) is a server role that allows you to build a public key infrastructure (PKI). Which can provide public key cryptography, digital certificates and digital signature capabiliti…

-   **[Cross Forest Attacks](cross-forest-attacks.md)**

    ---

    In this section we are going to abuse trusts between forests.

-   **[Domain Enumeration](domain-enumeration.md)**

    ---

    In order to obtain information about our target domain we need to enumerate it. There are several ways to enumerate the domain with some kali tools, but in this section we are going to use PowerShell and the .NET framew…

-   **[Domain Persistence](domain-persistence.md)**

    ---

    There is much more in Active Directory than just a Domain Admin. Once we have domain admin privileges new avenues of persistence, escalation to enterprise admin and attacks across trust appears.

-   **[Domain Privilege Escalation](domain-privesc.md)**

    ---

    Lets talk about some attacks to carry out a domain privilege escalation in order to obtain a Domain Controller.

-   **[Forest Persistence](forest-persistence.md)**

    ---

    We are going to discuss some ways to do a persistence in a forest root.

-   **[Basics](introduction.md)**

    ---

    1. Invoke-Mimikatz for dumping secrets. 2. Look for interesting internal files.

-   **[Lateral Movement](lateral-movement.md)**

    ---

    Once a machine is compromised, we need to jump to others in order to find more valuable targets. For that task we can use PowerShell Remoting which is increasingly used in enterprises and enabled by default on Server 20…

-   **[Hardening Active Directory](securing-ad.md)**

    ---

    In this section some detection, defense tools and security advisors are going to be discussed.

</div>
