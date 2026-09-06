---
title: "VMware Holodeck Multi-Host VCF: Lab Setup & Configuration"
description: "Set up a multi-host VMware Holodeck lab with full VCF stack, networking and VSAN. Step-by-step config and the unsupported-but-it-works gotchas."
date: 2024-01-17T17:29:38+00:00
modified: 2026-06-01T19:02:58+00:00
author: James Kilby
categories:
  - VMware
  - VCF
  - VMware Cloud on AWS
  - Artificial Intelligence
  - Automation
tags:
  - #Holodeck
  - #MultiHost
  - #VCF
  - #VMware
url: https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/
image: https://jameskilby.co.uk/wp-content/uploads/2023/12/Holodeck-Overview.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/12/Holodeck-Overview.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/)

# VMware Holodeck Multi-Host VCF: Lab Setup & Configuration

By[James](https://jameskilby.co.uk) January 17, 2024 · Updated June 1, 2026 • 📖4 min read(891 words)

Disclaimer: This is **not** a supported configuration by the Holodeck team, please don’t reach out to them for help. As of today the only way to run Holodeck and receive support is to do it on a single compute node.

## Table of Contents

The [VCF Holodeck](https://core.vmware.com/introducing-holodeck-toolkit) toolkit is an excellent tool for learning not just VCF but a lot of technology that can be run on top of it. e.g. HCX, Tanzu vRA etc. Several guides have been written to assist with that.

However, the downside is that you need a single large fast vSphere host to run it on. The minimum specs are listed below for a few different configuration options. This shouldn’t be a challenge for a company or partner to provide but as a homelab enthusiast, this was always going to be a challenge. Many folks I know can cover the below resource requirements with the homelab they have. But the challenge is doing this with a single node. This was also going to be an issue for me. Therefore I needed to come up with a plan to make this work across at least 2 hosts…

## Holodeck recommended specifications

Minimum Hardware (1 env)| Recommended Hardware (2 envs)| Recommended Hardware (3-5 envs)  
---|---|---  
VCF Consolidated  | VCF Standard (MGMT + WLD) | VCF Standard (MGMT + WLD)  
2 sockets – Total 16 cores | 2 sockets – Total 32 core | 2 sockets – Total 64 cores  
384 GB RAM | 1024 GB RAM | 1.5 TB RAM  
3.5 TB SSD Disk | 2 – 3.5 TB SSD Disk | 4 – 3.5TB SSD Disks  
  
I was planning to use two of my existing Supermicro hosts that were already connected to my vCenter. They each have 2x Intel Xeon CPU E5-2670 @ 2.60GHz with 192GB of RAM each. The combined resources should be enough to run Holodeck and experiment with other toolsets on top. All of the storage is to be presented by my [TrueNas](https://jameskilby.co.uk/lab/) setup.

## Networking

Both hosts were originally connected through a DVSwitch and 2x25Gb/s physical adaptors. To change the configuration for Holodeck I removed one of the adaptors in each host from the DVswitch. I then followed the Holodeck guide and configured the standard switch as required on each host. I then added the unused 25Gb/s adaptor to the standard switch and then physically connected the two hosts with a short DAC cable as seen below.

![MultiHost Holodeck VCF](https://jameskilby.co.uk/wp-content/uploads/2024/01/IMG_5286-1-1024x996.jpeg)Physical Network ![Standard Switch](https://jameskilby.co.uk/wp-content/uploads/2024/01/Standard-Switch-1024x299.png)Standard Switch configuration

## DNS

Holodeck can be deployed either directly to an ESX Host or through a vCenter. As my VC and Hosts are part of the jameskilby.cloud domain I needed to ensure that the private IPs were being returned to the Holodeck Console VM for deployment. This can be handled in several ways however I believe the most elegant is to edit the holohosts.txt file on the HoloBuilder VM. This host file is copied over to the HoloConsole VM as part of the deployment and therefore the builder can always resolve the correct IPs irrespective of the state of the DNS on the CloudBuilder/HoloConsole VM.

The file is located at
    
    
    C:\Users\Administrator\Downloads\holodeck-standard-main2.0\holodeck-standard-main\Holo-Console\holohosts.txt

📋 Copy

I have added these values for my VC and the 2 Hosts that will be used as seen below.
    
    
    # Enter physical hosts or vCenter Server instances supporting Holodeck Deployment below
    
    10.203.42.1 w4-hs6-i1209.eng.vmware.com
    192.168.38.19 uk-poo-p-vc-1.jameskilby.cloud
    192.168.38.20 uk-bhr-p-esx-a.jameskilby.cloud
    192.168.38.21 uk-bhr-p-esx-b.jameskilby.cloud
    
    # Remaining entries are used for standardized Holdeck deployment
    10.0.0.101  esxi-1.vcf.sddc.lab 
    10.0.0.102  esxi-2.vcf.sddc.lab 
    10.0.0.103  esxi-3.vcf.sddc.lab 
    10.0.0.104  esxi-4.vcf.sddc.lab 
    10.0.0.4 sddc-manager.vcf.sddc.lab
    10.0.0.12 vcenter-mgmt.vcf.sddc.lab
    10.0.0.20 nsx-mgmt.vcf.sddc.lab 
    10.60.0.150 vrslcm.vcf.sddc.lab
    10.60.0.151 ws1.vcf.sddc.lab 
    10.60.0.170 vra.vcf.sddc.lab 
    10.0.0.150 kubeapi.vcf.sddc.lab 
    10.0.20.101  esxi-1.vcf2.sddc.lab 
    10.0.20.102  esxi-2.vcf2.sddc.lab 
    10.0.20.103  esxi-3.vcf2.sddc.lab 
    10.0.20.104  esxi-4.vcf2.sddc.lab 
    10.0.20.4 sddc-manager.vcf2.sddc.lab
    10.0.20.12 vcenter-mgmt.vcf2.sddc.lab
    10.0.20.20 nsx-mgmt.vcf2.sddc.lab 
    10.60.20.150 vrslcm.vcf2.sddc.lab
    10.60.20.151 ws1.vcf2.sddc.lab 
    10.60.20.170 vra.vcf2.sddc.lab 
    10.0.20.150 kubeapi.vcf2.sddc.lab 
    

📋 Copy

## vCenter Configuration

As I was deploying to a preexisting cluster I needed to make some small changes before Holodeck would deploy.

HA needs to be disabled and DRS either needs to be off or partially automated. I never like switching DRS off ( if you’ve ever used vCloud Director you will know why) so I went with partially automated.

## CPU/EVC config

The last step I personally needed to do (and I suspect this is due to the age of the CPUs in my hosts) was to disable EVC. I would suggest attempting to deploy with this in place and only turning it off if required.

I will detail some of the other fixes I needed specifically due to my CPU age in a separate [blog. ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

## Holodeck deployment

With these fixes in place, it was time to run the VLCGui Powershell file.

As you can see below this was pointed at my VC with the cluster used for deployment highlighted.

![MultiHost Holodeck VCF Screenshot](https://jameskilby.co.uk/wp-content/uploads/2024/01/Screenshot-2024-01-19-at-09.08.41-1-1024x545.png)

## Success

With the above in place the full deployment of the 7 vSphere hosts, NSX managers & Edges plus Tanzu is done in 4hr 11 Mins.

![MultiHost Holodeck VCF Screenshot](https://jameskilby.co.uk/wp-content/uploads/2024/01/Screenshot-2024-01-17-at-15.39.41-1024x549.png)Successful Deployment

## Deployment Notes

A few things that catch people out specifically with Holodeck. The first is if you happen to restart the HoloConsole VM before VCF deployment it loses a route. This is by design. When VCF is stood up all external network access is done through the CloudBuilder VM. To fix this run this at the command line on the HoloConsole VM
    
    
    route add 0.0.0.0 mask 0.0.0.0 10.0.0.1

📋 Copy

Another point of note: the CPU’s in my hosts were identical. If you have different generation Intel CPUs or a mix of AMD/Intel then further consideration is likely to be required.

## 📚 Related Posts

  * [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

## Similar Posts

  * [ ![vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

By[James](https://jameskilby.co.uk) November 17, 2023 · Updated June 1, 2026

An Overview of vSAN ESA in VMC 

  * [ ![Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash-768x417.png) ](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

By[James](https://jameskilby.co.uk) January 27, 2026 · Updated June 5, 2026

How to leverage Content Libraries to deploy into VMware Cloud on AWS faster.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated July 11, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [ ![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk) August 14, 2025 · Updated July 11, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk) July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.