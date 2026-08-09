---
title: "How VMware Cloud on AWS Handles Host Failures Automatically"
description: "How VMware Cloud on AWS automatically detects and remediates a host failure — I watched it provision a replacement and evacuate the faulty host seamlessly."
date: 2020-09-15T10:56:32+00:00
modified: 2026-06-05T19:05:19+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - VCF
  - Homelab
  - AWS
  - Personal
  - Runecast
  - Ansible
  - Automation
  - Docker
  - Traefik
tags:
  - #AWS
  - #Failure
  - #SRE
  - #VMC
  - #VMware
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2020/09/vmc-host-errors/
image: https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-1024x526.png
---

![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1.png)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# How VMware Cloud on AWS Handles Host Failures Automatically

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026 • 📖1 min read(217 words)

📅**Published:** September 15, 2020•**Updated:** June 05, 2026

Here is how VMware Cloud on AWS handles a host failure automatically, based on one I watched happen in production. When you run a large enough infrastructure, failure is inevitable. How you handle that can be a big differentiator. With [VMware Cloud on AWS](https://aws.amazon.com/vmware/), the hosts are monitored 24×7 by VMware/AWS Support all as part of the service. If you pay for X number of hosts you should have X. That includes during maintenance and failure operations.

## Watching a Host Failure Get Remediated

I’m not sure lucky is the right word but I did witness a host failure with a customer I was working with. True to the marketing, it was picked up and automatically remediated.

![VMC Host Errors Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2020-08-27-at-16.56.37-1536x182-2-1024x121.png)

Looking at the log extract above a new host was being provisioned the same minute the issue was identified. Obviously, this needed to boot and join the VMware/vSAN cluster before a full data evacuation takes place on the faulty host and finally, the host is removed.

All of this was seamless to the customer. I noticed it as a few HA alarms tripped in the vCenter (these were cosmetic only).

Just another reason why you should look at the VMware Cloud on AWS Service… For more on the hardware behind this, see my [VMware Cloud on AWS hosts deep-dive](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/).

## 📚 Related Posts

  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [Monitoring VMware Cloud on AWS: Tools &#038; Approaches (Part 1)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)
  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

## Similar Posts

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk) October 23, 2023 · Updated July 11, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [ ![AWS Solution Architect – Associate](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png) ](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [AWS Solution Architect – Associate](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

By[James](https://jameskilby.co.uk) December 16, 2019 · Updated May 31, 2026

I renewed my AWS Solution Architect certification.

  * [ ![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png) ](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk) August 14, 2025 · Updated July 11, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.