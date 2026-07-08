---
title: "Analytics in a privacy focused world"
description: "I recently helped my friend Dean Lewis @veducate with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress"
date: 2023-11-10T16:45:03+00:00
modified: 2026-06-01T19:02:53+00:00
author: James Kilby
categories:
  - Hosting
  - Personal
  - Artificial Intelligence
  - Docker
  - VMware
  - Wordpress
  - Automation
  - Homelab
  - NVIDIA
  - Traefik
  - AWS
  - Cloudflare
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

![Plausible Analytics Icon Top](https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Personal](https://jameskilby.co.uk/category/personal/)

# Analytics in a privacy focused world

By[James](https://jameskilby.co.uk)November 10, 2023 · Updated June 1, 2026 • 📖1 min read(254 words)

📅**Published:** November 10, 2023•**Updated:** June 01, 2026

I recently helped my friend Dean Lewis [@veducate](https://veducate.co.uk) with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress instance. He has been a pretty prolific blogger over the years pumping out an amazing amount of really good content. It also highlighted to me that I didn’t know if anyone was reading my blog as I removed Google Analytics years ago over privacy concerns. I had seen from Myles’s [blog](http://blah.cloud) that he had done something similar as part of his blog revamp. Myles was using [Plausible](https://plausible.io/open-source-website-analytics) and seeing as they had a self-hosted version of this I decided to give it a whirl.

## Install 

Luckily for me Truecharts has a prebuilt plausible container so I fired that up and set an ingress entry of plausible.jameskilby.cloud on the container so that it uses my Traefik instance as an entry into my Truenas K3s environment. In my WordPress origin site I added the Plausible plugin and defined the endpoint. The last step was to expose the container to the outside world. To do this I created a public DNS record in Cloudflare and pointed this at an existing Cloudflare tunnel terminating in my Truenas K3s setup. 

The entire process took approx 30 mins to set up and I’m really pleased with the results. 

![Plausible results](https://jameskilby.co.uk/wp-content/uploads/2023/11/Screenshot-2023-11-10-at-16.42.39-1024x527.png)

Plausible real time stats

Update:

I am now happy with this and have decided to make my stats public to show exactly what information I can and can’t see. This can be seen [here](https://plausible.jameskilby.cloud/jameskilby.co.uk/)

## 📚 Related Posts

  * [Hosting This Blog on Cloudflare Workers: Why &#038; How I Did It](https://jameskilby.co.uk/2022/01/web-development/)
  * [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)
  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)

## Similar Posts

  * [![How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.30.47-768x411.png)](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

By[James](https://jameskilby.co.uk)January 29, 2025 · Updated June 5, 2026

Update: Hoarder has now been renamed to Karakeep due to a trademark issue I’ve been on a mission recently to regain control of my data.

  * [![VMware – Going out with a Bang!](https://jameskilby.co.uk/wp-content/uploads/2023/10/rnli-logo-768x384.png)](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [VMware – Going out with a Bang!](https://jameskilby.co.uk/2023/10/going-out-with-a-bang/)

By[James](https://jameskilby.co.uk)October 7, 2023 · Updated June 1, 2026

There is a lot of uncertainty with VMware at the moment. This is all due to the pending acquisition by Broadcom.

  * [![Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

By[James](https://jameskilby.co.uk)January 4, 2022 · Updated June 1, 2026

I have been making several changes (mainly cosmetic) to this site over the last day or so. On most changes I have been doing an export and then uploading the site to Cloudflare using Wrangler.

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk)April 4, 2026 · Updated June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [![AWS Solution Architect – Associate](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png)](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [AWS Solution Architect – Associate](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

By[James](https://jameskilby.co.uk)December 16, 2019 · Updated May 31, 2026

I renewed my AWS Solution Architect certification.

  * [![Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

By[James](https://jameskilby.co.uk)October 20, 2022 · Updated June 1, 2026

For a while now I have been running this site directly from Cloudflare utilising their excellent worker’s product.