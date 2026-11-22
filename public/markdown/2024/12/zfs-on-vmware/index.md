---
title: "How to Run ZFS on VMware vSphere: Setup Guide and Best Practices"
description: "Running ZFS on VMware vSphere without HBA passthrough: when it makes sense, and how to handle copy-on-write, stable disk IDs and TRIM."
date: 2024-12-18T17:47:57+00:00
modified: 2026-11-17T08:08:20+00:00
author: James Kilby
categories:
  - TrueNAS Scale
  - VMware
  - vSAN
  - vSphere
  - Homelab
  - Networking
  - Nutanix
  - VMware Cloud on AWS
  - Ansible
  - Automation
  - Veeam
tags:
  - #Homelab
  - #Trim
  - #UNMAP
  - #VMware
  - #ZFS
url: https://jameskilby.co.uk/2024/12/zfs-on-vmware/
image: https://jameskilby.co.uk/wp-content/uploads/2024/12/IMG_20140330_210511-1024x845.jpeg
---

![ZFS logo](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

# How to Run ZFS on VMware vSphere: Setup Guide and Best Practices

By[James Kilby](https://jameskilby.co.uk) December 18, 2024 · Updated November 17, 2026 • 📖3 min read(531 words)

## Table of Contents

## Introduction

I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010. The image below is my lab at the time with an IBM head unit that I think had 18GB of RAM 6x450GB SAS drives and this was then connected to the Dell PowerVault SCSI Array above it with 14x146GB 10K SAS drives….

![How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/wp-content/uploads/2024/12/IMG_20140330_210511-1024x845.jpeg)Original Nexenta Setup

The number one rule is to ALWAYS give ZFS access to the underlying raw storage. You don’t want a raid controller or anything else interfering with the IO path. This is similar to how vSAN works with VMware.

But rules are meant to be broken right….. 

I have virtualized a few copies of TrueNAS Scale and Core using ZFS on top of VMware. In these particular instances I specifically DON’T want to pass through the storage HBA. Why would I do this? Mainly for two reasons. This allows me to test upgrades of my physical TrueNAS setup with an easy rollback if needed by not passing the drives or controllers in I can clone and snapshot the VMs just as if it was any other and move it around my lab infrastructure.

## Copy on Write

ZFS is a “Copy on Write” file system which means that it never overwrites existing blocks of storage. It always places writes into new blocks. This is unfriendly with “thin provisioning” something I am a huge fan of. This means that over time even a tiny database writing one megabyte file over and over again will slowly clog the entire file system.

So if you’re going to break the rules. The way I see it is you might as well do it properly

The first requirement is that the VMs be provisioned with thin disks in vSphere. If it is not thin then unmap won’t work. This is important in case you are thin at the underlay storage level.

## Disk IDs

What you also need to do is to ensure that TrueNAS can see unique disk IDs. To do this shut down the VM’s and add the following parameter to the VMware VM’s configuration
    
    
     disk.EnableUUID=TRUE

📋 Copy

Once this is done when you power the VM’s on you should be able to see unique serials of each disk similar to this screenshot. Prior to this change, the serial section is blank.

![Disk list showing drive serial numbers](https://jameskilby.co.uk/wp-content/uploads/2024/12/Disk-Serials-1024x125.png)

## Trim

Once the disks are seen as unique it is possible to enable trim. To confirm that trim is working execute the below command. ( I have no idea why this is a blocker but it is)
    
    
    Sudo pool trim Pool-1

📋 Copy

I decided to manually enable it by executing the command in the shell. (my Pool is called Pool-1)

To confirm that trim is working, execute the below command
    
    
    sudo zpool status Pool-1

📋 Copy

If everything is working you will see trimming running next to the pool.

![Terminal output of zpool trim and zpool status on TrueNAS](https://jameskilby.co.uk/wp-content/uploads/2024/12/trimming-1-1024x452.png)

A further validation that this is working is to review the VM’s storage used, see the before and after of this VM’s storage

![VM usage before the change: 0 MHz CPU, 0 MB memory, 209.15 GB storage](https://jameskilby.co.uk/wp-content/uploads/2024/12/vm-Before-2.png) ![VM usage after the change: 1.014 GHz CPU, 1.92 GB memory, 48.23 GB storage](https://jameskilby.co.uk/wp-content/uploads/2024/12/vm-After.png)

Additional confirmation can be seen by reviewing the underlying (vSAN consumption in this case). Before and after listed below.

![vSAN capacity before: 2.91 TB used of 7.42 TB](https://jameskilby.co.uk/wp-content/uploads/2024/12/vSAN-Before.png) ![vSAN capacity after: 2.33 TB used of 7.42 TB](https://jameskilby.co.uk/wp-content/uploads/2024/12/vSAN-After-1.png)

## 📚 Related Posts

  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)
  * [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

## Similar Posts

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)

By[James Kilby](https://jameskilby.co.uk) January 6, 2022 · Updated May 31, 2026

I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes.

  * [ ![Front of a Nutanix-branded SuperMicro BigTwin chassis](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg) ](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James Kilby](https://jameskilby.co.uk) July 2, 2024 · Updated November 16, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James Kilby](https://jameskilby.co.uk) July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.

  * [ ![VMware by Broadcom and AWS logos](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James Kilby](https://jameskilby.co.uk) August 14, 2025 · Updated November 15, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png) ](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James Kilby](https://jameskilby.co.uk) April 15, 2026 · Updated June 1, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introduction One of the larger costs of running my homelab is the electricity….

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

### [Lab Update – Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

By[James Kilby](https://jameskilby.co.uk) January 6, 2022 · Updated June 1, 2026

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things.