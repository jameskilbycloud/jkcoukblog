---
title: "Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide"
description: "Step-by-step setup of Nvidia Tesla P4 vGPU on VMware ESXi for a homelab. Drivers, licence server, vGPU profiles, plus gotchas and performance notes."
date: 2023-10-23T14:56:58+00:00
modified: 2026-06-01T19:02:51+00:00
author: James Kilby
categories:
  - Homelab
  - VMware
  - Personal
  - Docker
  - Hosting
  - Kubernetes
  - VMware Cloud on AWS
  - vSphere
  - Ansible
  - Artificial Intelligence
  - Containers
  - Devops
  - NVIDIA
  - Traefik
tags:
  - #Homelab
  - #Nvidia
  - #vGPU
url: https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/
image: https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide

By[James](https://jameskilby.co.uk) October 23, 2023June 1, 2026 • 📖4 min read(862 words)

📅 **Published:** October 23, 2023• **Updated:** June 01, 2026

## Table of Contents

A little while ago I decided to play with vGPU in my homelab. This was something I had dabbled with in the past but never really had the time or need to get working properly. 

The first thing that I needed was a GPU. I did have a Dell T20 with an iGPU built into the CPU but I wanted a more enterprise card for my testing. I therefore decided to pick up a Nvidia Tesla P4 from eBay for the princely sum of £185.

The card stats are not impressive by modern standards but it was good enough for what I needed combined with the fact that it was a single-width PCIe 3.0 x16 card and didn’t require external power. An important note is that this is a passively cooled card so if it’s not located in a server with a reasonable airflow then you may run into some thermal issues. 3D printer fan shrouds are available on eBay to work around this issue.

## Card Stats

GPU 1 NVIDIA Pascal™ GPU  
NVIDIA® CUDA® Cores 2,560  
Memory Size 8 GB GDDR5  
H.264 1080p30 Streams 24  
vGPU Profiles 1 GB, 2 GB, 4 GB, 8 GB  
Form Factor PCle 3.0 single slot  
(low profile) for rack servers  
Power 75 W  
Thermal Solution Passive

In a VMware environment, the first decision is how are you going to use the card? There are two basic modes of operation either GPU pass through where the entire card is passed into a single VM or vGPU where the card can be carved up into multiple gFX cards and be presented to one or more VMs at the same time. It was this latter option that I planned to implement. I wanted at least one node presented through to a Horizon VDI instance. The other node was going to be used as a [Tdarr](https://home.tdarr.io) Node

## Install steps

I installed the card into one of my 4 Supermicro nodes. With the graphics card installed I was limited to the onboard 2xGb Nic’s but that would be sufficient for initial testing. Initial attempts at getting this to work with vSphere 8 seemed to have issues so I rolled this node back to vSphere 7.0u2 as I knew this combo would work.

The first step is to install the drivers into the ESXi Host. This is straightforward and as I was only doing this to a single host I copied the relevant driver to a datastore and then ran the below command to perform the install.
    
    
    esxcli software vib install -v /vmfs/volumes/623a916d-ccad8ff0-0000-000000000000/Nvidia/NVD_bootbank_NVD-VMware_ESXi_7.0.2_Driver_535.54.06-1OEM.702.0.0.17630552.vib

📋 Copy

At the end of the installation, a host reboot is required (even if it says it isn’t).

Once this has been done you should have the ability to add PCI devices with the associated Nvidia Profile as you can see all of the below ones are grid_p4 as this is the card that I am using. 

![Nvidia Tesla P4 Homelab Setup Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/10/Screenshot-2023-10-23-at-15.00.32-1024x435.png)

The Nvidia GPU Software Docs list the capabilities of each profile. I have copied the relevant table below.

Virtual GPU Type| Intended Use Case| Frame Buffer (MB)| Virtual Display Heads| Maximum Resolution per Display Head| Maximum vGPUs per GPU| Maximum vGPUs per Board| Required License Edition  
---|---|---|---|---|---|---|---  
P4-8Q| Virtual Workstations| 8192| 4| 4096×2160| 1| 1| Quadro vDWS  
P4-4Q| Virtual Workstations| 4096| 4| 4096×2160| 2| 2| Quadro vDWS  
P4-2Q| Virtual Workstations| 2048| 4| 4096×2160| 4| 4| Quadro vDWS  
P4-1Q| Virtual Desktops, Virtual Workstations| 1024| 2| 4096×2160| 8| 8| Quadro vDWS  
P4-8C| Training Workloads| 8192| 1| 4096×2160[2](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__c-series-vgpu-graphics-note)| 1| 1| vCS or Quadro vDWS  
P4-4C| Inference Workloads| 4096| 1| 4096×2160[2](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__c-series-vgpu-graphics-note)| 2| 2| vCS or Quadro vDWS  
P4-2B| Virtual Desktops| 2048| 2| 4096×2160| 4| 4| GRID Virtual PC or Quadro vDWS  
P4-2B4| Virtual Desktops| 2048| 4| 2560×1600| 4| 4| GRID Virtual PC or Quadro vDWS  
P4-1B| Virtual Desktops| 1024| 4| 2560×1600| 8| 8| GRID Virtual PC or Quadro vDWS  
P4-1B4| Virtual Desktops| 1024| 1| 4096×2160| 8| 8| GRID Virtual PC or Quadro vDWS  
P4-8A| Virtual Applications| 8192| [4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)1| 1280×1024[4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)| 1| 1| GRID Virtual Application  
P4-4A| Virtual Applications| 4096| 1[4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)| 1280×1024[4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)| 2| 2| GRID Virtual Application  
P4-2A| Virtual Applications| 2048| 1[4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)| 1280×1024[4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)| 4| 4| GRID Virtual Application  
P4-1A| Virtual Applications| 1024| 1[4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)| 1280×1024[4](https://docs.nvidia.com/grid/9.0/grid-vgpu-user-guide/index.html#virtual-gpu-types-grid__a-series-vgpu-max-res-note)| 8| 8| GRID Virtual Application  
  
## VM Provisioning 

With that configured the next step was to provision a VM and use the associated drivers within the VM.

![Nvidia Tesla P4 Homelab Setup Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/10/Screenshot-2023-10-23-at-15.00.07-1024x313.png)

Please note that when utilising PCI passthrough all of the memory must be reserved for the VM.

With the VM running and the drivers installed we can now see the graphics card in Windows.

![Nvidia Tesla P4 Homelab Setup Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/10/Screenshot-2023-10-23-at-15.25.01-1-1024x850.png)

Using GPU-Z we can validate the resources being presented through to the Virtual Machine.

![Nvidia Tesla P4 Homelab Setup Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/10/Screenshot-2023-10-23-at-15.24.54-746x1024.png)

## Folding@Home

As a final step it was worth proving that the GPU can actually be used by the workload. For this I used the folding@home application as can be seen below. 

![Nvidia Tesla P4 Homelab Setup Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/10/Screenshot-2023-10-09-at-17.36.02-1024x408.png)Folding at home slots overview

My Folding@home stats can be seen [here](https://stats.foldingathome.org/donor/69704482) and consider joining your compute to the project as well 

Just a side note that folding@home will use all of the CPU and GPU if you let it. Here is the power utilisation of the node and you can easily see where Folding@Home started.

![Nvidia Tesla P4 Homelab Setup Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/10/Screenshot-2023-10-07-at-14.12.01-1024x273.png)

## 📚 Related Posts

  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)
  * [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [ ![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png) ](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk) September 13, 2020May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.

  * [ ![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png) ](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk) December 9, 2022June 1, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk) July 2, 2020June 1, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup the “i3en”. This is based on the i3en.

  * [ ![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png) ](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk) December 14, 2022June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [ ![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg) ](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James](https://jameskilby.co.uk) February 10, 2019June 1, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk) February 9, 2026May 31, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere