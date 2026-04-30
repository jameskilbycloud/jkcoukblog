---
title: "Starlink Satellite Internet Review: Rural Broadband Solution"
description: "Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Ze..."
date: 2022-10-11T21:40:50+00:00
modified: 2026-04-16T22:01:54+00:00
author: James Kilby
categories:
  - Homelab
  - Hosting
  - Cloudflare
  - Wordpress
  - TrueNAS Scale
  - VMware
  - vSAN
  - vSphere
  - Storage
  - Synology
tags:
  - #Homelab
  - #Starlink
url: https://jameskilby.co.uk/2022/10/starlink/
image: https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920.jpg
---

![Spacexs Starlink To Supply Free Satellite Internet To Famili U44U.1920](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

# Starlink Satellite Internet Review: Rural Broadband Solution

By[James](https://jameskilby.co.uk)October 11, 2022April 16, 2026 • 📖4 min read(747 words)

📅 **Published:** October 11, 2022• **Updated:** April 16, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three. These are both plumbed into my WatchGuard Firewall with multi-wan configured. Most of the time the usability is ok but there are multiple times a day when latency or packet loss is not acceptable. From living at previous locations where I had multiple companies that would deliver Gigabit Internet connections it was far from ideal. My job at VMware involves numerous calls with customers every day, typically presenting things to them and often with video on. Even a small interruption can leave a bad impression. VMware sells an SDWan product (Velocloud) and enables staff to use them. I was given one not long after I started, however, integrating it with my network has been suboptimal (as the device is locked down by VMware Corporate IT) 

One of the nice features of the WatchGuard is that it monitors the WAN interfaces for me. At the time of writing this blog the Zen interface was dropping approx 10% of traffic (This is unusually bad) and although it isn’t easy to see the Three interface was also a non-zero packet loss. The Starlink one is showing as I had configured the interface but it was not connected at the time.

![Screenshot 2022 10 05 at 12.56.21 1](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-10-05-at-12.56.21-1-1024x187.png)Packet Loss on WAN interfaces

Given we have no plans to move I decided to bite the bullet and pay for Starlink. Prior to doing this I downloaded the Starlink App and used the Visibility function to scan the sky for obstructions. I climbed out onto part of our roof that is flat and scanned the sky. This uses the iPhone camera and the accelerometer’s to scan the sky for obstructions. Luckily the results were positive. 

The intention is to drop the Zen connection when my contract runs out in a few months’ time. I can work around not having the /29 that comes with it with some Cloudflare magic that I will try and document in a follow-up post.

One thing to remember is that by default Starlink doesn’t ship you an ethernet adaptor. I ordered mine on the same day but it was shipped separately meaning I had to wait a few days before I could properly hook the system up. It’s a bit annoying to pay for an extra adaptor but £35 won’t break the bank. The other thing to pay attention to is the length of cable that you need. I went for the standard 75ft cable but it only just covers the length I need to get back to my firewall.

While waiting on the adaptor I decided to do some speed tests over Wifi from my iPhone 13 Pro

![IMG 8711](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_8711-805x1024.png)

To prove it wasn’t Starlink massaging the numbers I also performed a number of speed tests to other third parties and got broadly similar results. 

When the ethernet adaptor arrived I put the Starlink router in bypass mode. This can only be done from the iOS/Android App. The WatchGuard firewall interface was set to DHCP but once bypass was enabled it would not pick up a new address. I, therefore, rebooted the firewall and it came back with a CGNAT 100.65.x.x address removing the additional level of NAT. I will add a static entry on the firewall so I can still get to the Starlink management page. I believe the business service offers a fully routable IP.

![IMG 8718 1](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_8718-710x1536-1-473x1024.png)

Once all the above had been done. It was a case of connecting Starlink to the relevant port on my firewall. I had already configured the port as an “External interface” and set the IP endpoint to monitor. The WatchGuard immediately picked up that the ethernet port came up and tried to hit its monitoring endpoint. As soon as this was successful traffic started to route over this link as intended.

![Screenshot 2022 10 11 at 13.03.37 1](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-10-11-at-13.03.37-2048x695-1-1024x348.png)Traffic starting to use Starlink ( Bottom Left) 

Due to the way I have configured traffic egress from the WatchGuard to the internet each TCP/IP session will stay on a link (unless there is a failure) and they will get moved to the next available link. New sessions will be distributed based on the weightings I have applied. With the WatchGuard I have this configured on a per-firewall policy basis. Most traffic I allow uses any available link however some traffic I steer e.g. SMTP is configured to only use the Zen link.

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

## Similar Posts

  * [![What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png)](https://jameskilby.co.uk/2018/03/cloudflare/)

[Hosting](https://jameskilby.co.uk/category/hosting/)

### [What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/2018/03/cloudflare/)

By[James](https://jameskilby.co.uk)March 27, 2018April 16, 2026

Cloudflare – What is it and why would I care? I have been using Cloudflare for a long time.

  * [![Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

By[James](https://jameskilby.co.uk)October 20, 2022April 16, 2026

For a while now I have been running this site directly from Cloudflare utilising their excellent worker’s product.

  * [![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg)](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James](https://jameskilby.co.uk)February 10, 2019April 16, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.

  * [![How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg)](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

By[James](https://jameskilby.co.uk)December 18, 2024April 16, 2026

Introduction Copy on Write Disk IDs Trim Introduction I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010.

  * [![Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-12-14-at-21.45.23.png)](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Forcing an Upgrade to vSphere 8](https://jameskilby.co.uk/2022/12/forcing-an-upgrade-to-vsphere-8/)

By[James](https://jameskilby.co.uk)December 14, 2022April 16, 2026

I run a reasonably extensive homelab that is of course built around the VMware ecosystem.

  * [![Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/wp-content/uploads/2022/11/BrokenHardDive-1200x630-1-768x403.jpg)](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [Homelab SSD Failure: How Synology RAID Saved My Data](https://jameskilby.co.uk/2022/11/homelab-bad-days-almost/)

By[James](https://jameskilby.co.uk)November 21, 2022April 16, 2026

I recently spent 3 weeks in Ireland with my wife Wendy and our son Nate.