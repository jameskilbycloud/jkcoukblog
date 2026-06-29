---
title: "An in-depth look at VMware Cloud on AWS hosts"
description: "A full side-by-side comparison of every VMware Cloud on AWS host type — I3.metal, I3en.metal and I4i.metal — covering CPU, memory, storage and networking specs."
date: 2025-08-14T12:32:01+00:00
modified: 2026-06-05T18:44:50+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - Homelab
  - Runecast
  - Artificial Intelligence
  - Automation
  - Docker
  - NVIDIA
  - Traefik
  - vSAN
  - Personal
tags:
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2025/08/vmc-host-deepdive/
image: https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png
---

![Picture 1 E1768509620339](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# An in-depth look at VMware Cloud on AWS hosts

By[James](https://jameskilby.co.uk)August 14, 2025 · Updated June 5, 2026 • 📖1 min read(244 words)

📅**Published:** August 14, 2025•**Updated:** June 05, 2026

This is a single page intended to collate every single feature of the current [VMware Cloud on AWS hosts](https://techdocs.broadcom.com/us/en/vmware-cis/cloud/vmware-cloud-on-aws/SaaS/operations-guide/managing-sddc-hosts-and-clusters/vmware-cloud-on-aws-host-types.html) for easy comparison.

All of this data is publicly available. I have just collated it into a single page.. For more on running VMware Cloud on AWS, see my post on [Time Sync in a VMC environment](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/).

## VMware Cloud on AWS Host Comparison

| **I3**.**metal**| **I3en**.**metal**| **I4i**.**metal**  
---|---|---|---  
**CPU**| | |   
Processor Name| Intel Xeon E5-2686 v4 | Intel Xeon Platinum 8175| Intel Xeon 8375c  
No of Physical Cores| 36| 48| 64  
Hyperthreading| No| Yes| Yes  
Base Clock| 2.3GHz| 2.5 GHz| 2.9 GHz  
Turbo Clock| N/A| 3.1 GHz| 3.5 GHz  
Processor Family| Broadwell| Skylake| Ice Lake  
Custom Core Count| 8 16 36| 8 16 24   
30 36 48| 8 16 24   
30 36 48 64  
**Memory**| | |   
Capacity GiB| 512| 768| 1024  
Memory Speed| DDR4-2400| DDR4-2666| DDR4-3200  
**Networking**| | |   
Network Adaptor Speed Gb/s| 25| 100| 75   
Hardware Network Encryption in Transit| No| Yes| Yes  
**Storage**| | |   
Physical Drives| 8×1900| 8×7500| 8×3570  
vSAN OSA Cache Disk| 2| 4*| 2  
vSAN OSA Capacity Disk| 6| 28*| 6  
vSAN Compression| Yes| Yes| Yes  
vSAN Deduplication| Yes| No| No  
vSAN OSA Support| Yes| Yes| Yes  
vSAN ESA Support| No| No| Yes  
  
*I3en is using NVMe namespace to split the 8 physical disks into 32 NVMe namespaces. 

Please note the I3.metal instance is no longer available to purchase from Broadcom but is still part of the running fleet for existing customers.

## 📚 Related Posts

  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)
  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

## Similar Posts

  * [![Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_4536-scaled-1-768x1024.jpg)](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)

By[James](https://jameskilby.co.uk)January 6, 2022 · Updated February 16, 2026

Quite a few changes have happened in the lab recently. I decided to do a multipart blog on the changes.

  * [![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png)](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk)May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk)April 4, 2026 · Updated June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [![vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg)](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

### [vSAN Cluster Shutdown – Orchestration](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

By[James](https://jameskilby.co.uk)December 6, 2025 · Updated June 1, 2026

How to safely shut down a vSAN Environment

  * [![VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png)](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

By[James](https://jameskilby.co.uk)May 21, 2025 · Updated June 24, 2026

Quick reference guide to the available storage resources that you get in VMware Cloud on AWS

  * [![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png)](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk)September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.