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
  - Storage
  - vExpert
  - Synology
  - Veeam
  - Personal
  - Hosting
  - Ansible
tags:
  - #Upgrade
  - #vSphere 8
url: https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/
image: https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.24.32.png
---

![Screenshot 2022 12 14 At 21.45.23](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

# Forcing an Upgrade to vSphere 8

By[James](https://jameskilby.co.uk)December 14, 2022 · Updated June 1, 2026 • 📖1 min read(283 words)

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

  * [![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png)](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk)April 17, 2023 · Updated June 1, 2026

I have been a VMware vExpert for many years and it has brought me many benefits over the years.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [My First Homelab Storage Setup: HP Gen8 & Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

By[James](https://jameskilby.co.uk)January 6, 2018 · Updated June 1, 2026

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Lab Update – Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

By[James](https://jameskilby.co.uk)January 6, 2022 · Updated June 1, 2026

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things.

  * [![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png)](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk)September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.

  * [![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg)](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk)October 11, 2022 · Updated June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png)](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk)September 2, 2025 · Updated June 5, 2026

An intro on how I use SemaphoreUI to manage my Homelab