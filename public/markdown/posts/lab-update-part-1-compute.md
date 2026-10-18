---
title: "Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup"
description: "Quite a few changes have happened in the lab recently. I decided to do a multipart blog on the changes."
date: 2022-01-06T11:12:00+00:00
modified: 2026-02-16T16:15:03+00:00
author: James Kilby
categories:
  - Homelab
  - VMware
  - Ansible
  - Automation
  - Artificial Intelligence
  - Docker
  - Networking
  - Personal
tags:
  - #Homelab
  - #Supermicro
  - #VMware
url: https://jameskilby.co.uk/2022/01/lab-update-part-1-compute/
image: https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_4536-scaled-1-768x1024.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_4536-scaled-1.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Homelab Compute Upgrade: SuperMicro BigTwin & vSphere Setup

By[James](https://jameskilby.co.uk) January 6, 2022 · Updated February 16, 2026 • 📖1 min read(223 words)

Quite a few changes have happened in the lab recently, so I decided to do a multipart blog on the changes.

The refresh was triggered by the purchase of a SuperMicro Server ([2027TR-H71FRF](https://www.supermicro.com/products/system/2U/2027/SYS-2027TR-H71FRF.cfm)) chassis with 4x X9DRT Nodes / Blades. This is known as a BigTwin configuration in SuperMicro parlance. This is something I was very familiar with as most of the Nutanix nodes that we deployed at Zen were of this design.

Each node has 2x Intel Xeon CPU E5-2670 @ 2.60GHz. 3 Nodes have 192GB of RAM and 1 has 128GB giving a combined 64c/128t and 704GB of RAM. Quite an amount to be squeezed into 2U.

This is a huge uplift in compute resources so is more than welcome. I also decided to put what I could in a proper rack and purchased a Startech 25U rack to mount it.

![Lab Update - Compute](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_4536-scaled-1-768x1024.jpg) One of the Compute nodes was removed from the server…

The plan is also to make a serious network investment (to move me away from 1Gb) but I haven’t completely decided what that will look like. This will likely be the final investment for a while.

With the additional Supermicro compute available, I have made the Z840 a sort of standalone node. I will keep it around as it’s the only thing capable of running my Nvidia K2. 

## 📚 Related Posts

  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [Lab Update &#8211; Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)
  * [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

## Similar Posts

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg) ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk) October 11, 2024 · Updated July 11, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [ ![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png) ](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk) December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk) October 23, 2023 · Updated July 11, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [ ![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png) ](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk) June 26, 2024 · Updated July 11, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [ ![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png) ](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk) September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.