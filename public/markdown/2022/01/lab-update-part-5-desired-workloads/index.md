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
  - VCF
  - Networking
  - Mikrotik
  - VMware Cloud on AWS
  - Ansible
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

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [ ![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast-768x219.webp) ](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Unleashing the UDM Beast](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

By[James](https://jameskilby.co.uk) June 20, 2026 · Updated August 24, 2026

Retiring my ageing WatchGuard M200, I swap in the UniFi UDM Beast — a hardware tour, first iperf and WAN tests, the BGP/FRR setup, and the homelab services I’m consolidating onto it.

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk) October 23, 2023 · Updated July 11, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [ ![CRS-504](https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600-768x427.jpg) ](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

[Mikrotik](https://jameskilby.co.uk/category/mikrotik/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

By[James](https://jameskilby.co.uk) September 9, 2024 · Updated June 5, 2026

My journey to superfast networking in my homelab

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [ ![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png) ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk) September 2, 2025 · Updated June 5, 2026

An intro on how I use SemaphoreUI to manage my Homelab