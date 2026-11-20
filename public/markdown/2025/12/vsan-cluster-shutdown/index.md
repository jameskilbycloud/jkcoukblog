---
title: "vSAN Cluster Shutdown – Orchestration"
description: "As can be seen on my Lab Overview page. I have a GPU/Management cluster that is usually running 24x7."
date: 2025-12-06T10:59:14+00:00
modified: 2026-11-16T23:12:20+00:00
author: James Kilby
categories:
  - VMware
  - vSAN
  - VMware Cloud on AWS
  - Personal
  - TrueNAS Scale
url: https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/
image: https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg
---

![Powered by VMware vSAN logo](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

# vSAN Cluster Shutdown – Orchestration

By[James Kilby](https://jameskilby.co.uk) December 6, 2025 · Updated November 16, 2026 • 📖1 min read(112 words)

As can be seen on my Lab Overview page, I have a GPU/Management cluster that is usually running 24×7. I also have a 3x Node vSAN cluster that I use when I need more resources (or specifically if I need vSAN to test with)

This allows me to 

See the overview below

![Homelab vSphere diagram: management cluster, vSAN ESA cluster and TrueNAS iSCSI storage](https://jameskilby.co.uk/wp-content/uploads/2024/12/vSphere-Overview-1024x530.png)

To shut down a vSAN cluster, there is a nice workflow built into vCenter that will orchestrate all the required actions for you

![vSAN services page with the shutdown cluster option highlighted](https://jameskilby.co.uk/wp-content/uploads/2025/04/vSAN-Services-Menu-1024x564.png)

![vSAN cluster shutdown wizard: pre-checks passed](https://jameskilby.co.uk/wp-content/uploads/2025/04/Shutdown-Precheck.png)

![vSAN cluster shutdown wizard: confirm shutdown step](https://jameskilby.co.uk/wp-content/uploads/2025/04/Confirmation.png)

And there you have it…

To restart the cluster, ensure all the hosts are booted. Leave them in maintenance mode and then select “Restart vSAN Services”. The workflow will bring them back into operation. 

![vSAN cluster shut down message with a Restart button](https://jameskilby.co.uk/wp-content/uploads/2025/03/Restart-vSAN.png)Restart vSAN Services

## 📚 Related Posts

  * [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)
  * [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James Kilby](https://jameskilby.co.uk) July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.

  * [ ![VMware by Broadcom and AWS logos](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

By[James Kilby](https://jameskilby.co.uk) May 21, 2025 · Updated July 11, 2026

Quick reference guide to the available storage resources that you get in VMware Cloud on AWS

  * [ ![VMware Certified Advanced Professional Data Center Virtualization Deploy 2023 badge](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James Kilby](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![VMware Cloud on AWS logo](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

By[James Kilby](https://jameskilby.co.uk) April 1, 2026 · Updated November 15, 2026

We’ve expanded the VMC fleet with the new i7i (i7i.

  * [ ![VMware by Broadcom and AWS logos](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James Kilby](https://jameskilby.co.uk) August 14, 2025 · Updated November 15, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![ZFS logo](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg) ](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

By[James Kilby](https://jameskilby.co.uk) December 18, 2024 · Updated November 17, 2026

Introduction Copy on Write Disk IDs Trim Introduction I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010.