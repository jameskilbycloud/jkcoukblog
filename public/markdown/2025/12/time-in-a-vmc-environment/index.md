---
title: "VMware Cloud on AWS Time Sync & NTP Configuration"
description: "How to configure Time Sync and NTP in VMware Cloud on AWS using the Amazon Time Sync Service — setup, firewall rules, and troubleshooting tips."
date: 2025-12-08T14:03:44+00:00
modified: 2026-06-05T17:52:07+00:00
author: James Kilby
categories:
  - VMware Cloud on AWS
  - VMware
  - vSAN
tags:
  - #NTP
  - #VMware Cloud on AWS
url: https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/
image: https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339.png)

[VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

# VMware Cloud on AWS Time Sync & NTP Configuration

By[James](https://jameskilby.co.uk) December 8, 2025 · Updated June 5, 2026 • 📖3 min read(614 words)

📅**Published:** December 08, 2025•**Updated:** June 05, 2026

This post covers how Time Sync works in VMware Cloud on AWS (VMC), using the [Amazon Time Sync Service](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html) to keep accurate NTP across your SDDC. One of the nice things about the VMC Service is that you dont have to worry about a number of the traditional infrastructure services that you typically obsess over when your running your own infrastructure. One of those is Time — a key requirement for any enterprise platform.

## Table of Contents

## What is the Amazon Time Sync Service?

The Amazon Time Sync Service is a highly accurate and reliable time source provided by AWS. It uses a fleet of redundant satellite-connected and atomic reference clocks to deliver Coordinated Universal Time (UTC) to AWS services and resources. In a VMware Cloud on AWS environment, the VMC infrastructure itself uses this service, and guest workloads can also be configured to use it directly.

The service is accessible at the link-local IP address **169.254.169.123** over UDP port 123. This is the same address used by standard EC2 instances and is always available within the AWS network — no internet access required.

## Time

VMC allows you to utilise the Amazon Time Sync Service for keeping an accurate and precise time. Because VMware Cloud on AWS is a fully managed service, the ESXi hosts are already configured to synchronise time correctly. However, for guest VMs running inside the VMC environment, you will want to ensure they are also pointed at a reliable time source rather than relying on VMware Tools time sync alone.

For Windows VMs, configure the NTP server using the Windows Time Service (w32tm). For Linux VMs, update your chrony or ntpd configuration to point to `169.254.169.123`. This provides a consistent, low-latency time source that stays local to the AWS infrastructure rather than traversing your network back to an on-premises NTP server.

## Firewall Config

To utilise the Amazon Time Sync Service from a VMC guest perspective, the appropriate NSX-T firewall rules need to be in place. On the Compute Gateway, you need to allow UDP port 123 outbound to **169.254.169.123**.

The IP address 169.254.169.123 is part of the link-local address range 169.254.0.0/16. It is worth noting that .123 was deliberately chosen to match the NTP port number — a neat detail from the AWS team.

To create the rule: in the VMC Console navigate to Networking & Security → Gateway Firewall → Compute Gateway. Add a rule allowing UDP port 123 from your VM segment to destination 169.254.169.123. Without this rule, guest VMs will be blocked from reaching the time sync endpoint.

## Troubleshooting

If time sync is not working for your guest VMs in VMware Cloud on AWS, check the following:

  * Verify the Compute Gateway firewall rule allows UDP 123 to 169.254.169.123
  * Confirm the NTP client service is running inside the guest VM
  * Check that the guest OS NTP configuration points to 169.254.169.123
  * If using a Route-based VPN with the default route on-premises, the link-local address will not be reachable over the VPN — use an alternative NTP server in that configuration

## Summary

VMware Cloud on AWS takes care of many traditional infrastructure concerns for you, and time sync is a great example. By leveraging the Amazon Time Sync Service at 169.254.169.123, you get a highly accurate, low-latency NTP source that is always available within the AWS network without any complex configuration. The only requirement on your part is ensuring the correct NSX-T Compute Gateway firewall rule is in place to allow UDP port 123 from your guest VMs to reach that link-local address. Once that is done, your workloads will have reliable, accurate time. For another VMC time-saver, see my post on [using Content Libraries in VMC](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/).

## 📚 Related Posts

  * [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)
  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

## Similar Posts

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020 · Updated June 5, 2026

Learn how host failures are handled within VMC

  * [ ![vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/wp-content/uploads/2023/11/OrigionalPoweredByvSAN-550x324-1.jpg) ](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/)

### [vSAN ESA in VMware Cloud on AWS: What Changed in VMC M24](https://jameskilby.co.uk/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc/)

By[James](https://jameskilby.co.uk) November 17, 2023 · Updated June 1, 2026

An Overview of vSAN ESA in VMC 

  * [ ![VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Storage Sizing Quick Reference Guide](https://jameskilby.co.uk/2025/05/vmc-quick-sizing-guide/)

By[James](https://jameskilby.co.uk) May 21, 2025 · Updated June 1, 2026

Quick reference guide to the available storage resources that you get in VMware Cloud on AWS

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk) July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.

  * [ ![An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [An in-depth look at VMware Cloud on AWS hosts](https://jameskilby.co.uk/2025/08/vmc-host-deepdive/)

By[James](https://jameskilby.co.uk) August 14, 2025 · Updated June 5, 2026

This is single page intended to collate every single feature of the current VMware Cloud on AWS hosts for easy comparison.

  * [ ![Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/wp-content/uploads/2026/01/Firefly_Gemini-Flash-768x417.png) ](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)

By[James](https://jameskilby.co.uk) January 27, 2026 · Updated June 5, 2026

How to leverage Content Libraries to deploy into VMware Cloud on AWS faster.