---
title: "What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained"
description: "Cloudflare - What is it and why would I care? I have been using Cloudflare for a long time."
date: 2018-03-27T12:30:48+00:00
modified: 2026-06-01T21:58:21+00:00
author: James Kilby
categories:
  - Hosting
  - Ansible
  - Automation
  - Cloudflare
  - Devops
  - Artificial Intelligence
  - Docker
tags:
  - #Cloudflare
url: https://jameskilby.co.uk/2018/03/cloudflare/
image: https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png)

[Hosting](https://jameskilby.co.uk/category/hosting/)

# What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained

By[James](https://jameskilby.co.uk) March 27, 2018 · Updated June 1, 2026 • 📖1 min read(287 words)

## Cloudflare – What is it and why would I care?

I have been using Cloudflare for a long time. It is one of my go-to services and I use it to protect all of the public services I run for myself and other sites/organisations.

The basic premise of what Cloudflare do is that they are a distributed Web Application Firewall (WAF) and CDN but they also offer so much more. Because they have a large number of POPs they can cache and push content closer to your end users to give them a better experience. This also offloads work from your firewalls, DNS, Web and Database servers. At present they have [139 sites](https://www.cloudflare.com/network/) globally allowing you to host a site anywhere and get good global performance.

Cloudflare has an amazing free tier so you can get started easily. I use this to host all of my public DNS records. So what does that look like?

[codeblocks name=’host -a’]

As you can see they have given me 2 Nameserver records (Matt and Fay) and also 2 A records. Neither of which are my source web server.

Then within the Cloudflare portal, you input where the real webserver lives. Cloudflare will do the rest. My blog is still a little bit light on readership but you can see Cloudflare handling the spike in requests.

They are also handling the SSL cert for me and the redirect so all traffic is HTTPS to my site allowing me to close port 80 on the firewall all within the free tier.

If you are using WordPress I would strongly recommend the Cloudflare plugin is installed. This way when you make changes to your site it will automatically purge the cache if required….

## 📚 Related Posts

  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)
  * [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)
  * [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

## Similar Posts

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2025/10/Github-Actions.webp) ](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Devops](https://jameskilby.co.uk/category/devops/)

### [How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

By[James](https://jameskilby.co.uk) October 6, 2025 · Updated July 11, 2026

I wanted to automate the publishing of my blog from the authoring side to the public side. These are some of the improvements I made.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated July 11, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.30.47-768x411.png) ](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/)

### [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

By[James](https://jameskilby.co.uk) January 29, 2025 · Updated July 11, 2026

Update: Hoarder has now been renamed to Karakeep due to a trademark issue I’ve been on a mission recently to regain control of my data.

  * [ ![Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg) ](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

By[James](https://jameskilby.co.uk) October 20, 2022 · Updated July 11, 2026

For a while now I have been running this site directly from Cloudflare utilising their excellent worker’s product.

  * [ ![Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/wp-content/uploads/2026/01/Website-Optimisations-768x560.png) ](https://jameskilby.co.uk/2026/01/web-development-improvements/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/2026/01/web-development-improvements/)

By[James](https://jameskilby.co.uk) January 15, 2026 · Updated July 11, 2026

I have spent the Christmas break making some improvements to this blog.