---
title: "Using Content Libraries in VMC to deploy software faster"
description: "Using VMware Cloud on AWS Content Libraries to deploy ISOs and OVAs to new SDDCs in minutes instead of hours. Setup, layout, and a working example."
date: 2026-01-27T22:19:39+00:00
modified: 2026-06-05T17:47:43+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - Homelab
  - Networking
  - Storage
  - Runecast
  - Ansible
  - Automation
  - Docker
  - Traefik
  - VCF
tags:
  - #Content Library
  - #VMC
  - #VMware
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/
image: https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash.png
---

![Firefly Gemini Flash](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# Using Content Libraries in VMC to deploy software faster

By[James](https://jameskilby.co.uk)January 27, 2026 · Updated June 5, 2026 • 📖5 min read(997 words)

📅**Published:** January 27, 2026•**Updated:** June 05, 2026

This post shows how I use Content Libraries in VMware Cloud on AWS (VMC) to deploy software to new SDDCs far faster. As part of my role spinning up new SDDC’s to test things is quite a common occurrence. This is both a blessing and a curse. The new SDDC is 100% Vanilla and perfectly self contained. Therefore you can do the testing required, knowing that you won’t impact anything else and you’re not inheriting a legacy setting from previous testing.

However the downside is you need to get the configuration and the software you require into the SDDC. This can take some time. For configuration it’s possible to use IAC tools like Terraform. To speed up the process of deploying software I decided to leverage Content Library specifically for this task. This is a much faster and more reliable way to get what I need into the SDDC.

William Lam has previously [written ](https://williamlam.com/2018/07/creating-a-vsphere-content-library-directly-on-amazon-s3.html#google_vignette)about ways of doing this by utilising AWS S3 as the backend

## Table of Contents

## Prerequisites

  * **On-premises vCenter** — a local vCenter instance to act as the publishing source. Any version supporting Content Library publish/subscribe (vSphere 6.0+) will work.
  * **VMware Cloud on AWS SDDC** — the destination environment. The subscribing Content Library is created here.
  * **Network connectivity between source and destination** — on-premises vCenter must be able to reach the VMC management network over HTTPS (TCP 443). Typically achieved via a Direct Connect or VPN connection to the VMC Management CIDR.
  * **Firewall rules** — outbound TCP 443 from on-prem vCenter to the VMC vCenter IP, and the reverse for subscription synchronisation. Check your NSX gateway firewall in the VMC SDDC.
  * **Storage capacity in VMC** — the Content Library occupies space on the VMC datastore. Factor in the size of your ISOs and OVF templates before enabling immediate sync.
  * **vCenter credentials** — a user account with the _Content Library > Create local library_ and _Content Library > Create subscribed library_ privileges on both vCenter instances.

## Introduction

For those unfamiliar with Content Libraries they are a storage medium for storing templates and ISO files for easy use within a vCentre environment or sharing with other vCentres. You can see some of the recent updates to this feature [here](https://blogs.vmware.com/cloud-foundation/2020/01/22/creating-and-using-content-library/)

## Networking

For this to work you need network connectivity between the source and destination vCentre. For my use case I use my on premises vCentre as the source and VMC as the destination. However you can use VMC as the source if preferable.

![Content Library Flow](https://jameskilby.co.uk/wp-content/uploads/2026/01/ContentLibraryFlow-1024x358.png)

Usually I don’t utilise/DX for this although it will absolutely work over those connections and would be purely private IP

I have a NAT rule on one of my public IP’s on my Onprem Watchguard Firewall to connect through to the Onprem vCentre. The URL of my vCentre will publicly resolve to this IP. I have restricted this connection to only allow from the public IP of the VMC vCentre. For the VMC vCentre there shouldn’t be any changes required as outbound https is allowed by default on the management gateway.

### Create Publishing Content Library

I already use content libraries extensively in my lab and didn’t need everything uploading to VMC. So I created a new Library just for this purpose and added some select software. If you don’t have a content library or need to create another one. These are the steps you will need to follow.

To create a new Library from the vSphere Client from the top menu select **Content Libraries**

![Content Libary](https://jameskilby.co.uk/wp-content/uploads/2026/01/ContentLibary-1024x368.png)

Name the Content Library appropriately and add a description.

![Name Location](https://jameskilby.co.uk/wp-content/uploads/2026/01/NameLocation-1024x440.png)

Configure the Content Library

As this will be the source Content Library we will set this to be a local content library and then enable the publishing feature to allow other vCentre’s to subscribe to this. I choose not to use authentication for this purpose as there is nothing sensitive 

![Configure Content Library](https://jameskilby.co.uk/wp-content/uploads/2026/01/ConfigureContentLibrary-1024x631.png)

The next step is to define what Datastore the Content Library will reside on.

Here I am using my datastore called “ISO” as it saves my valuable NVMe datastore for workloads.

![Select Storage](https://jameskilby.co.uk/wp-content/uploads/2026/01/Select-Storage-1024x481.png)

Ready to complete

![Ready To Complete](https://jameskilby.co.uk/wp-content/uploads/2026/01/ReadyToComplete-1024x507.png)

Complete the creation and then go back into the Content Library settings. It will show you a Subscription URL which we will need later. Take a copy of the full Subscription URL

![Complete With Url](https://jameskilby.co.uk/wp-content/uploads/2026/01/CompleteWithUrl-1024x558.png)

### Create Subscribing Content Library

We need to repeat the procedure in VMC however now we need to create a Subscribed Content Library. Input the URL that we saved earlier

<https://uk-bhr-p-vc-1.jameskilby.cloud:443/cls/vcsp/lib/165734dc-81a8-464a-bbe5-a99e4ae597da/lib.json>

![VMC Subscriber](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMCSubscriber-1024x906.png)

## Download content option

There are two options for how you want the Subscribed Content Library to behave on first connection/new content. The first is to synchronise the content as soon as possible. This is what I use. However if you have a large catalogue and not all items are required in the VMC vCentre an option to save storage would be to only download content on demand. The downside to this option is that deployment would take longer, waiting for the item to synchronise before it can be used. 

## Conclusion

Content Libraries are one of those VMware features that solve a real operational pain point without much ceremony. Once the publishing/subscribing relationship is established between your on-premises vCenter and VMC, getting ISOs and OVF templates into a fresh SDDC drops from a manual upload process to a few clicks — or nothing at all if you enable immediate synchronisation.

The main trade-off to consider is storage vs. speed. Immediate sync keeps everything local and ready to deploy instantly, but it consumes datastore space even for templates you may never use in a given SDDC. On-demand download is more storage-efficient and works well when you spin up SDDCs infrequently, though the first deployment of any template will wait for the download to complete. For testing environments where time matters, I lean towards immediate sync for the templates I know I’ll use frequently, and on-demand for everything else.

If you’re already using Content Libraries on-premises, adding VMC as a subscriber takes under ten minutes. If you’re not using them yet, this is a good reason to start.

## 📚 Related Posts

  * [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)
  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)
  * [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

## Similar Posts

  * [![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png)](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk)December 19, 2022 · Updated June 1, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png)](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk)September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png)](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk)August 14, 2025 · Updated June 5, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png)](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk)May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png)](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk)July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.

  * [![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png)](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk)April 10, 2026 · Updated June 1, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.