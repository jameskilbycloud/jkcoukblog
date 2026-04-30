---
title: "Automated VCF 9 Offline Depot"
description: "One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let's Encrypt wildcard certs via Cloudflare DNS."
date: 2026-04-10T11:36:03+00:00
modified: 2026-04-16T22:01:37+00:00
author: James Kilby
categories:
  - Ansible
  - Automation
  - Docker
  - Homelab
  - Traefik
  - VCF
  - VMware
  - Hosting
  - Cloudflare
  - Personal
  - Wordpress
  - TrueNAS Scale
  - vSAN
  - vSphere
  - VMware Cloud on AWS
  - Networking
  - Storage
tags:
  - #Ansible
  - #Automation
  - #Bash
  - #Cloudflare
  - #Docker
  - #Homelab
  - #HTTPS
  - #Lets Encrypt
  - #Nginx
  - #Reverse Proxy
  - #Traefik
  - #Ubuntu
  - #VCF
  - #VCF 9
  - #VCF Offline Depot
url: https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/
image: https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png
---

![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Automated VCF 9 Offline Depot

By[James](https://jameskilby.co.uk)April 10, 2026April 16, 2026 • 📖7 min read(1,427 words)

📅 **Published:** April 10, 2026• **Updated:** April 16, 2026

This Automated VCF 9 Offline Depot was built to solve a simple problem: [VCF 9](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-0.html) changed its deployment model, and I needed a repeatable, hands-off way to spin one up in my lab. The script and Ansible playbook take a fresh Ubuntu VM and turn it into a fully working depot with publicly-trusted SSL certificates from Let’s Encrypt.

The deployment means no manual Docker installs, no messing with certificates, no clicking through dashboards. Just SSH in, run one command, and have a fully working HTTPS file server with automatic Let’s Encrypt certificates via Cloudflare DNS. It basically simplifies and automates the official process documented [here](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-0/deployment/deploying-a-new-vmware-cloud-foundation-or-vmware-vsphere-foundation-private-cloud-/preparing-your-environment/downloading-binaries-to-the-vcf-installer-appliance/connect-to-an-offline-depot-to-download-binaries/set-up-an-offline-depot-web-server-for-vmware-cloud-foundation.html). Thanks to [Gareth ](https://www.virtualisedfruit.co.uk)for pushing me to finish this and helping with testing.

If you want to jump in and deploy right away, you can execute the below or go and look at the GitHub repo [here](https://github.com/jameskilbynet/iac/tree/main/docker/vcf9-offline-depot)
    
    
    curl -sSL https://raw.githubusercontent.com/jameskilbynet/iac/main/docker/vcf9-offline-depot/deploy.sh -o /tmp/deploy.sh
    sudo bash /tmp/deploy.sh

📋 Copy

## Table of Contents

## Prerequisites

  * A Cloudflare-managed domain + API key with DNS `Zone:DNS:Edit` and `Zone:Zone:Read` permissions
  * Ubuntu 22.04+ with at least 100GB of free disk space. I would recommend 200GB+ 
  * Internet access from the Ubuntu VM
  * DNS records to be used for the web server and the Traefik dashboard. For this I am using `vcf.jameskilby.cloud `and `traefik.jameskilby.cloud`

## What it does

  * A single bash script takes a vanilla Ubuntu server and builds the entire stack:
  * Installs **Git** , **Ansible** , **Docker Engine** and **Docker Compose**
  * Deploys **Traefik** as a reverse proxy with automatic wildcard SSL via Cloudflare DNS challenge
  * Deploys **Nginx** as a file server with directory browsing enabled
  * Creates a `/vcf` directory on the host, owned by the deploying user, mounted into the container
  * Protects the web server with **HTTP basic authentication**
  * Forces all HTTP traffic to HTTPS
  * Exposes the **Traefik dashboard** on its own subdomain

![VCF Offline Depot](https://jameskilby.co.uk/wp-content/uploads/2026/04/VCF-Offline-Depot-1024x538.png)

The script pulls and executes the below files.
    
    
    docker/traefik-nginx/
    ├── deploy.sh              # Bootstrap script — run this
    ├── playbook.yml           # Ansible playbook — does the work
    ├── docker-compose.yml     # Root compose file
    ├── .env.example           # Example environment variables
    └── compose/
        ├── traefik.yml        # Traefik reverse proxy
        └── nginx.yml          # Nginx file server

📋 Copy

When it’s deployed you can drop the VCF installer files into the /vcf directory and they are passed through to the web server for use in VCF deployments. I do this using FileZilla but any method will work.

What the script does under the hood is 

**1\. Docker Installation** — Adds Docker’s official GPG key and APT repository, installs Docker Engine, CLI, containerd, Buildx and the Compose plugin. It detects the system architecture automatically so it works on both amd64 and arm64.

 **2\. Directory Structure** — Creates the stack directory at `/opt/traefik-nginx` with subdirectories for compose files, Traefik config, and Nginx config. Creates `/vcf` owned by the user who ran `sudo` so you can write files there without root.

 **3\. Nginx Config** — Writes a custom `default.conf` that enables `autoindex` for directory browsing with human-readable file sizes and local timestamps.

 **4\. Traefik Static Config** — Generates `traefik.yml` with:

  * HTTP and HTTPS entrypoints
  * Cloudflare DNS challenge for Let’s Encrypt certificates
  * Docker provider for automatic service discovery
  * Dashboard enabled via its own subdomain

 **5\. Environment File** — Writes `.env` (mode `0600`) containing the domain, subdomain, Cloudflare token, basic auth hash, and install directory. Docker Compose interpolates these into container labels at runtime.

 **6\. Network & Stack** — Creates the `traefik` Docker network (idempotent), then runs `docker compose up -d`.

The stack is split across two compose files included from a root `docker-compose.yml`:

 **Traefik** (`compose/traefik.yml`):

  * Binds ports 80 and 443
  * Mounts the Docker socket (read-only) for container discovery
  * Global HTTP-to-HTTPS redirect via a catchall router
  * Dashboard exposed at `traefik.yourdomain.com`

 **Nginx** (`compose/nginx.yml`):

  * Mounts `/vcf` from the host as the web root (read-only)
  * Custom nginx config for directory browsing
  * Basic auth middleware via Traefik labels, reading credentials from `${BASICAUTH_USERS}` in `.env`
  * Serves on `${SUBDOMAIN}.${DOMAIN}`

Both containers run with `no-new-privileges` security option and JSON file logging with rotation.

## Security

Whenever you’re adding passwords or tokens into a system, care needs to be taken. The script will handle the Cloudflare API Token and password in a secure manner. When the secure variables are entered they are handled with `read -rsp` this means that they don’t echo to the terminal as they are entered. These secrets are stored temporarily in a file with root only readable permissions. This has an automatic cleanup so that if the script completes successfully or if it crashes or is stopped manually this file is removed using ``trap 'rm -f "$VARS_FILE"' EXIT INT TERM``. Unset is also used to clear plaintext variables from the shell after they have been written to disk.

## How to use

SSH into your VM and run 
    
    
    curl -sSL https://raw.githubusercontent.com/jameskilbynet/iac/main/docker/vcf9-offline-depot/deploy.sh -o /tmp/deploy.sh
    sudo bash /tmp/deploy.sh

📋 Copy

The script will prompt for your domain, subdomain, web-server username and password, and Cloudflare API token. It confirms your input, then handles everything else. 

![RunDeployment](https://jameskilby.co.uk/wp-content/uploads/2026/04/RunDeployment-1024x508.png)

A few minutes later you’ll see:
    
    
    ═══════════════════════════════════════════
      Deployment Complete
    ═══════════════════════════════════════════
    
      Nginx:     https://vcf.jameskilby.cloud
      Traefik:   https://traefik.jameskilby.cloud
      Web root:  /vcf
      Stack dir: /opt/vcf9-offline-depot
    
      DNS: Point *.jameskilby.cloud to this server's IP.
      Certs will be issued automatically via Cloudflare DNS.

📋 Copy

Your Automated VCF 9 Offline Depot is now running and accessible over HTTPS.

If you then access the nginx web server at your defined address i.e. https://vcf.jameskilby.cloud 

It should prompt you to log in using the credentials you defined at runtime. If it’s all working you should be presented with the following webpage and it should be on a fully trusted SSL certificate.

![workingnginx](https://jameskilby.co.uk/wp-content/uploads/2026/04/workingnginx-1024x752.png)

## Related reading

If you like the Traefik + Cloudflare DNS pattern used here, the same stack powers my homelab AI infrastructure. These posts cover how it all fits together:

  * [Automating the deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)
  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

## Troubleshooting

Most problems fall into one of a handful of categories. Here are the checks I run first when something doesn’t come up clean.

### Certificates aren’t being issued

The first thing to do is wait. It can take a minute or more for the process of issuing the certificate to complete. **Don’t** start troubleshooting immediately.

If, after a minute, Traefik is still serving the default self-signed certificate instead of a Let’s Encrypt one, it’s almost always the Cloudflare API token. Verify the token is valid and scoped correctly:
    
    
    curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
      -H "Authorization: Bearer <token>"

📋 Copy

The token needs `Zone:DNS:Edit` and `Zone:Zone:Read` permissions on the zone you’re issuing certificates for. Then check the Traefik logs for ACME errors:
    
    
    docker logs traefik 2>&1 | grep -i acme

📋 Copy

One issue you might hit (which I ran into while documenting things) was hitting Let’s Encrypt’s rate limits. You will see something like this in the Traefik logs if you do
    
    
    sudo docker logs traefik 2>&1 | grep -i "docker" | tail -10
    
    ERR Unable to obtain ACME certificate for domains error="unable to generate a certificate for the domains [jameskilby.cloud *.jameskilby.cloud]: acme: error: 429 :: POST :: https://acme-v02.api.letsencrypt.org/acme/new-order :: urn:ietf:params:acme:error:rateLimited :: too many certificates (5) already issued for this exact set of identifiers in the last 168h0m0s, retry after 2026-04-11 03:06:50 UTC: see https://letsencrypt.org/docs/rate-limits/#new-certificates-per-exact-set-of-identifiers" ACME CA=https://acme-v02.api.letsencrypt.org/directory acmeCA=https://acme-v02.api.letsencrypt.org/directory domains=["jameskilby.cloud","*.jameskilby.cloud"] providerName=cloudflare.acme routerName=nginx@docker rule=Host(`vcf.jameskilby.cloud`)

📋 Copy

If you’re stuck on a staging certificate after fixing the token, truncate `acme.json` and restart Traefik so it requests a fresh one:
    
    
    truncate -s 0 /opt/traefik-nginx/traefik/acme.json
    docker restart traefik

📋 Copy

### Docker fails to install

If the playbook fails installing Docker, the VM usually has pending kernel updates waiting for a reboot. Either reboot manually and re-run, or allow the playbook to reboot for you by re-running with `-e allow_reboot=true`.

## Increase Disk Size 

The script will fail if you don’t have 100GB of available storage. You will need at least this for the VCF install binaries. If you have presented a single large disk to the VM and used Ubuntu’s auto partitioning it won’t utilise all of the drive. See my blog [here](https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/) on how to expand the disk to its full size

### Review the Traefik Dashboard

If you’re still having issues review the Traefik Dashboard `https://traefik.domain.com`

You should see four routers and six services like the attached screenshots

![traefikrouters](https://jameskilby.co.uk/wp-content/uploads/2026/04/traefikrouters-1024x254.png)![traefikservices](https://jameskilby.co.uk/wp-content/uploads/2026/04/traefikservices-1024x326.png)

### Basic auth prompt loops

If the depot keeps prompting for credentials even with the right ones, it’s almost always `$` escaping. Docker Compose treats `$` as variable interpolation, so every `$` in the apr1 hash must be doubled to `$$`. The deploy script handles this automatically, but if you’re editing `.env` by hand, double-check the escaping.

## 📚 Related Posts

  * [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)
  * [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

## Similar Posts

  * [![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png)](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk)April 15, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introudction One of the larger costs of running my homelab is the electricity….

  * [![Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png)](https://jameskilby.co.uk/2022/01/web-development/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Personal](https://jameskilby.co.uk/category/personal/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Hosting This Blog on Cloudflare Workers: Why & How I Did It](https://jameskilby.co.uk/2022/01/web-development/)

By[James](https://jameskilby.co.uk)January 4, 2022April 16, 2026

A while ago I started messing with Cloudflare Workers. I have now moved this site permanently over to them.

  * [![How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg)](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

By[James](https://jameskilby.co.uk)December 18, 2024April 16, 2026

Introduction Copy on Write Disk IDs Trim Introduction I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010.

  * [![New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp)](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [New VMware Cloud on AWS Host: i7i.metal-24xl](https://jameskilby.co.uk/2026/04/new-vmc-host-i7i-metal-24xl/)

By[James](https://jameskilby.co.uk)April 1, 2026April 16, 2026

We’ve expanded the VMC fleet with the new i7i (i7i.

  * [![MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/wp-content/uploads/2023/04/2157_hi_res-768x346.png)](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/) | [Storage](https://jameskilby.co.uk/category/storage/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [MikroTik CRS504 Review: 100Gb/s Networking in My Homelab](https://jameskilby.co.uk/2022/12/100gb-s-in-my-homelab-sort-of/)

By[James](https://jameskilby.co.uk)December 19, 2022April 16, 2026

For a while, I’ve been looking to update the networking at the core of my homelab.

  * [![Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/wp-content/uploads/2022/01/maxresdefault-768x432.jpeg)](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/)

### [Lab Update – Part 2 Storage Truenas Scale](https://jameskilby.co.uk/2022/01/lab-update-part-2-storage/)

By[James](https://jameskilby.co.uk)January 11, 2022April 16, 2026

The HP Z840 has changed its role to a permanent storage box running Truenas Scale.