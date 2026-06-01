---
title: "Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense"
description: "I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes."
date: 2022-01-06T19:25:40+00:00
modified: 2026-05-31T11:36:27+00:00
author: James Kilby
categories:
  - Homelab
  - Networking
  - Hosting
  - Ansible
  - Storage
  - VMware
  - Artificial Intelligence
  - Containers
  - Devops
  - NVIDIA
  - Traefik
tags:
  - #Homelab
  - #Networking
url: https://jameskilby.co.uk/2022/01/lab-update-part-3-network/
image: https://jameskilby.co.uk/wp-content/uploads/2025/12/ChatGPT-Image-Dec-17-2025-at-09_03_10-PM.png
---

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

# Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense

By[James](https://jameskilby.co.uk) January 6, 2022May 31, 2026 • 📖1 min read(113 words)

📅 **Published:** January 06, 2022• **Updated:** May 31, 2026

I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes. I will likely virtualise this in the future.

In terms of network/switching I have moved to an intermediate step here. vMotion and Storage are running over DAC’s while VMware management and VM traffic is still over 1Gb/s networking. This is working incredibly well. Due to the onboard network cards I am able to vMotion at 40Gb/s which for a home lab is game-changing. Storage is currently over 25Gb/s and the long-term plan is to get a 25Gb/s switch. The contenders at the moment are a Used Dell enterprise switch or possibly a QNAP box.

## 📚 Related Posts

  * [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)
  * [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [ ![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg) ](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk) October 11, 2022June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [ ![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png) ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk) September 2, 2025June 1, 2026

An intro on how I use SemaphoreUI to manage my Homelab

  * [ ![Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault-768x432.jpeg) ](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

By[James](https://jameskilby.co.uk) January 11, 2022June 1, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale.

  * [ ![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png) ](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk) December 19, 2022June 1, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk) February 9, 2026June 1, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg) ](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James](https://jameskilby.co.uk) February 10, 2019June 1, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.