---
title: "My First Homelab Storage Setup: HP Gen8 & Xpenology"
description: "I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it's as below."
date: 2018-01-06T17:39:20+00:00
modified: 2026-06-01T21:58:16+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - Synology
  - Ansible
  - Artificial Intelligence
  - Networking
  - Automation
tags:
  - #Homelab
  - #Storage
url: https://jameskilby.co.uk/2018/01/lab-storage/
image: https://jameskilby.co.uk/wp-content/uploads/2025/12/ChatGPT-Image-Dec-17-2025-at-09_03_10-PM.png
---

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

# My First Homelab Storage Setup: HP Gen8 & Xpenology

By[James Kilby](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026 • 📖1 min read(197 words)

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below. I will add some pics when I have tidied up the lab/cables….

My primary lab storage is all contained within an HP Gen8 Microserver.

Currently Configured:

1x INTEL Core i3-4130 running at 2.3Ghz

16Gb of RAM

4x 1Gb/s NIC

2x 3TB WD Red

2x Intel SSD 320 Series 80GB, 25nm MLC

This is running Xpenology.

I have the 4 Nics split into two LACP bonds. One for the management traffic and one for pure NFS traffic.

The 2x WD Reds are in an SHR configuration with the SSDs running as an SSD read-write cache.

This gives me 2.6TB useable which is plenty to lab and store photos and media and with the RW cache, the perf is pretty damn good.

I also have a DS216+II Synology with 2x 2TB WD Red’s this is my tier 2 lab storage, for backups ISO’s etc

I am running a few apps/containers on the Xpenology install as it has a lot more ram/processing power.

At the moment this consists of:

Docker – GitLab

Docker – PHPipam

Plex

## 📚 Related Posts

  * [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)
  * [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)
  * [Homelab Storage Upgrade: Synology DS918 for VMware &#038; NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

## Similar Posts

  * [ ![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png) ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James Kilby](https://jameskilby.co.uk) September 2, 2025 · Updated June 5, 2026

An intro on how I use SemaphoreUI to manage my Homelab

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James Kilby](https://jameskilby.co.uk) February 9, 2026 · Updated October 19, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png) ](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James Kilby](https://jameskilby.co.uk) April 17, 2023 · Updated October 19, 2026

I have been a VMware vExpert for many years and it has brought me many benefits over the years.

  * [ ![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg) ](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James Kilby](https://jameskilby.co.uk) February 10, 2019 · Updated June 5, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)

By[James Kilby](https://jameskilby.co.uk) January 6, 2022 · Updated May 31, 2026

I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James Kilby](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.