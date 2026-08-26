---
title: "Nutanix Command Reference Guide"
description: "Nutanix Command List This is a list of Nutanix commands I have found useful."
date: 2018-06-05T20:59:24+00:00
modified: 2026-07-11T08:02:12+00:00
author: James Kilby
categories:
  - Nutanix
  - Homelab
  - Personal
tags:
  - #CLI
  - #Nutanix
url: https://jameskilby.co.uk/2018/06/nutanix-command-reference-guide/
image: https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg)

[Nutanix](https://jameskilby.co.uk/category/nutanix/)

# Nutanix Command Reference Guide

By[James](https://jameskilby.co.uk) June 5, 2018 · Updated July 11, 2026 • 📖1 min read(106 words)

## Nutanix Command List

This is a list of Nutanix commands I have found useful. It’s here as a reference and if I need a command more than a few times I’ll generally add it here.

#### CLI

  * ncli cluster get-domain-fault-tolerance-status type=node (Checks if all of the storage components meet the desired replication factor)
  * cvm_shutdown -P now ( Correct way to shut down a CVM)
  * ncc health_checks run_all –parallel=4 . ( 4 is the max number)
  * curator_cli get_under_replication_info summary=true Checks if any objects are not at the desired replication factor
  * curl localhost:2019/prism/leader . Find the leader

#### WEB

  * http://{curator-master-cvm-ip}:2010/master/control ( If you want to invoke a curator scan manually)

## 📚 Related Posts

  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [Passing the Nutanix NCP Exam: Free Training &#038; My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)
  * [Nutanix Life Cycle Manager](https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/)

## Similar Posts

  * [ ![Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg) ](https://jameskilby.co.uk/2018/01/nutanix-ce/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/2018/01/nutanix-ce/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home.

  * [ ![Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg) ](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

By[James](https://jameskilby.co.uk) July 2, 2020 · Updated May 31, 2026

I saw a tweet a couple of weeks ago mentioning that Nutanix were offering a free go at the Nutanix Certified Professional exam.

  * [ ![Nutanix Life Cycle Manager](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg) ](https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Nutanix Life Cycle Manager](https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/)

By[James](https://jameskilby.co.uk) April 3, 2018 · Updated June 5, 2026

What Is Nutanix Life Cycle Manager (LCM)? With the introduction of AOS 5, Nutanix introduced Life Cycle Manager (LCM), something that Is one of the best but least known Nutanix features. Put simply it’s part of the Nutanix update mechanism but for dealing with hardware rather than the software components. To me what makes LCM…

  * [ ![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg) ](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk) July 2, 2024 · Updated July 11, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .