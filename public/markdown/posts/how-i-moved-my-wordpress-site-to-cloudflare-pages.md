---
title: "Static WordPress hosting using Cloudflare"
description: "For a while now I have been running this site directly from Cloudflare utilising their excellent worker’s product. I did this originally as a learning exerci..."
date: 2022-10-20T15:26:08+00:00
modified: 2026-04-16T22:01:53+00:00
author: James Kilby
categories:
  - Cloudflare
  - Hosting
  - Wordpress
  - Ansible
  - Automation
  - Docker
  - Homelab
  - Traefik
  - VCF
  - VMware
  - Personal
  - AWS
  - Kubernetes
tags:
  - #Cloudflare
  - #Hosting
  - #Wordpress
  - #Workers
url: https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/
image: https://jameskilby.co.uk/wp-content/uploads/2022/10/iu.jpeg
---

![Iu](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu.jpeg)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

# Static WordPress hosting using Cloudflare

By[James](https://jameskilby.co.uk)October 20, 2022April 16, 2026 • 📖4 min read(851 words)

📅 **Published:** October 20, 2022• **Updated:** April 16, 2026

For a while now I have been running this site directly from [Cloudflare](http:// <p>For a while now I have been running this site directly from Cloudflare utilising their workers product. This has brought several benefits:</p>   <p>Crazy Web Performance</p>   <p>High Availability </p>   <p>Zero attack surface</p>   <p>A couple of people have asked me about the setup so I thought I would try and document it.</p>   <p>Firstly although this is effectively Serverless, I still have a copy of WordPress running. It lives in some docker containers on my NAS and it is not currently published to the outside world. This hugely reduces the attack surface. Editing and contributing content works in exactly the same way however publishing is where the difference is seen.</p>   <p>At a very high level I have a WordPress plugin that generates the static content, This is then pushed into a GitHub Repo and from there its pushed to Cloudflare Pages.</p> ) utilising their excellent worker’s product. I did this originally as a learning exercise but due to the benefits It brought and the ease of use I decided to stick with it. The benefits are several fold:

  * Crazy Web Performance (Typically full page load in less than 500ms see below)
  * High Availability globally
  * Zero attack surface
  * ~Zero hosting costs

![Screenshot 2022 10 19 at 23.02.09 1](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-10-19-at-23.02.09-2048x860-1-1024x430.png)Gtmetrix Speed Test

A couple of people have asked me about the setup so I thought I would try and document an overview.

## Introduction

Firstly although this setup is effectively Serverless you need to have a copy of WordPress somewhere to make your edits. This doesn’t need to be exposed to the outside world (or can even be run just on your workstation/laptop using [local](https://localwp.com). I have chosen to keep WordPress running in some docker containers on my [Synology](https://jameskilby.co.uk/lab/)

The security of this setup is increased as WordPress is not published to the outside world. I do all of my editing locally, however, if I needed to change this I would leverage Cloudflare Access. Not publishing the site externally hugely reduces the attack surface as there is no implementation to attack. Editing and contributing content works in exactly the same way the difference is how content is published

At a very high level, I have a WordPress plugin that generates static content. This is then pushed into a GitHub Repo and from there, it’s pushed to Cloudflare Pages.

For

## WordPress Setup

Within WordPress, I am utilising the simply static [plugin](https://simplystatic.com) to generate the static content.

Initially, I was using the free plugin but I have since decided to upgrade to the paid-for version.

In terms of the plugin setup, I have it set to use relative URL’s with a delivery method set to GitHub. This is done as the WordPress site is on my NAS and therefore has a URL of http://nas1.jameskilby.net/

I have then excluded the WordPress management URL’s in the static generation.
    
    
    http://wordpress.jameskilby.cloud/wp-json
    https://wordpress.jameskilby.cloud/wp-login.php

📋 Copy

## GitHub Setup

In the deployment section, I have added the relevant details so that the simply static plugin can push the relevant content into a GitHub repo

![Static WordPress hosting using Cloudflare Screenshot](https://jameskilby.co.uk/wp-content/uploads/2022/10/Screenshot-2022-07-09-at-17.29.07-2048x1191-1-1024x596.png)

Within GitHub, I have created a repo (Called jameskilbycouksite) I have made this private but it could easily be a public repo. I have then added my [personal access token ](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)so that SimplyStatic can push to the repo and lastly added a webhook to be called when the site has been updated (More on this a bit later)

## Cloudflare Page Builds

The Cloudflare setup is probably the most complex part of the process but once it has been set up it’s fire and forget. The page’s site needs to be set up in Cloudflare and then a Webhook is created that the WordPress site can trigger. This is triggered when all of the site is committed to GitHub to tell Cloudflare to refresh the build.

When you are logged into Cloudflare navigate to the pages section and create a project. At this point, I selected connect to Git and login/select the relevant GitHub account and Repo. For this to function, the GitHub Pages application needs to have been given permission in your GitHub Account

![Static WordPress hosting using Cloudflare Screenshot](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-07-09-at-18.53.21-1024x925.png)GitHub Pages Permissions

When a page is complete and published at a WordPress level a new button is enabled called “Generate Static” When this is clicked it will run the process to generate the static page, push it to GitHub and then to Cloudflare.

The Paid plugin allows for updating a single page, whereas the free plugin needs to generate the entire site again.

As seen below, a single page usually takes around 9 seconds to update with this setup. Generating the entire site and uploading took approx 30 mins.
    
    
    [2022-07-17 18:37:46] Setting up
    [2022-07-17 18:37:49] Fetched 1 of 1 pages/files
    [2022-07-17 18:37:51] Committed / Updated 81 of 81 pages/files
    [2022-07-17 18:37:55] Wrapping up
    [2022-07-17 18:37:55] Done! Finished in 00:00:09

📋 Copy

Lastly, I have removed Google Analytics for privacy reasons and just utilise the web analytics built natively into Cloudflare.

## Costs

The cost of running the site in Cloudflare for my blog is exactly zero which is amazing. This is one of the reasons I decided to buy the plugin as it was roughly equivalent to a year’s worth of decent hosting.

If your site is more popular then you may require one of the paid plans that starts at $5 a month.

The free tier gives you:

 **Workers Bundled (Workers Compute time)**

  * Up to 10ms CPU time per request
  * Lowest latency after the first request
  * Up to 100,000 requests per day (UTC+0)

 **KV (Key Value Storage)**

  * Global low-latency key-value edge storage
  * Up to 100,000 read operations per day
  * Up to 1,000 write, delete, list operations per day

Although I have paid $99 for the single-site plugin this is not essential. It does however eliminate some manual steps which I was keen to avoid. Plus although I am not currently using them it does support forms and search capabilities.

For more like this why not follow me on [Twitter](https://x.com/jameskilbynet)

## 📚 Related Posts

  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)
  * [How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)
  * [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

## Similar Posts

  * [![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png)](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk)April 10, 2026April 16, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png)](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk)January 4, 2022April 16, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [![What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png)](https://jameskilby.co.uk/2018/03/cloudflare/)

[Hosting](https://jameskilby.co.uk/category/hosting/)

### [What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/2018/03/cloudflare/)

By[James](https://jameskilby.co.uk)March 27, 2018April 16, 2026

Cloudflare – What is it and why would I care? I have been using Cloudflare for a long time.

  * [![Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

By[James](https://jameskilby.co.uk)January 4, 2022April 16, 2026

I have been making several changes (mainly cosmetic to this site over the last day or so) On most changes I have been doing an export and then uploading the site to Cloudflare using Wrangler.

  * [![AWS Status Page – Monitoring Included](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png)](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [AWS Status Page – Monitoring Included](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

By[James](https://jameskilby.co.uk)May 15, 2018April 16, 2026

AWS Status Page – Enhancements The tool I deployed lambstatus supports pulling metrics from AWS Cloudwatch and displaying them.

  * [![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png)](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk)December 9, 2022April 16, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….