---
title: "MikroTik CRS504 Review: 100Gb/s Networking in My Homelab"
description: "For a while, I’ve been looking to update the networking at the core of my homelab."
date: 2022-12-19T10:09:58+00:00
modified: 2026-06-01T19:02:42+00:00
author: James Kilby
categories:
  - Homelab
  - Networking
  - Storage
  - VMware
  - Personal
  - vSphere
  - Synology
  - Automation
  - Github
  - VMware Cloud on AWS
tags:
  - #Homelab
  - #Mikrotik
url: https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/
image: https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res.png
---

![2157 Hi Res](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res.png)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# MikroTik CRS504 Review: 100Gb/s Networking in My Homelab

By[James](https://jameskilby.co.uk)December 19, 2022 · Updated June 1, 2026 • 📖2 min read(303 words)

📅**Published:** December 19, 2022•**Updated:** June 01, 2026

For a while, I’ve been looking to update the networking at the core of my homelab. I have had some great results with the current setup utilising a number of DACs but there were a couple of things that were annoying me. 

Then MikroTik dropped the [CRS504-4XQ-IN](https://mikrotik.com/product/crs504_4xq_in) and if the price wasn’t horrendous then that was the route I was going to go to alleviate these issues. Yes, it’s 100Gb/s and only has 4 ports but that should be all I need… I managed to locate one in stock for £587 plus VAT

![2157 Hi Res](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-1024x462.png)

As you can see the switch has redundant power not often found at this price point. It actually has 4 ways to power it. 2 AC supplies, a DC input and then strangest of all, it can be powered by PoE in. This last point showcases how power efficient it is which is a huge win for a homelab.

My plan is to utilise the existing Intel 25Gb NICs I have and split the 100’s on the switch into 4×25. This technically gives me 16 usable 25Gb ports which are way more than I need. This will allow me to accommodate the TrueNAS box and the 2x Supermicro nodes I usually run for my lab. The other 2 nodes will get an upgrade at a future date. 

Initial impressions are that the switch is very quiet and also incredibly power efficient. (It can be powered just from PoE). However, the config is way more complex than I have seen before. This is because it’s basically a router that can switch at wire speed. The other challenge I have had is connecting my legacy 1Gb/s network. This is still a work in progress but for now, Storage and vMotion have been migrated. 

I will report back when everything has been migrated.

## 📚 Related Posts

  * [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)
  * [Unleashing the Beast](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png)](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk)November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [My First Homelab Storage Setup: HP Gen8 & Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

By[James](https://jameskilby.co.uk)January 6, 2018 · Updated June 1, 2026

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below.

  * [![Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault-768x432.jpeg)](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

By[James](https://jameskilby.co.uk)January 11, 2022 · Updated June 1, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale.

  * [![Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/wp-content/uploads/2026/04/packer-github-actions-vsphere-pipeline-768x452.png)](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Github](https://jameskilby.co.uk/category/github/)

### [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

By[James](https://jameskilby.co.uk)April 30, 2026 · Updated June 5, 2026

A walk-through of an automated golden-image pipeline for vSphere: HashiCorp Packer builds six Ubuntu LTS templates (22.04, 24.04, 26.04 — server and desktop) driven by three GitHub Actions workflows covering PR validation, parallel template builds, and ISO management via a self-hosted runner.

  * [![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png)](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk)July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.

  * [![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png)](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk)September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.