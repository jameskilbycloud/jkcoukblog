---
title: "An in-depth look at VMware Cloud on AWS hosts"
description: "A full side-by-side comparison of every VMware Cloud on AWS host type — I3.metal, I3en.metal and I4i.metal — covering CPU, memory, storage and networking specs."
date: 2025-08-14T12:32:01+00:00
modified: 2026-11-15T08:49:30+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - Runecast
  - Automation
  - Homelab
  - Networking
  - VCF
tags:
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2025/08/vmc-host-deepdive/
image: https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png
---

![VMware by Broadcom and AWS logos](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# An in-depth look at VMware Cloud on AWS hosts

By[James Kilby](https://jameskilby.co.uk) August 14, 2025 · Updated November 15, 2026 • 📖1 min read(275 words)

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
**Memory** | | | |   
Capacity GiB| 512| 768| 1024| 768  
Memory Speed| DDR4-2400| DDR4-2666| DDR4-3200| DDR5-5600  
**Networking**| | | |   
Network Adaptor   
Speed Gb/s| 25| 100| 75 | 56.25  
Hardware Network   
Encryption in Transit| No| Yes| Yes| Yes  
**Storage**| | | |   
Physical Drives| 8×1900| 8×7500| 8×3750| 6×3750  
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

  * [ ![Runecast logo](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png) ](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James Kilby](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [ ![Illustration of a content library syncing from a source vCenter to a target vCenter](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash-768x417.png) ](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

By[James Kilby](https://jameskilby.co.uk) January 27, 2026 · Updated November 17, 2026

How to leverage Content Libraries to deploy into VMware Cloud on AWS faster.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James Kilby](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [ ![HashiCorp Packer logo](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png) ](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Template Deployment with Packer](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

By[James Kilby](https://jameskilby.co.uk) January 21, 2021 · Updated June 5, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while.

  * [ ![MikroTik CRS504 100GbE switch](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png) ](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James Kilby](https://jameskilby.co.uk) December 19, 2022 · Updated November 16, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [ ![VMware Holodeck architecture overview diagram](https://jameskilby.co.uk/wp-content/uploads/2023/12/Holodeck-Overview.png) ](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/)

### [VMware Holodeck Multi-Host VCF: Lab Setup & Configuration](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/)

By[James Kilby](https://jameskilby.co.uk) January 17, 2024 · Updated November 16, 2026

How to Deploy VMware Holodeck on multiple hosts