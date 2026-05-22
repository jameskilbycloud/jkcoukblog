---
title: "How to Expand Ubuntu Disk Space: LVM pvresize Step-by-Step"
description: "How to expand disks from the command line in Ubuntu. This is something I do fairly frequently, and I can never remember the steps."
date: 2025-12-15T20:56:40+00:00
modified: 2026-04-16T22:01:40+00:00
author: James Kilby
categories:
  - Ubuntu
  - Ansible
  - Automation
  - Docker
  - Homelab
  - Traefik
  - VCF
  - VMware
tags:
  - #Disk Expand
  - #Ubuntu
url: https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/
image: https://jameskilby.co.uk/wp-content/uploads/2025/12/UbuntuExpand.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2025/12/UbuntuExpand.png)

[Ubuntu](https://jameskilby.co.uk/category/ubuntu/)

# How to Expand Ubuntu Disk Space: LVM pvresize Step-by-Step

By[James](https://jameskilby.co.uk) December 15, 2025April 16, 2026 • 📖1 min read(91 words)

📅 **Published:** December 15, 2025• **Updated:** April 16, 2026

How to expand disks from the command line in Ubuntu.

This is something I do fairly frequently, and I can never remember the steps. So I decided to write them down.

## Table of Contents

## 1\. Rescan for disk size changes

sudo tee /sys/class/block/sda/device/rescan

## 2\. Extend the physical partition (if needed)

sudo growpart /dev/sda 3

## 3\. Resize the physical volume

sudo pvresize /dev/sda3

## 4\. Extend the logical volume to use all available space

sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv

## 5\. Resize the filesystem

sudo resize2fs /dev/ubuntu-vg/ubuntu-lv

## 6\. Verify the new size

df -h

## Similar Posts

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026April 16, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.