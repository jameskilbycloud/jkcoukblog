---
title: "VMware Holodeck Multi-Host VCF: Lab Setup & Configuration"
description: "MultiHost Holodeck VCF offers insights on deploying VMware Holodeck across multiple hosts. Learn more about the setup and specifications today!"
date: 2024-01-17T17:29:38+00:00
modified: 2026-04-11T09:00:47+00:00
author: James Kilby
categories:
  - VMware
  - VCF
  - Homelab
  - Networking
  - Storage
  - Artificial Intelligence
  - Automation
  - Docker
  - NVIDIA
  - Traefik
  - Nutanix
  - Ansible
  - Containers
  - Devops
  - Personal
  - vSphere
  - Veeam
tags:
  - #Holodeck
  - #MultiHost
  - #VCF
  - #VMware
url: https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/
image: https://jameskilby.co.uk/wp-content/uploads/2023/12/Holodeck-Overview.png
---

![Holodeck Overview](https://jameskilby.co.uk/wp-content/uploads/2023/12/Holodeck-Overview.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/)

# VMware Holodeck Multi-Host VCF: Lab Setup & Configuration

By[James](https://jameskilby.co.uk)January 17, 2024April 11, 2026 • 📖4 min read(891 words)

📅 **Published:** January 17, 2024• **Updated:** April 11, 2026

Disclaimer: This is **not** a supported configuration by the Holodeck team please don’t reach out to them for help. As of today the only way to run Holodeck and receive support is to do it on a single compute node.

## Table of Contents

The [VCF Holodeck](https://core.vmware.com/introducing-holodeck-toolkit) toolkit is an excellent tool for learning not just VCF but a lot of technology that can be run on top of it. e.g. HCX, Tanzu vRA etc. Several guides have been written to assist with that.

However, the downside is that you need a single large fast vSphere host to run it on. The minimum specs are listed below for a few different configuration options. This shouldn’t be a challenge for a company or partner to provide but as a homelab enthusiast, this was always going to be a challenge. Many folks I know can cover the below resource requirements with the homelab they have. But the challenge is doing this with a single node. This was also going to be an issue for me. Therefore I needed to come up with a plan to make this work across at least 2 hosts….

## Holodeck recommended specifications

Minimum Hardware (1 env)| Recommended Hardware (2 envs)| Recommended Hardware (3-5 envs)  
---|---|---  
VCF Consolidated | VCF Standard (MGMT + WLD)| VCF Standard (MGMT + WLD)  
2 sockets – Total 16 cores| 2 sockets – Total 32 core| 2 sockets – Total 64 cores  
384 GB RAM| 1024 GB RAM| 1.5 TB RAM  
3.5 TB SSD Disk| 2 – 3.5 TB SSD Disk| 4 – 3.5TB SSD Disks  
  
I was planning to use two of my existing Supermicro hosts that were already connected to my vCenter. They each have 2x Intel Xeon CPU E5-2670 @ 2.60GHz with 192GB of RAM each. The combined resources should be enough to run Holodeck and experiment with other toolsets on top. All of the storage is to be presented by my [TrueNas](https://jameskilby.co.uk/lab/) setup.

## Networking

Both hosts were originally connected through a DVSwitch and 2x25Gb/s physical adaptors. To change the configuration for Holodeck I removed one of the adaptors in each host from the DVswitch. I then followed the Holodeck guide and configured the standard switch as required on each host. I then added the unused 25Gb/s adaptor to the standard switch and then physically connected the two hosts with a short DAC cable as seen below.

![MultiHost Holodeck VCF](https://jameskilby.co.uk/wp-content/uploads/2024/01/IMG_5286-1-1024x996.jpeg)Physical Network![Standard Switch](https://jameskilby.co.uk/wp-content/uploads/2024/01/Standard-Switch-1024x299.png)Standard Switch configuration

## DNS

Holodeck can be deployed either directly to an ESX Host or through a vCenter. As my VC and Hosts are part of the jameskilby.cloud domain I needed to ensure that the private IPs were being returned to the Holodeck Console VM for deployment. This can be handled in several ways however I believe the most elegant is to edit the holohosts.txt file on the HoloBuilder VM. This host file is copied over to the HoloConsole VM as part of the deployment and therefore the builder can always resolve the correct IP’s irrespective of the state of the DNS on the CloudBuilder/HoloConsole VM.

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

With the above in place the full deployment of the 7 vSphere hosts. NSX managers & Edges plus Tanzu is done in 4hr 11 Mins.

![MultiHost Holodeck VCF Screenshot](https://jameskilby.co.uk/wp-content/uploads/2024/01/Screenshot-2024-01-17-at-15.39.41-1024x549.png)Successful Deployment

## Deployment Notes

A few things that catch people out specifically with Holodeck. The first is if you happen to restart the HoloConsole VM before VCF deployment it loses a route. This is by design. When VCF is stood up all external network access is done through the CloudBuilder VM. To fix this run this at the command line on the HoloConsole VM
    
    
    route add 0.0.0.0 mask 0.0.0.0 10.0.0.1

📋 Copy

Another point of note. The CPU’s in my hosts were identical. If you have different generation Intel CPU’s or a mix of AMD/Intel then further consideration is likely to be required.

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

## Similar Posts

  * [![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png)](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk)December 19, 2022April 11, 2026

For a while, I’ve been looking to update the networking at the core of my homelab. I have had some great results with the current setup utilising a number of DAC’s but there were a couple of things that were annoying me. Then MikroTik dropped the CRS504-4XQ-IN and if the price wasn’t horrendous then that…

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk)March 27, 2026April 10, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg)](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk)July 2, 2024April 11, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul. The below post describes what I bought why and how I have configured it. Table of Contents Node Choice Bill of Materials Rescue IPMI…

  * [![Automating the deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png)](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk)February 9, 2026March 15, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png)](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk)November 10, 2023March 10, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal. I had some downtime and decided to use one of the three exam vouchers VMware give me each year. This upgrades me to a…

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Lab Update – Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

By[James](https://jameskilby.co.uk)January 6, 2022March 10, 2026

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things. Sometimes because I break things (not always by accident) sometimes it’s a great way to learn…. I decided to list the workloads I am looking to run (some of these are already in place) Infrastucture…