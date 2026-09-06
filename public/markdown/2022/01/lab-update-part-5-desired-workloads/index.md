---
title: "Lab Update – Desired Workloads"
description: "My lab is always undergoing change. Partially as I want to try new things or new ways of doing things."
date: 2022-01-06T19:23:11+00:00
modified: 2026-06-01T19:02:36+00:00
author: James Kilby
categories:
  - Homelab
  - Veeam
  - VMware
  - Networking
  - Storage
  - Artificial Intelligence
  - Docker
  - VMware Cloud on AWS
tags:
  - #Desired State
  - #Homelab
  - #VMware
url: https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/
image: https://jameskilby.co.uk/wp-content/uploads/2025/12/ChatGPT-Image-Dec-17-2025-at-09_03_10-PM.png
---

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Lab Update – Desired Workloads

By[James](https://jameskilby.co.uk) January 6, 2022 · Updated June 1, 2026 • 📖1 min read(141 words)

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things. Sometimes because I break things (not always by accident); sometimes it’s a great way to learn…

I decided to list the workloads I am looking to run (some of these are already in place)

## Infrastructure

Active Directory – Done

vRealize Lifecycle Manager – Done

vRealize Operations Manager – Done

vRealize Log Insight

vRealize Network Insight

Vault

SecretServer

Nutanix CE

Hyper-V

Tanzu CE

VMware Horizon – Done

VMware HCX

vCloud Director

VMware Cloud Foundation

Docker

K8s

K3s

## Networking

PFsense – Done

Sophos UTM – Done

Avi

## Monitoring

Grafana

Runecast

Veeam One

## Backups/Recovery

Veeam Backup & Replication

Veeam Service Provider Console

VMware Cloud Disaster Recovery

SRM

## Storage

TrueNAS

HP Store Once

Minio

AWS Storage Gateway

## Automation

VMware Event Broker

vRealize Automation

VMware Orchestrator

## 📚 Related Posts

  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [Homelab Compute Upgrade: SuperMicro BigTwin &#038; vSphere Setup](https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/)
  * [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

## Similar Posts

  * [ ![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png) ](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk) June 26, 2024 · Updated July 11, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [ ![TrueNAS Logo](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2023-05-22-at-18.49.21-768x198.png) ](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Homelab Storage Refresh (Part 1)](https://jameskilby.co.uk/2023/05/homelab-storage-refresh-part-1/)

By[James](https://jameskilby.co.uk) May 23, 2023 · Updated July 11, 2026

Table of Contents Background ZFS Overview Read Cache (ARC and L2ARC) ZIL (ZFS Intent Log) Hardware Background I have just completed the move of all my production and media-based storage/services to TrueNAS Scale. ( I will just refer to this as TrueNAS) This is based on my HP Z840 and I have now retired my…

  * [ ![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg) ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk) October 11, 2024 · Updated July 11, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [ ![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast-768x219.webp) ](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Unleashing the UDM Beast](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

By[James](https://jameskilby.co.uk) June 20, 2026 · Updated August 24, 2026

Retiring my ageing WatchGuard M200, I swap in the UniFi UDM Beast — a hardware tour, first iperf and WAN tests, the BGP/FRR setup, and the homelab services I’m consolidating onto it.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [My First Homelab Storage Setup: HP Gen8 & Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC