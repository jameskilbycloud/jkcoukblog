---
title: "VMware Cloud on AWS Storage Sizing Quick Reference Guide"
description: "VMware Cloud on AWS storage sizing reference: usable TiB by host count for i3i, i3en, and i4i, plus the FTT/RAID policy used at each cluster size."
date: 2025-05-21T09:33:04+00:00
modified: 2026-07-11T08:02:12+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - VCF
  - vSAN
  - Runecast
  - Artificial Intelligence
  - Automation
tags:
  - #Sizing
  - #VMC
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/
image: https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# VMware Cloud on AWS Storage Sizing Quick Reference Guide

By[James](https://jameskilby.co.uk) May 21, 2025 · Updated July 11, 2026 • 📖4 min read(750 words)

This VMware Cloud on AWS storage sizing guide is a quick reference for the usable storage you get per host, across i3, i3en, and I4i clusters of 2 to 16 hosts. Use it to estimate capacity before you size a cluster, plan a host type change, or check how much usable space a given cluster size actually delivers once vSAN’s data protection overhead is accounted for.

For up to date info always use the official sizing tool located [here ](https://vmc.vmware.com/)

## VMware Cloud on AWS host types covered here

This guide covers the i3, i3en, and I4i host types. For host specs and background, see [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/) and [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/). The newer I7i.metal-24xl host isn’t in the official sizing tool yet, so it’s listed in the table below – see [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/) for what’s known so far.

## VMware Cloud on AWS storage sizing table (vSAN OSA, 2-16 hosts)

This is based on vSAN OSA and excludes the management overhead (i.e. valid for secondary clusters). It also uses the most efficient storage policy that is supported based on the number of hosts available.

Each row shows the usable capacity per host once vSAN’s storage policy overhead is applied, not raw disk capacity. Multiply by host count for a rough cluster total, then validate against the official sizing tool for your specific configuration.

**Host Type**| **i3**| **i3en**| **I4i**| **i7i.metal-24xl**|   
---|---|---|---|---|---  
**No of Hosts**|  TiB Available| TiB Available| TiB Available | TiB Available| FTT in use  
2| 11.2| 41.39| 18.48| 12.28| FTT1 RAID1  
3| 16.8| 62.09| 27.71| 18.41| FTT1 RAID1  
4| 33.68| 124.49| 55.57| | FTT1 RAID5  
5| 42.1| 155.61| 69.46| | FTT1 RAID5  
6| 44.8| 165.57| 73.9| 49.11| FTT2 RAID6  
7| 52.26| 193.17| 86.22| 57.29| FTT2 RAID6  
8| 59.73| 220.77| 98.54| 65.47| FTT2 RAID6  
9| 67.2| 248.36| 110.85| 73.66| FTT2 RAID6  
10| 74.66| 275.96| 123.17| 81.84| FTT2 RAID6  
11| 82.13| 303.55| 135.49| 90.03| FTT2 RAID6  
12| 89.6| 331.15| 147.8| 98.21| FTT2 RAID6  
13| 97.06| 358.74| 160.12| 106.4| FTT2 RAID6  
14| 104.53| 386.34| 172.44| 114.58| FTT2 RAID6  
15| 112| 413.94| 184.75| 122.77| FTT2 RAID6  
16| 119.46| 441.53| 197.07| 130.95| FTT2 RAID6  
  
## VMware Cloud on AWS storage sizing table (vSAN ESA, 2-16 hosts)

| I4i| **i7i.metal-24xl**|  FTT in use  
---|---|---|---  
**No of Hosts**|  TiB Available| TiB Available|   
2| 20.98| 18.41| FTT: 1, RAID: 1  
3| 41.96| 36.83| FTT: 1, RAID: 5  
4| 55.94| 49.1| FTT: 1, RAID: 5  
5| 69.93| 61.38| FTT: 1, RAID: 5  
6| 83.91| 73.66| FTT: 2, RAID: 6  
7| 97.90| 85.93| FTT: 2, RAID: 6  
8| 111.88| 98.21| FTT: 2, RAID: 6  
9| 125.87| 110.48| FTT: 2, RAID: 6  
10| 139.86| 122.76| FTT: 2, RAID: 6  
11| 153.84| 135.04| FTT: 2, RAID: 6  
12| 167.83| 147.31| FTT: 2, RAID: 6  
13| 181.81| 159.59| FTT: 2, RAID: 6  
14| 195.8| 171.86| FTT: 2, RAID: 6  
15| 209.78| 184.14| FTT: 2, RAID: 6  
16| 223.77| 196.42| FTT: 2, RAID: 6  
  
## How FTT and RAID policy affect VMware Cloud on AWS storage sizing

vSAN raises its data protection policy as the cluster grows, which is why usable capacity above doesn’t scale in a straight line. At 2-3 hosts, only FTT1 with RAID-1 mirroring is available – it tolerates one failure but costs more capacity. At 4-5 hosts, FTT1 with RAID-5 erasure coding kicks in, improving efficiency. From 6 hosts up, vSAN moves to FTT2 with RAID-6, tolerating two simultaneous failures while keeping reasonable efficiency at scale.

In practice, usable capacity per host is highest right at the top of each policy band. If your workload allows it, sizing for 4 or 5 hosts rather than 3, or 6 or more rather than 5, gets you more usable storage for the same policy.

## Cluster conversions and management overhead

If you are planning to do a cluster conversion between host types then the management stack size doesn’t change.

What does change is usable capacity at each cluster size, since host types differ in raw capacity per disk group. Re-check the table above for the new host type before committing to a conversion.

## vSAN ESA storage sizing in VMware Cloud on AWS

VMware Cloud on AWS also supports vSAN ESA (Express Storage Architecture), which changes the storage efficiency math compared to the OSA table above. For what changed and why it matters, see [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/). A full vSAN ESA storage sizing table for 2-16 hosts, matching the format above, is coming soon.

## 📚 Related Posts

  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)
  * [VMware Cloud on AWS i3en Host: Specs, Storage &#038; Performance](https://jameskilby.co.uk/2020/07/i3en/)

## Similar Posts

  * [ ![VMware Holodeck Multi-Host VCF: Lab Setup & Configuration](https://jameskilby.co.uk/wp-content/uploads/2023/12/Holodeck-Overview.png) ](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/)

### [VMware Holodeck Multi-Host VCF: Lab Setup & Configuration](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/)

By[James](https://jameskilby.co.uk) January 17, 2024 · Updated June 1, 2026

How to Deploy VMware Holodeck on multiple hosts

  * [ ![vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

### [vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

By[James](https://jameskilby.co.uk) December 6, 2025 · Updated June 1, 2026

How to safely shut down a vSAN Environment

  * [ ![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png) ](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [ ![vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

By[James](https://jameskilby.co.uk) November 17, 2023 · Updated June 1, 2026

An Overview of vSAN ESA in VMC 

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated July 11, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.