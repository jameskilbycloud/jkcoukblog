---
title: "Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU"
description: "Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the su"
date: 2024-10-11T15:03:26+00:00
modified: 2026-07-11T07:33:51+00:00
author: James Kilby
categories:
  - Artificial Intelligence
  - Docker
  - Homelab
  - Nutanix
  - VMware
  - Automation
  - Github
  - Mikrotik
  - Networking
  - Hosting
  - Kubernetes
tags:
  - #Artificial Intelligence
  - #Homelab
  - #Nvidia
url: https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/
image: https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-1024x683.jpg
---

![](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-scaled.jpg)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

# Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU

By[James](https://jameskilby.co.uk) October 11, 2024 · Updated July 11, 2026 • 📖5 min read(1,068 words)

📅**Published:** October 11, 2024•**Updated:** July 11, 2026

Artificial intelligence is all the rage at the moment. It’s getting included in every product announcement from pretty much every vendor under the sun. Nvidia’s stock price has gone to the moon. So I thought I better get some knowledge and understand some of this.

As it’s a huge field and I wasn’t exactly sure where to start I decided to follow [Tim’s](https://www.youtube.com/@TechnoTim) excellent [video ](https://www.youtube.com/watch?v=GrLpdfhTwLg)and [guide](https://technotim.live/posts/ai-stack-tutorial/) as to what he has deployed. This blog is a bit more of a reminder for me of what I have done. I won’t go into all the details as Tim has done a better job than I will. 

## Table of Contents

## Introduction

Yes, you can do some AI things with a CPU but the reality at the moment is that it’s better suited to being executed on a GPU and depending on what you’re doing a GPU(s) with lots of memory are what you need. I didn’t fancy spending any money so I thought I would start with my Nvidia P4 and see where I get to.

### Nvidia Tesla P4 Specs

The Nvidia P4 has 8GB of GDDR5 memory which is enough for running some smaller models 

### OS Choice

I chose to use one of my vSphere Hosts with a VM running Ubuntu 24.04 

### vHardware Spec

In vSphere, I allocated 8x vCPUs, 20GB of memory, and 256GB of storage to the VM with the P4 passed in directly. This means I didn’t need any additional NVIDIA licences.

Install Ubuntu 24.04 ( or use your template) & make sure it’s patched
    
    
    sudo apt-get update && sudo apt-get upgrade

📋 Copy

## Install NVIDIA Software

The first step is to install the Nvidia drivers.
    
    
    sudo ubuntu-drivers install 
    

📋 Copy

reboot and then use “sudo nvidia-smi” to validate that the card is now functioning within the VM. The output below shows that the Ubuntu server can see the Tesla P4
    
    
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 470.256.02   Driver Version: 470.256.02   CUDA Version: 11.4     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |                               |                      |               MIG M. |
    |===============================+======================+======================|
    |   0  Tesla P4            Off  | 00000000:0B:00.0 Off |                    0 |
    | N/A   46C    P0    23W /  75W |      0MiB /  7611MiB |      0%      Default |
    |                               |                      |                  N/A |
    +-------------------------------+----------------------+----------------------+
                                                                                   
    +-----------------------------------------------------------------------------+
    | Processes:                                                                  |
    |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
    |        ID   ID                                                   Usage      |
    |=============================================================================|
    |  No running processes found                                                 |
    +-----------------------------------------------------------------------------+

📋 Copy

## Install Docker

The next step is to install docker as the AI engines will all be running within docker.
    
    
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Add the repository to Apt sources:
    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

📋 Copy
    
    
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

📋 Copy

Use Docker without SUDO
    
    
    sudo usermod -aG docker $USER

📋 Copy

## NVIDIA Container Toolkit

The next thing to do is to install the Nvidia container toolkit. This allows containers to interact with the graphics card
    
    
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

📋 Copy

sudo apt-get update
    
    
    sudo apt-get install -y nvidia-container-toolkit

📋 Copy
    
    
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker

📋 Copy

Test NVIDIA Docker
    
    
    sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi

📋 Copy

If the above worked, you have a functioning system where docker can communicate with your GPU.

## Overview

Tim’s blog has a decent overview of the containers and what they are doing so I won’t detail it here.

## Chat in Action

So the next obvious thing I needed to do was ask it some questions. So I asked the gemma2 model the question “What AI models can I run on a Nvidia p4?”

and it answered….

You’re right to be specific! While the Nvidia P4 is _technically_ an AI-capable GPU, it’s designed more for inference (running pre-trained models) than training complex ones from scratch. Think of it like a powerful calculator for AI, not a research lab.

Here’s a breakdown of what you can realistically expect on an Nvidia P4:

**1\. Lightweight Models are Your Friend:**

  * **Object Detection:** Tiny YOLOv3 variants or lightweight MobileNet-based detectors. Expect lower accuracy than bigger models but fast inference speeds for real-time applications.
  * **Image Classification:** MobileNet V2, Inception v3 (downscaled), SqueezeNet – these are pre-trained and optimized for mobile devices.

**2\. Frameworks Matter:**

  * **TensorRT** : This is Nvidia’s specialized engine for P4. It optimizes your models for performance, even converting them into a more efficient format.
  * **ONNX Runtime** : This open-source runtime supports various AI frameworks, and can be used to run models on the P4 after conversion.

**3\. Practical Applications:**

  * **Edge Devices:** Think smart cameras, embedded systems, or robotics where low power consumption and quick responses are crucial.
  * **Demo Projects:** Great for learning about deployment and seeing how AI works in real-time, even if the accuracy isn’t state-of-the-art.

**What You CAN’T Do:**

  * Train massive neural networks from scratch (think GPT-3 or large image generators). The P4 lacks the memory and compute power.
  * Run cutting-edge research models that demand immense resources. Those are best left to specialized cloud GPUs or supercomputers.

Let me know if you have a specific AI task in mind – I might be able to suggest suitable pre-trained models or optimizations for your Nvidia P4 setup!

As a response, I was certainly impressed with it

## Power Consumption

Obviously, I am very aware of the power usage on my lab so I thought it was interesting to dig into how much running chat queries may impact things. According to NVTOP The P4 normally idles around 7 Watts, however, once a model is loaded even if it’s not running any queries this increases to around 24W this is probably due to the increased memory clock speed.

![Screenshot 2024 09 05 at 11.57.47](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-09-05-at-11.57.47.png)Idle consumption ![Screenshot 2024 09 05 at 12.01.26](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-09-05-at-12.01.26.png)Models loaded ![Screenshot 2024 09 16 at 14.41.52](https://jameskilby.co.uk/wp-content/uploads/2024/09/Screenshot-2024-09-16-at-14.41.52.png)Models Running

When queries are running it will typically use 50-60 watts.

## Summary 

Obviously it’s early days for my experimentation into what is a large and rapidly changing field. But it’s certainly something I will be playing with a lot.

## 📚 Related Posts

  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [ ![Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/wp-content/uploads/2023/04/81-ZoEW24UL._SL1500_-768x461.jpg) ](https://jameskilby.co.uk/2019/02/lab-storage-2/)

[Homelab](https://jameskilby.co.uk/category/homelab/)

### [Homelab Storage Upgrade: Synology DS918 for VMware & NFS](https://jameskilby.co.uk/2019/02/lab-storage-2/)

By[James](https://jameskilby.co.uk) February 10, 2019 · Updated June 5, 2026

Since starting my new role with Xtravirt my Homelab has gone through several fairly significant changes.

  * [ ![New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/wp-content/uploads/2024/07/IMG_6629-768x149.jpeg) ](https://jameskilby.co.uk/2024/07/new-nodes/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [New Homelab Nodes: SuperMicro BigTwin for VMware & Nutanix](https://jameskilby.co.uk/2024/07/new-nodes/)

By[James](https://jameskilby.co.uk) July 2, 2024 · Updated July 11, 2026

I recently decided to update some of my homelab hosts and I managed to do this at very little cost by offloading 2 of my Supermicro e200’s to fellow vExpert Paul .

  * [ ![Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/wp-content/uploads/2026/04/packer-github-actions-vsphere-pipeline-768x452.png) ](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

[Automation](https://jameskilby.co.uk/category/automation/) | [Github](https://jameskilby.co.uk/category/github/)

### [Automating vSphere Golden Images with Packer and GitHub Actions](https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/)

By[James](https://jameskilby.co.uk) April 30, 2026 · Updated June 5, 2026

A walk-through of an automated golden-image pipeline for vSphere: HashiCorp Packer builds six Ubuntu LTS templates (22.04, 24.04, 26.04 — server and desktop) driven by three GitHub Actions workflows covering PR validation, parallel template builds, and ISO management via a self-hosted runner.

  * [ ![CRS-504](https://jameskilby.co.uk/wp-content/uploads/2024/09/s-l1600-768x427.jpg) ](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

[Mikrotik](https://jameskilby.co.uk/category/mikrotik/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Home Network Upgrade to 25Gb/s with MikroTik Switching](https://jameskilby.co.uk/2024/09/home-network-upgrade/)

By[James](https://jameskilby.co.uk) September 9, 2024 · Updated June 5, 2026

My journey to superfast networking in my homelab

  * [ ![Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg) ](https://jameskilby.co.uk/2018/01/nutanix-ce/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/2018/01/nutanix-ce/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home.

  * [ ![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png) ](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk) December 9, 2022 · Updated June 5, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….