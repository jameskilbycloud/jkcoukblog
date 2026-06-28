---
title: "VMware Cloud on AWS Storage Sizing Quick Reference Guide"
description: "VMware Cloud on AWS storage sizing reference: usable TiB by host count for i3i, i3en, and i4i, plus the FTT/RAID policy used at each cluster size."
date: 2025-05-21T09:33:04+00:00
modified: 2026-06-24T10:40:08+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - Personal
  - vSAN
  - Homelab
  - Artificial Intelligence
  - Automation
  - Docker
  - NVIDIA
  - Traefik
  - AWS
  - Veeam
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

By[James](https://jameskilby.co.uk) May 21, 2025 · Updated June 24, 2026 • 📖3 min read(610 words)

📅**Published:** May 21, 2025•**Updated:** June 24, 2026

This VMware Cloud on AWS storage sizing guide is a quick reference for the usable storage you get per host, across i3i, i3en, and I4i clusters of 2 to 16 hosts. Use it to estimate capacity before you size a cluster, plan a host type change, or check how much usable space a given cluster size actually delivers once vSAN’s data protection overhead is accounted for.

For up to date info always use the official sizing tool located [here ](https://vmc.vmware.com/)

## VMware Cloud on AWS host types covered here

This guide covers the i3i, i3en, and I4i host types. For host specs and background, see [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/) and [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/). The newer I7i.metal-24xl host isn’t in the official sizing tool yet, so it’s listed in the table below without figures – see [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/) for what’s known so far.

## VMware Cloud on AWS storage sizing table (vSAN OSA, 2-16 hosts)

This is based on vSAN OSA and excludes the management overhead (i.e. valid for secondary clusters). It also uses the most efficient storage policy that is supported based on the number of hosts available.

Each row shows the usable capacity per host once vSAN’s storage policy overhead is applied, not raw disk capacity. Multiply by host count for a rough cluster total, then validate against the official sizing tool for your specific configuration.

**Host Type**| **i3** i| **i3en**| **I4i**| **I7i**|   
---|---|---|---|---|---  
**No of Hosts**|  i3 (TiB)| i3en (TiB)| I4i (TiB)| | FTT in use  
2| 11.2| 41.39| 18.48| | FTT1 RAID1  
3| 16.8| 62.09| 27.71| | FTT1 RAID1  
4| 33.68| 124.49| 55.57| | FTT1 RAID5  
5| 42.1| 155.61| 69.46| | FTT1 RAID5  
6| 44.8| 165.57| 73.9| | FTT2 RAID6  
7| 52.26| 193.17| 86.22| | FTT2 RAID6  
8| 59.73| 220.77| 98.54| | FTT2 RAID6  
9| 67.2| 248.36| 110.85| | FTT2 RAID6  
10| 74.66| 275.96| 123.17| | FTT2 RAID6  
11| 82.13| 303.55| 135.49| | FTT2 RAID6  
12| 89.6| 331.15| 147.8| | FTT2 RAID6  
13| 97.06| 358.74| 160.12| | FTT2 RAID6  
14| 104.53| 386.34| 172.44| | FTT2 RAID6  
15| 112| 413.94| 184.75| | FTT2 RAID6  
16| 119.46| 441.53| 197.07| | FTT2 RAID6  
  
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

  * [ ![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png) ](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk) October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [ ![vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

### [vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

By[James](https://jameskilby.co.uk) December 6, 2025 · Updated June 1, 2026

How to safely shut down a vSAN Environment

  * [ ![Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_4536-scaled-1-768x1024.jpg) ](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

By[James](https://jameskilby.co.uk) January 6, 2022 · Updated February 16, 2026

Quite a few changes have happened in the lab recently. I decided to do a multipart blog on the changes.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk) October 23, 2023 · Updated June 5, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [ ![Monitoring VMware Cloud on AWS: Tools & Approaches \(Part 1\)](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [AWS](https://jameskilby.co.uk/category/aws/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

### [Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

By[James](https://jameskilby.co.uk) December 17, 2019 · Updated June 5, 2026

As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring.