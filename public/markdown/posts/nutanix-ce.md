---
title: "Running Nutanix CE at Home: AHV Setup & First Impressions"
description: "I ran a Nutanix CE server at home for a little while when it first came out."
date: 2018-01-06T17:28:56+00:00
modified: 2026-06-01T21:58:18+00:00
author: James Kilby
categories:
  - Homelab
  - Nutanix
  - Storage
  - Hosting
  - Networking
  - VMware
  - Synology
  - Docker
  - Kubernetes
  - TrueNAS Scale
tags:
  - #Nutanix
url: https://jameskilby.co.uk/2018/01/nutanix-ce/
image: https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

# Running Nutanix CE at Home: AHV Setup & First Impressions

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026 • 📖1 min read(191 words)

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

  * [ ![TrueNAS Logo](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2023-05-22-at-18.49.21-768x198.png) ](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Homelab Storage Refresh (Part 1)](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

By[James](https://jameskilby.co.uk) May 23, 2023 · Updated June 1, 2026

Table of Contents Background ZFS Overview Read Cache (ARC and L2ARC) ZIL (ZFS Intent Log) Hardware Background I have just completed the move of all my production and media-based storage/services to TrueNAS Scale. ( I will just refer to this as TrueNAS) This is based on my HP Z840 and I have now retired my…

  * [ ![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg) ](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk) October 11, 2022 · Updated June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [ ![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png) ](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk) December 19, 2022 · Updated June 1, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [ ![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg) ](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk) November 21, 2022 · Updated June 1, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [ ![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png) ](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk) December 9, 2022 · Updated June 5, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….

  * [ ![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png) ](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James](https://jameskilby.co.uk) September 12, 2024 · Updated June 1, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.