---
title: "vSAN Cluster Shutdown – Orchestration"
description: "As can be seen on my Lab Overview page, I have a GPU/Management cluster that is usually running 24×7."
date: 2025-12-06T10:59:14+00:00
modified: 2026-06-01T21:07:13+00:00
author: James Kilby
categories:
  - VMware
  - vSAN
  - VMware Cloud on AWS
  - Ansible
  - Artificial Intelligence
  - Containers
  - Devops
  - Homelab
  - NVIDIA
  - Traefik
  - Automation
  - Docker
  - VCF
  - Veeam
url: https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/
image: https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg
---

![Origionalpoweredbyvsan 550X324 1](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

# vSAN Cluster Shutdown – Orchestration

By[James](https://jameskilby.co.uk)December 6, 2025June 1, 2026 • 📖1 min read(112 words)

📅 **Published:** December 06, 2025• **Updated:** June 01, 2026

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

  * [![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png)](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk)August 14, 2025June 1, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png)](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk)February 9, 2026June 1, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk)April 4, 2026June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg)](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk)January 18, 2024June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Lab Update – Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

By[James](https://jameskilby.co.uk)January 6, 2022June 1, 2026

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things.

  * [![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg)](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk)October 23, 2023June 1, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.