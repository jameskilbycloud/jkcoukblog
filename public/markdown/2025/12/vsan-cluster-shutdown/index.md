---
title: "vSAN Cluster Shutdown – Orchestration"
description: "As can be seen on my Lab Overview page. I have a GPU/Management cluster that is usually running 24x7."
date: 2025-12-06T10:59:14+00:00
modified: 2026-06-01T21:07:13+00:00
author: James Kilby
categories:
  - VMware
  - vSAN
  - VMware Cloud on AWS
  - Personal
  - Ansible
  - Automation
  - Artificial Intelligence
  - VCF
url: https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/
image: https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

# vSAN Cluster Shutdown – Orchestration

By[James](https://jameskilby.co.uk) December 6, 2025 · Updated June 1, 2026 • 📖1 min read(112 words)

**Published:** December 06, 2025•**Updated:** June 01, 2026

As can be seen on my Lab Overview page, I have a GPU/Management cluster that is usually running 24×7. I also have a 3x Node vSAN cluster that I use when I need more resources (or specifically if I need vSAN to test with)

This allows me to 

See the overview below

![V Sphere Overview](https://jameskilby.co.uk/wp-content/uploads/2024/12/vSphere-Overview-1024x530.png)

To shut down a vSAN cluster, there is a nice workflow built into vCenter that will orchestrate all the required actions for you

![V SAN Services Menu](https://jameskilby.co.uk/wp-content/uploads/2025/04/vSAN-Services-Menu-1024x564.png)

![Shutdown Precheck](https://jameskilby.co.uk/wp-content/uploads/2025/04/Shutdown-Precheck.png)

![Confirmation](https://jameskilby.co.uk/wp-content/uploads/2025/04/Confirmation.png)

And there you have it…

To restart the cluster, ensure all the hosts are booted. Leave them in maintenance mode and then select “Restart vSAN Services”. The workflow will bring them back into operation. 

![Restart V SAN](https://jameskilby.co.uk/wp-content/uploads/2025/03/Restart-vSAN.png)Restart vSAN Services

## 📚 Related Posts

  * [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)
  * [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [ ![VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

[VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

By[James](https://jameskilby.co.uk) December 8, 2025 · Updated July 11, 2026

How to use the Amazon Time Sync Service in a VMC environment

  * [ ![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk) August 14, 2025 · Updated July 11, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk) March 27, 2026 · Updated May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s