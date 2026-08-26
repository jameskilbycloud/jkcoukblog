---
title: "How to Expand Ubuntu Disk Space: LVM pvresize Step-by-Step"
description: "Step-by-step Ubuntu disk expansion with LVM: pvresize, vgextend, lvextend, resize2fs. Works after resizing the VM disk in vSphere/Hyper-V/KVM."
date: 2025-12-15T20:56:40+00:00
modified: 2026-05-24T06:41:45+00:00
author: James Kilby
categories:
  - Ubuntu
  - Automation
  - Github
  - Ansible
tags:
  - #Disk Expand
  - #Ubuntu
url: https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/
image: https://jameskilby.co.uk/wp-content/uploads/2025/12/UbuntuExpand.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2025/12/UbuntuExpand.png)

[Ubuntu](https://jameskilby.co.uk/category/ubuntu/)

# How to Expand Ubuntu Disk Space: LVM pvresize Step-by-Step

By[James](https://jameskilby.co.uk) December 15, 2025 · Updated May 24, 2026 • 📖1 min read(91 words)

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

## 📚 Related Posts

  * [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [ ![Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/wp-content/uploads/2026/04/packer-github-actions-vsphere-pipeline-768x452.png) ](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Github](https://jameskilby.co.uk/category/github/)

### [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

By[James](https://jameskilby.co.uk) April 30, 2026 · Updated June 5, 2026

A walk-through of an automated golden-image pipeline for vSphere: HashiCorp Packer builds six Ubuntu LTS templates (22.04, 24.04, 26.04 — server and desktop) driven by three GitHub Actions workflows covering PR validation, parallel template builds, and ISO management via a self-hosted runner.

  * [ ![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png) ](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk) April 10, 2026 · Updated July 11, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.