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
  - vSphere
  - VMware Cloud on AWS
  - Storage
  - Synology
  - TrueNAS Scale
  - AWS
  - Veeam
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

  * [ ![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png) ](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk) December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [ ![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk) August 14, 2025 · Updated July 11, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg) ](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk) November 21, 2022 · Updated July 11, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.

  * [ ![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png) ](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James](https://jameskilby.co.uk) September 12, 2024 · Updated July 11, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [ ![Monitoring VMware Cloud on AWS: Tools & Approaches \(Part 1\)](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [AWS](https://jameskilby.co.uk/category/aws/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

### [Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

By[James](https://jameskilby.co.uk) December 17, 2019 · Updated June 5, 2026

As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring.