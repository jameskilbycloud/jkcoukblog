---
title: "Hosting This Blog on Cloudflare Workers: Why & How I Did It"
description: "A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them. This is partly related to some issues I have bee..."
date: 2022-01-04T11:27:12+00:00
modified: 2026-04-16T22:01:57+00:00
author: James Kilby
categories:
  - Hosting
  - Cloudflare
  - Personal
  - Wordpress
  - Ansible
  - Automation
  - Docker
  - Homelab
  - Traefik
  - VCF
  - VMware
  - Kubernetes
  - AWS
  - Artificial Intelligence
  - NVIDIA
tags:
  - #Cloudflare
  - #Hosting
url: https://jameskilby.co.uk/2022/01/web-development/
image: https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png
---

![Iu 2](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

# Hosting This Blog on Cloudflare Workers: Why & How I Did It

By[James](https://jameskilby.co.uk)January 4, 2022April 16, 2026 • 📖1 min read(211 words)

📅 **Published:** January 04, 2022• **Updated:** April 16, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them. This is partly related to some issues I have been having with internet access at home. Prior to this, the site ran from within my lab.

This means the site is now super fast (hopefully :p). It was cached by Cloudflare previously and now it’s served entirely from within their network.

![Web performance report](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2021-12-19-at-19.30.43-2048x751-1-1024x376.png)The speed report looks good

To enable this workflow I have retained a WordPress instance running within a docker instance on my Synology. I have also set up Cloudflare teams to access this.

This allows me to have the convenience of utilising WordPress as a CMS without having to worry about the security aspect as all public content is static. It also means that I don’t care about the uptime of the particular instance.

When I have finished writing the post I use the Simply Static Plugin to Generate the required static files. I then copy these to my wrangler site location on my laptop and ask Wrangler to publish them.
    
    
    wrangler publish --env production

📋 Copy

I wrote a post on the initial setup of Cloudflare Workers heck it out if you are interested in more of how this works.

## 📚 Related Posts

  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)
  * [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)
  * [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

## Similar Posts

  * [![Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

By[James](https://jameskilby.co.uk)January 4, 2022April 16, 2026

I have been making several changes (mainly cosmetic to this site over the last day or so) On most changes I have been doing an export and then uploading the site to Cloudflare using Wrangler.

  * [![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png)](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk)April 10, 2026April 16, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png)](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk)October 7, 2023April 16, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png)](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk)December 9, 2022April 16, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….

  * [![AWS Status Page – Monitoring Included](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png)](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [AWS Status Page – Monitoring Included](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

By[James](https://jameskilby.co.uk)May 15, 2018April 16, 2026

AWS Status Page – Enhancements The tool I deployed lambstatus supports pulling metrics from AWS Cloudwatch and displaying them.

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk)April 4, 2026April 16, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.