---
title: "Template Deployment with Packer"
description: "How I got HashiCorp Packer set up on macOS to automate VMware template deployment — including the vSphere datacenter error I hit and how I fixed it."
date: 2021-01-21T22:26:10+00:00
modified: 2026-06-05T19:02:09+00:00
author: James Kilby
categories:
  - Automation
  - Homelab
  - VMware
  - Artificial Intelligence
  - vSphere
  - Veeam
  - Personal
  - VMware Cloud on AWS
  - Storage
tags:
  - #Automation
  - #Hashicorp
  - #Homelab
  - #packer
url: https://jameskilby.co.uk/2021/01/hashicorp-packer/
image: https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Template Deployment with Packer

By[James](https://jameskilby.co.uk) January 21, 2021 · Updated June 5, 2026 • 📖2 min read(366 words)

📅**Published:** January 21, 2021•**Updated:** June 05, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while. But until now I had never played with it. That was until I saw the below tweet by the legend that is [William Lam](https://williamlam.com/)

> 🤩 THIS IS AWESOME 🤩  
>   
> For those who ❤️ Automation, check out [@tenthirtyam](https://x.com/tenthirtyam?ref_src=twsrc%5Etfw) amazing repo w/working examples to build Photon OS 3/4, Ubuntu 18.04/20.04, RHEL 7/8, CentOS 7/8 & Windows Server 2016/2019 VM images using Packer & pushing to Cont Lib! Well done <https://t.co/o7FQXtrpRn>
> 
> — William Lam (@lamw) [November 30, 2020](https://x.com/lamw/status/1333546472155987969?ref_src=twsrc%5Etfw)

## Getting Packer Running

That was the kicker I needed to go and have a look at getting Packer set up and running. As I run a Mac as my main machine it was easy to get deployed following the instructions using [brew](https://brew.sh) and the GitHub Repo that William had pointed to.

## Fixing the Packer Datacenter Error

However, once I had added my vSphere credentials I was having a few issues. On execution, I was getting the error message “default datacenter resolves to multiple instances”. I did a bit of digging and discovered that the code didn’t specify a VMware datacenter and in my lab environment, I have 2 physical sites with a VMware datacenter in each, therefore, I needed to specify which one. Once this was fixed I started rolling out some Linux templates and it worked flawlessly until I got to the photon 4 server. I again spotted a typo and a syntax error on a command being passed into the photon VM. I corrected this and decided that actually, I should work out how to get this fixed upstream to help the wider community.

Once this was working it was onto the Windows templates. Once all the relevant ISOs and configs were in place I was able to fully deploy 4 Windows servers that were patched and added to my content library in about 40 mins. So whenever I go to deploy an Image it is always up to date…

Thanks to [Ryan](https://github.com/tenthirtyam) for an incredible piece of work I now lean on tools like this for wider [homelab automation](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/).

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [ ![Free Octopus Agile Battery & Solar Calculator: 5 Batteries Tested](https://jameskilby.co.uk/wp-content/uploads/2026/03/Octopus-Energy-logo.jpg) ](https://jameskilby.co.uk/2026/03/octopus-agile-battery-solar-calculator/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Free Octopus Agile Battery & Solar Calculator: 5 Batteries Tested](https://jameskilby.co.uk/2026/03/octopus-agile-battery-solar-calculator/)

By[James](https://jameskilby.co.uk) March 9, 2026 · Updated June 1, 2026

I am quite a heavy consumer of electricity at home. This is primarily driven by my lab but having a young son and two golden retrievers means more washing and drying.

  * [ ![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png) ](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk) December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Veeam](https://jameskilby.co.uk/category/veeam/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Lab Update – Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

By[James](https://jameskilby.co.uk) January 6, 2022 · Updated June 1, 2026

My lab is always undergoing change. Partially as I want to try new things or new ways of doing things.

  * [ ![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png) ](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk) September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.

  * [ ![VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

By[James](https://jameskilby.co.uk) May 21, 2025 · Updated June 24, 2026

Quick reference guide to the available storage resources that you get in VMware Cloud on AWS

  * [ ![Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault-768x432.jpeg) ](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

By[James](https://jameskilby.co.uk) January 11, 2022 · Updated June 1, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale.