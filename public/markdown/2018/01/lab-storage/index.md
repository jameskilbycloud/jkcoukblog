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
  - TrueNAS Scale
  - VMware
  - Ansible
  - Automation
  - Networking
  - VCF
tags:
  - #Homelab
  - #Storage
url: https://jameskilby.co.uk/2018/01/lab-storage/
image: https://jameskilby.co.uk/wp-content/uploads/2025/12/ChatGPT-Image-Dec-17-2025-at-09_03_10-PM.png
---

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

# My First Homelab Storage Setup: HP Gen8 & Xpenology

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026 • 📖1 min read(197 words)

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

  * [ ![How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg) ](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

By[James](https://jameskilby.co.uk) December 18, 2024 · Updated June 1, 2026

Introduction Copy on Write Disk IDs Trim Introduction I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast-768x219.webp) ](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Unleashing the UDM Beast](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

By[James](https://jameskilby.co.uk) June 20, 2026 · Updated August 24, 2026

Retiring my ageing WatchGuard M200, I swap in the UniFi UDM Beast — a hardware tour, first iperf and WAN tests, the BGP/FRR setup, and the homelab services I’m consolidating onto it.

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [ ![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg) ](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk) November 21, 2022 · Updated July 11, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [ ![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png) ](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk) December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.