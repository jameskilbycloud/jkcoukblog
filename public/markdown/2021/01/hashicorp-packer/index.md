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
  - VCF
  - Networking
  - Github
  - Storage
  - VMware Cloud on AWS
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

By[James Kilby](https://jameskilby.co.uk) January 21, 2021 · Updated June 5, 2026 • 📖2 min read(366 words)

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

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James Kilby](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [ ![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast-768x219.webp) ](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [UniFi UDM Beast Review: My Homelab Firewall Upgrade](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

By[James Kilby](https://jameskilby.co.uk) June 20, 2026 · Updated November 13, 2026

Retiring my ageing WatchGuard M200, I swap in the UniFi UDM Beast — a hardware tour, first iperf and WAN tests, the BGP/FRR setup, and the homelab services I’m consolidating onto it.

  * [ ![Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/wp-content/uploads/2026/04/packer-github-actions-vsphere-pipeline-768x452.png) ](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Github](https://jameskilby.co.uk/category/github/)

### [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

By[James Kilby](https://jameskilby.co.uk) April 30, 2026 · Updated June 5, 2026

A walk-through of an automated golden-image pipeline for vSphere: HashiCorp Packer builds six Ubuntu LTS templates (22.04, 24.04, 26.04 — server and desktop) driven by three GitHub Actions workflows covering PR validation, parallel template builds, and ISO management via a self-hosted runner.

  * [ ![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg) ](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James Kilby](https://jameskilby.co.uk) November 21, 2022 · Updated July 11, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [ ![Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash-768x417.png) ](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

By[James Kilby](https://jameskilby.co.uk) January 27, 2026 · Updated June 5, 2026

How to leverage Content Libraries to deploy into VMware Cloud on AWS faster.

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James Kilby](https://jameskilby.co.uk) October 23, 2023 · Updated July 11, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.