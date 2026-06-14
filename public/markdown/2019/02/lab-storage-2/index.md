---
title: "Homelab Storage Upgrade: Synology DS918 for VMware & NFS"
description: "My homelab storage upgrade — adding a Synology DS918+ with SSDs, presenting it to VMware over NFS 4.1, and testing VAAI and NFS multipathing."
date: 2019-02-10T23:59:20+00:00
modified: 2026-06-05T19:12:06+00:00
author: James Kilby
categories:
  - Homelab
  - Artificial Intelligence
  - Docker
  - Ansible
  - Storage
  - vExpert
  - VMware
  - Automation
  - NVIDIA
  - Traefik
tags:
  - #Homelab
  - #Storage
  - #Synology
url: https://jameskilby.co.uk/2019/02/lab-storage-2/
image: https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_.jpg
---

![81 Zoew24Ul. Sl1500 ](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/)

# Homelab Storage Upgrade: Synology DS918 for VMware & NFS

By[James](https://jameskilby.co.uk)February 10, 2019 · Updated June 5, 2026 • 📖1 min read(224 words)

📅**Published:** February 10, 2019•**Updated:** June 05, 2026

## Homelab Storage Upgrade

This post covers my homelab storage upgrade. Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes. At the moment it’s very much focused on the VMware stack and one of the things I needed was some more storage and especially some more storage performance. With that in mind, I purchased a new [Synology DS918](https://www.synology.com)…

![Lab Storage](https://jameskilby.co.uk/wp-content/uploads/2023/04/iu-768x432-1.jpg)

It’s a very compact unit with a quad-core Intel Celeron & I have left the RAM at 4 GB for now.

I have added some of the existing SSDs I had, giving me about 3TB of usable flash. I am presenting this back to my VMware hosts using NFS 4.1. I must have missed the announcement as this is now built into the Synology GUI (it used to be a command-line-only option). I have verified the VAAI works as expected in this configuration. At present I am using this with a single network connection however I will be testing NFS Multipathing shortly.

The performance improvement has been noticeable and I have now removed all non-Synology systems from primary storage. This has left me with the DS918+ detailed here and a DS216+ with 2TB of Raid1 WD Reds. I am using this for ISOs and some general file storage. I later expanded the lab further with [new homelab nodes](https://jameskilby.co.uk/2024/07/new-nodes/).

## 📚 Related Posts

  * [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)
  * [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)
  * [My First Homelab Storage Setup: HP Gen8 &#038; Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

## Similar Posts

  * [![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg)](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk)October 11, 2024 · Updated June 1, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [![Wa](https://jameskilby.co.uk/wp-content/uploads/2025/04/210902461-012e7273-413a-4ec7-be44-e854347f5a21-768x180.png)](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Warp – The intelligent terminal](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

By[James](https://jameskilby.co.uk)April 11, 2025 · Updated June 1, 2026

How Warp is helping me run my homelab. 

  * [![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png)](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk)September 2, 2025 · Updated June 5, 2026

An intro on how I use SemaphoreUI to manage my Homelab

  * [![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png)](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk)April 17, 2023 · Updated June 1, 2026

I have been a VMware vExpert for many years and it has brought me many benefits over the years.

  * [![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg)](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk)October 23, 2023 · Updated June 5, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk)March 27, 2026 · Updated May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.