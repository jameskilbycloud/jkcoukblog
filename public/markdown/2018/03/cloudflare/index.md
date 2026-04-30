---
title: "What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained"
description: "I have been using Cloudflare for a long time. It is one of my go-to services and I use it to protect all of the public services I run for myself and other s..."
date: 2018-03-27T12:30:48+00:00
modified: 2026-04-16T22:02:04+00:00
author: James Kilby
categories:
  - Hosting
  - Artificial Intelligence
  - Docker
  - Homelab
  - Kubernetes
  - Cloudflare
  - Personal
  - Wordpress
  - AWS
tags:
  - #Cloudflare
url: https://jameskilby.co.uk/2018/03/cloudflare/
image: https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png
---

![Iu 2](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png)

[Hosting](https://jameskilby.co.uk/category/hosting/)

# What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained

By[James](https://jameskilby.co.uk)March 27, 2018April 16, 2026 • 📖1 min read(288 words)

📅 **Published:** March 27, 2018• **Updated:** April 16, 2026

## Cloudflare – What is it and why would I care?

I have been using Cloudflare for a long time. It is one of my go-to services and I use it to protect all of the public services I run for myself and other sites/ organizations.

The basic premise of what Cloudflare do is that they are a distributed Web Application Firewall (WAF) and CDN but they also offer so much more. Because they have a large number of POP’s they can cache and push content closer to your end users to give them a better experience. This also offloads work from your firewalls, DNS, Web and Database servers. At present they have [139 sites](https://www.cloudflare.com/network/) globally allowing you to host a site anywhere and get good global performance.

Cloudflare has an amazing free tier so you can get started easily. I use this to host all of my public DNS records. So what does that look like?

[codeblocks name=’host -a’]

As you can see they have given me 2 Nameserver records (Matt and Fay) and also 2 A records Neither of which are my source web server.

Then within the Cloudflare portal, you input where the real webserver lives cloudflare will do the rest. My blog is still a little bit light on readership but you can see Cloudflare handling the spike in requests.

They are also handling the SSL cert for me and the redirect so all traffic is HTTPS to my site allowing me to close port 80 on the firewall all within the free tier.

If you are using WordPress I would strongly recommend the Cloudflare plugin is installed. This way when you make changes to your site it will automatically purge the cache if required

## 📚 Related Posts

  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)
  * [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)
  * [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

## Similar Posts

  * [![How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.30.47-768x411.png)](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

By[James](https://jameskilby.co.uk)January 29, 2025April 16, 2026

Update: Hoarder has now been renamed to Karakeep due to a trademark issue I’ve been on a mission recently to regain control of my data.

  * [![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png)](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk)December 9, 2022April 16, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….

  * [![Fixing Wrangler Node.js Version Conflicts After Brew Upgrade](https://jameskilby.co.uk/wp-content/uploads/2022/01/WranglerCrab-1-768x256.png)](https://jameskilby.co.uk/2022/01/wrangler-and-node-versions/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/)

### [Fixing Wrangler Node.js Version Conflicts After Brew Upgrade](https://jameskilby.co.uk/2022/01/wrangler-and-node-versions/)

By[James](https://jameskilby.co.uk)January 15, 2022April 16, 2026

I am a massive fan of the brew package management system for macOS and use it on all of my Mac’s I typically just upgrade everything blindly and have never had an issue.

  * [![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg)](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk)October 11, 2022April 16, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png)](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk)January 4, 2022April 16, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [![AWS Status Page – Monitoring Included](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png)](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [AWS Status Page – Monitoring Included](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

By[James](https://jameskilby.co.uk)May 15, 2018April 16, 2026

AWS Status Page – Enhancements The tool I deployed lambstatus supports pulling metrics from AWS Cloudwatch and displaying them.