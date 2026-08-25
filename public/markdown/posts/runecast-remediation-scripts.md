---
title: "Runecast Remediation Scripts: Auto-Fix VMware Storage Issues"
description: "I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab."
date: 2023-05-16T10:38:45+00:00
modified: 2026-06-01T21:58:53+00:00
author: James Kilby
categories:
  - Runecast
  - VMware
  - Ansible
  - Automation
  - Personal
  - Homelab
  - Hosting
  - Storage
  - VMware Cloud on AWS
tags:
  - #Homelab
  - #PowerCLI
  - #Runecast
  - #VMware
url: https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/
image: https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Runecast Remediation Scripts: Auto-Fix VMware Storage Issues

By[James](https://jameskilby.co.uk) May 16, 2023 · Updated June 1, 2026 • 📖2 min read(442 words)

**Published:** May 16, 2023•**Updated:** June 01, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab. One of the really cool features I wanted to mention today was the remediation script function. 

I have been playing with storage a lot in my lab recently as part of a wider storage migration piece but also as part of testing Intel Optane drives. Runecast flagged up that I didn’t have Storage I/O Control enabled for these data stores. It gave a great overview of what that issue means:

It is a good practice to enable SIOC, especially in environments where storage is overutilized. SIOC monitors the latency of I/Os to data stores at each ESX host sharing that device. When the average normalized datastore latency exceeds a set threshold (30ms by default), the datastore is considered to be congested, and SIOC kicks in to distribute the available storage resources to virtual machines in proportion to their shares. This is to ensure that low-priority workloads do not monopolize or reduce I/O bandwidth for high-priority workloads.

But the issue I want to highlight is it will generate the code to resolve it for you. 

If I drill into the specific issue, I get the view below.

![Runecast Remediation Script's Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/05/Screenshot-2023-05-16-at-11.31.30-1024x536.png)

Here you can confirm the discovered issue and the remediation action. ( I have chosen not to enable SIOC on my ISO-NFS datastore)

The below code is what Runecast generated for me.
    
    
    # Automatically generated action. Always review before executing.
    
    # Start of the section for Enabling of Storage IO control on datastore
    # This action is going to be performed on the following Datastores: "Optane-iSCSI"
    
    Write-Host "`n[RCA] Connecting to vCenter Server "uk-poo-p-vc-1.jameskilby.cloud"..." -ForegroundColor Cyan
    $vcConnection = Connect-VIServer -Server "uk-poo-p-vc-1.jameskilby.cloud"
    
    $datastoreIds = "Datastore-datastore-50097"
    
    foreach($datastoreId in $datastoreIds) 
    {
        try 
        {
            $ds = Get-Datastore -Id $datastoreId -ErrorAction Stop
            Write-Host "`n[RCA] Reconfiguring datastore with current name $($ds.name)" -ForegroundColor Yellow
            Write-Host "`n[RCA] Enabling Storage I/O Control" -ForegroundColor Yellow
            $ds | Set-Datastore -StorageIOControlEnabled $true -ErrorAction Stop | Format-Table name,Id,StorageIOControlEnabled
            
        }
        catch 
        {
            Write-Host "`n[RCA] Datastore with ID $datastoreId was not found or the reconfiguration failed" -ForegroundColor Red
        }
        
    }
    
    Write-Host "`n[RCA] Disconnecting from vCenter Server "uk-poo-p-vc-1.jameskilby.cloud"..." -ForegroundColor Cyan
    Disconnect-VIServer $vcConnection -Confirm:$false
    
    # End of the section for Enabling of Storage IO control on datastore

📋 Copy

Dropping this into a PowerCLI session, we get…
    
    
    [RCA] Connecting to vCenter Server  uk-poo-p-vc-1.jameskilby.cloud...
    
    Specify Credential
    Please specify server credential
    User: administrator@vsphere.cloud
    Password for user administrator@vsphere.cloud: ************
    
    
    [RCA] Reconfiguring datastore with current name Optane-iSCSI
    
    [RCA] Enabling Storage I/O Control
    
    Name         Id                        StorageIOControlEnabled
    ----         --                        -----------------------
    Optane-iSCSI Datastore-datastore-50097                    True
    
    
    [RCA] Disconnecting from vCenter Server  uk-poo-p-vc-1.jameskilby.cloud...
    PS /Users/w20kilja> 

📋 Copy

What an amazing little feature!!!

## 📚 Related Posts

  * [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)
  * [New Homelab Nodes: SuperMicro BigTwin for VMware &#038; Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)
  * [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

## Similar Posts

  * [ ![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png) ](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk) April 15, 2026 · Updated June 1, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introduction One of the larger costs of running my homelab is the electricity….

  * [ ![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png) ](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk) October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [ ![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg) ](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk) October 11, 2022 · Updated June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [ ![Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/wp-content/uploads/2024/09/QuantaGrid-SD1Q-1ULH-Front-Three-Quarter.png) ](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Can you really squeeze 96TB in 1U ?](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

By[James](https://jameskilby.co.uk) September 12, 2024 · Updated July 11, 2026

Yes, that’s a clickbait title. But technically it’s possible if I dropped all drive redundancy… I recently saw an advert for a server that was just too good to be true.

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk) July 2, 2020 · Updated June 5, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup: the “i3en”. This is based on the i3en.