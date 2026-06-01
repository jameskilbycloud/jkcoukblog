---
title: "Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)"
description: "As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring"
date: 2019-12-17T23:01:27+00:00
modified: 2026-06-01T19:02:23+00:00
author: James Kilby
categories:
  - VMware
  - AWS
  - Veeam
  - Personal
  - vSphere
  - VMware Cloud on AWS
  - Hosting
  - Ansible
  - Automation
  - Docker
  - Homelab
  - Traefik
  - VCF
  - Artificial Intelligence
  - Containers
  - Devops
  - NVIDIA
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

By[James](https://jameskilby.co.uk) December 17, 2019June 1, 2026 • 📖2 min read(470 words)

📅 **Published:** December 17, 2019• **Updated:** June 01, 2026

As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring.

This is an interesting topic as VMC is technically “as a service” therefore the monitoring approach is a bit different. Technically AWS and VMware’s SRE teams will be monitoring all of the infrastructure components,

however, you still need to monitor your Virtual Machines. If it was me I would still want some monitoring of the Infrastructure and I see two different reasons why you would want to do this:

Firstly I want to check that the VMware Cloud on AWS service is doing what I am paying for. Secondly, I still need to monitor my VMs to ensure they are all behaving properly, the added factor is that with a good real-time view of my workload, I can potentially optimise the number of VMC hosts in my fleet reducing the costs.

With that in mind, I decided to look at a few options for connecting some monitoring tools to a VMC environment to see what worked and what didn’t. I am expecting some things could behave differently as you don’t have true root/admin access as you would usually do. All of the tests will be done with the cloudadmin@vmc.local account. This is the highest-level account that a service user has within VMC.

The first product that I decided to test was [Veeam One](https://www.veeam.com/virtualization-management-one-solution.html). This made sense for a few reasons: Firstly I’m a [Veeam Vanguard](https://jameskilby.co.uk/about-me/) and am very familiar with the product. I also have access to the Beta versions of the v10 products as part of the Vanguard program.

Secondly, it’s pretty easy to spin up a test server to kick the tyres and finally, the config is incredibly quick to implement.

I could have easily added a VMC vCenter to my existing Veeam servers however I chose to deploy a new server just for this testing. Assuming you have network access between your Veeam One server and the VMC vCenter then adding to Veeam One is straightforward. If not, you will need to open up the relevant firewalls.

Once done Veeam performs an inventory operation and returns all of the objects you would expect. This test was shortly after a VMC environment was created so it doesn’t yet have any workloads migrated to it. However, as you can see below it’s correctly reporting on the hosts and VM workloads. It is correctly reporting back that the hosts are running ESXi 6.9.1.

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

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png) ](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

[VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

By[James](https://jameskilby.co.uk) December 8, 2025May 25, 2026

How to use the Amazon Time Sync Service in a VMC environment

  * [ ![AWS Status Page – Monitoring Included](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png) ](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [AWS Status Page – Monitoring Included](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

By[James](https://jameskilby.co.uk) May 15, 2018June 1, 2026

AWS Status Page – Enhancements The tool I deployed, lambstatus, supports pulling metrics from AWS Cloudwatch and displaying them.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026April 16, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk) February 9, 2026May 31, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

By[James](https://jameskilby.co.uk) April 1, 2026April 16, 2026

We’ve expanded the VMC fleet with the new i7i (i7i.