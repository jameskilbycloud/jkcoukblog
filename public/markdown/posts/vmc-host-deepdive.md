---
title: "An in-depth look at VMware Cloud on AWS hosts"
description: "A full side-by-side comparison of every VMware Cloud on AWS host type — I3.metal, I3en.metal and I4i.metal — covering CPU, memory, storage and networking specs."
date: 2025-08-14T12:32:01+00:00
modified: 2026-07-11T13:21:16+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - vSAN
  - Homelab
  - Networking
  - Storage
  - AWS
  - Veeam
  - Automation
tags:
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2025/08/vmc-host-deepdive/
image: https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png
---

![Picture 1 E1768509620339](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# An in-depth look at VMware Cloud on AWS hosts

By[James](https://jameskilby.co.uk)August 14, 2025 · Updated July 11, 2026 • 📖1 min read(275 words)

📅**Published:** August 14, 2025•**Updated:** July 11, 2026

This is a single page intended to collate every single feature of the current [VMware Cloud on AWS hosts](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/managing-sddc-hosts-and-clusters/vmware-cloud-on-aws-host-types.html) for easy comparison.

All of this data is publicly available. I have just collated it into a single page. For more on running VMware Cloud on AWS, see my post on [Time Sync in a VMC environment](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/).

## VMware Cloud on AWS Host Comparison

| **I3**.**metal**  
(END OF LIFE)| **I3en**.**metal**| **I4i**.**metal**|  i7i.metal-24xl  
---|---|---|---|---  
**CPU**| | | |   
Processor Name| Intel Xeon   
E5-2686 v4 | Intel Xeon   
Platinum 8175| Intel   
Xeon 8375c| Intel Xeon 8559c  
No of Physical Cores| 36| 48| 64| 48  
Hyperthreading| No| Yes| Yes| Yes  
Base Clock| 2.3GHz| 2.5 GHz| 2.9 GHz| 3.2 GHz  
Turbo Clock| N/A| 3.1 GHz| 3.5 GHz| 4.0 GHz  
Processor Family| Broadwell| Skylake| Ice Lake| Emerald Rapids  
Custom Core Count| 8 16 36| 8 16 24   
30 36 48| 8 16 24   
30 36 48 64| 8 16 24 30 36  
**Memory**| | | |   
Capacity GiB| 512| 768| 1024| 768  
Memory Speed| DDR4-2400| DDR4-2666| DDR4-3200| DDR5-5600  
**Networking**| | | |   
Network Adaptor   
Speed Gb/s| 25| 100| 75 | 56.25  
Hardware Network   
Encryption in Transit| No| Yes| Yes| Yes  
**Storage**| | | |   
Physical Drives| 8×1900| 8×7500| 8×3570| 6×3750  
vSAN OSA Cache Disk| 2| 4*| 2| 2  
vSAN OSA Capacity Disk| 6| 28*| 6| 4  
vSAN Compression| Yes| Yes| Yes| Yes  
vSAN Deduplication| Yes| No| No| No  
vSAN OSA Support| Yes| Yes| Yes| Yes  
vSAN ESA Support| No| No| Yes| Yes  
  
*I3en is using NVMe namespace to split the 8 physical disks into 32 NVMe namespaces. 

Please note the I3.metal instance is no longer available to purchase from Broadcom but is still part of the running fleet for existing customers.

## 📚 Related Posts

  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)
  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

## Similar Posts

  * [![vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg)](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

### [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

By[James](https://jameskilby.co.uk)November 17, 2023 · Updated June 1, 2026

An Overview of vSAN ESA in VMC 

  * [![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png)](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk)December 19, 2022 · Updated June 1, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg)](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk)October 23, 2023 · Updated July 11, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [![Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_4536-scaled-1-768x1024.jpg)](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

By[James](https://jameskilby.co.uk)January 6, 2022 · Updated February 16, 2026

Quite a few changes have happened in the lab recently. I decided to do a multipart blog on the changes.

  * [![Monitoring VMware Cloud on AWS: Tools & Approaches \(Part 1\)](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [AWS](https://jameskilby.co.uk/category/aws/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

### [Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

By[James](https://jameskilby.co.uk)December 17, 2019 · Updated June 5, 2026

As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring.

  * [![Template Deployment with Packer](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png)](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Template Deployment with Packer](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

By[James](https://jameskilby.co.uk)January 21, 2021 · Updated June 5, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while.