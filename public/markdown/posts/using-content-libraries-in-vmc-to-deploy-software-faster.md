---
title: "Using Content Libraries in VMC to deploy software faster"
description: "Learn how to use VMware Content Libraries in VMware Cloud on AWS (VMC) to speed up template and VM deployments, reducing manual steps and improving consistency."
date: 2026-01-27T22:19:39+00:00
modified: 2026-03-12T21:52:11+00:00
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
  - Storage
  - vExpert
  - Automation
  - Docker
  - Personal
tags:
  - #Content Library
  - #VMC
  - #VMware
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/
image: https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash.png
---

![Firefly Gemini Flash](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# Using Content Libraries in VMC to deploy software faster

By[James](https://jameskilby.co.uk)January 27, 2026March 12, 2026 • 📖5 min read(975 words)

📅 **Published:** January 27, 2026• **Updated:** March 12, 2026

As part of my role spinning up new SDDC’s to test things is quite a common occurrence. This is both a blessing and a curse. The new SDDC is 100% Vanilla and perfectly self contained. Therefore you can do the testing required, knowing that you won’t impact anything else and you’re not inheriting a legacy setting from previous testing.

However the downside is you need to get the configuration and the software you require into the SDDC. This can take some time. For configuration it’s possible to use IAC tools like Terraform. To speed up the process of deploying software I decided to leverage Content Library specifically for this task. This is a much faster and more reliable way to get what I need into the SDDC.

William Lam has previously [written ](https://williamlam.com/2018/07/creating-a-vsphere-content-library-directly-on-amazon-s3.html#google_vignette)about ways of doing this by utilising AWS S3 as the backend

## Table of Contents

## Prerequisites

  *  **On-premises vCenter** — a local vCenter instance to act as the publishing source. Any version supporting Content Library publish/subscribe (vSphere 6.0+) will work.
  *  **VMware Cloud on AWS SDDC** — the destination environment. The subscribing Content Library is created here.
  *  **Network connectivity between source and destination** — on-premises vCenter must be able to reach the VMC management network over HTTPS (TCP 443). Typically achieved via a Direct Connect or VPN connection to the VMC Management CIDR.
  *  **Firewall rules** — outbound TCP 443 from on-prem vCenter to the VMC vCenter IP, and the reverse for subscription synchronisation. Check your NSX gateway firewall in the VMC SDDC.
  *  **Storage capacity in VMC** — the Content Library occupies space on the VMC datastore. Factor in the size of your ISOs and OVF templates before enabling immediate sync.
  *  **vCenter credentials** — a user account with the _Content Library > Create local library_ and _Content Library > Create subscribed library_ privileges on both vCenter instances.

## Introduction

For those unfamiliar with Content Libraries they are a storage medium for storing templates and ISO files for easy use within a vCentre environment or sharing with other vCentres. You can see some of the recent updates to this feature [here](https://blogs.vmware.com/cloud-foundation/2020/01/22/creating-and-using-content-library/)

## Networking

For this to work you need network connectivity between the source and destination vCentre. For my use case I use my on premises vCentre as the source and VMC as the destination. However you can use VMC as the source if preferable.

![Content Library Flow](https://jameskilby.co.uk/wp-content/uploads/2026/01/ContentLibraryFlow-1024x358.png)

Usually I don’t utilise/DX for this although It will absolutely work over those connections and would be purely private IP

I have a NAT rule on one of my public IP’s on my Onprem Watchguard Firewall to connect through to the Onprem vCentre. The URL of my vCentre will publicly resolve to this IP. I have restricted this connection to only allow from the public IP of the VMC vCentre. For the VMC vCentre there shouldn’t be any changes required as outbound https is allowed by default on the management gateway.

### Create Publishing Content Library

I already use content libraries extensively in my lab and didn’t need everything uploading to VMC. So I created a new Library just for this purpose and added some select software. If you don’t have a content library or need to create another one. These are the steps you will need to follow.

To create a new Library from the vSphere Client from the top menu select **Content Libraries**

![Content Libary](https://jameskilby.co.uk/wp-content/uploads/2026/01/ContentLibary-1024x368.png)

Name the Content Library appropriately and add a description.

![Name Location](https://jameskilby.co.uk/wp-content/uploads/2026/01/NameLocation-1024x440.png)

Configure the Content Library

As this will be the source Content Library we will set this to be a local content library and then enable the publishing feature to allow other vCentre’s to subscribe to this. I choose not to use authentication for this purpose as there is nothing sensitive 

![Configure Content Library](https://jameskilby.co.uk/wp-content/uploads/2026/01/ConfigureContentLibrary-1024x631.png)

The next step is to define what Datastore the Content Library will reside on.

Here I am using my datastore called “ISO” as it saves my valuable NVMe datastore for workloads.

![Select Storage](https://jameskilby.co.uk/wp-content/uploads/2026/01/Select-Storage-1024x481.png)

Ready to complete

![Ready To Complete](https://jameskilby.co.uk/wp-content/uploads/2026/01/ReadyToComplete-1024x507.png)

Complete the creation and then go back into the Content Library settings. It will show you a Subscription URL which we will need later. Take a copy of the full Subscription URL

![Complete With Url](https://jameskilby.co.uk/wp-content/uploads/2026/01/CompleteWithUrl-1024x558.png)

### Create Subscribing Content Library

We need to repeat the procedure in VMC however now we need to create a Subscribed Content Library. Input the URL that we saved earlier

<https://uk-bhr-p-vc-1.jameskilby.cloud:443/cls/vcsp/lib/165734dc-81a8-464a-bbe5-a99e4ae597da/lib.json>

![VMC Subscriber](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMCSubscriber-1024x906.png)

## Download content option

There are two options for how you want the Subscribed Content Library to behave on first connection/new content. The first is to synchronise the content as soon as possible. This is what I use. However if you have a large catalogue and not all items are required in the VMC vCentre an option to save storage would be to only download content on demand. The downside to this option is that deployed would take longer, waiting for the item to synchronise before it can be used. 

## Conclusion

Content Libraries are one of those VMware features that solve a real operational pain point without much ceremony. Once the publishing/subscribing relationship is established between your on-premises vCenter and VMC, getting ISOs and OVF templates into a fresh SDDC drops from a manual upload process to a few clicks — or nothing at all if you enable immediate synchronisation.

The main trade-off to consider is storage vs. speed. Immediate sync keeps everything local and ready to deploy instantly, but it consumes datastore space even for templates you may never use in a given SDDC. On-demand download is more storage-efficient and works well when you spin up SDDCs infrequently, though the first deployment of any template will wait for the download to complete. For testing environments where time matters, I lean towards immediate sync for the templates I know I’ll use frequently, and on-demand for everything else.

If you’re already using Content Libraries on-premises, adding VMC as a subscriber takes under ten minutes. If you’re not using them yet, this is a good reason to start.

## 📚 Related Posts

  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)
  * [Automating the deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)
  * [vSAN Cluster Shutdown &#8211; Orchestration](https://jameskilby.co.uk/2025/12/vsan-cluster-shutdown/)

## Similar Posts

  * [![Automating the deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png)](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk)February 9, 2026March 15, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [![Intel Optane NVMe Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png)](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Intel Optane NVMe Homelab](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk)April 17, 2023October 1, 2025

I have been a VMware vExpert for many years and it has brought me many many benefits over the years. I don’t think it’s an understatement to say I probably wouldn’t have my current role within VMware without it. One of the best benefits has been access to a huge amount of licences for VMware…

  * [![My Self-Hosted AI Stack: Architecture Overview \(Part 1\)](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk)March 27, 2026March 27, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png)](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk)September 13, 2020March 10, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.20). I won’t go into any details of the contents but I will comment that I felt the questions were fair and that there wasn’t anything in it to trip you up. The required knowledge was certainly wider than the vSAN specialist exam. This…

  * [![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png)](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk)August 14, 2025March 10, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison. All of this data Is publicly available. I have just collated into a single page I3.metal I3en.metal I4i.metal CPU Processor Name Intel Xeon E5-2686 v4 Intel Xeon Platinum 8175 Intel Xeon 8375c No of…

  * [![VMC New Host -i3en](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png)](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMC New Host -i3en](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk)July 2, 2020July 10, 2024

VMware Cloud on AWS (VMC) has introduced a new host to its lineup the “i3en”. This is based on the i3en.metal AWS instance. The specifications are certainly impressive packing in 96 logical cores, 768GiB RAM, and approximately 45.84 TiB of NVMe raw storage capacity per host. It’s certainly a monster with a 266% uplift in…