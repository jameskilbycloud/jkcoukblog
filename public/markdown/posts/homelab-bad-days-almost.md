---
title: "Homelab SSD Failure: How Synology RAID Saved My Data"
description: "I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate. This involves driving from the south coast of Dorset up to Scotland and then"
date: 2022-11-21T15:46:53+00:00
modified: 2026-06-01T19:02:40+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - Synology
  - Hosting
  - Networking
  - VMware
  - Nutanix
  - TrueNAS Scale
  - Automation
tags:
  - #Homelab
  - #Storage
url: https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/
image: https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1.jpg
---

![Brokenharddive 1200X630 1](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

# Homelab SSD Failure: How Synology RAID Saved My Data

By[James](https://jameskilby.co.uk)November 21, 2022 · Updated June 1, 2026 • 📖2 min read(362 words)

📅**Published:** November 21, 2022•**Updated:** June 01, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate. This involves driving from the south coast of Dorset up to Scotland and then getting a ferry over to Belfast before travelling west to the Republic. While driving I got a slack notification that one of my SSDs in my Synology DS918+ was in a bad way. (You do have notifications set up, right? ) The timing could not have been worse. Now for years anyone that I have talked to at VMUG’s around data protection etc, I have advocated never using RAID 5. The reasons for this are well known. But when it’s your homelab and your wallet is on the line corners sometimes need to be cut.

When I got to Ireland I logged into the Synology, it was pretty obvious it wasn’t happy

![Homelab bad days \(almost\) Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-11-14-at-20.56.39.png)Unhappy Array (for historical reasons I was using slots 1, 2 and 4)

and it had pages and pages like this….

![Drive Errors 2048x236](https://jameskilby.co.uk/wp-content/uploads/2023/04/Drive-Errors-2048x236-1-1024x118.png)

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

  * [![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg)](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk)October 11, 2022 · Updated June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png)](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk)December 19, 2022 · Updated June 1, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg)](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk)July 2, 2024 · Updated June 5, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png)](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James](https://jameskilby.co.uk)September 12, 2024 · Updated June 1, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.

  * [![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast-768x219.webp)](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Unleashing the Beast](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

By[James](https://jameskilby.co.uk)June 20, 2026 · Updated June 21, 2026

Retiring my ageing WatchGuard M200, I swap in the UniFi UDM Beast — a hardware tour, first iperf and WAN tests, the BGP/FRR setup, and the homelab services I’m consolidating onto it.

  * [![Template Deployment with Packer](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png)](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Template Deployment with Packer](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

By[James](https://jameskilby.co.uk)January 21, 2021 · Updated June 5, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while.