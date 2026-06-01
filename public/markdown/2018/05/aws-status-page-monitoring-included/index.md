---
title: "AWS Status Page – Monitoring Included"
description: "AWS Status Page – Enhancements The tool I deployed lambstatus supports pulling metrics from AWS Cloudwatch and displaying them."
date: 2018-05-15T21:41:14+00:00
modified: 2026-06-01T19:00:02+00:00
author: James Kilby
categories:
  - AWS
  - Hosting
  - Homelab
  - Personal
  - Cloudflare
  - Wordpress
  - VMware
  - VMware Cloud on AWS
tags:
  - #AWS
  - #Lambda
url: https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/
image: https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_.png)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

# AWS Status Page – Monitoring Included

By[James](https://jameskilby.co.uk) May 15, 2018June 1, 2026 • 📖1 min read(105 words)

📅 **Published:** May 15, 2018• **Updated:** June 01, 2026

## **AWS Status Page – Enhancements**

The tool I deployed [lambstatus](https://lambstatus.github.io/get-started/) supports pulling metrics from AWS Cloudwatch and displaying them. As part of my personal development, I thought I would include this on my status page.

I managed to get this working as can be seen [here. ](https://d1wijjwc03zzo1.cloudfront.net)This is a lambda function running once a minute polling this website and adding the response time into AWS Cloudwatch which Lambstatus is allowed to call. It has been running without a hitch for nearly a month now at **effectively zero cost**

#### Site Response

![Screen Shot 2018 05 15 at 22.39.01](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screen-Shot-2018-05-15-at-22.39.01.png)

The guide I followed is very good and is documented in the Git repo [here](https://lambstatus.github.io/set-up-custom-http-s-monitoring/)

## 📚 Related Posts

  * [Monitoring VMware Cloud on AWS: Tools &#038; Approaches (Part 1)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)
  * [AWS Solution Architect &#8211; Associate](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)
  * [AWS For Beginners: IAM Setup, Root Security &#038; Billing Alerts](https://jameskilby.co.uk/2018/03/aws-for-beginners1/)

## Similar Posts

  * [ ![Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/wp-content/uploads/2022/10/spacexs-starlink-to-supply-free-satellite-internet-to-famili_u44u.1920-768x432.jpg) ](https://jameskilby.co.uk/2022/10/starlink/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [Starlink Satellite Internet Review: Rural Broadband Solution](https://jameskilby.co.uk/2022/10/starlink/)

By[James](https://jameskilby.co.uk) October 11, 2022June 1, 2026

Since moving to Dorset last year internet connectivity has been the bane of my existence. Currently, I have an ADSL connection provided by my old employer Zen and a 5G connection provided by Three.

  * [ ![AWS Solution Architect – Associate](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png) ](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [AWS Solution Architect – Associate](https://jameskilby.co.uk/2019/12/aws-solution-architect-associate/)

By[James](https://jameskilby.co.uk) December 16, 2019May 31, 2026

I renewed my AWS Solution Architect certification.

  * [ ![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk) January 4, 2022May 25, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [ ![Analytics in a privacy focused world](https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png) ](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

By[James](https://jameskilby.co.uk) November 10, 2023June 1, 2026

I recently helped my friend Dean Lewis @veducate with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress instance.

  * [ ![What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2018/03/cloudflare/)

[Hosting](https://jameskilby.co.uk/category/hosting/)

### [What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/2018/03/cloudflare/)

By[James](https://jameskilby.co.uk) March 27, 2018June 1, 2026

Cloudflare – What is it and why would I care? I have been using Cloudflare for a long time.

  * [ ![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png) ](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [How VMware Cloud on AWS Handles Host Failures Automatically](https://jameskilby.co.uk/2020/09/vmc-host-errors/)

By[James](https://jameskilby.co.uk) September 15, 2020June 1, 2026

Learn how host failures are handled within VMC