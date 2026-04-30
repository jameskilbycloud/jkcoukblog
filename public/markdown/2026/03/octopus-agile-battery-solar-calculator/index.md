---
title: "Free Octopus Agile Battery & Solar Calculator: 5 Batteries Tested"
description: "I am quite a heavy consumer of electricity at home. This is primarily driven by my lab but having a young son and two golden retrievers means more washing an..."
date: 2026-03-09T23:39:37+00:00
modified: 2026-04-16T22:01:38+00:00
author: James Kilby
categories:
  - Artificial Intelligence
  - Automation
  - Docker
  - Homelab
  - NVIDIA
  - Traefik
  - VMware
  - Ansible
  - Containers
  - Devops
tags:
  - #Energy
  - #Octopus
  - #Smart Home
url: https://jameskilby.co.uk/2026/03/octopus-agile-battery-solar-calculator/
image: https://jameskilby.co.uk/wp-content/uploads/2026/03/Octopus-Energy-logo.jpg
---

![Octopus Energy Logo](https://jameskilby.co.uk/wp-content/uploads/2026/03/Octopus-Energy-logo.jpg)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/)

# Free Octopus Agile Battery & Solar Calculator: 5 Batteries Tested

By[James](https://jameskilby.co.uk)March 9, 2026April 16, 2026 • 📖5 min read(979 words)

📅 **Published:** March 09, 2026• **Updated:** April 16, 2026

I am quite a heavy consumer of electricity at home. This is primarily driven by my [lab](https://jameskilby.co.uk/lab/) but having a young son and two golden retrievers means more washing and drying. As a result I am always looking to try and reduce the electrical costs as it’s not cheap in the UK.

## Table of Contents

## Problem

Sadly my roof isn’t an ideal candidate for solar panels as the south facing part isn’t huge and has some shade, therefore I was looking at other options. I have been an Octopus Energy customer for a number of years, they have become one of the larger suppliers in the UK by offering a wide range of interesting tariffs and good customer support. I am on the “Agile Tariff” which means the price of electricity that I pay varies widely with the price changing every 30 minutes. Despite having some expensive time periods I generally come out ahead. ( I am £178 better off than a tracker tariff over the last 4 months)

I have often wondered if I can make a household battery make financial sense. A lot of the public calculators didn’t really give me the level of information I needed. Therefore I decided to build this Octopus Agile battery calculator. Disclaimer: all of the coding for this project was done by [Claude](http://Claude.ai) — I can’t take any credit for it and for legal reasons double check the maths.

Below is the typical profile taken from today’s rates. Although the price changes based on demand and generation, typically windy and sunny days are the best. The typical cost profile follows this shape. Generally cheaper electricity most of the day and an expensive period between 4 and 7pm. At the time of writing the Middle East conflict has just started so the prices are higher than typical and the range between the lower and higher rate is narrower than usual.

![Agile Rate Profile](https://jameskilby.co.uk/wp-content/uploads/2026/03/Screenshot-2026-03-07-at-07.30.35-1024x713.png)

## Code

If you want to skip reading and jump straight to the code on [Github](https://github.com/jameskilbynet/AgileBatteryPredicter)

You need Python 3.8 and requests module and to add your Octopus API key to the .env file and then run the script.To get your API key just head to your Octopus account dashboard and open [**Developer settings**.](https://octopus.energy/dashboard/new/accounts/personal-details) When you run the script it will connect to the Octopus Kraken system and pull your historic usage and pricing data in 30-minute chunks. Once it has done this it will generate an HTML file called octopus_battery_report.html next to the python script for easy consumption.

You can also execute the code as a one liner:
    
    
    python3 octopus_battery_analysis.py --api-key sk_live_yourkey

📋 Copy

I have also included a diagnostic script in the repo for troubleshooting API issues octopus_diagnose.py

## Report Overview

I have built an example report that can be seen [here](https://jameskilbynet.github.io/AgileBatteryPredicter/example_report.html) below is the extract from my usage.

### Usage Summary

![Agile Usage Summary](https://jameskilby.co.uk/wp-content/uploads/2026/03/Agile-usage-Summary-1024x247.png)

This is my usage report, and as can be seen I used 9,615kWh over the last year. For someone with gas heating and no electric cars this is quite high. I could also see this usage increasing. It also shows I had 164 hours at 0 cost or where Octopus paid me a small amount to use energy. The report then goes into a bit more consumption detail which is fairly self-explanatory.

### Agile Rate Distribution

![Agile Rate Distribution](https://jameskilby.co.uk/wp-content/uploads/2026/03/Agile-Rate-Distribution-1024x347.png)

The distribution is important to understand so we can see if we can push our usage to the left with a battery. 

The report then goes on to make battery recommendations based on the data with multiple charging strategies. The default strategy is a very simple one: we charge the battery if the charge is ≤10.0p and discharge≥20.0p

### Battery Recommendation 

The report has details of five of the most common batteries in the UK. Powerwall 2, GivEnergy 9.5kWh, Givenergy 13.5kWh, Sonnen 10kWh, Pylontech 7.4kWh. They all have different capacities and an estimated install cost is also assumed. It then calculates what savings could be achieved with each of these setups with either the default charging strategy or an optimised one.

Based on my usage the payback is never and the 15yr return on investment is very negative. This was disappointing. 

![Battery Recommendation](https://jameskilby.co.uk/wp-content/uploads/2026/03/BatteryRecomendation--1024x447.png)

### What If Calculator

I decided to see if I could improve by simulating some what-if scenarios so I added a slider into the report to take account of the cost of the battery system reducing and the price of electricity increasing. Unfortunately for my use case even if the price of batteries halve and the price of electric doubles it still doesn’t make sense for me to install a battery.

### Solar

OK so what if I was to add solar to the mix? This brings another factor to consider as effectively it leads to three strategies, Solar only, Battery only or Solar and Battery. The report will showcase some typical solar installs and calculate the solar generation where the energy would be consumed by my home first and then being exported. It will model several typical solar setups 3, 4 and 6kW and ultimately recommend the most cost effective setup.I was surprised by the answer to this where a 4kW solar system without a battery is what is ultimately recommended. However this still looks like a poor investment for me personally.

![Best Solar and Battery Combination](https://jameskilby.co.uk/wp-content/uploads/2026/03/Best-Combination-1024x375.png)

#### SEG – Smart Export Guarantee

The calculator will also include earnings for any unused solar energy. This is an important factor in the calculations 

## Conclusion

For my current usage neither a battery nor solar panels make a good investment however, I will be reviewing this periodically as the benefits and the price of both solar and battery have changed dramatically in the last couple of years. Hopefully you have a better output from the calculator.

I am also incredibly impressed with Claude’s ability to build this with limited prompting from me. The results look interesting although the script has gone through limited testing due to me only having access to two accounts with Octopus.

## 📚 Related Posts

  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk)April 4, 2026April 16, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png)](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk)April 15, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introudction One of the larger costs of running my homelab is the electricity….

  * [![Template Deployment with Packer](https://jameskilby.co.uk/wp-content/uploads/2021/01/logo_packer.png)](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Template Deployment with Packer](https://jameskilby.co.uk/2021/01/hashicorp-packer/)

By[James](https://jameskilby.co.uk)January 21, 2021April 16, 2026

Packer is one of those tools I have heard about, and some of the cool people on Twitter that I follow have been using it for a while.

  * [![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png)](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk)February 9, 2026April 16, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg)](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk)October 11, 2024April 16, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk)March 27, 2026April 16, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.