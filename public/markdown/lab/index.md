---
title: "Homelab – Hardware"
description: "An upto date inventory of the things running in my lab"
date: 2020-06-27T20:08:38+00:00
modified: 2026-08-21T10:00:15+00:00
author: James Kilby
url: https://jameskilby.co.uk/lab/
image: https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6628-1-1024x372.jpeg
---

My homelab is a constantly evolving platform for learning, self-hosting, and running serious workloads — from VMware vSphere clusters and AI inference to network automation and cloud integration. It lives in a dedicated server room, built around a StarTech 25U open-frame rack, and extends into the cloud via AWS and Cloudflare.

[See also: Homelab Software →](https://jameskilby.co.uk/homelab-software/)

Live homelab power draw

—W

connecting…

What am I looking at?

That figure is what my homelab is drawing from the wall right now — a live reading, not a number I typed in once and forgot about.

Home Assistant asks each machine's management controller how much it is using: the Nutanix cluster reports its shared chassis power supplies over Redfish, and the Quanta storage server reports over IPMI. Those get added into a single whole-lab total.

Every 30 seconds Home Assistant pushes that total out to a Cloudflare Worker, which keeps the latest reading (and the last half hour of them, for the sparkline) at the edge. This page reads it straight back, so what you see is at most a minute or so behind reality. Nothing here talks to my house directly — the lab only ever pushes out.

Readings are taken at the power supplies, so the true draw at the socket is roughly 5–10% higher. If the dot turns grey, the lab has stopped reporting.

## Table of Contents

## At a Glance

Compute Nodes| Total RAM| Usable Storage| Network Uplinks  
---|---|---|---  
4 (3× NX-1365-G4 + HP Z840)| 1,280 GB| 95.9 TB| 25 GbE  
  
I would estimate the replacement value sits somewhere around £15–20k. This has been accumulated over the years through a mix of enterprise surplus finds and deliberate upgrades.

My hardware choices are driven by a consistent set of design principles — some are non-negotiable, others are strong preferences:

  * **vSphere compatibility** — HCL-listed hardware wherever possible, so certifications mean something
  * **IPMI / remote management** — everything must be operable headlessly
  * **Rack-mount form factor** — clean, manageable, and expandable
  * **Low-power 24/7 operation** — the lab runs continuously, so efficiency matters
  * Noise isn’t really a factor due to location
  * Heat output isn’t a huge factor
  * A GPU is essential in at least one node.

## Physical Hardware

### Overview

![](https://jameskilby.co.uk/wp-content/uploads/2024/12/vSphere-Overview-1024x530.png)

#### GPU/ Management Cluster

This is made up of a single HP Z840 running ESXi 8.0U3. It is an amazing workhorse and has been a key part of my lab (running multiple functions for over 6 years). It currently runs vSphere and I often use it for running Holodeck on top of vSphere.

**Component**| **Description**  
---|---  
HP | Z840  
CPU | 2x CPU E5-2673 v3 @ 2.40GHz 30MB Cache, 5.0GTs, 105W  
RAM | 256GB  
NIC 0 | Supermicro Intel AOC-STGN-i2S 10Gb Dual Port  
Storage 0 | Intel Optane DC P4800X used for Local NVMe Datastore  
Storage 1 | Intel 2TB NVMe used for Local NVMe Datastore  
GPU0 | NVIDIA GeForce GT 730 — display adapter only (the Z840 would not boot without a GPU installed; keeps the A10 free for compute)  
GPU1 | NVIDIA Ampere A10 (24 GB) — GPU compute: AI inference, LLM serving, and ML workloads | Boot Volume | 2x1TB Raid 1  
  
### Compute Cluster

#### Nutanix NX – 3x NX-1365-G4

This is a significant resource for running a lot of my workloads however, due to electric costs, it does not run all the time. It is made up of 3x Nodes in a Supermicro Big-Twin with an identical configuration as below…..

This is running vSphere 8 with VSAN ESA being used as storage

**Component**| **Description**  
---|---  
Model | NXS2U4NL12G400  
CPU | 2x XEON E5-2640 V3  
RAM | 256GB  
NIC | Intel Ethernet Controller XXV710 for 25GbE SFP28  
Boot Disk | 64 GB SATADOM  
SSD 1 | Samsung PM863 960GB  
SSD 2 | Samsung PM863 960GB  
SSD 3 | Samsung PM863 960GB  
  
# Storage

## Primary Storage

### Quanta D51PH-1ULH (66.3TiB usable)

Quanta server running TrueNAS scale. This was originally configured with striped mirrors. I have changed this to a RAIDZ2 config, giving me a usable 66.3 TB. This is presented as SMB/NFS and iSCSI to multiple environments. More details are [here](https://jameskilby.co.uk/2024/09/can-you-really-squeeze-96tb-in-1u/)

## Secondary Storage

### Synology DS1512+ 4x8TB SHR1 ( 21.8TiB Usable)

This is in my office and used for “offsite backups”

Hostname| Model| NVMe Capacity (TB)| SSD Capacity (TB)| HDD Capacity (TB)  
---|---|---|---|---  
HP | HP Z840 | 2.6 |  |   
| vSAN ESA | 0 | 7.42 |   
| Quanta D51PH-1ULH | 0 | 0 | 66.3  
| Synology DS1512+ |  |  | 21.8  
Total TB (Usable) |  | 2.6 | 7.42 | 95.9  
  
## Network

### Physical Network

![](https://jameskilby.co.uk/wp-content/uploads/2026/08/NewHouseNet-4-1024x634.png)

Model| Description  
---|---  
Ubiquiti Dream Machine Beast | Core Firewall  
Mikrotik CRS504-4XQ-IN | Core Fibre Switch  
Mikrotik CSS610-8P-2S+IN | POE Switch  
Mikrotik CRS305-1G-4S+ | Fibre to Ethernet Switch  
  
### Wireless Network

AP Model| Description  
---|---  
Ubiquiti UniFi AC-Pro| Access Point — Office  
Ubiquiti UniFi 6 Pro| Access Point — House  
Ubiquiti UniFi Lite Pro| Access Point — House  
  
### WAN

Wan Providers| Description  
---|---  
Zen FTTP (Via CityFibre) | 2300/2300 with a /29 IPV4