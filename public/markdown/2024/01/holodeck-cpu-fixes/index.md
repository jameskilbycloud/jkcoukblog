---
title: "VMware Holodeck on Older CPUs: Fixing Compatibility Issues"
description: "Disclaimer: This is not a supported configuration by the Holodeck team please don't reach out to them for help."
date: 2024-01-18T14:37:04+00:00
modified: 2026-06-01T19:02:57+00:00
author: James Kilby
categories:
  - VCF
  - VMware
  - VMware Cloud on AWS
  - Ansible
  - Automation
  - Personal
  - Homelab
  - Hosting
tags:
  - #CPU
  - #Holodeck
  - #Homelab
  - #VMware
url: https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/
image: https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743.jpg)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# VMware Holodeck on Older CPUs: Fixing Compatibility Issues

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026 • 📖1 min read(268 words)

Disclaimer: This is **not** a supported configuration by the Holodeck team, please don’t reach out to them for help. No support will be given for running CPUs without the required feature sets.

## Table of Contents

In my [previous post](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/) about my Holodeck experience, I mentioned that I had some issues due to the age of the physical CPUs in the hosts that I was using to run Holodeck. This error will manifest itself in three places during the deployment.

  * Nested ESX Power On
  * vCLS machine deployment
  * NSX Edge deployment

## Nested ESX Power On

Obviously, my CPUs are not supported for ESXi 8.0.1 and when the host is powered on you will see the image below. 

![ESXi unsupported error](https://jameskilby.co.uk/wp-content/uploads/2023/09/Screenshot-2023-09-27-at-12.55.09.png)

Just like with a physical host, it is possible to override this. 

This is done by adding 
    
    
    --ignoreprereqwarnings --ignoreprereqerrors --forceunsupportedinstall

📋 Copy

to the VLCGUI.ps1 script.

For the same reasons when the cluster is built and the vCLS VMs for DRS are deployed, they will fail to power on. 

## NSX Edge

![Holodeck CPU Fixes Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/10/Screenshot-2023-10-02-at-14.28.25.png)

And last of all when the NSX edges attempt to power on they will fail due to the lack of a feature in the CPU called 1G huge page support. These issues can manifest when deploying NSX outside of VCF so a lot has been written about these issues and how to overcome them.

## Solution

Luckily, a colleague of mine, Tim Sommer, has made all of the required changes to the VLCGUI.ps1 deployment script and that is available [here ](https://ent.box.com/s/u4wiwh2mq8o05ct8e67ndapvxhudkhe2)

I have tried this multiple times and I have had a 100% success rate with the deployment with no manual fixes being required.

## 📚 Related Posts

  * [VMware Holodeck Multi-Host VCF: Lab Setup &#038; Configuration](https://jameskilby.co.uk/2024/01/multihost-holodeck-vcf/)
  * [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)
  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

## Similar Posts

  * [ ![vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

By[James](https://jameskilby.co.uk) November 17, 2023 · Updated June 1, 2026

An Overview of vSAN ESA in VMC 

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk) July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg) ](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk) October 11, 2022 · Updated June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [ ![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg) ](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James](https://jameskilby.co.uk) February 10, 2019 · Updated June 5, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.