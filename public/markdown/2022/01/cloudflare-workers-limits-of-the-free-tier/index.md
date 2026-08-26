---
title: "Cloudflare Workers – Limits of the free tier"
description: "I have been making several changes (mainly cosmetic to this site over the last day or so) On most changes I have been doing an export and then uploading th"
date: 2022-01-04T21:11:23+00:00
modified: 2026-07-11T13:21:16+00:00
author: James Kilby
categories:
  - Hosting
  - Wordpress
  - Cloudflare
  - Devops
  - Personal
  - Artificial Intelligence
  - Automation
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

By[James](https://jameskilby.co.uk) January 4, 2022 · Updated July 11, 2026 • 📖1 min read(280 words)

I have been making several changes (mainly cosmetic to this site over the last day or so) On most changes I have been doing an export and then uploading the site to Cloudflare using Wrangler. 

After a while I received an email from Cloudflare saying:

_Hi,_

You’re _50% of the way to reaching one of your daily Cloudflare Workers KV free tier limits. You can view complete usage information in the dashboard._

_If you do not take any action and exceed the daily limit, requests to the Workers KV API will return 429 errors, and operations within a worker will fail until the limit resets at 2022-01-05 at 00:00:00 UTC._

I decided to keep ploughing on with my changes to see what happens when I go over this.

The next email I received was slightly more informative as it said which limit I had breached.

_You have exceeded the daily Cloudflare Workers KV free tier limit of 1000 Workers KV put operations._

When I next tried to publish I got the following: 
    
    
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

  * [ ![How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2025/10/Github-Actions.webp) ](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Devops](https://jameskilby.co.uk/category/devops/)

### [How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

By[James](https://jameskilby.co.uk) October 6, 2025 · Updated July 11, 2026

I wanted to automate the publishing of my blog from the authoring side to the public side. These are some of the improvements I made.

  * [ ![Analytics in a privacy focused world](https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png) ](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

I recently helped my friend Dean Lewis @veducate with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress instance.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated July 11, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/wp-content/uploads/2026/01/Website-Optimisations-768x560.png) ](https://jameskilby.co.uk/2026/01/web-development-improvements/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/2026/01/web-development-improvements/)

By[James](https://jameskilby.co.uk) January 15, 2026 · Updated July 11, 2026

I have spent the Christmas break making some improvements to this blog.

  * [ ![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk) January 4, 2022 · Updated July 11, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [ ![What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2018/03/cloudflare/)

[Hosting](https://jameskilby.co.uk/category/hosting/)

### [What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/2018/03/cloudflare/)

By[James](https://jameskilby.co.uk) March 27, 2018 · Updated June 1, 2026

Cloudflare – What is it and why would I care? I have been using Cloudflare for a long time.