---
title: "MikroTik CRS504 Review: 100Gb/s Networking in My Homelab"
description: "For a while, I've been looking to update the networking at the core of my homelab."
date: 2022-12-19T10:09:58+00:00
modified: 2026-06-01T19:02:42+00:00
author: James Kilby
categories:
  - Homelab
  - Networking
  - Storage
  - VMware
  - vSAN
  - Nutanix
  - VMware Cloud on AWS
  - Personal
tags:
  - #Homelab
  - #Mikrotik
url: https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/
image: https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res.png)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# MikroTik CRS504 Review: 100Gb/s Networking in My Homelab

By[James Kilby](https://jameskilby.co.uk) December 19, 2022 · Updated June 1, 2026 • 📖2 min read(303 words)

For a while, I’ve been looking to update the networking at the core of my homelab. I have had some great results with the current setup utilising a number of DACs but there were a couple of things that were annoying me. 

Then MikroTik dropped the [CRS504-4XQ-IN](https://mikrotik.com/product/crs504_4xq_in) and if the price wasn’t horrendous then that was the route I was going to go to alleviate these issues. Yes, it’s 100Gb/s and only has 4 ports but that should be all I need… I managed to locate one in stock for £587 plus VAT

![2157 Hi Res](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-1024x462.png)

As you can see the switch has redundant power not often found at this price point. It actually has 4 ways to power it. 2 AC supplies, a DC input and then strangest of all, it can be powered by PoE in. This last point showcases how power efficient it is which is a huge win for a homelab.

My plan is to utilise the existing Intel 25Gb NICs I have and split the 100’s on the switch into 4×25. This technically gives me 16 usable 25Gb ports which are way more than I need. This will allow me to accommodate the TrueNAS box and the 2x Supermicro nodes I usually run for my lab. The other 2 nodes will get an upgrade at a future date. 

Initial impressions are that the switch is very quiet and also incredibly power efficient. (It can be powered just from PoE). However, the config is way more complex than I have seen before. This is because it’s basically a router that can switch at wire speed. The other challenge I have had is connecting my legacy 1Gb/s network. This is still a work in progress but for now, Storage and vMotion have been migrated. 

I will report back when everything has been migrated.

## 📚 Related Posts

  * [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)
  * [UniFi UDM Beast Review: My Homelab Firewall Upgrade](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)

By[James Kilby](https://jameskilby.co.uk) January 6, 2022 · Updated May 31, 2026

I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes.

  * [ ![vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

### [vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

By[James Kilby](https://jameskilby.co.uk) December 6, 2025 · Updated June 1, 2026

How to safely shut down a vSAN Environment

  * [ ![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg) ](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James Kilby](https://jameskilby.co.uk) July 2, 2024 · Updated July 11, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [ ![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James Kilby](https://jameskilby.co.uk) August 14, 2025 · Updated July 11, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![UniFi DHCP Option 43: Adopt Devices Across Subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png) ](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [UniFi DHCP Option 43: Adopt Devices Across Subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James Kilby](https://jameskilby.co.uk) June 26, 2024 · Updated November 13, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James Kilby](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.