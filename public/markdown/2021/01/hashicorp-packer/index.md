---
title: "Template Deployment with Packer"
description: "How I got HashiCorp Packer set up on macOS to automate VMware template deployment — including the vSphere datacenter error I hit and how I fixed it."
date: 2021-01-21T22:26:10+00:00
modified: 2026-06-05T19:02:09+00:00
author: James Kilby
categories:
  - Automation
  - Homelab
  - VMware
  - Storage
  - Synology
  - Artificial Intelligence
  - Docker
  - NVIDIA
  - Traefik
  - Runecast
  - Ansible
  - Personal
  - vSphere
  - Devops
tags:
  - #Automation
  - #Hashicorp
  - #Homelab
  - #packer
url: https://jameskilby.co.uk/2021/01/hashicorp-packer/
image: https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Template Deployment with Packer

By[James](https://jameskilby.co.uk) January 21, 2021 · Updated June 5, 2026 • 📖2 min read(366 words)

📅**Published:** January 21, 2021•**Updated:** June 05, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while. But until now I had never played with it. That was until I saw the below tweet by the legend that is [William Lam](https://williamlam.com/)

> 🤩 THIS IS AWESOME 🤩  
>   
> For those who ❤️ Automation, check out [@tenthirtyam](https://x.com/tenthirtyam?ref_src=twsrc%5Etfw) amazing repo w/working examples to build Photon OS 3/4, Ubuntu 18.04/20.04, RHEL 7/8, CentOS 7/8 & Windows Server 2016/2019 VM images using Packer & pushing to Cont Lib! Well done <https://t.co/o7FQXtrpRn>
> 
> — William Lam (@lamw) [November 30, 2020](https://x.com/lamw/status/1333546472155987969?ref_src=twsrc%5Etfw)

## Getting Packer Running

That was the kicker I needed to go and have a look at getting Packer set up and running. As I run a Mac as my main machine it was easy to get deployed following the instructions using [brew](https://brew.sh) and the GitHub Repo that William had pointed to.

## Fixing the Packer Datacenter Error

However, once I had added my vSphere credentials I was having a few issues. On execution, I was getting the error message “default datacenter resolves to multiple instances”. I did a bit of digging and discovered that the code didn’t specify a VMware datacenter and in my lab environment, I have 2 physical sites with a VMware datacenter in each, therefore, I needed to specify which one. Once this was fixed I started rolling out some Linux templates and it worked flawlessly until I got to the photon 4 server. I again spotted a typo and a syntax error on a command being passed into the photon VM. I corrected this and decided that actually, I should work out how to get this fixed upstream to help the wider community.

Once this was working it was onto the Windows templates. Once all the relevant ISOs and configs were in place I was able to fully deploy 4 Windows servers that were patched and added to my content library in about 40 mins. So whenever I go to deploy an Image it is always up to date…

Thanks to [Ryan](https://github.com/tenthirtyam) for an incredible piece of work I now lean on tools like this for wider [homelab automation](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/).

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [ ![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg) ](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk) November 21, 2022 · Updated July 11, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated July 11, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png) ](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [ ![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png) ](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk) April 15, 2026 · Updated June 1, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introduction One of the larger costs of running my homelab is the electricity….

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![My First GitHub Pull Request: Contributing to Open Source](https://jameskilby.co.uk/wp-content/uploads/2020/12/175jvBleoQfAZJc3sgTSPQA.jpg) ](https://jameskilby.co.uk/2020/12/my-first-pull/)

[Devops](https://jameskilby.co.uk/category/devops/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [My First GitHub Pull Request: Contributing to Open Source](https://jameskilby.co.uk/2020/12/my-first-pull/)

By[James](https://jameskilby.co.uk) December 22, 2020 · Updated June 5, 2026

I was initially going to add in the contents of this post to one that I have been writing about my exploits with HashiCorp Packer but I decided it probably warranted being separated out.