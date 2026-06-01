---
title: "Starlink Satellite Internet Review: Rural Broadband Solution"
description: "Since moving to Dorset last year internet connectivity has been the bane of my existence."
date: 2022-10-11T21:40:50+00:00
modified: 2026-06-01T21:06:43+00:00
author: James Kilby
categories:
  - Homelab
  - Hosting
  - Artificial Intelligence
  - Docker
  - Storage
  - vExpert
  - Networking
  - Kubernetes
  - Cloudflare
  - Personal
  - Wordpress
  - Ansible
tags:
  - #Homelab
  - #Starlink
url: https://jameskilby.co.uk/2022/10/starlink/
image: https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920.jpg)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

# Starlink Satellite Internet Review: Rural Broadband Solution

By[James](https://jameskilby.co.uk) October 11, 2022June 1, 2026 • 📖4 min read(747 words)

📅 **Published:** October 11, 2022• **Updated:** June 01, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three. These are both plumbed into my WatchGuard Firewall with multi-wan configured. Most of the time the usability is ok but there are multiple times a day when latency or packet loss is not acceptable. From living at previous locations where I had multiple companies that would deliver Gigabit Internet connections it was far from ideal. My job at VMware involves numerous calls with customers every day, typically presenting things to them and often with video on. Even a small interruption can leave a bad impression. VMware sells an SD-WAN product (VeloCloud) and enables staff to use them. I was given one not long after I started, however, integrating it with my network has been suboptimal (as the device is locked down by VMware Corporate IT).. 

One of the nice features of the WatchGuard is that it monitors the WAN interfaces for me. At the time of writing this blog the Zen interface was dropping approx 10% of traffic (This is unusually bad) and although it isn’t easy to see the Three interface was also a non-zero packet loss. The Starlink one is showing as I had configured the interface but it was not connected at the time.

![Screenshot 2022 10 05 at 12.56.21 1](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-10-05-at-12.56.21-1-1024x187.png)Packet Loss on WAN interfaces

Given we have no plans to move I decided to bite the bullet and pay for Starlink. Prior to doing this I downloaded the Starlink App and used the Visibility function to scan the sky for obstructions. I climbed out onto part of our roof that is flat and scanned the sky. This uses the iPhone camera and the accelerometers to scan the sky for obstructions. Luckily the results were positive. 

The intention is to drop the Zen connection when my contract runs out in a few months’ time. I can work around not having the /29 that comes with it with some Cloudflare magic that I will try and document in a follow-up post.

One thing to remember is that by default Starlink doesn’t ship you an ethernet adaptor. I ordered mine on the same day but it was shipped separately meaning I had to wait a few days before I could properly hook the system up. It’s a bit annoying to pay for an extra adaptor but £35 won’t break the bank. The other thing to pay attention to is the length of cable that you need. I went for the standard 75ft cable but it only just covers the length I need to get back to my firewall.

While waiting on the adaptor I decided to do some speed tests over Wi-Fi from my iPhone 13 Pro

![IMG 8711](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_8711-805x1024.png)

To prove it wasn’t Starlink massaging the numbers I also performed a number of speed tests to other third parties and got broadly similar results. 

When the ethernet adaptor arrived I put the Starlink router in bypass mode. This can only be done from the iOS/Android App. The WatchGuard firewall interface was set to DHCP but once bypass was enabled it would not pick up a new address. I, therefore, rebooted the firewall and it came back with a CGNAT 100.65.x.x address removing the additional level of NAT. I will add a static entry on the firewall so I can still get to the Starlink management page. I believe the business service offers a fully routable IP.

![IMG 8718 1](https://jameskilby.co.uk/wp-content/uploads/2023/04/IMG_8718-710x1536-1-473x1024.png)

Once all the above had been done, it was a case of connecting Starlink to the relevant port on my firewall. I had already configured the port as an “External interface” and set the IP endpoint to monitor. The WatchGuard immediately picked up that the ethernet port came up and tried to hit its monitoring endpoint. As soon as this was successful traffic started to route over this link as intended.

![Screenshot 2022 10 11 at 13.03.37 1](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-10-11-at-13.03.37-2048x695-1-1024x348.png)Traffic starting to use Starlink ( Bottom Left) 

Due to the way I have configured traffic egress from the WatchGuard to the internet each TCP/IP session will stay on a link (unless there is a failure) and they will get moved to the next available link. New sessions will be distributed based on the weightings I have applied. With the WatchGuard I have this configured on a per-firewall policy basis. Most traffic I allow uses any available link however some traffic I steer e.g. SMTP is configured to only use the Zen link.

## 📚 Related Posts

  * [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [ ![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg) ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk) October 11, 2024June 1, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [ ![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png) ](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk) April 17, 2023June 1, 2026

I have been a VMware vExpert for many years and it has brought me many benefits over the years.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Homelab Network Upgrade: DACs, 40Gb/s vMotion & pfSense](https://jameskilby.co.uk/2022/01/lab-update-part-3-network/)

By[James](https://jameskilby.co.uk) January 6, 2022May 31, 2026

I have retired the WatchGuard Devices with the migration to PFSense running bare-metal in one of the Supermicro Nodes.

  * [ ![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png) ](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk) December 9, 2022June 1, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….

  * [ ![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk) January 4, 2022May 25, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [ ![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png) ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk) September 2, 2025June 1, 2026

An intro on how I use SemaphoreUI to manage my Homelab