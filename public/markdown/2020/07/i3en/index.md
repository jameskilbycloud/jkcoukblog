---
title: "VMware Cloud on AWS i3en Host: Specs, Storage & Performance"
description: "A look at the new VMware Cloud on AWS i3en host — 96 cores, 768GiB RAM and ~46TiB of NVMe storage, and what that means for storage-bound clusters."
date: 2020-07-02T22:01:39+00:00
modified: 2026-06-05T19:07:48+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - Ansible
  - Artificial Intelligence
  - Containers
  - Devops
  - Homelab
  - NVIDIA
  - Traefik
  - Personal
  - vSphere
tags:
  - #VMC
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2020/07/i3en/
image: https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-1024x526.png
---

![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# VMware Cloud on AWS i3en Host: Specs, Storage & Performance

By[James](https://jameskilby.co.uk)July 2, 2020 · Updated June 5, 2026 • 📖2 min read(435 words)

📅**Published:** July 02, 2020•**Updated:** June 05, 2026

VMware Cloud on AWS (VMC) has introduced a new i3en host to its lineup. This is based on the [i3en.metal AWS instance](https://aws.amazon.com/ec2/instance-types/i3en/).

## i3en Host Specifications

The specifications are certainly impressive, packing in 96 logical cores, 768GiB RAM, and approximately 45.84 TiB of NVMe raw storage capacity per host.

It’s certainly a monster with a 266% uplift in CPU, a 50% increase in RAM and a whopping 440% increase in raw storage per host compared to the i3. Most of the engagements I have worked on so far have discovered that they are storage limited requiring extra hosts to handle the required storage footprint. With such a big uplift in storage capacity, hopefully this will trend towards filling up CPU, RAM & Storage at the same time. This is the panacea of Hyperconvergence.

## i3en Host Performance

The other two noticeable changes are that the processor is based on a much later Intel family. It is now based on 3.1 GHz all-core turbo Intel® Xeon® Scalable (Skylake) processors. This is a much more modern processor than the Broadwells in the original i3. This brings several processor extension improvements including Intel AVX, Intel AVX2, Intel AVX-512

The other noticeable change is the networking uplift with 100Gb/s available to each host.

Model|  pCPU| Memory GiB| Networking Gbps| Storage TB| AWS Host Pricing (On-demand in US-East-2 Ohio)  
---|---|---|---|---|---  
i3.metal| 36*| 512| 25| 8×1.9| $5.491  
i3en.metal| 96| 768| 100| 8×7.5| $11.933  
  
*The i3.metal instance, when used with VMware Cloud on AWS has hyperthreading disabled.

At present this host is only available in the newer SDDC versions (1.10v4 or later) and limited locations.

It also looks like the i3 still has to be the node used in the first cluster within the SDDC (where the management components reside) and they aren’t supported in 2 node clusters.

~~At the time of writing pricing from VMware is not available however pricing is available for the hosts if they were bought directly from AWS. Assuming the VMware costs fall broadly in line with this giving:~~

VMware have now released pricing. The below is for On-Demand in the AWS US-East region.

i3.Metal is £6.213287 per hour & i3en.Metal £13.6221 per hour giving:

  * A cost per GB of SSD instance storage that is up to 50% lower
  * Storage density (GB per vCPU) that is roughly 2.6x greater
  * Ratio of network bandwidth to vCPUs that is up to 2.7x greater

This new host type adds complication to choosing host types within VMware Cloud on AWS but makes it a very compelling solution. See how it compares to other hosts in my [VMware Cloud on AWS hosts deep-dive](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/).

## 📚 Related Posts

  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)
  * [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

## Similar Posts

  * [![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png)](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk)February 9, 2026 · Updated June 5, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png)](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk)September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.

  * [![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png)](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk)October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png)](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk)December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png)](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk)August 14, 2025 · Updated June 5, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [![Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash-768x417.png)](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

By[James](https://jameskilby.co.uk)January 27, 2026 · Updated June 5, 2026

How to leverage Content Libraries to deploy into VMware Cloud on AWS faster.