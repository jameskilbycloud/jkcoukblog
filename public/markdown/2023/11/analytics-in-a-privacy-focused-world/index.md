---
title: "Analytics in a privacy focused world"
description: "I recently helped my friend Dean Lewis @veducate with some hosting issues."
date: 2023-11-10T16:45:03+00:00
modified: 2026-04-16T22:01:49+00:00
author: James Kilby
categories:
  - Hosting
  - Personal
  - VMware
  - Artificial Intelligence
  - Docker
  - Nutanix
  - vSphere
  - Cloudflare
  - Devops
  - Github
  - Wordpress
  - Ansible
  - Automation
  - Homelab
  - Traefik
  - VCF
tags:
  - #Analytics
  - #Cloudflare
  - #Hosting
  - #Ingress
  - #Plausible
  - #Privacy
  - #Tunnel
url: https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/
image: https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Personal](https://jameskilby.co.uk/category/personal/)

# Analytics in a privacy focused world

By[James](https://jameskilby.co.uk) November 10, 2023April 16, 2026 • 📖1 min read(254 words)

📅 **Published:** November 10, 2023• **Updated:** April 16, 2026

I recently helped my friend Dean Lewis [@veducate](https://veducate.co.uk) with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress instance. He has been a pretty prolific blogger over the years pumping out an amazing amount of really good content. It also highlighted to me that I didn’t know if anyone was reading my blog as i removed Google Analytics years ago over privacy concerns. I had seen from Myles’s [blog](http://blah.cloud) that he had done something similar as part of his blog revamp. Myles was using [Plausible](https://plausible.io/open-source-website-analytics) and seeing as they had a self hosted version of this I decided to give it a whirl.

## Install 

Luckily for me Truecharts has a prebuilt plausible container so i fired that up and set an ingress entry of plausible.jameskilby.cloud on the container so that it uses my Traefik instance as an entry into my Truenas K3s environment. In my WordPress origin site I added the Plausible plugin and defined the endpoint. The last step was to expose the container to the outside world. To do this I created a public DNS record in Cloudflare and pointed this at an existing Cloudflare tunnel terminating in my Truenas K3s setup. 

The entire process took approx 30 mins to setup and Im really pleased with the results. 

![Plausible results](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-10-at-16.42.39-1024x527.png)

Plausible real time stats

Update:

I am now happy with this and have decided to make my stats public to show exactly what information I can and can’t see. This can be seen [here](https://plausible.jameskilby.cloud/jameskilby.co.uk/)

## 📚 Related Posts

  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)
  * [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)
  * [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

## Similar Posts

  * [ ![VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/wp-content/uploads/2020/09/vmware_SP_HCI20.png) ](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

[Personal](https://jameskilby.co.uk/category/personal/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Certified Master Specialist HCI 2020](https://jameskilby.co.uk/2020/09/vmware-certified-master-specialist-hci-2020/)

By[James](https://jameskilby.co.uk) September 13, 2020April 16, 2026

I recently sat (and passed the VMware HCI Master Specialist exam (5V0-21.

  * [ ![How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.30.47-768x411.png) ](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

By[James](https://jameskilby.co.uk) January 29, 2025April 16, 2026

Update: Hoarder has now been renamed to Karakeep due to a trademark issue I’ve been on a mission recently to regain control of my data.

  * [ ![Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg) ](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

By[James](https://jameskilby.co.uk) July 2, 2020April 16, 2026

I saw a tweet a couple of weeks ago mentioning that Nutanix were offering a free go at the Nutanix Certified Professional exam.

  * [ ![Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/wp-content/uploads/2023/11/image.png) ](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [Advanced Deploy VMware vSphere 7.x 3V0-22.21N](https://jameskilby.co.uk/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n/)

By[James](https://jameskilby.co.uk) November 10, 2023April 16, 2026

Yesterday I sat and passed the above exam. It had been on my todo list for a good number of years. With the current pause in the Broadcom VMware takeover deal.

  * [ ![How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2025/10/Github-Actions.webp) ](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Github](https://jameskilby.co.uk/category/github/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

By[James](https://jameskilby.co.uk) October 6, 2025April 16, 2026

I wanted to automate the publishing of my blog from the authoring side to the public side. These are some of the improvements I made.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026April 16, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.