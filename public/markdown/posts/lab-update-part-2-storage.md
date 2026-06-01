---
title: "Lab Update – Part 2 Storage Truenas Scale"
description: "The HP Z840 has changed its role to a permanent storage box running Truenas Scale."
date: 2022-01-11T22:35:02+00:00
modified: 2026-06-01T21:58:40+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - Artificial Intelligence
  - Docker
  - vExpert
  - VMware
  - vSphere
  - Nutanix
  - Automation
  - NVIDIA
  - Traefik
  - Networking
tags:
  - #NVMe
  - #SSD
  - #Truenas
  - #TrueNAS Scale
url: https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/
image: https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault.jpeg
---

![](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault.jpeg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

# Lab Update – Part 2 Storage Truenas Scale

By[James](https://jameskilby.co.uk) January 11, 2022June 1, 2026 • 📖2 min read(495 words)

📅 **Published:** January 11, 2022• **Updated:** June 01, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale. This is in addition to my Synology DS918+…

TrueNas is the successor to FreeNas, a very popular BSD based StorageOS and TrueNas scale is a fork of this based on Linux.

The Synology has been an amazing piece of kit handling VM storage, Docker, File sharing and Plex duties. It will maintain most of these roles. However, I needed something faster for my lab and especially something with faster network access. The Synology I had was limited to 2xGb interfaces. An option was to buy a newer Synology but I felt a better route was to try a “Storage OS” on some of my existing hardware with some network tweaks to be seen later.

The Spec of the Z840 Workstation I am using to run Truenas is 2x Intel Xeon CPU E5-2673 v3 @ 2.40GHz and 128GB of RAM. More than enough for my needs. I will use the 2xGb interfaces for management and the new network for a combination of iSCSI/NFS…

Within one of the 5 1/2 inch drive bays I have placed an Icy Dock express cage giving me 6 additional 2.5 drive bays.

![Lab Update - Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2023/04/iu-1.jpeg)ICY Dock

I have placed the TrueNAS OS on 2x Intel 80GB SSDs running within these.

For now, I have configured 2 storage pools. One NVMe with a single INTEL SSDPE2MX020T7. This will be very high-performance storage but for now, is not redundant. I plan to mitigate this with regular backups.

The other is reusing some 3TB WD Red drives from the Synology in a Raid-Z config. I will likely add some SSD as a ZLOG at a later date.

This is presented back to my VMware hosts using iSCSI over a 25Gb direct network. I have only done basic testing so far. John would murder me for this but I did a test using CrystalDisk just to check everything was in the correct realms of what I would expect. (These numbers will have been influenced by cache size as they easily fit in the working set)

I chose to use the real-world test built into CrystalDiskMark. I’m sure the numbers would be much higher with other configs. This was also done with a 4GiB file which isn’t huge, but I used it to keep the testing short. I will come back and test the storage properly at a later date.

![Lab Update - Part 2 Storage Truenas Scale Screenshot](https://jameskilby.co.uk/wp-content/uploads/2022/01/Screenshot-2022-01-17-at-09.11.14.png)

NVMe initial performance test. I had a number of VMs running on the NVMe test at the time testing was running. This may account for the read being slightly lower than the SATA disks but the Write performance is much higher.

![Lab Update - Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/NVMe.png)

TrueNAS SATA test. 3x SATA disks in RAID 5 

![Lab Update - Part 2 Storage Truenas Scale Screenshot](https://jameskilby.co.uk/wp-content/uploads/2022/01/Screenshot-2022-01-17-at-09.07.00.png)

Comparison with Synology 3x SSD Raid 5 ( 2x1Gb/s ) Networking. You can see this is significantly lower than the Freenas box. The Synology was running a number of docker containers and apps at the time so I’m sure performance could be higher.

![Synology](https://jameskilby.co.uk/wp-content/uploads/2022/01/Synology-1024x725.png)

## 📚 Related Posts

  * [Using Intel Optane NVMe in a VMware Homelab: Setup &#038; Results](https://jameskilby.co.uk/2023/04/intel-optane/)
  * [Homelab Storage Refresh (Part 1)](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)
  * [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

## Similar Posts

  * [ ![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg) ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk) October 11, 2024June 1, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [ ![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png) ](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk) April 17, 2023June 1, 2026

I have been a VMware vExpert for many years and it has brought me many benefits over the years.

  * [ ![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png) ](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk) December 14, 2022June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [ ![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg) ](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk) July 2, 2024June 1, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk) March 27, 2026May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [ ![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png) ](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk) June 26, 2024June 1, 2026

How to configure DHCP Option 43 for UniFi devices