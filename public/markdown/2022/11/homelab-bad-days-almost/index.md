---
title: "Homelab SSD Failure: How Synology RAID Saved My Data"
description: "I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate."
date: 2022-11-21T15:46:53+00:00
modified: 2026-11-16T23:12:23+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - Synology
  - Artificial Intelligence
  - Automation
  - Ansible
  - Hosting
  - TrueNAS Scale
  - VMware
  - Veeam
tags:
  - #Homelab
  - #Storage
url: https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/
image: https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1.jpg
---

![Shattered hard disk platter](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

# Homelab SSD Failure: How Synology RAID Saved My Data

By[James Kilby](https://jameskilby.co.uk) November 21, 2022 · Updated November 16, 2026 • 📖2 min read(362 words)

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate. This involves driving from the south coast of Dorset up to Scotland and then getting a ferry over to Belfast before travelling west to the Republic. While driving I got a slack notification that one of my SSDs in my Synology DS918+ was in a bad way. (You do have notifications set up, right? ) The timing could not have been worse. Now for years anyone that I have talked to at VMUG’s around data protection etc, I have advocated never using RAID 5. The reasons for this are well known. But when it’s your homelab and your wallet is on the line corners sometimes need to be cut.

When I got to Ireland I logged into the Synology. It was pretty obvious it wasn’t happy

![Homelab bad days \(almost\) Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-11-14-at-20.56.39.png)Unhappy Array (for historical reasons I was using slots 1, 2 and 4)

and it had pages and pages like this….

![Synology log of drive errors](https://jameskilby.co.uk/wp-content/uploads/2023/04/Drive-Errors-2048x236-1-1024x118.png)

I had 3 SSDs in this particular array all from around the same time. Out of curiosity, I checked how old they were. The drive that failed had a power-on-hours count of 49599 hours (5.6 Years). It had more than served its purpose so some replacements were ordered for when I was back in Poole. For now I had to run the risk and hope another drive didn’t fail. Returning home to swap a drive was never going to go down well with the family.

I decided to order 4x 2TB SSDs and went with the Samsung 870 QVO’s. They are def on the budget end of SSDs but are cost-effective and given the limited network bandwidth on my Synology were more than adequate.

I first replaced the failed drive and then when this was complete extended the array to be 4x Disk before replacing the other 2 existing drives one at a time.

![Homelab bad days \(almost\) Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-11-21-at-16.43.51.png)Everything is green again

Everything is now back to being green and hunky dory. I have run scrubs to validate all data. I still have RAID 5 on both volumes but I have undertaken a task to improve some of my backup handling. Just in case…..

## 📚 Related Posts

  * [My First Homelab Storage Setup: HP Gen8 &#038; Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)
  * [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)
  * [Homelab Storage Upgrade: Synology DS918 for VMware &#038; NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

## Similar Posts

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James Kilby](https://jameskilby.co.uk) April 4, 2026 · Updated November 17, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png) ](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James Kilby](https://jameskilby.co.uk) April 15, 2026 · Updated June 1, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introduction One of the larger costs of running my homelab is the electricity….

  * [ ![SpaceX Starlink rocket launch at sunset](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg) ](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James Kilby](https://jameskilby.co.uk) October 11, 2022 · Updated November 16, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [ ![ZFS logo](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg) ](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

By[James Kilby](https://jameskilby.co.uk) December 18, 2024 · Updated November 17, 2026

Introduction Copy on Write Disk IDs Trim Introduction I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

### [Lab Update – Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

By[James Kilby](https://jameskilby.co.uk) January 6, 2022 · Updated June 1, 2026

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things.

  * [ ![TrueNAS Scale logo](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault-768x432.jpeg) ](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

By[James Kilby](https://jameskilby.co.uk) January 11, 2022 · Updated November 16, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale.