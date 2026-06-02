---
title: "Cloudflare Workers – Limits of the free tier"
description: "I have been making several changes (mainly cosmetic to this site over the last day or so) On most changes I have been doing an export and then uploading th"
date: 2022-01-04T21:11:23+00:00
modified: 2026-06-01T21:58:35+00:00
author: James Kilby
categories:
  - Hosting
  - Wordpress
  - AWS
  - Cloudflare
  - Artificial Intelligence
  - Automation
  - Docker
  - Homelab
  - NVIDIA
  - Traefik
  - VMware
  - Personal
tags:
  - #Blogging
  - #Cloudflare
  - #Workers
url: https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/
image: https://jameskilby.co.uk/wp-content/uploads/2022/10/iu.jpeg
---

![](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu.jpeg)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

# Cloudflare Workers – Limits of the free tier

By[James](https://jameskilby.co.uk) January 4, 2022 · Updated June 1, 2026 • 📖1 min read(280 words)

📅 **Published:** January 04, 2022• **Updated:** June 01, 2026

I have been making several changes (mainly cosmetic to this site over the last day or so) On most changes I have been doing an export and then uploading the site to Cloudflare using Wrangler. 

After a while I received an email from Cloudflare saying:

_Hi,_

You’re _50% of the way to reaching one of your daily Cloudflare Workers KV free tier limits. You can view complete usage information in the dashboard._

_If you do not take any action and exceed the daily limit, requests to the Workers KV API will return 429 errors, and operations within a worker will fail until the limit resets at 2022-01-05 at 00:00:00 UTC._

I decided to keep ploughing on with my changes to see what happens when I go over this.

The next email I received was slightly more informative as it said which limit I had breached.

_You have exceeded the daily Cloudflare Workers KV free tier limit of 1000 Workers KV put operations._

When I next tried to publish I got the following::: 
    
    
    wrangler publish --env production
    ✨  Built successfully, built project size is 13 KiB.
    🌀  Using namespace for Workers Site "__jameskilbycouk-production-workers_sites_assets"
    ✨  Success
    🌀  Uploading site files
    Error: ⚠️  Code 10048: your account has reached the free usage limit for this operation for today

📋 Copy

The same error was observed when running “Wrangler dev”

I had the option of upgrading for the cost of $5 which includes a very generous 10 million read operations and 1 million each of write, delete and list operations however it’s just not worth it for this site. I will wait until tomorrow to publish.

Detailed info on the limits is published [here ](https://developers.cloudflare.com/workers/platform/limits)

## 📚 Related Posts

  * [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)
  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)
  * [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

## Similar Posts

  * [ ![AWS Status Page – Monitoring Included](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png) ](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [AWS Status Page – Monitoring Included](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

By[James](https://jameskilby.co.uk) May 15, 2018 · Updated June 1, 2026

AWS Status Page – Enhancements The tool I deployed, lambstatus, supports pulling metrics from AWS Cloudwatch and displaying them.

  * [ ![Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg) ](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

By[James](https://jameskilby.co.uk) October 20, 2022 · Updated June 1, 2026

For a while now I have been running this site directly from Cloudflare utilising their excellent worker’s product.

  * [ ![What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2018/03/cloudflare/)

[Hosting](https://jameskilby.co.uk/category/hosting/)

### [What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/2018/03/cloudflare/)

By[James](https://jameskilby.co.uk) March 27, 2018 · Updated June 1, 2026

Cloudflare – What is it and why would I care? I have been using Cloudflare for a long time.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk) January 4, 2022 · Updated May 25, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [ ![Fixing Wrangler Node.js Version Conflicts After Brew Upgrade](https://jameskilby.co.uk/wp-content/uploads/2022/01/WranglerCrab-1-768x256.png) ](https://jameskilby.co.uk/2022/01/wrangler-and-node-versions/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/)

### [Fixing Wrangler Node.js Version Conflicts After Brew Upgrade](https://jameskilby.co.uk/2022/01/wrangler-and-node-versions/)

By[James](https://jameskilby.co.uk) January 15, 2022 · Updated June 1, 2026

I am a massive fan of the brew package management system for macOS and use it on all of my Macs. I typically just upgrade everything blindly and have never had an issue.