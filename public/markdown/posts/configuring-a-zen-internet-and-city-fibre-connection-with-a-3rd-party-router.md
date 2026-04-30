---
title: "Configuring a Zen Internet and City Fibre connection with a 3rd party router"
description: "Back in July I bought a new house and one of the best things about the property was that it was already in a City Fibre location."
date: 2023-11-15T19:27:48+00:00
modified: 2026-04-16T22:01:48+00:00
author: James Kilby
categories:
  - Networking
  - Homelab
  - Storage
  - VMware
  - Mikrotik
tags:
  - #City Fibre
  - #VLAN911
  - #Watchguard
  - #Zen Internet
url: https://jameskilby.co.uk/2023/11/configuring-a-zen-internet-and-city-fibre-connection-with-a-3rd-party-router/
image: https://jameskilby.co.uk/wp-content/uploads/2023/11/cityfibre-zen-1024x538.jpg
---

![Cityfibre Zen](https://jameskilby.co.uk/wp-content/uploads/2023/11/cityfibre-zen.jpg)

[Networking](https://jameskilby.co.uk/category/networking/)

# Configuring a Zen Internet and City Fibre connection with a 3rd party router

By[James](https://jameskilby.co.uk)November 15, 2023April 16, 2026 • 📖2 min read(314 words)

📅 **Published:** November 15, 2023• **Updated:** April 16, 2026

Back in July I bought a new house and one of the best things about the property was that it was already in a City Fibre location. That meant I could take my Zen internet connection with me but ditch the ADSL (and Phone Line requirement). This gave me a much better connection in terms of throughput and latency at a lower overall cost.

I have seen a few people on Reddit etc. post about using third-party router/firewalls and struggling to get it working. This is my setup using my WatchGuard M200 and I believe that other City Fibre connections with other providers will be configured the same.

The first step is to create an Interface for the WatchGuard to use and set this to be a VLAN Interface as shown below.

![VLAN Interface](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-14-at-09.32.55.png)

The next step is to set up the VLAN interface

This is located in Networks>VLAN of the Web UI

Add a VLAN Interface and set the VLAN ID to 911 and set it to Tagged traffic

![Configuring a Zen Internet and City Fibre connection with a 3rd party router Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-14-at-19.38.42-1024x455.png)

When the security zone is defined as External three config options become available on the Network tab

![Configuring a Zen Internet and City Fibre connection with a 3rd party router Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-15-at-19.12.27-1024x932.png)

I have a /29 address range from Zen so I add my username and password to the network page together with the router IP. The router IP is the highest of the allocated range so in my case X.X.X.174

To utilise the other addresses allocated by Zen these are added to the secondary tab as /32’s

![Configuring a Zen Internet and City Fibre connection with a 3rd party router Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-15-at-19.22.11-1024x537.png)

And that’s all there is to it. With the above config, I have my 6 usable IP’s up and running.

One of the nice capabilities that the WatchGuard Firewall is it can monitor your interfaces (and make routing decisions if multiple connections are available)

I no longer use this feature as the single connection is reliable enough for my needs, but nonetheless the monitoring part is still useful.

![Configuring a Zen Internet and City Fibre connection with a 3rd party router Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-15-at-19.28.44-1024x503.png)

Example Route to Cloudflare 1.1.1.1

![Configuring a Zen Internet and City Fibre connection with a 3rd party router Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-15-at-19.30.15-1-1024x243.png)

## 📚 Related Posts

  * [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)
  * [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)
  * [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

## Similar Posts

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)

By[James](https://jameskilby.co.uk)January 6, 2022April 16, 2026

I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes.

  * [![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png)](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk)June 26, 2024March 10, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png)](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk)December 19, 2022April 16, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [![CRS-504](https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600-768x427.jpg)](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

[Mikrotik](https://jameskilby.co.uk/category/mikrotik/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

By[James](https://jameskilby.co.uk)September 9, 2024April 11, 2026

My journey to superfast networking in my homelab