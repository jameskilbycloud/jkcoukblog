---
title: "vSAN Cluster Shutdown – Orchestration"
description: "As can be seen on my Lab Overview page. I have a GPU/Management cluster that is usually running 24x7."
date: 2025-12-06T10:59:14+00:00
modified: 2026-06-01T21:07:13+00:00
author: James Kilby
categories:
  - VMware
  - vSAN
  - Homelab
  - Networking
  - Storage
  - Personal
  - VMware Cloud on AWS
  - Runecast
url: https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/
image: https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

# vSAN Cluster Shutdown – Orchestration

By[James](https://jameskilby.co.uk) December 6, 2025 · Updated June 1, 2026 • 📖1 min read(112 words)

📅**Published:** December 06, 2025•**Updated:** June 01, 2026

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

  * [ ![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png) ](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk) December 19, 2022 · Updated June 1, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [ ![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png) ](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk) October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [ ![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png) ](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk) September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.

  * [ ![New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

By[James](https://jameskilby.co.uk) April 1, 2026 · Updated June 1, 2026

We’ve expanded the VMC fleet with the new i7i (i7i.

  * [ ![VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

By[James](https://jameskilby.co.uk) May 21, 2025 · Updated June 24, 2026

Quick reference guide to the available storage resources that you get in VMware Cloud on AWS

  * [ ![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png) ](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.