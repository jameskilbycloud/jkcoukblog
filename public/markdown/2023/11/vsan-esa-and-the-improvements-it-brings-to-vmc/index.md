---
title: "vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24"
description: "vSAN ESA - Benefits Performance benefits Efficiency benefits Resilience Benefits Sizing vSAN Express Storage Architecture (ESA) was announced at VMware Exp"
date: 2023-11-17T11:29:42+00:00
modified: 2026-06-01T21:58:58+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - vSAN
  - Artificial Intelligence
  - Automation
  - Docker
  - Homelab
  - NVIDIA
  - Traefik
  - VCF
  - Ansible
  - Personal
tags:
  - #Storage
  - #VMware Cloud on AWS
  - #vSAN
  - #vSAN ESA
url: https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/
image: https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

# vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24

By[James](https://jameskilby.co.uk) November 17, 2023 · Updated June 1, 2026 • 📖4 min read(852 words)

📅**Published:** November 17, 2023•**Updated:** June 01, 2026

## Table of Contents

vSAN Express Storage Architecture (ESA) was announced at VMware Explore last year (2022) and while it’s been available for our on-premise customers for nearly a year it hasn’t been available in VMC until now… With the release of the M24 version of VMC, it is now an option for newly provisioned SDDCs

So why is this such an important change? To answer that we need a history lesson on vSAN

![Introducing ESA Figure01](https://jameskilby.co.uk/wp-content/uploads/2023/10/Introducing-ESA-Figure01-1024x422.png)

vSAN first came to market in 2014, and the typical hardware of the day from a storage perspective was dominated by spindles. Flash had arrived on the scene but was VERY expensive and datacenter networking was in the transition from 1Gb/s to 10Gb/s. As a result of this and other factors design decisions were made in the original vSAN (referred to here as OSA) to implement a tiered storage architecture. This was made up of flash-based cache drives and flash or hard disk-based capacity drives. These were then combined into something called a disk group. This decision led to several consequences.

The first is that the cache drive cannot be used for storing data it is only a transient write buffer. As all writes go to the cache drive in a disk group in some circumstances this could limit the peak I/O available. 

It also meant that the endurance of this drive was paramount. This was a challenge in the early days of flash drives. 

To improve performance and reduce failure domains it’s possible to have multiple disk groups within a host. This is something that we implement in VMC using vSAN OSA. This further compounds the reduction in usable storage, as multiple drives are allocated to the cache role.

As All-Flash has now become the normality it was worth revisiting the architecture. 

To understand more about the under-the-hood architecture of vSAN see the [official overview ](https://core.vmware.com/blog/introduction-vsan-express-storage-architecture)

## vSAN ESA – Benefits

Putting all of the above changes together brings significant benefits to VMC customers when using the ESA version of vSAN.

### Performance benefits

  * Significant increase in available IOPS ( all drives are used for reading and writing)
  * Adaptive write path for maximum throughput (Especially relevant for customers that require high throughput on a single or low number of VMDKs) 
  * Improved snapshot mechanisms reduce the impact on the guest workload (Snapshot deletion is up to 100x faster combined with much reduced primary latency when running workloads from snapshots.) As business demands lower RPO’s, any improvement in snapshot mechanisms reduce the overhead to the guest workload.

### Efficiency benefits 

  * Improved compression algorithms for better data reduction
  * More efficient compression algorithms free up the Host CPU for Guest OS processing
  * Reduced storage network traffic (compression happens on the source host and then all replication is already compressed)
  * Further enhancements reduce the CPU overhead when using vSAN Encryption (This is always used in VMC)
  * Always on [UNMAP/Trim](https://www.techtarget.com/searchstorage/definition/TRIM) (This helps to free up unused blocks at the Nand block level) 
  * The ability to deploy a parity-based (RAID5) with 3 Nodes. (OSA requires a minimum of 4)
  * The performance of the parity-based (RAID5/6) of the ESA implementation now exceeds the RAID1 performance of OSA. Customers can get increased savings by changing the storage policy.

### Resilience Benefits

  * fewer rewrites in the event of a device replacement – Although this is a significant benefit for on-premise customers with VMC if we have a drive failure we will replace the entire node. 

vSAN ESA will only be available on the i4.metal-based VMC hosts at launch. It is also not currently available in a 2-node or Stretched SDDC configuration…

## Sizing

As part of my job in VMware Cloud Pre-Sales a critical aspect is sizing VMC solutions for customers. This is usually done as a first pass with [RVtools](https://www.robware.net/rvtools/) inputs into our sizing tools. 

But what does that mean to a customer?

My colleague [Nikolay](https://nkulikov.com) put together this handy table. This is assuming a conservative compression ratio of 1.25x for ESA. The reality is we expect this to be higher.

**Nodes**| **OSA (Compression 1.25)  
Policy In use**| **Capacity (TiB)**| **ESA  
(Compression 1.25)  
Policy In use**| **Capacity (TiB)**| **Delta %**  
---|---|---|---|---|---  
2| FTT1, Mirror| 14.09| N/A| N/A| N/A  
3| FTT1, Mirror| 23.5| FTT1, RAID5| 37.22| 58.38  
4| FTT1, RAID5| 51.87| FTT1, RAID5| 51.21| -1.27*  
5| FTT1, RAID5| 66.03| FTT1, RAID5| 65.19| -1.27*  
6| FTT2, RAID6| 70.56| FTT2, RAID6| 79.18| 12.22  
7| FTT2, RAID6| 83.11| FTT2, RAID6| 93.16| 12.09  
8| FTT2, RAID6| 95.65| FTT2, RAID6| 107.15| 12.02  
9| FTT2, RAID6| 108.2| FTT2, RAID6| 121.13| 11.95  
10| FTT2, RAID6| 120.75| FTT2, RAID6| 135.12| 11.90  
11| FTT2, RAID6| 133.3| FTT2, RAID6| 149.1| 11.85  
12| FTT2, RAID6| 145.85| FTT2, RAID6| 163.09| 11.82  
13| FTT2, RAID6| 158.4| FTT2, RAID6| 177.08| 11.79  
14| FTT2, RAID6| 170.95| FTT2, RAID6| 191.06| 11.76  
15| FTT2, RAID6| 183.5| FTT2, RAID6| 205.05| 11.74  
16| FTT2, RAID6| 196.04| FTT2, RAID6| 219.03| 11.73  
  
*As ESA has a dynamic parity-based mechanism it can either use 2+1 or 4+1 however OSA has the capability of using 3+1. This is why the 4- and 5-node configurations have a lower usable space. 

The above table is the usable capacity for workloads including the management objects. Additional clusters would have more space.

## 📚 Related Posts

  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)
  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

## Similar Posts

  * [ ![vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

### [vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

By[James](https://jameskilby.co.uk) December 6, 2025 · Updated June 1, 2026

How to safely shut down a vSAN Environment

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk) March 27, 2026 · Updated May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [ ![VMware Holodeck Multi-Host VCF: Lab Setup & Configuration](https://jameskilby.co.uk/wp-content/uploads/2023/12/Holodeck-Overview.png) ](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/)

### [VMware Holodeck Multi-Host VCF: Lab Setup & Configuration](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/)

By[James](https://jameskilby.co.uk) January 17, 2024 · Updated June 1, 2026

How to Deploy VMware Holodeck on multiple hosts

  * [ ![Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash-768x417.png) ](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

By[James](https://jameskilby.co.uk) January 27, 2026 · Updated June 5, 2026

How to leverage Content Libraries to deploy into VMware Cloud on AWS faster.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png) ](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk) October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.