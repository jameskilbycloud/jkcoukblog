---
title: "Can you really squeeze 96TB in 1U ?"
description: "Yes, that’s a clickbait title."
date: 2024-09-12T12:39:16+00:00
modified: 2026-06-01T19:03:02+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - TrueNAS Scale
  - Networking
  - VMware
  - Artificial Intelligence
  - Automation
  - Docker
  - NVIDIA
  - Traefik
  - vSphere
  - Ansible
  - Containers
  - Devops
  - VCF
tags:
  - #Homelab
  - #Storage
url: https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/
image: https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

# Can you really squeeze 96TB in 1U ?

By[James](https://jameskilby.co.uk) September 12, 2024 · Updated June 1, 2026 • 📖4 min read(773 words)

📅 **Published:** September 12, 2024• **Updated:** June 01, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy…

I recently saw an advert for a server that was just too good to be true. It promised to bring a huge amount of storage and future options in a quite hard-to-believe 1U. The price it was on offer for was also unreal. I wasn’t looking for a new storage server but knew I would be able to make good use of this one. It would allow me to consolidate a few bits and pieces so it just had to be done…

## Table of Contents

## Intro

The server is a D51PH-1ULH from a vendor called [Quanta Cloud Technology](http://qct.io). They are a vendor that doesn’t seem to be very well known outside of the HyperScalers. It’s described as an Ultra dense storage server and with the capacity for 12×3.5″ plus 4×2.5″ drives it’s hard to argue with that. It also comes with IPMIv2.0 and 2x10Gb SFP+ connections. One really interesting thing is that at first glance the drives don’t look like they are hot-swap. However, the server comes with a giant hard drive tray that slides out the front and then individual drives can be swapped.

The seller also threw in a few 480GB Samsung Enterprise SSDs and 16x8TB Seagate Exos making it the bargain of the century. This allowed me to fully populate the chassis and still have 4 8TB drives spare. I typically don’t like using second-hand storage but in this instance, I was willing to make an exception.

![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/08/IMG_7063-744x1024.jpeg)Server shortly before being installed in my Rack

## OS Setup

I have stuck with TrueNAS Scale as the OS of choice for my dedicated storage systems. It’s something I’m familiar with and served my needs in the past well. However, I have decided to leave this as primarily a pure “Storage Server”. The available storage will be served out as a mixture of iSCSI, NFS, and SMB natively by TrueNAS and then I will run a MINIO container on top to offer S3-based object services.

## Hardware

I swapped out the 480GB Samsung drives for some larger 2TB consumer-based drives. The current configuration is listed below.

The servers also included rails which was a much appreciated benefit. The only downside is I underestimated just how long these servers are. The good news is I can adjust my Startech rack to make it longer and accommodate this. The downside is I need to derack the rest of my gear to do it. So for now it’s sitting on top of one of my other Supermicro servers.

CPU| 2x Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz  
---|---  
Memory | 256 DDR4  
Boot Device | 32 GB SATADom  
HDD | 12x ST8000NM0075 8TB 12Gb SAS  
SSD | 3x2TB Samsung Evo  
NIC | 2x 25Gb  
  
## Pool Configuration

For performance reasons, I have chosen to go with 6x Mirrored vDevs 2x wide. Conceptually this is similar to RAID 10. This uses all 12 of the 3.5-inch drives in a single pool. This gives a usable pool capacity of just under 43.5TB

Although I lose 50% of the usable capacity I wanted the write performance that this gives

This is then complemented by three 2TB SSDs being used as L2ARC (Read cache) and as I have so much read cache the drives basically just do writes.

## Performance

I haven’t bothered benchmarking the setup from a performance perspective as I have actual workloads on it that would be annoying to move. However, from what I am seeing in the latency graphs of vCenter I am happy with the results.

As you can see below the ARC is holding all of the really hot data in RAM.

![Can you really squeeze 96TB in 1U ? Screenshot](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-08-29-at-10.02.01.png)

The warm data is being served from the 6TB of SSD in the server, however it has not finished warming up yet. The L2ARC data can also be compressed so the reality is that it’s probably closer to the equivalent of 12TB.

![L2ARC Warming up](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-09-11-at-15.07.42-1024x203.png)L2ARC Warming up

A benefit of TrueNAS Scale is that the L2ARC persists between reboots. Otherwise, it would take a very long time to finish warming up with my workload.

This means the performance graphs of the actual disks tend to look like this. Only two are shown but all of the main drives appear like this. Yes, there are some reads (Blue) but the majority of the time they are only doing writes ( Pink) for the system.

![Can you really squeeze 96TB in 1U ? Screenshot](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-09-10-at-11.32.39-1024x513.png)

## Upgrades:

### SATADom

I have managed to source a compatible SATADom (32GB rather than the 128GB Partcode SD131C-032GM-JM-A) I was looking for. The migration of the TrueNAS install was super smooth.

### Networking

I have also upgraded the NIC to a Quanta ConnectX-4 LX Dual-Port 25GbE 

![s l1600 1](https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600-1-1024x537.jpg)

## 📚 Related Posts

  * [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)
  * [My First Homelab Storage Setup: HP Gen8 &#038; Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)
  * [Homelab Storage Upgrade: Synology DS918 for VMware &#038; NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

## Similar Posts

  * [ ![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png) ](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk) December 19, 2022 · Updated June 1, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [ ![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png) ](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk) June 26, 2024 · Updated June 1, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png) ](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk) December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk) February 9, 2026 · Updated June 1, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s