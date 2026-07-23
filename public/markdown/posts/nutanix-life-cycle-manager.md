---
title: "Nutanix Life Cycle Manager"
description: "A practical walkthrough of Nutanix Life Cycle Manager (LCM) and how it simplifies firmware and hardware upgrades across your Nutanix cluster, step by step."
date: 2018-04-03T10:30:00+00:00
modified: 2026-06-05T19:49:29+00:00
author: James Kilby
categories:
  - Nutanix
  - Homelab
  - Personal
  - VMware
tags:
  - #Nutanix
url: https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/
image: https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg
---

![Nutanix Logo Hi Rez Reverse W Carrier](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier.jpg)

[Nutanix](https://jameskilby.co.uk/category/nutanix/)

# Nutanix Life Cycle Manager

By[James](https://jameskilby.co.uk)April 3, 2018 · Updated June 5, 2026 • 📖2 min read(432 words)

📅**Published:** April 03, 2018•**Updated:** June 05, 2026

## What Is Nutanix Life Cycle Manager (LCM)?

With the introduction of AOS 5, Nutanix introduced [Life Cycle Manager (LCM)](https://www.nutanix.com/products/cloud-infrastructure), something that Is one of the best but least known Nutanix features. Put simply it’s part of the Nutanix update mechanism but for dealing with hardware rather than the software components.

To me what makes LCM stand out is its pure simplicity. I have seen other solutions where it can be confusing to find out what hardware is on the HCL and then what firmware version is required and then the appropriate driver for that combination. This becomes unmanageable at a large enough scale. Where I currently work we have a mix of five different Nutanix node types of different hardware generations. ( All based on Supermicro hardware) . The below screenshots walk through an upgrade of one of these clusters.

## Walking Through an LCM Upgrade

![Nutanix Life Cycle Manager dashboard showing an available Cluster Software Component update](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screen-Shot-2018-02-14-at-19.38.25-1024x238.png)

The above picture demonstrates the simplicity, It’s showing that at present the only update available is to the “Cluster Software Component” Once this has been updated the next step is to perform an Inventory of your cluster.  
LCM will then show you all of the components in your cluster and the relevant upgrades available. If you work in a “Dark Site” . Offline downloads are also available.  
The below cluster has not had any updates run against it.

![Nutanix Life Cycle Manager inventory screen before any updates have been run](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screen-Shot-2018-02-14-at-19.38.36-2-1024x486.png)

Once the inventory has been done it’s time to decide if you want to run all of the updates or just a selection and off you go.

![Nutanix Life Cycle Manager listing available firmware updates on a three-node cluster](https://jameskilby.co.uk/wp-content/uploads/2018/04/DeviceToUpdate.png)

You can see above all of the available updates in this 3-node cluster. Note that only 2 of the SSDs needed updates as we had previously had one replaced and this was shipped with a later firmware.

Because the LCM is aware of the end-to-end stack it’s aware of any relevant dependencies. The upgrade for the HBA listed below doesn’t have any.  
![Screen Shot 2018 03 10 At 20.41.50 300X156](https://jameskilby.co.uk/wp-content/uploads/2018/03/Screen-Shot-2018-03-10-at-20.41.50-300x156.png)

## How LCM Handles the Upgrade Orchestration

Once you have started the upgrade progress LCM handles the orchestration piece, stopping just the required services and functions to allow the upgrade to complete.

![Screen Shot 2018 02 14 At 22.25.32 300X160](https://jameskilby.co.uk/wp-content/uploads/2018/03/Screen-Shot-2018-02-14-at-22.25.32-300x160.png)  
For the HBA upgrade, LCM stopped the storage-related services on the CVM but it left the CVM powered on and was not required to evacuate VM’s from the ESXi host. This meant that the upgrade was done very quickly and the storage services started again before moving to the next node.

As you can see the Host Boot Device (SATADom) and drives do require maintenance mode but again all of this is handled by LCM

And that’s it…. For more, check out my [Nutanix Command Reference Guide](https://jameskilby.co.uk/nutanix-command-reference-guide/).

## 📚 Related Posts

  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [Passing the Nutanix NCP Exam: Free Training &#038; My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)
  * [Nutanix Command Reference Guide](https://jameskilby.co.uk/2018/06/nutanix-command-reference-guide/)

## Similar Posts

  * [![Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2018/01/nutanix-ce/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/2018/01/nutanix-ce/)

By[James](https://jameskilby.co.uk)January 6, 2018 · Updated June 1, 2026

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home.

  * [![Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

By[James](https://jameskilby.co.uk)July 2, 2020 · Updated May 31, 2026

I saw a tweet a couple of weeks ago mentioning that Nutanix were offering a free go at the Nutanix Certified Professional exam.

  * [![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg)](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk)July 2, 2024 · Updated July 11, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [![Nutanix Command Reference Guide](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2018/06/nutanix-command-reference-guide/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Nutanix Command Reference Guide](https://jameskilby.co.uk/2018/06/nutanix-command-reference-guide/)

By[James](https://jameskilby.co.uk)June 5, 2018 · Updated July 11, 2026

A list of useful Nutanix Commands