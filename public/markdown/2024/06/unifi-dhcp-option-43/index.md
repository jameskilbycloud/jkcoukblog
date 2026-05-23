---
title: "Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets"
description: "Configure DHCP Option 43 so UniFi APs and switches auto-adopt across subnets. Includes the hex converter, OPNsense + Mikrotik examples, and a UDM guide."
date: 2024-06-26T10:50:17+00:00
modified: 2026-05-23T09:46:27+00:00
author: James Kilby
categories:
  - Homelab
  - Networking
  - Storage
  - TrueNAS Scale
  - VMware
  - Veeam
  - vExpert
tags:
  - #DHCP
  - #Option 43
  - #Unifi
url: https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/
image: https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-1024x683.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_.png)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

# Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets

By[James](https://jameskilby.co.uk) June 26, 2024May 23, 2026 • 📖1 min read(270 words)

📅 **Published:** June 26, 2024• **Updated:** May 23, 2026

## Table of Contents

## Intro

I have recently juggled some of my homelab services around, which involved moving my UniFi server to a different subnet. This meant that new UniFi devices could not find the UniFi server for adoption/control purposes as this is usually done with broadcast.

## Layer 3 Adoption Options

For Remote Adoption/Layer 3 UniFi supports:

  * SSH
  * DNS
  * DHCP Option 43

I discounted SSH as who wants to manually log into things and make changes and I discounted DNS. That left me with DHCP option 43

I decided to configure my DHCP server to hand out “option 43” on the network subnet the Access Points were connected to. The implementation of this will differ depending on what DHCP server you are using. Mine is the one built into my WatchGuard Firebox M200.

In this, I have set a custom option and then it asks for four values:

Code| 43  
---|---  
Name | Unifi  
Type | Hexadecimal  
Value | 01:04:c0:a8:14:02  
  
All of which are straightforward except the last one so let me explain. It is made up of 2 parts

The first two parts 01:04 Is fixed for UniFi. I am hosting the controller on IP 192.168.20.2 The remaining part of the value (c0:a8:14:02) is the IP address of the UniFi controller in Hex. Please note this method does not support DNS.

A multitude of tools exist for converting IP to HEX one can be found [here](https://www.browserling.com/tools/ip-to-hex)

And there you have it. I can connect a factory fresh UniFi device to my network DHCP will hand out an IP on one subnet and tell the device how to reach the controller in a different subnet.

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

## Similar Posts

  * [ ![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png) ](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James](https://jameskilby.co.uk) September 12, 2024April 16, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.

  * [ ![Configuring a Zen Internet and City Fibre connection with a 3rd party router](https://jameskilby.co.uk/wp-content/uploads/2023/11/cityfibre-zen-768x403.jpg) ](https://jameskilby.co.uk/2023/11/configuring-a-zen-internet-and-city-fibre-connection-with-a-3rd-party-router/)

[Networking](https://jameskilby.co.uk/category/networking/)

### [Configuring a Zen Internet and City Fibre connection with a 3rd party router](https://jameskilby.co.uk/2023/11/configuring-a-zen-internet-and-city-fibre-connection-with-a-3rd-party-router/)

By[James](https://jameskilby.co.uk) November 15, 2023April 16, 2026

Back in July I bought a new house and one of the best things about the property was that it was already in a City Fibre location.

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk) October 23, 2023April 16, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [ ![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg) ](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James](https://jameskilby.co.uk) February 10, 2019April 16, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Lab Update – Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

By[James](https://jameskilby.co.uk) January 6, 2022April 16, 2026

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things.

  * [ ![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png) ](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk) April 17, 2023April 16, 2026

I have been a VMware vExpert for many years and it has brought me many many benefits over the years.