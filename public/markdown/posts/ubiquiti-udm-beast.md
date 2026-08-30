---
title: "Unleashing the UDM Beast"
description: "I retired my 7-year-old WatchGuard M200 for the UniFi UDM Beast — the spec, my iperf and WAN tests, the BGP/FRR setup, and what I consolidated onto it."
date: 2026-06-20T19:49:43+00:00
modified: 2026-08-24T18:12:00+00:00
author: James Kilby
categories:
  - Homelab
  - Networking
  - Unifi
  - Nutanix
  - Ansible
  - Artificial Intelligence
  - Mikrotik
  - Automation
  - Storage
  - Docker
tags:
  - #Dream Machine
  - #Homelab
  - #Ubiquiti
  - #Unifi
url: https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/
image: https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast.webp
---

![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast.webp)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Unifi](https://jameskilby.co.uk/category/unifi/)

# Unleashing the UDM Beast

By[James](https://jameskilby.co.uk) June 20, 2026 · Updated August 24, 2026 • 📖6 min read(1,131 words)

## Updated to 2.3Gbps:

I have now upgraded my Zen connection to 2.3Gbps and the Beast handles this with ease. This is always useful to know as with a PPPoE connection the overhead and processing can be a limiting factor. 

![](https://jameskilby.co.uk/wp-content/uploads/2026/06/Beast2.3Gbps.png)

## Intro

I thought it was time to update my firewall as the one I have been using for at least 7 years has been showing its age to say the least. Therefore I have decided to retire my WatchGuard M200 and replace it with a [Ubiquiti Dream Machine Beast](https://uk.store.ui.com/uk/en/products/udm-beast) (UDM Beast) The WatchGuard I was using has served me very well but the fans were a bit noisy and it was well past its shelf life. The M200 was originally launched way back in 2015 and officially hit end of life in 2023.

![Angled product render of the UniFi UDM Beast, showing its front drive bays, RJ45 ports and SFP cages.](https://jameskilby.co.uk/wp-content/uploads/2026/06/udm-beast-5-1024x1024.png)

## Table of Contents

## UDM Beast Specifications

The Beast packs an impressive specification with a variety of ports (14 of both copper and fibre)

  * 2× 1GbE RJ45
  * 8× 10GbE RJ45
  * 2× 10G SFP+
  * 2× 25G SFP28

It’s based on an octa-core ARMv9 at 2.1 GHz with 16GB of RAM.

It also has an internal integrated 128GB SSD plus 2x 3.5-inch drive bays. 

## Performance

The main reason for the upgrade for me was that I needed better inter-VLAN performance. I could have chosen to do this on my [switch](https://jameskilby.co.uk/2024/09/home-network-upgrade/) but I much prefer doing all of my security in one place. Therefore forcing the traffic to the firewall worked for me. According to the spec sheet the Beast can not only route at 25Gb/s but it has a promised 25Gb/s IDS/IPS throughput — something that is unheard of at this price point. I will test this in the future. For now I have just done some basic testing.

For now I need to physically relocate the Beast to get the 25Gb connections to work. Doing this will also allow me to remove a switch, reducing configuration changes, plus a small power and cooling improvement. The below testing is done just with 10Gb uplinks as can be seen by the topology below

![Network topology diagram: a 900 Mb/s internet link feeds the UDM Beast firewall in the House; 10 Gb/s links connect the Office and House to a core switch in the Server Room, where the vSAN cluster, management/GPU host and TrueNAS connect at 25 Gb/s.](https://jameskilby.co.uk/wp-content/uploads/2026/06/NewHouseNet-3-1024x634.png)

### iperf

iperf testing from a VMware VM to my bare-metal TrueNAS Scale instance.
    
    
     iperf3 -c 192.168.60.1 -P 4 -t 30
    
    [ ID] Interval           Transfer     Bitrate         Retr
    [  5]   0.00-30.00  sec  8.39 GBytes  2.40 Gbits/sec  1397            sender
    [  5]   0.00-30.00  sec  8.38 GBytes  2.40 Gbits/sec                  receiver
    [  7]   0.00-30.00  sec  8.63 GBytes  2.47 Gbits/sec  1164            sender
    [  7]   0.00-30.00  sec  8.63 GBytes  2.47 Gbits/sec                  receiver
    [  9]   0.00-30.00  sec  8.44 GBytes  2.42 Gbits/sec  1780            sender
    [  9]   0.00-30.00  sec  8.44 GBytes  2.42 Gbits/sec                  receiver
    [ 11]   0.00-30.00  sec  6.97 GBytes  1.99 Gbits/sec  2521            sender
    [ 11]   0.00-30.00  sec  6.96 GBytes  1.99 Gbits/sec                  receiver
    [SUM]   0.00-30.00  sec  32.4 GBytes  9.28 Gbits/sec  6862             sender
    [SUM]   0.00-30.00  sec  32.4 GBytes  9.28 Gbits/sec                  receive

📋 Copy

The retry count on this figure is higher than I would like, but I haven’t had time to investigate yet.

### WAN

The Beast has integrated speedtest capabilities. This is measured directly from the device. 

![UniFi UDM Beast WAN speed test result showing 877 Mbps download, 977 Mbps upload and 8 ms latency on 16 June 2026.](https://jameskilby.co.uk/wp-content/uploads/2026/06/ZenWanPerfomance.png)

My WAN connection is served over PPP, although DHCP is becoming more popular it is still fairly rare in the UK. Some devices struggle with achieving the expected performance when PPP is in use. Therefore I am pleased this did exactly what I would expect. 

To set the PPPoE connection up on my Zen Internet connection it was very straightforward. The physical fibre is presented by CityFibre and therefore the VLAN I need to configure is 911. In the connection setup you then add the PPP username and password that Zen have given you. I have then added my extra IPs from my /29 allocation as individual /32 addresses. 

![UDM Beast WAN setup for the Zen Internet connection on Port 9 \(10 GbE\), with VLAN ID 911 set manually for CityFibre.](https://jameskilby.co.uk/wp-content/uploads/2026/06/CityFibreVlan.png) ![UDM Beast PPPoE configuration showing the Zen Internet username and password, plus the additional /32 IPv4 addresses from the /29 allocation.](https://jameskilby.co.uk/wp-content/uploads/2026/06/PPP-and-IP-689x1024.png)

## Consolidation

The Beast will take on responsibility of a lot of services in my environment. Some of these were running on the previous WatchGuard Firebox others were on separate systems that can now be consolidated.

The plan is to move a number of services that I run in my lab over to the beast. This is a work in progress. So far I have moved the UniFi controller I was using for controlling my access points and removed Frigate video recording as this should be able to be handled by the Integrated UniFi Protect. I haven’t fully consolidated everything yet. 

So far the Beast is running:

  * UniFi Network Controller
  * UniFi Protect
  * DHCP Server
  * BGP

One role has moved off the Beast: it can no longer act as an NTP server, so NTP now runs on the core switch. DHCP, however, remains on the Beast. I always like to have a physical device reach out to the internet for NTP and then all my devices reference that device.

## BGP with FRR

I have BGP established between my core switch and the Dream Machine, the config on this is a bit weird. First you have to create a config file in FRR format. Then you upload it directly to the Beast. One of the downsides to this is if there is an error in your config the device silently accepts the config and does nothing. A review of the logs showed I had end of line comments that are not supported in FRR format.

The below is the config I am using. 
    
    
    !
    ! FRR BGP configuration for UniFi UDM (Dream Machine Beast)
    ! iBGP peering with MikroTik switch at 192.168.3.1
    ! UDM link IP on 192.168.3.0/24 = 192.168.3.248, AS 65000 (iBGP, same AS both ends)
    !
    ! NOTE: FRR does not support trailing/end-of-line comments.
    ! Every comment must be a full line beginning with "!". Do not add "! text"
    ! after a command on the same line, or the gateway will reject the config.
    !
    router bgp 65000
     bgp router-id 192.168.3.248
     bgp log-neighbor-changes
     no bgp default ipv4-unicast
     neighbor 192.168.3.1 remote-as 65000
     neighbor 192.168.3.1 description MikroTik-Switch
     neighbor 192.168.3.1 update-source 192.168.3.248
     !
     address-family ipv4 unicast
      redistribute connected
      neighbor 192.168.3.1 activate
      neighbor 192.168.3.1 next-hop-self
      neighbor 192.168.3.1 soft-reconfiguration inbound
     exit-address-family
    !
    

📋 Copy

Utilising BGP in this manner allows me to add a network to my core switch, done with [Ansible ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)that is then used for my VMware VCF environment. This can be seen in the route table below

![UniFi UDM Beast routing table showing BGP-learned routes \(192.168.100.0/24 to 192.168.105.0/24\) via next hop 192.168.3.1, alongside directly connected VLANs such as iSCSI, VMware MGMT, IoT and ServerVlan.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiRouteTable-1024x549.png)

## Conclusion

While it’s certainly a bit overkill for now, especially with my 900Mb internet connection, if it has even half the lifetime that the WatchGuard had then it will certainly come into its own. I may even treat myself to upgrading my Zen connection as they do support 2.3Gb

## Next Steps

The first priority is to get the box located next to my Servers and core switch. That will allow me to connect the 2x25Gb/s connections back to the core and do some proper throughput testing with IDS/IPS enabled and see if it really can do what UniFI claim.

The second one is to enable the protect recording of my cameras

## 📚 Related Posts

  * [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)
  * [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)
  * [Homelab Network Upgrade: DACs, 40Gb/s vMotion &#038; pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)

## Similar Posts

  * [ ![Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg) ](https://jameskilby.co.uk/2018/01/nutanix-ce/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/2018/01/nutanix-ce/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home.

  * [ ![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png) ](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk) February 9, 2026 · Updated July 11, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [ ![CRS-504](https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600-768x427.jpg) ](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

[Mikrotik](https://jameskilby.co.uk/category/mikrotik/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

By[James](https://jameskilby.co.uk) September 9, 2024 · Updated June 5, 2026

My journey to superfast networking in my homelab

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk) March 27, 2026 · Updated May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [ ![Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault-768x432.jpeg) ](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

By[James](https://jameskilby.co.uk) January 11, 2022 · Updated June 1, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale.

  * [ ![How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.30.47-768x411.png) ](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/)

### [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

By[James](https://jameskilby.co.uk) January 29, 2025 · Updated July 11, 2026

Update: Hoarder has now been renamed to Karakeep due to a trademark issue I’ve been on a mission recently to regain control of my data.