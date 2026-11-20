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
  - Artificial Intelligence
  - Docker
  - Personal
  - Kubernetes
  - VMware Cloud on AWS
  - Homelab
  - Storage
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

  * [ ![Abstract illustration of a hand touching a digital network](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg) ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James Kilby](https://jameskilby.co.uk) October 11, 2024 · Updated November 17, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [ ![RNLI Lifeboats logo](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png) ](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James Kilby](https://jameskilby.co.uk) October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [ ![TrueNAS Logo](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2023-05-22-at-18.49.21-768x198.png) ](https://jameskilby.co.uk/2023/11/truenas-scale-useful-commands/)

[Kubernetes](https://jameskilby.co.uk/category/kubernetes/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [TrueNAS Scale CLI Reference: Storage & Kubernetes Commands](https://jameskilby.co.uk/2023/11/truenas-scale-useful-commands/)

By[James Kilby](https://jameskilby.co.uk) November 13, 2023 · Updated April 11, 2026

A list of useful Truenas Scale commands

  * [ ![VMware by Broadcom and AWS logos](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James Kilby](https://jameskilby.co.uk) August 14, 2025 · Updated November 15, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![Shattered hard disk platter](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg) ](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James Kilby](https://jameskilby.co.uk) November 21, 2022 · Updated November 16, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [ ![QuantaGrid SD1Q-1ULH 1U server](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png) ](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James Kilby](https://jameskilby.co.uk) September 12, 2024 · Updated November 16, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.