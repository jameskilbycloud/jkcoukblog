---
title: "Use Portainer in a Homelab with GitHub"
description: "How I use Portainer to manage Docker containers in my homelab, deploying stacks straight from a GitHub repository. Setup and a working example."
date: 2022-12-09T09:06:37+00:00
modified: 2026-06-05T18:57:49+00:00
author: James Kilby
categories:
  - Docker
  - Homelab
  - Hosting
  - Kubernetes
  - Artificial Intelligence
  - Automation
  - NVIDIA
  - Traefik
  - VMware
  - Wordpress
  - Cloudflare
  - Ansible
  - Storage
  - Synology
  - VCF
tags:
  - #Containers
  - #Docker
  - #Homelab
url: https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/
image: https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png
---

![22225832](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

# Use Portainer in a Homelab with GitHub

By[James](https://jameskilby.co.uk)December 9, 2022 · Updated June 5, 2026 • 📖2 min read(474 words)

📅**Published:** December 09, 2022•**Updated:** June 05, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to [Portainer](https://www.portainer.io)….

I use it for managing the docker containers on my Synology but it can also be used for managing lots of other things. In their own words “Portainer accelerates container adoption. It reduces operational complexity and addresses the security challenges of running containers in Docker, Swarm, Nomad and Kubernetes.”

![Screenshot 2022 11 21 at 17.36.13](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-11-21-at-17.36.13-1024x638.png)Portainer Platform

Based on the capabilities shown above I am only scratching the surface but I thought I would showcase one of the key features that I am utilising in deployment and updating containers.

## Prerequisites

For now, I am going to assume that you have a Synology, Docker Installed and Portainer deployed. Plus have a GitHub (or similar) version control system that Portainer can reach. If you don’t have this check out Marius’s great blog with detailed instructions for [Docker](https://mariushosting.com/docker/) and [Portainer](https://mariushosting.com/synology-30-second-portainer-install-using-task-scheduler-docker/) It’s also important to understand user and user id’s and a great blog on this can be found [here](https://drfrankenstein.co.uk/step-2-setting-up-a-restricted-docker-user-and-obtaining-ids/)

## Portainer Container Provisioning

To deploy a container with Portainer I prefer to deploy them in Stacks even if it’s a single container.

Navigate to the Stacks section and select “Add Stack”

![Screenshot 2022 11 21 at 17.59.31](https://jameskilby.co.uk/wp-content/uploads/2023/04/Screenshot-2022-11-21-at-17.59.31.png)Add Stack 

I will show the deployment of a stack to run Grafana as it’s a simple container and popular with homelabbers. The first step is to name the stack which I have called grafana – note these must be lowercase.

The YAML code that the container will use is shown below. This is stored in my private docker repository located at https://github.com/jameskilbynet/docker/grafana
    
    
    version: '3.3'
    services:
        grafana:
            container_name: grafana
            image: grafana/grafana
            user: "1024"
            ports:
                - "3000:3000"  
            volumes:
             - /volume1/docker/grafana:/var/lib/grafana

📋 Copy

Reviewing the YAML code it’s clear that volume mapping is being used. This is a feature to expose a file or folder of the underlying Docker Host into the container. In this case /volume1/docker/grafana Therefore this folder must be created manually. Docker will then map this folder into var/lib/grafana within the container to the /volume1/docker/grafana folder on my Synology

Within Portainer to use a git repository change to the Git tab and enter the relevant details.

![Screenshot 2022 11 22 at 11.56.52 1](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-11-22-at-11.56.52-2048x1133-1-1024x567.png)

I am using a private repository and therefore need to enable authentication to allow Portainer to access the private repo. This requires a Personal Access Token to be created as documented [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

When all of the relevant settings are input then click “Deploy the Stack”

Portainer will then instruct docker to fetch the container (if it hasn’t already) and deploy the stack.

If for any reason this errors, it is usually because the volume map is not set up correctly or a permissions issue. If it’s the former the docker app in Synology will show you.

For more homelab automation, see my post on [managing my homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/).

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)

By[James](https://jameskilby.co.uk)March 27, 2026 · Updated May 31, 2026

A walkthrough of my self-hosted AI stack: Ollama, Open WebUI, ComfyUI, Whishper, n8n, Qdrant, SearxNG, and a full observability layer — all running on my own hardware with Docker Compose.

  * [![Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Cloudflare Workers – Limits of the free tier](https://jameskilby.co.uk/2022/01/cloudflare-workers-limits-of-the-free-tier/)

By[James](https://jameskilby.co.uk)January 4, 2022 · Updated July 11, 2026

I have been making several changes (mainly cosmetic) to this site over the last day or so. On most changes I have been doing an export and then uploading the site to Cloudflare using Wrangler.

  * [![WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/wp-content/uploads/2023/05/simply-static-logo.png)](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)

By[James](https://jameskilby.co.uk)May 14, 2023 · Updated June 1, 2026

Table of Contents The Tooling The Process WordPress Plugin Install GitHub setup Cloudflare setup I have been using Cloudflare to protect my web assets for a really long time.

  * [![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png)](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk)April 15, 2026 · Updated June 1, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introduction One of the larger costs of running my homelab is the electricity….

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [My First Homelab Storage Setup: HP Gen8 & Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

By[James](https://jameskilby.co.uk)January 6, 2018 · Updated June 1, 2026

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below.

  * [![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png)](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk)April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.