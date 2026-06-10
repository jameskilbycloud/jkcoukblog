---
title: "Home Network Upgrade to 25Gb/s with MikroTik Switching"
description: "My home network upgrade to 25Gb/s: MikroTik CRS504 switching, DACs, optics, and the gotchas I hit going beyond 10Gb at home."
date: 2024-09-09T08:25:08+00:00
modified: 2026-06-05T18:49:23+00:00
author: James Kilby
categories:
  - Mikrotik
  - Networking
  - Artificial Intelligence
  - Docker
  - Homelab
  - Ansible
  - Containers
  - Devops
  - NVIDIA
  - Traefik
  - VMware
  - Storage
  - TrueNAS Scale
  - VCF
  - Automation
tags:
  - #Homelab
  - #Mikrotik
  - #Networking
url: https://jameskilby.co.uk/2024/09/home-network-upgrade/
image: https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600.jpg
---

![CRS-504](https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600.jpg)

[Mikrotik](https://jameskilby.co.uk/category/mikrotik/) | [Networking](https://jameskilby.co.uk/category/networking/)

# Home Network Upgrade to 25Gb/s with MikroTik Switching

By[James](https://jameskilby.co.uk) September 9, 2024 · Updated June 5, 2026 • 📖2 min read(475 words)

📅**Published:** September 09, 2024•**Updated:** June 05, 2026

I have recently moved over to Mikrotik Switching for all of my Home environment as part of my home network upgrade. What started life as a move away from gigabit networking had some serious scope creep. As I needed new switches, network adaptors and cabling I evaluated the obvious choice of just upgrading to 10Gb/s. However, when looking at the price comparison to upgrade to 25Gb/s I felt the cost uplift was justified and certainly better future-proofed. This became the baseline for the majority of my server workloads. The Access switch layer has basically stayed gigabit but with 10Gb/s uplinks. This followed on from my recent [homelab compute upgrade](https://jameskilby.co.uk/2024/07/new-nodes/).

## Table of Contents

## Why I Did This Home Network Upgrade

The decision to go to Mikrotik was predominantly based on the huge performance available for limited costs. So far I have been impressed with the switches once I got over the initial steep learning curve of RouterOS. I have purchased several switches spread out over a few months. This coincided with a property move so some extras were bought to accommodate the new layout. In the property, my lab was relocated to a dedicated space and I also wanted wired connectivity into my office.

## Switches Purchased

Number| Model| £Price | Function| OS  
---|---|---|---|---  
1| [CRS504_4XQ](https://mikrotik.com/product/crs504_4xq_in)| 704.40| Core Switch| RouterOS  
1|   
[CRS305-1G-4S+IN](https://mikrotik.com/product/crs305_1g_4s_in)| 131.15| Breakout Switch| RouterOS  
2| [CSS610-8P-2S+IN](https://mikrotik.com/product/css610_8p_2s_in)| 193.46| House and Office Switch| SwitchOS Lite  
1|   
[CSS610-8G-2S+](https://mikrotik.com/product/css610_8g_2s_in)| 183.87| OOB Switch| SwitchOS Lite  
Total| | 1406.34| |   
  
The 100Gb/s Switch is effectively my core switch. It only has 4 physical ports however each of these can be split into 4x25gb/s or slower ports if needed. In the current state all 4 ports are used, however I do have 3 remaining breakouts available if needed.

I have then used the 5-Port 10 Gb/s switch sort of as a media translator for connections to the access switches around the house with 10Gb uplinks to distribute the network around the home and present ethernet ports to my devices.

![Network Overview](https://jameskilby.co.uk/wp-content/uploads/2025/01/Home-Net-overview-1024x633.png)

## Configuring the MikroTik Switches

Mikrotik Switches can typically run one of two operating systems either RouterOS or SwitchOS. (The 3 ethernet port switches will only run SwOS)

SwitchOS is a much simpler setup and is similar to a web-managed switch from other manufacturers. It’s a trivial setup for anyone that’s used a web-managed switch before. 

The config for these switches takes a little bit of time to get familiar with as they are incredibly powerful. It’s possible to run RouterOS or SwitchOS on them however I could never get SwitchOS to boot correctly on the 100Gb/s switch so I stuck with RouterOS and persevered through the config. Part 2 will go into my RouterOS setup.

I have a draft post of the steps I have used to get RouterOS configured how I like. I will try and finish that off when I get some more time.

## 📚 Related Posts

  * [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)
  * [Homelab Network Upgrade: DACs, 40Gb/s vMotion &#038; pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)
  * [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

## Similar Posts

  * [ ![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg) ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk) October 11, 2024 · Updated June 1, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk) February 9, 2026 · Updated June 5, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png) ](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James](https://jameskilby.co.uk) September 12, 2024 · Updated June 1, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png) ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk) September 2, 2025 · Updated June 5, 2026

An intro on how I use SemaphoreUI to manage my Homelab