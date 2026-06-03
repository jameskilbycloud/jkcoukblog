---
title: "Use Portainer in a Homelab with GitHub"
description: "Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer …."
date: 2022-12-09T09:06:37+00:00
modified: 2026-06-01T19:02:44+00:00
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
  - Nutanix
  - Ansible
  - VCF
  - AWS
  - Storage
tags:
  - #Containers
  - #Docker
  - #Homelab
url: https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/
image: https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

# Use Portainer in a Homelab with GitHub

By[James](https://jameskilby.co.uk) December 9, 2022 · Updated June 1, 2026 • 📖2 min read(459 words)

📅 **Published:** December 09, 2022• **Updated:** June 01, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to [Portainer](https://www.portainer.io)….

I use it for managing the docker containers on my Synology but it can also be used for managing lots of other things. In their own words “Portainer accelerates container adoption. It reduces operational complexity and addresses the security challenges of running containers in Docker, Swarm, Nomad and Kubernetes.”

![Screenshot 2022 11 21 at 17.36.13](https://jameskilby.co.uk/wp-content/uploads/2022/12/Screenshot-2022-11-21-at-17.36.13-1024x638.png)Portainer Platform

Based on the capabilities shown above I am only scratching the surface but I thought I would showcase one of the key features that I am utilising in deployment and updating containers.

## Prerequisites 

For now, I am going to assume that you have a Synology, Docker Installed and Portainer deployed. Plus have a GitHub (or similar) version control system that Portainer can reach. If you don’t have this check out Marius’s great blog with detailed instructions for [Docker](https://mariushosting.com/docker/) and [Portainer](https://mariushosting.com/synology-30-second-portainer-install-using-task-scheduler-docker/) It’s also important to understand user and user id’s and a great blog on this can be found [here](https://drfrankenstein.co.uk/step-2-setting-up-a-restricted-docker-user-and-obtaining-ids/)

## Container Provision

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

## 📚 Related Posts

  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [How I Migrated from Pocket to Hoarder with AI Integration](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [ ![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png) ](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk) April 4, 2026 · Updated June 1, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [ ![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg) ](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James](https://jameskilby.co.uk) February 10, 2019 · Updated June 1, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.

  * [ ![Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg) ](https://jameskilby.co.uk/2018/01/nutanix-ce/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/2018/01/nutanix-ce/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated June 1, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [ ![AWS Status Page – Monitoring Included](https://jameskilby.co.uk/wp-content/uploads/2018/05/AmazonWebservices_Logo.svg_-768x307.png) ](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

[AWS](https://jameskilby.co.uk/category/aws/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

### [AWS Status Page – Monitoring Included](https://jameskilby.co.uk/2018/05/aws-status-page-monitoring-included/)

By[James](https://jameskilby.co.uk) May 15, 2018 · Updated June 1, 2026

AWS Status Page – Enhancements The tool I deployed, lambstatus, supports pulling metrics from AWS Cloudwatch and displaying them.

  * [ ![Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault-768x432.jpeg) ](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

By[James](https://jameskilby.co.uk) January 11, 2022 · Updated June 1, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale.