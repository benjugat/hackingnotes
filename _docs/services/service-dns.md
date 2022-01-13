---
description: >-
  The Domain Name System (DNS) is the phonebook of the Internet. Humans access
  information online through domain names, like nytimes.com or espn.com.
---

# PORT 53/tcp/udp - DNS

## Introduction

In this section only will be shown the methodology to enumerate locally the DNS service. If you need to take a look of DNS enumeration vía internet, you will found in the following section.

{% content-ref url="../reconnaissance/information-gathering.md" %}
[information-gathering.md](../reconnaissance/information-gathering.md)
{% endcontent-ref %}

**DNS queries** produce listing calls Resource Records. This is a representation of Resource Records:

![Table of DNS Record Types](../.gitbook/assets/Understanding-Different-Types-of-Record-in-DNS-Server-2-1.png)

## Enumeration

First we will need to a Reverse DNS Lookup,

With **Reverse DNS Lookup**, we will receive the IP address associated to a given domain name.

```
# With nslookup
nslookup
> server IP_DNS_SERVER
> IP

# With dig
dig -x IP @IP_DNS_SERVER
```

There are usually two name servers. Take note of both of them an run the next command to show all A records:

```
nslookup -query=AXFR [Domain] [Nameserver]
dig axfr DOMAIN.LOCAL @IP_DNS_SERVER
```

Finally, just add the DNS records to you `/etc/hosts`.
