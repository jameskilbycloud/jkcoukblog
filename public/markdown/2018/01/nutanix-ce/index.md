---
title: "Running Nutanix CE at Home: AHV Setup & First Impressions"
description: "I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to"
date: 2018-01-06T17:28:56+00:00
modified: 2026-06-01T21:58:18+00:00
author: James Kilby
categories:
  - Homelab
  - Nutanix
  - Networking
  - VMware
  - Personal
  - Automation
tags:
  - #Nutanix
url: https://jameskilby.co.uk/2018/01/nutanix-ce/
image: https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg
---

![Nutanix Logo Hi Rez Reverse W Carrier](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

# Running Nutanix CE at Home: AHV Setup & First Impressions

By[James](https://jameskilby.co.uk)January 6, 2018 · Updated June 1, 2026 • 📖1 min read(191 words)

📅**Published:** January 06, 2018•**Updated:** June 01, 2026

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home. This was compounded by the fact that I have many clusters to play with at work. These all run my Hypervisor of choice vSphere so I thought it was about time to see what was new with AHV and Nutanix CE….

I downloaded the latest copy of CE from the Nutanix site and extracted it to a USB stick with [Rufus.](https://rufus.akeo.ie/) (This took about 30 mins)

The server that I chose to run this on was the same server I ran initially, a Dell T20 with the Xeon processor 32GB of RAM 1x240GB SSD and 1x3TB WD Red. The installation is pretty straightforward and is covered a lot elsewhere.

I am just kicking the tyres with it at the moment and running a few VMs. I have also shared the storage from my Nutanix CE setup back to my vSphere environment.

I’ll post back with some updates of what I get up to with it

## 📚 Related Posts

  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [Passing the Nutanix NCP Exam: Free Training &#038; My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)
  * [Nutanix Command Reference Guide](https://jameskilby.co.uk/2018/06/nutanix-command-reference-guide/)

## Similar Posts

  * [![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png)](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk)June 26, 2024 · Updated June 5, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg)](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk)July 2, 2024 · Updated June 5, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast-768x219.webp)](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Unleashing the Beast](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

By[James](https://jameskilby.co.uk)June 20, 2026 · Updated June 21, 2026

Retiring my ageing WatchGuard M200, I swap in the UniFi UDM Beast — a hardware tour, first iperf and WAN tests, the BGP/FRR setup, and the homelab services I’m consolidating onto it.

  * [![Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

By[James](https://jameskilby.co.uk)July 2, 2020 · Updated May 31, 2026

I saw a tweet a couple of weeks ago mentioning that Nutanix were offering a free go at the Nutanix Certified Professional exam.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)

By[James](https://jameskilby.co.uk)January 6, 2022 · Updated May 31, 2026

I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes.

  * [![Template Deployment with Packer](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png)](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Template Deployment with Packer](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

By[James](https://jameskilby.co.uk)January 21, 2021 · Updated June 5, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while.