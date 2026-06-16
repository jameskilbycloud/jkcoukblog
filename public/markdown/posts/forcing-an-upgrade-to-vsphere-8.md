---
title: "Forcing an Upgrade to vSphere 8"
description: "I run a reasonably extensive homelab that is of course built around the VMware ecosystem."
date: 2022-12-14T21:43:39+00:00
modified: 2026-06-01T19:02:43+00:00
author: James Kilby
categories:
  - Homelab
  - VMware
  - vSphere
  - Networking
  - Storage
  - Synology
  - Runecast
  - VMware Cloud on AWS
  - Ansible
  - Artificial Intelligence
  - Containers
  - Devops
  - NVIDIA
  - Traefik
  - AWS
  - Veeam
tags:
  - #Upgrade
  - #vSphere 8
url: https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/
image: https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.24.32.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

# Forcing an Upgrade to vSphere 8

By[James](https://jameskilby.co.uk) December 14, 2022 · Updated June 1, 2026 • 📖1 min read(283 words)

📅**Published:** December 14, 2022•**Updated:** June 01, 2026

I run a reasonably extensive [homelab](https://jameskilby.co.uk/lab/) that is of course built around the VMware ecosystem. So with the release of vSphere 8 I was obviously going to upgrade, however, a few personal things blocked me from doing it until now. The vCenter upgrade was smooth; however, knowing that some of the hardware I am running is a little dated this was always going to carry a risk.

I tried using lifecycle manager (vLCM) within vCenter but I was faced with the following and I couldn’t see a way to force remediate from within vCenter. Therefore I resorted to doing it from the command line.

![Screenshot 2022 12 14 at 21.24.32](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.24.32-1024x245.png)Host is not compatible

Firstly enable SSH on each of the hosts to be upgraded

Then Allow HTTP traffic in the ESXi firewall
    
    
    esxcli network firewall ruleset set -e true -r httpClient

📋 Copy

The next step is to list the available ESXi profiles using the online depot. In my case, I was looking for ESXi 8.0a
    
    
    esxcli software sources profile list -d https://hostupdate.vmware.com/software/VUM/PRODUCTION/main/vmw-depot-index.xml | grep -i ESXi-8.0a

📋 Copy

Then comes the Install, I had validated that this would be ok by installing from USB to another node. All of the hardware that I needed continued to work as expected with the only significant loss being the Mellanox Connect X-3 40Gb/s adaptor. 
    
    
    esxcli software profile update -p ESXi-8.0a-20842819-standard -d https://hostupdate.vmware.com/software/VUM/PRODUCTION/main/vmw-depot-index.xml --no-hardware-warning

📋 Copy

Update Result

Message: The update completed successfully, but the system needs to be rebooted for the changes to be effective. Reboot Required: true

It also listed all of the newly installed VIB’s 

The last step is to disable the firewall rule and then SSH 
    
    
     esxcli network firewall ruleset set -e false -r httpClient

📋 Copy

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

## Similar Posts

  * [ ![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png) ](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk) June 26, 2024 · Updated June 5, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [ ![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg) ](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk) November 21, 2022 · Updated June 1, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [ ![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png) ](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [ ![New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

By[James](https://jameskilby.co.uk) April 1, 2026 · Updated June 1, 2026

We’ve expanded the VMC fleet with the new i7i (i7i.

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk) February 9, 2026 · Updated June 5, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![Monitoring VMware Cloud on AWS: Tools & Approaches \(Part 1\)](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [AWS](https://jameskilby.co.uk/category/aws/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

### [Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

By[James](https://jameskilby.co.uk) December 17, 2019 · Updated June 5, 2026

As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring.