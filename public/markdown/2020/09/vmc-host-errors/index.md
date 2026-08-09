---
title: "How VMware Cloud on AWS Handles Host Failures Automatically"
description: "How VMware Cloud on AWS automatically detects and remediates a host failure — I watched it provision a replacement and evacuate the faulty host seamlessly."
date: 2020-09-15T10:56:32+00:00
modified: 2026-06-05T19:05:19+00:00
author: James Kilby
categories:
  - VMware
  - VMware Cloud on AWS
  - AWS
  - Homelab
  - vSphere
  - TrueNAS Scale
  - vSAN
  - Personal
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

By[James](https://jameskilby.co.uk)September 15, 2020 · Updated June 5, 2026 • 📖1 min read(217 words)

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

  * [![New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp)](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

By[James](https://jameskilby.co.uk)April 1, 2026 · Updated July 11, 2026

We’ve expanded the VMC fleet with the new i7i (i7i.

  * [![AWS For Beginners: IAM Setup, Root Security & Billing Alerts](https://jameskilby.co.uk/wp-content/uploads/2018/03/raf750x1000075t101010_01c5ca27c6.u2.jpg)](https://jameskilby.co.uk/2018/03/aws-for-beginners1/)

[AWS](https://jameskilby.co.uk/category/aws/)

### [AWS For Beginners: IAM Setup, Root Security & Billing Alerts](https://jameskilby.co.uk/2018/03/aws-for-beginners1/)

By[James](https://jameskilby.co.uk)March 30, 2018 · Updated June 1, 2026

AWS For Beginners Account Guide

  * [![VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png)](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

[VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

By[James](https://jameskilby.co.uk)December 8, 2025 · Updated July 11, 2026

How to use the Amazon Time Sync Service in a VMC environment

  * [![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png)](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk)December 14, 2022 · Updated June 1, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [![How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg)](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

By[James](https://jameskilby.co.uk)December 18, 2024 · Updated June 1, 2026

Introduction Copy on Write Disk IDs Trim Introduction I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010.

  * [![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png)](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk)October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.