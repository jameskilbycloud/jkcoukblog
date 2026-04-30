---
title: "Lab Update – Part 2 Storage Truenas Scale"
description: "The HP Z840 has changed its role to a permanent storage box running Truenas Scale. This is in addition to my Synology DS918+..."
date: 2022-01-11T22:35:02+00:00
modified: 2026-04-16T22:01:55+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - Artificial Intelligence
  - Synology
  - VMware
  - Nutanix
  - Docker
  - Hosting
  - Kubernetes
  - TrueNAS Scale
tags:
  - #NVMe
  - #SSD
  - #Truenas
  - #TrueNAS Scale
url: https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/
image: https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault.jpeg
---

![Maxresdefault](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault.jpeg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

# Lab Update – Part 2 Storage Truenas Scale

By[James](https://jameskilby.co.uk)January 11, 2022April 16, 2026 • 📖2 min read(495 words)

📅 **Published:** January 11, 2022• **Updated:** April 16, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale. This is in addition to my Synology DS918+

TrueNas is the successor to FreeNas a very popular BSD based StorageOS and TrueNas scale is a fork of this based on Linux.

The Synology has been an amazing piece of kit handling VM storage, Docker, File sharing and Plex duties. It will maintain most of these roles. However, I needed something faster for my lab and especially something with faster network access. The Synology I had was limited to 2xGb interfaces. An option was to buy a newer Synology but I felt a better route was to try a “Storage OS” on some of my existing hardware with some network tweaks to be seen later.

The Spec of the Z840 Workstation I am using to run Truenas is 2x Intel Xeon CPU E5-2673 v3 @ 2.40GHz and 128GB of RAM. More than enough for my needs. I will use the 2xGb interfaces for management and the new network for a combination of iSCSI/NFS

Within one of the 5 1/2 inch drive bays I have placed an Icy Dock express cage giving me 6 additional 2.5 drive bays.

![Lab Update - Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2023/04/iu-1.jpeg)ICY Dock

I have placed the TrueNAS OS on 2x Intel 80GB SSD’s running within these.

For now, I have configured 2 storage pools. One NVMe with a single INTEL SSDPE2MX020T7. This will be very high-performance storage but for now, is not redundant. I plan to mitigate this with regular backups.

The other is reusing some 3TB WD Red drives from the Synology in a Raid-Z config. I will likely add some SSD as a ZLOG at a later date.

This is presented back to my VMware hosts using iSCSI over a 25Gb direct network. I have only done basic testing so far. John would murder me for this but I did a test using CrystalDisk just to check everything was in the correct realms of what I would expect. (These numbers will have been influenced by cache size as they easily fit in the working set)

I chose to use the real-world test built into Crystel Disk Mark. I’m sure the numbers would be much higher with other configs. This was also done with a 4GiB file which isn’t huge but I used to keep the testing short. I will come back and test the storage properly at a later date.

![Lab Update - Part 2 Storage Truenas Scale Screenshot](https://jameskilby.co.uk/wp-content/uploads/2022/01/Screenshot-2022-01-17-at-09.11.14.png)

NVMe initial performance test. I had a number of VM’s running on the NVMe test at the time testing was running. This may account for the read being slightly lower than the SATA disks but the Write performance is much higher.

![Lab Update - Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/NVMe.png)

TrueNAS SATA test. 3x Sata disks in Raid5 

![Lab Update - Part 2 Storage Truenas Scale Screenshot](https://jameskilby.co.uk/wp-content/uploads/2022/01/Screenshot-2022-01-17-at-09.07.00.png)

Comparison with Synology 3x SSD Raid 5 ( 2x1Gb/s ) Networking. You can see this is significantly lower than the Freenas box. The Synology was running a number of docker containers and apps at the time so I’m sure performance could be higher.

![Synology](https://jameskilby.co.uk/wp-content/uploads/2022/01/Synology-1024x725.png)

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

## Similar Posts

  * [![Wa](https://jameskilby.co.uk/wp-content/uploads/2025/04/210902461-012e7273-413a-4ec7-be44-e854347f5a21-768x180.png)](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Warp – The intelligent terminal](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

By[James](https://jameskilby.co.uk)April 11, 2025April 16, 2026

How Warp is helping me run my homelab. 

  * [![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg)](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk)November 21, 2022April 16, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg)](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk)October 23, 2023April 16, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg)](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk)July 2, 2024April 16, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png)](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk)December 9, 2022April 16, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….

  * [![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png)](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James](https://jameskilby.co.uk)September 12, 2024April 16, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.