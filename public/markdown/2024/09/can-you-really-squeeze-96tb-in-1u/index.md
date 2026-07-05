---
title: "Can you really squeeze 96TB in 1U ?"
description: "Yes, that’s a clickbait title."
date: 2024-09-12T12:39:16+00:00
modified: 2026-06-01T19:03:02+00:00
author: James Kilby
categories:
  - Homelab
  - Storage
  - TrueNAS Scale
  - Synology
  - Kubernetes
  - Ansible
  - Automation
  - VCF
  - VMware
  - Artificial Intelligence
  - Docker
  - NVIDIA
  - Traefik
  - Github
tags:
  - #Homelab
  - #Storage
url: https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/
image: https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

# Can you really squeeze 96TB in 1U ?

By[James](https://jameskilby.co.uk) September 12, 2024 · Updated June 1, 2026 • 📖4 min read(773 words)

📅**Published:** September 12, 2024•**Updated:** June 01, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy…

I recently saw an advert for a server that was just too good to be true. It promised to bring a huge amount of storage and future options in a quite hard-to-believe 1U. The price it was on offer for was also unreal. I wasn’t looking for a new storage server but knew I would be able to make good use of this one. It would allow me to consolidate a few bits and pieces so it just had to be done…

## Table of Contents

## Intro

The server is a D51PH-1ULH from a vendor called [Quanta Cloud Technology](http://qct.io). They are a vendor that doesn’t seem to be very well known outside of the HyperScalers. It’s described as an Ultra dense storage server and with the capacity for 12×3.5″ plus 4×2.5″ drives it’s hard to argue with that. It also comes with IPMIv2.0 and 2x10Gb SFP+ connections. One really interesting thing is that at first glance the drives don’t look like they are hot-swap. However, the server comes with a giant hard drive tray that slides out the front and then individual drives can be swapped.

The seller also threw in a few 480GB Samsung Enterprise SSDs and 16x8TB Seagate Exos making it the bargain of the century. This allowed me to fully populate the chassis and still have 4 8TB drives spare. I typically don’t like using second-hand storage but in this instance, I was willing to make an exception.

![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/08/IMG_7063-744x1024.jpeg)Server shortly before being installed in my Rack

## OS Setup

I have stuck with TrueNAS Scale as the OS of choice for my dedicated storage systems. It’s something I’m familiar with and served my needs in the past well. However, I have decided to leave this as primarily a pure “Storage Server”. The available storage will be served out as a mixture of iSCSI, NFS, and SMB natively by TrueNAS and then I will run a MINIO container on top to offer S3-based object services.

## Hardware

I swapped out the 480GB Samsung drives for some larger 2TB consumer-based drives. The current configuration is listed below.

The servers also included rails which was a much appreciated benefit. The only downside is I underestimated just how long these servers are. The good news is I can adjust my Startech rack to make it longer and accommodate this. The downside is I need to derack the rest of my gear to do it. So for now it’s sitting on top of one of my other Supermicro servers.

CPU| 2x Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz  
---|---  
Memory | 256 DDR4  
Boot Device | 32 GB SATADom  
HDD | 12x ST8000NM0075 8TB 12Gb SAS  
SSD | 3x2TB Samsung Evo  
NIC | 2x 25Gb  
  
## Pool Configuration

For performance reasons, I have chosen to go with 6x Mirrored vDevs 2x wide. Conceptually this is similar to RAID 10. This uses all 12 of the 3.5-inch drives in a single pool. This gives a usable pool capacity of just under 43.5TB

Although I lose 50% of the usable capacity I wanted the write performance that this gives

This is then complemented by three 2TB SSDs being used as L2ARC (Read cache) and as I have so much read cache the drives basically just do writes.

## Performance

I haven’t bothered benchmarking the setup from a performance perspective as I have actual workloads on it that would be annoying to move. However, from what I am seeing in the latency graphs of vCenter I am happy with the results.

As you can see below the ARC is holding all of the really hot data in RAM.

![Can you really squeeze 96TB in 1U ? Screenshot](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-08-29-at-10.02.01.png)

The warm data is being served from the 6TB of SSD in the server, however it has not finished warming up yet. The L2ARC data can also be compressed so the reality is that it’s probably closer to the equivalent of 12TB.

![L2ARC Warming up](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-09-11-at-15.07.42-1024x203.png)L2ARC Warming up

A benefit of TrueNAS Scale is that the L2ARC persists between reboots. Otherwise, it would take a very long time to finish warming up with my workload.

This means the performance graphs of the actual disks tend to look like this. Only two are shown but all of the main drives appear like this. Yes, there are some reads (Blue) but the majority of the time they are only doing writes ( Pink) for the system.

![Can you really squeeze 96TB in 1U ? Screenshot](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-09-10-at-11.32.39-1024x513.png)

## Upgrades:

### SATADom

I have managed to source a compatible SATADom (32GB rather than the 128GB Partcode SD131C-032GM-JM-A) I was looking for. The migration of the TrueNAS install was super smooth.

### Networking

I have also upgraded the NIC to a Quanta ConnectX-4 LX Dual-Port 25GbE 

![s l1600 1](https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600-1-1024x537.jpg)

## 📚 Related Posts

  * [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)
  * [My First Homelab Storage Setup: HP Gen8 &#038; Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)
  * [Homelab Storage Upgrade: Synology DS918 for VMware &#038; NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

## Similar Posts

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [My First Homelab Storage Setup: HP Gen8 & Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below.

  * [ ![TrueNAS Logo](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2023-05-22-at-18.49.21-768x198.png) ](https://jameskilby.co.uk/2023/11/truenas-scale-useful-commands/)

[Kubernetes](https://jameskilby.co.uk/category/kubernetes/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [TrueNAS Scale CLI Reference: Storage & Kubernetes Commands](https://jameskilby.co.uk/2023/11/truenas-scale-useful-commands/)

By[James](https://jameskilby.co.uk) November 13, 2023 · Updated April 11, 2026

A list of useful Truenas Scale commands

  * [ ![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png) ](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk) April 15, 2026 · Updated June 1, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introduction One of the larger costs of running my homelab is the electricity….

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk) March 27, 2026 · Updated May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [ ![Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/wp-content/uploads/2026/04/packer-github-actions-vsphere-pipeline-768x452.png) ](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Github](https://jameskilby.co.uk/category/github/)

### [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

By[James](https://jameskilby.co.uk) April 30, 2026 · Updated June 5, 2026

A walk-through of an automated golden-image pipeline for vSphere: HashiCorp Packer builds six Ubuntu LTS templates (22.04, 24.04, 26.04 — server and desktop) driven by three GitHub Actions workflows covering PR validation, parallel template builds, and ISO management via a self-hosted runner.