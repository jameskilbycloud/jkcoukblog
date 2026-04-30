---
title: "Nutanix Command Reference Guide"
description: "Access a comprehensive list of useful Nutanix commands. Enhance your skills and streamline your operations with our handy reference guide."
date: 2018-06-05T20:59:24+00:00
modified: 2026-03-10T20:35:15+00:00
author: James Kilby
categories:
  - Nutanix
  - Homelab
  - VMware
  - Personal
tags:
  - #CLI
  - #Nutanix
url: https://jameskilby.co.uk/2018/06/nutanix-command-reference-guide/
image: https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg
---

![Nutanix Logo Hi Rez Reverse W Carrier](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg)

[Nutanix](https://jameskilby.co.uk/category/nutanix/)

# Nutanix Command Reference Guide

By[James](https://jameskilby.co.uk)June 5, 2018March 10, 2026 • 📖1 min read(105 words)

📅 **Published:** June 05, 2018• **Updated:** March 10, 2026

## Nutanix Command List

This is a list of Nutanix commands I have found useful. Its here as a reference and if i need a command more than a few times ill generally add it here.

#### CLI

  * ncli cluster get-domain-fault-tolerance-status type=node (Checks if all of the storage components meet the desired replication factor)
  * cvm_shutdown -P now ( Correct way to shutdown a CVM)
  * ncc health_checks run_all –parallel=4 . ( 4 is the max number)
  * curator_cli get_under_replication_info summary=true Checks if any objects are not at the desired replication factor
  * curl localhost:2019/prism/leader . Find the leader

#### WEB

  * http://{curator-master-cvm-ip}:2010/master/control ( If you want to invoke a curator scan manually)

## 📚 Related Posts

  * [New Nodes](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [Nutanix NCP](https://jameskilby.co.uk/2020/07/nutanix-ncp/)
  * [Nutanix CE](https://jameskilby.co.uk/2018/01/nutanix-ce/)

## Similar Posts

  * [![New Nodes](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg)](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Nodes](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk)July 2, 2024March 10, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul. The below post describes what I bought why and how I have configured it. Table of Contents Node Choice Bill of Materials Rescue IPMI…

  * [![Nutanix NCP](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Nutanix NCP](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

By[James](https://jameskilby.co.uk)July 2, 2020July 10, 2024

I saw a tweet a couple of weeks ago mentioning that Nutanix were offering a free go at the Nutanix Certified Professional exam. They are also offering free on-demand training to go with it. In my current role, I haven’t used Nutanix however I have good experience using it as the storage platform with vSphere…

  * [![Nutanix CE](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2018/01/nutanix-ce/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Nutanix CE](https://jameskilby.co.uk/2018/01/nutanix-ce/)

By[James](https://jameskilby.co.uk)January 6, 2018July 10, 2024

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home. This was compounded by the fact that I have many clusters to play with at work. These all run my…