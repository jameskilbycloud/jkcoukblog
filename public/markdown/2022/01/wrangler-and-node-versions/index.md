---
title: "Fixing Wrangler Node.js Version Conflicts After Brew Upgrade"
description: "I am a massive fan of the brew package management system for macOS and use it on all of my Mac's I typically just upgrade everything blindly and have never"
date: 2022-01-15T08:42:36+00:00
modified: 2026-07-11T07:47:13+00:00
author: James Kilby
categories:
  - Cloudflare
  - Hosting
  - Personal
  - Wordpress
  - Ansible
  - Automation
  - Docker
  - Homelab
  - Traefik
  - VCF
  - VMware
  - Artificial Intelligence
  - NVIDIA
tags:
  - #Cloudflare
  - #Homebrew
  - #Node
  - #Workers
url: https://jameskilby.co.uk/2022/01/wrangler-and-node-versions/
image: https://jameskilby.co.uk/wp-content/uploads/2022/01/WranglerCrab-1.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2022/01/WranglerCrab-1.png)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/)

# Fixing Wrangler Node.js Version Conflicts After Brew Upgrade

By[James](https://jameskilby.co.uk) January 15, 2022 · Updated July 11, 2026 • 📖1 min read(217 words)

📅**Published:** January 15, 2022•**Updated:** July 11, 2026

I am a massive fan of the brew package management system for macOS and use it on all of my Macs. I typically just upgrade everything blindly and have never had an issue… until today.

I went to push some changes to this site and got the following error message:
    
    
    wrangler publish --env production
    /usr/local/bin/node: bad option: --openssl-legacy-provider
    Error: failed to execute `"/usr/local/bin/node" "--openssl-legacy-provider" "/Users/jameskilby/Library/Caches/.wrangler/wranglerjs-1.19.6" "--output-file=/var/folders/89/z9t99sg16h9cw3t86wp920jr0000gn/T/.wranglerjs_outputGBCY9" "--wasm-binding=WASM_MODULE" "--no-webpack-config=1" "--use-entry=/Users/jameskilby/jameskilbycouk/workers-site/index.js"`: exited with exit status: 9

📋 Copy

A quick bit of digging and it turns out the error was due to a new version of node being used (Version 17) 

The brew search command showed that I still had node16 installed 
    
    
    brew search node  
    ==> Formulae
    libbitcoin-node             node ✔                      node-sass                   node@12                     node@16 ✔                   nodebrew                    nodenv
    llnode                      node-build                  node@10                     node@14                     node_exporter               nodeenv                     ode

📋 Copy

So I then removed the link to the generic node and forced the link to node@16
    
    
    brew unlink node
    
    brew link --overwrite node@16

📋 Copy

Once this was done wrangler worked as expected and published my changes
    
    
    rangler publish --env production
    ✨  Built successfully, built project size is 13 KiB.
    🌀  Using namespace for Workers Site "__jameskilbycouk-production-workers_sites_assets"
    ✨  Success
    🌀  Uploading site files
    

📋 Copy

Certainly not a complex fix but hopefully handy for anyone playing with Wrangler on a Mac and using homebrew.

## 📚 Related Posts

  * [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)
  * [Cloudflare Workers &#8211; Limits of the free tier](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)
  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)

## Similar Posts

  * [ ![Analytics in a privacy focused world](https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png) ](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

By[James](https://jameskilby.co.uk) November 10, 2023 · Updated June 1, 2026

I recently helped my friend Dean Lewis @veducate with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress instance.

  * [ ![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk) January 4, 2022 · Updated July 11, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [ ![Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/wp-content/uploads/2026/01/Website-Optimisations-768x560.png) ](https://jameskilby.co.uk/2026/01/web-development-improvements/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/2026/01/web-development-improvements/)

By[James](https://jameskilby.co.uk) January 15, 2026 · Updated July 11, 2026

I have spent the Christmas break making some improvements to this blog.

  * [ ![WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/wp-content/uploads/2023/05/simply-static-logo.png) ](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

By[James](https://jameskilby.co.uk) May 14, 2023 · Updated June 1, 2026

Table of Contents The Tooling The Process WordPress Plugin Install GitHub setup Cloudflare setup I have been using Cloudflare to protect my web assets for a really long time.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated July 11, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.