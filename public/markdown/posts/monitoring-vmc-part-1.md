---
title: "Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)"
description: "My approach to monitoring VMware Cloud on AWS — why you still need to monitor your VMs, and testing Veeam ONE as the first tool for the job."
date: 2019-12-17T23:01:27+00:00
modified: 2026-06-05T19:09:46+00:00
author: James Kilby
categories:
  - VMware
  - AWS
  - Veeam
  - Homelab
  - Storage
  - vExpert
  - Personal
  - VMware Cloud on AWS
  - vSphere
  - Automation
tags:
  - #AWS
  - #VMC
  - #VMware
url: https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/
image: https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp
---

![](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp)

[VMware](https://jameskilby.co.uk/category/vmware/) | [AWS](https://jameskilby.co.uk/category/aws/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

# Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)

By[James](https://jameskilby.co.uk) December 17, 2019 · Updated June 5, 2026 • 📖2 min read(491 words)

📅**Published:** December 17, 2019•**Updated:** June 05, 2026

This is the first part of my series on monitoring VMware Cloud on AWS. As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring.

## Monitoring VMware Cloud on AWS: My Approach

This is an interesting topic as VMC is technically “as a service” therefore the monitoring approach is a bit different. Technically AWS and VMware’s SRE teams will be monitoring all of the infrastructure components,

however, you still need to monitor your Virtual Machines. If it was me I would still want some monitoring of the Infrastructure and I see two different reasons why you would want to do this:

Firstly I want to check that the VMware Cloud on AWS service is doing what I am paying for. Secondly, I still need to monitor my VMs to ensure they are all behaving properly, the added factor is that with a good real-time view of my workload, I can potentially optimise the number of VMC hosts in my fleet reducing the costs.

With that in mind, I decided to look at a few options for connecting some monitoring tools to a VMC environment to see what worked and what didn’t. I am expecting some things could behave differently as you don’t have true root/admin access as you would usually do. All of the tests will be done with the cloudadmin@vmc.local account. This is the highest-level account that a service user has within VMC.

The first product that I decided to test was [Veeam One](https://www.veeam.com/virtualization-management-one-solution.html). This made sense for a few reasons: Firstly I’m a [Veeam Vanguard](https://jameskilby.co.uk/about-me/) and am very familiar with the product. I also have access to the Beta versions of the v10 products as part of the Vanguard program.

Secondly, it’s pretty easy to spin up a test server to kick the tyres and finally, the config is incredibly quick to implement.

I could have easily added a VMC vCenter to my existing Veeam servers however I chose to deploy a new server just for this testing. Assuming you have network access between your Veeam One server and the VMC vCenter then adding to Veeam One is straightforward. If not, you will need to open up the relevant firewalls.

Once done Veeam performs an inventory operation and returns all of the objects you would expect. This test was shortly after a VMC environment was created so it doesn’t yet have any workloads migrated to it. However, as you can see below it’s correctly reporting on the hosts and VM workloads. It is correctly reporting back that the hosts are running ESXi 6.9.1…

I also ran a couple of test reports to check they functioned as expected. Everything seemed to work as I would expect.

![VMC Vms](https://jameskilby.co.uk/wp-content/uploads/2023/05/VMC-Vms-1024x296.png)

![Screenshot 2019 12 17 at 21.19.40](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2019-12-17-at-21.19.40-1024x500.png)

![Screenshot 2019 12 17 at 21.19.30](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2019-12-17-at-21.19.30-1024x472.png)

In Part Two I am going to look at using Grafana, InfluxDB and Telegraf and seeing if this common open-source monitoring stack works with VMC.

## 📚 Related Posts

  * [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)
  * [Using Content Libraries in VMC to deploy software faster](https://jameskilby.co.uk/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster/)
  * [Lab Update &#8211; Desired Workloads](https://jameskilby.co.uk/2022/01/lab-update-part-5-desired-workloads/)

## Similar Posts

  * [ ![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png) ](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk) April 17, 2023 · Updated June 1, 2026

I have been a VMware vExpert for many years and it has brought me many benefits over the years.

  * [ ![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png) ](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk) September 13, 2020 · Updated May 31, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.

  * [ ![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png) ](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk) October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [ ![New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

By[James](https://jameskilby.co.uk) April 1, 2026 · Updated July 11, 2026

We’ve expanded the VMC fleet with the new i7i (i7i.

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![Template Deployment with Packer](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png) ](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Template Deployment with Packer](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

By[James](https://jameskilby.co.uk) January 21, 2021 · Updated June 5, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while.