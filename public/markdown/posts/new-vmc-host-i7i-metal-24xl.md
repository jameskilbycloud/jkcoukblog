---
title: "New VMware Cloud on AWS Host: i7i.metal-24xl"
description: "We’ve expanded the VMC fleet with the new i7i (i7i."
date: 2026-04-01T08:06:00+00:00
modified: 2026-07-11T07:46:38+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - Ansible
  - Automation
  - Homelab
  - Personal
  - Artificial Intelligence
  - Runecast
tags:
  - #I7i
  - #VMware
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/
image: https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp
---

![](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# New VMware Cloud on AWS Host: i7i.metal-24xl

By[James](https://jameskilby.co.uk) April 1, 2026 · Updated July 11, 2026 • 📖4 min read(869 words)

**Published:** April 01, 2026•**Updated:** July 11, 2026

We’ve expanded the VMC fleet with the new **i7i**[**(i7i.24xlarge)** ](https://aws.amazon.com/ec2/instance-types/i7i/)host type. Powered by Intel Emerald Rapids processors with PCIe Gen5 connectivity, it delivers the fleet’s highest single-core performance and memory bandwidth, making it well suited for latency-sensitive workloads and high-performance vSAN configurations.

## Key Technical Specs:

  * **Performance:** Intel Emerald Rapids CPUs + PCIe Gen5, offering the fleet’s highest clock speeds and memory bandwidth.
  * **Storage:** Optimized for vSAN with the fastest available NVMe devices. Support for both vSAN OSA and ESA
  * **Security:** Enhanced security based on [Intel Total Memory Encryption](https://www.intel.com/content/dam/www/central-libraries/us/en/documents/white-paper-intel-tme.pdf)

This host brings a blend of usable options to complement the existing VMC fleet ranging from bleeding edge performance for tier one applications. It also supports expanded DR capabilities with SCFS via [VLR](https://techdocs.broadcom.com/us/en/vmware-cis/live-recovery.html).

The below table compares the specifications of all nodes currently running in VMC.

| **I3**| **I3en**| **I4i**| **I7i**  
---|---|---|---|---  
AWS Nitro Version| v2| v3| v4| v4  
**CPU**| | | |   
Processor Name| Intel Xeon E5-2686 v4 | Intel Xeon Platinum 8175| Intel Xeon 8375c| Intel Xeon 8559c  
No of Physical Cores| 36| 48| 64| 48  
Hyperthreading| No| Yes| Yes| Yes  
Base Clock| 2.3GHz| 2.5 Ghz| 2.9 GHz| 3.2 GHz  
Turbo Clock| N/A| 3.1 GHz| 3.5 GHz| 4.0 Ghz  
Processor Family| Broadwell| Skylake| Ice Lake| Emerald Rapids  
Supported Custom Core Counts| 8 16 36| 8 16 24   
30 36 48| 8 16 24   
30 36 48 64| 8 16 24 30 36  
**Memory** | | | |   
Capacity GiB| 512| 768| 1024| 768  
Memory Speed| DDR4-2400| DDR4-2666| DDR4-3200| DDR5-5600  
**Networking**| | | |   
Network Adaptor Speed Gb/s| 25| 100| 75 | 56.25  
Hardware Network Encryption | No| Yes| Yes| Yes  
**Storage**| | | |   
Drive Connection| PCIe Gen3| PCIe Gen3| PCIe Gen4| PCIe Gen5  
Physical Drives| 8×1900| 8×7500| 8×3570| 6×3750  
Physical Raw Space GiB| 15,200| 60,000| 28,560| 22,500  
vSAN OSA Cache Disk| 2| 4^| 2| 2  
vSAN OSA Capacity Disk| 6| 28^| 6| 4  
vSAN Compression| Yes| Yes| Yes| Yes  
vSAN OSA Deduplication| Yes| No| No| No  
vSAN OSA Support| Yes| Yes| Yes| Yes  
vSAN ESA Support| No| No| Yes| Yes  
Underlying Storage Performance IOPS*| –| 80000| 160000| 120000  
Underlying Storage Performance Throughput*| –| 2375| 5000| 3750  
  
*Storage performance figures taken from the instance’s website. vSAN performance will differ based on OSA/ESA, Storage Policy in use and number of hosts in the environment. 

^I3en hosts use NVMe namespaces to carve the disks up differently to how they are physically presented

** In vSAN ESA all drives are in a single tier and contribute to both performance and capacity

## What Workloads Benefit Most from the i7i?

The i7i.metal-24xl is optimised for I/O-intensive enterprise workloads that demand the highest possible random IOPS with predictable, sub-millisecond latency. It is particularly well-suited for:

  * **SQL Server and Oracle databases** — DDR5-5600 memory bandwidth and Gen5 NVMe deliver measurable query throughput gains over i4i hosts
  * **High-frequency messaging platforms** — Kafka and Redis workloads benefit from low-latency NVMe and improved single-core turbo performance up to 4.0 GHz
  * **AI/ML inference** — large model serving with high memory bandwidth maps well to the 768 GiB DDR5 configuration
  * **VDI and virtualised desktop workloads** — the Custom CPU Core Count option (8, 16, 24, 30, or 36 physical cores) allows cost-effective right-sizing per host
  * **Workloads currently on i3 or i3en** — the i7i offers significantly better compute, memory bandwidth, and storage performance

## vSAN Configuration and Deployment Requirements

The i7i.metal-24xl supports both **vSAN OSA** (Original Storage Architecture) and **vSAN ESA** (Express Storage Architecture). ESA is the recommended configuration for new deployments — it treats all six NVMe drives as a single-tier pool, delivering superior throughput and compression compared to OSA.

  * **SDDC version 1.26v2 or later** required for cluster conversions and new secondary cluster deployments
  * **Minimum 3-node cluster** — with vSAN compression enabled, a 3-node i7i cluster delivers strong usable capacity from the 6 × 3,750 GiB NVMe drives per host
  * **Stretched Cluster support** — opt-in multi-AZ stretched cluster deployments supported, providing HA across two AWS Availability Zones in a single region
  * **Custom CPU Core Count** — 8, 16, 24, 30, or 36 physical cores per host, useful for Oracle licensing optimisation

## Frequently Asked Questions

### How does the i7i.metal-24xl compare to the i4i?

The i7i delivers approximately **23% better compute performance** and over **10% better price-performance** than the i4i. It upgrades from 3rd Gen Intel Xeon (Ice Lake) to 5th Gen (Emerald Rapids), moves from DDR4 to DDR5-5600 memory, and adds PCIe Gen5 NVMe. Storage capacity is 22.5 TiB raw per host versus the i4i’s 30 TiB, but random IOPS is significantly higher.

### What SDDC version is required for the i7i.metal-24xl?

You need **SDDC version 1.26v2** or later to convert existing clusters or deploy new secondary clusters with i7i hosts. New SDDCs can be provisioned with i7i directly once the instance type is available in your region.

### Is stretched cluster supported on i7i?

Yes. Customers can opt in to a multi-AZ stretched cluster deployment for new SDDCs using i7i.metal-24xl hosts, providing high availability across two AWS Availability Zones within a single region.

### Can I mix i7i hosts with i4i or i3en in the same cluster?

No — VMware Cloud on AWS clusters are single host-type only. You can add an i7i as a secondary cluster within an existing SDDC, but mixing host types within the same cluster is not supported.

The official announcement can be found [here](https://blogs.vmware.com/cloud-foundation/2026/04/01/vmware-cloud-aws-i7i-metal-24xl-instance/).

## 📚 Related Posts

  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)
  * [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

## Similar Posts

  * [ ![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png) ](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk) April 15, 2026 · Updated June 1, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introduction One of the larger costs of running my homelab is the electricity….

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk) October 23, 2023 · Updated July 11, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk) March 27, 2026 · Updated May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [ ![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png) ](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.