---
title: "Hosting This Blog on Cloudflare Workers: Why & How I Did It"
description: "A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them."
date: 2022-01-04T11:27:12+00:00
modified: 2026-05-25T08:24:40+00:00
author: James Kilby
categories:
  - Hosting
  - Cloudflare
  - Personal
  - Wordpress
  - AWS
  - Devops
  - Github
  - Nutanix
tags:
  - #Cloudflare
  - #Hosting
url: https://jameskilby.co.uk/2022/01/web-development/
image: https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png
---

![Iu 2](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2.png)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

# Hosting This Blog on Cloudflare Workers: Why & How I Did It

By[James](https://jameskilby.co.uk)January 4, 2022 · Updated May 25, 2026 • 📖1 min read(211 words)

📅**Published:** January 04, 2022•**Updated:** May 25, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them. This is partly related to some issues I have been having with internet access at home. Prior to this, the site ran from within my lab.

This means the site is now super fast (hopefully :p). It was cached by Cloudflare previously and now it’s served entirely from within their network.

![Web performance report](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2021-12-19-at-19.30.43-2048x751-1-1024x376.png)The speed report looks good

To enable this workflow I have retained a WordPress instance running within a docker instance on my Synology. I have also set up Cloudflare teams to access this.

This allows me to have the convenience of utilising WordPress as a CMS without having to worry about the security aspect as all public content is static. It also means that I don’t care about the uptime of the particular instance.

When I have finished writing the post I use the Simply Static Plugin to Generate the required static files. I then copy these to my wrangler site location on my laptop and ask Wrangler to publish them.
    
    
    wrangler publish --env production

📋 Copy

I wrote a post on the initial setup of Cloudflare Workers. Check it out if you are interested in more of how this works.

## 📚 Related Posts

  * [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)
  * [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)
  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)

## Similar Posts

  * [![WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/wp-content/uploads/2023/05/simply-static-logo.png)](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

By[James](https://jameskilby.co.uk)May 14, 2023 · Updated June 1, 2026

Table of Contents The Tooling The Process WordPress Plugin Install GitHub setup Cloudflare setup I have been using Cloudflare to protect my web assets for a really long time.

  * [![AWS Solution Architect – Associate](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png)](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [AWS Solution Architect – Associate](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

By[James](https://jameskilby.co.uk)December 16, 2019 · Updated May 31, 2026

I renewed my AWS Solution Architect certification.

  * [![Analytics in a privacy focused world](https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png)](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

By[James](https://jameskilby.co.uk)November 10, 2023 · Updated June 1, 2026

I recently helped my friend Dean Lewis @veducate with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress instance.

  * [![How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2025/10/Github-Actions.webp)](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Github](https://jameskilby.co.uk/category/github/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare](https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/)

By[James](https://jameskilby.co.uk)October 6, 2025 · Updated June 5, 2026

I wanted to automate the publishing of my blog from the authoring side to the public side. These are some of the improvements I made.

  * [![Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

[Nutanix](https://jameskilby.co.uk/category/nutanix/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Passing the Nutanix NCP Exam: Free Training & My Experience](https://jameskilby.co.uk/2020/07/nutanix-ncp/)

By[James](https://jameskilby.co.uk)July 2, 2020 · Updated May 31, 2026

I saw a tweet a couple of weeks ago mentioning that Nutanix were offering a free go at the Nutanix Certified Professional exam.

  * [![AWS Status Page – Monitoring Included](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png)](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [AWS Status Page – Monitoring Included](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

By[James](https://jameskilby.co.uk)May 15, 2018 · Updated June 1, 2026

AWS Status Page – Enhancements The tool I deployed, lambstatus, supports pulling metrics from AWS Cloudwatch and displaying them.