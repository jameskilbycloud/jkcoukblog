---
title: "Homelab Storage Upgrade: Synology DS918 for VMware & NFS"
description: "Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes."
date: 2019-02-10T23:59:20+00:00
modified: 2026-06-01T21:58:25+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - Synology
  - Networking
  - Hosting
  - VCF
  - VMware
  - vSphere
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

By[James](https://jameskilby.co.uk)February 10, 2019 · Updated June 1, 2026 • 📖1 min read(205 words)

📅 **Published:** February 10, 2019• **Updated:** June 01, 2026

## Lab Storage Update.

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes. At the moment it’s very much focused on the VMware stack and one of the things I needed was some more storage and especially some more storage performance. With that in mind, I purchased a new Synology DS918…

![Lab Storage](https://jameskilby.co.uk/wp-content/uploads/2023/04/iu-768x432-1.jpg)

It’s a very compact unit with a quad-core Intel Celeron & I have left the RAM at 4 GB for now.

I have added some of the existing SSDs I had, giving me about 3TB of usable flash. I am presenting this back to my VMware hosts using NFS 4.1. I must have missed the announcement as this is now built into the Synology GUI (it used to be a command-line-only option). I have verified the VAAI works as expected in this configuration. At present I am using this with a single network connection however I will be testing NFS Multipathing shortly.

The performance improvement has been noticeable and I have now removed all non-Synology systems from primary storage. This has left me with the DS918+ detailed here and a DS216+ with 2TB of Raid1 WD Reds. I am using this for ISOs and some general file storage.

## 📚 Related Posts

  * [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)
  * [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)
  * [My First Homelab Storage Setup: HP Gen8 &#038; Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

## Similar Posts

  * [![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg)](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk)November 21, 2022 · Updated June 1, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png)](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk)June 26, 2024 · Updated June 1, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg)](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk)October 11, 2022 · Updated June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg)](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk)January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [![TrueNAS Logo](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2023-05-22-at-18.49.21-768x198.png)](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Homelab Storage Refresh (Part 1)](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

By[James](https://jameskilby.co.uk)May 23, 2023 · Updated June 1, 2026

Table of Contents Background ZFS Overview Read Cache (ARC and L2ARC) ZIL (ZFS Intent Log) Hardware Background I have just completed the move of all my production and media-based storage/services to TrueNAS Scale. ( I will just refer to this as TrueNAS) This is based on my HP Z840 and I have now retired my…

  * [![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png)](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk)December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.