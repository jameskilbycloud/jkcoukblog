---
title: "Running Nutanix CE at Home: AHV Setup & First Impressions"
description: "I ran a Nutanix CE server at home for a little while when it first came out."
date: 2018-01-06T17:28:56+00:00
modified: 2026-06-01T21:58:18+00:00
author: James Kilby
categories:
  - Homelab
  - Nutanix
  - VMware
  - Storage
  - Ansible
  - Artificial Intelligence
  - Automation
tags:
  - #Nutanix
url: https://jameskilby.co.uk/2018/01/nutanix-ce/
image: https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg
---

![Nutanix logo](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

# Running Nutanix CE at Home: AHV Setup & First Impressions

By[James Kilby](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026 • 📖1 min read(191 words)

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

  * [ ![SuperMicro BigTwin node removed from its chassis](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_4536-scaled-1-768x1024.jpg) ](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

By[James Kilby](https://jameskilby.co.uk) January 6, 2022 · Updated February 16, 2026

Quite a few changes have happened in the lab recently. I decided to do a multipart blog on the changes.

  * [ ![TrueNAS Logo](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2023-05-22-at-18.49.21-768x198.png) ](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Homelab Storage Refresh (Part 1)](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

By[James Kilby](https://jameskilby.co.uk) May 23, 2023 · Updated November 16, 2026

Table of Contents Background ZFS Overview Read Cache (ARC and L2ARC) ZIL (ZFS Intent Log) Hardware Background I have just completed the move of all my production and media-based storage/services to TrueNAS Scale. ( I will just refer to this as TrueNAS) This is based on my HP Z840 and I have now retired my…

  * [ ![NVIDIA and VMware logos](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James Kilby](https://jameskilby.co.uk) February 9, 2026 · Updated November 17, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James Kilby](https://jameskilby.co.uk) April 4, 2026 · Updated November 17, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Front of a Nutanix-branded SuperMicro BigTwin chassis](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg) ](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James Kilby](https://jameskilby.co.uk) July 2, 2024 · Updated November 16, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [ ![HashiCorp Packer logo](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png) ](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Template Deployment with Packer](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

By[James Kilby](https://jameskilby.co.uk) January 21, 2021 · Updated June 5, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while.