---
title: "What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained"
description: "I have been using Cloudflare for a long time. It is one of my go-to services and I use it to protect all of the public services I run for myself and"
date: 2018-03-27T12:30:48+00:00
modified: 2026-06-01T21:58:21+00:00
author: James Kilby
categories:
  - Hosting
  - Cloudflare
  - Wordpress
  - Personal
  - Ansible
  - Automation
  - Docker
  - Homelab
  - Traefik
  - VCF
  - VMware
tags:
  - #Cloudflare
url: https://jameskilby.co.uk/2018/03/cloudflare/
image: https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png
---

![Iu 2](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png)

[Hosting](https://jameskilby.co.uk/category/hosting/)

# What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained

By[James](https://jameskilby.co.uk)March 27, 2018 · Updated June 1, 2026 • 📖1 min read(287 words)

📅**Published:** March 27, 2018•**Updated:** June 01, 2026

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

  * [![Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

By[James](https://jameskilby.co.uk)October 20, 2022 · Updated June 1, 2026

For a while now I have been running this site directly from Cloudflare utilising their excellent worker’s product.

  * [![WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/wp-content/uploads/2023/05/simply-static-logo.png)](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

By[James](https://jameskilby.co.uk)May 14, 2023 · Updated June 1, 2026

Table of Contents The Tooling The Process WordPress Plugin Install GitHub setup Cloudflare setup I have been using Cloudflare to protect my web assets for a really long time.

  * [![Fixing Wrangler Node.js Version Conflicts After Brew Upgrade](https://jameskilby.co.uk/wp-content/uploads/2022/01/WranglerCrab-1-768x256.png)](https://jameskilby.co.uk/2022/01/wrangler-and-node-versions/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/)

### [Fixing Wrangler Node.js Version Conflicts After Brew Upgrade](https://jameskilby.co.uk/2022/01/wrangler-and-node-versions/)

By[James](https://jameskilby.co.uk)January 15, 2022 · Updated June 1, 2026

I am a massive fan of the brew package management system for macOS and use it on all of my Macs. I typically just upgrade everything blindly and have never had an issue.

  * [![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png)](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk)January 4, 2022 · Updated May 25, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png)](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk)April 10, 2026 · Updated June 1, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg)](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk)October 11, 2022 · Updated June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.