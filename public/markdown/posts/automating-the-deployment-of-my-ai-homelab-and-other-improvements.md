---
title: "Automating the Deployment of my Homelab AI Infrastructure"
description: "Build a complete homelab AI infrastructure using Ansible to automate Ubuntu with NVIDIA GPU passthrough, Docker, Traefik, and an end-to-end AI stack via Sema..."
date: 2026-02-09T11:54:54+00:00
modified: 2026-04-18T07:41:21+00:00
author: James Kilby
categories:
  - Ansible
  - Artificial Intelligence
  - Containers
  - Devops
  - Homelab
  - NVIDIA
  - Traefik
  - VMware
  - VMware Cloud on AWS
  - Networking
  - Nutanix
  - TrueNAS Scale
  - vSAN
  - vSphere
tags:
  - #AI
  - #Docker
  - #Homelab
  - #Nvidia
  - #Semaphore
url: https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/
image: https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv.png
---

![Vmware Nvidia Logos Ee2F18Dc 615D 4C9E 8F11 9C3C2Ce2Bf37 Prv](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv.png)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

# Automating the Deployment of my Homelab AI Infrastructure

By[James](https://jameskilby.co.uk)February 9, 2026April 18, 2026 • 📖17 min read(3,332 words)

📅 **Published:** February 09, 2026• **Updated:** April 18, 2026

In a previous [post](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/), I wrote about using my VMware lab with an NVIDIA Tesla P4 for running some AI services. This deployment was done with the P4 GPU in passthrough mode where the entire PCI card was presented into the VM. (I will refer to this as GPU mode). I wanted to take this to the next level. I also wanted to automate most of the steps. This was for a few reasons; firstly, I wanted to get better at automation in general.

Secondly, I found the setup brittle and wanted to improve the reliability of deployments. This post will be about using automation to deploy the VM infrastructure required to be able to run AI Workloads. This is something I presented on with my good friend [Gareth](https://www.virtualisedfruit.co.uk/) at the London VMUG.

However, in a homelab enviroment a more straightforward Docker-based setup could be more appropriate….

I also decided to bite the bullet and update the graphics card I was using to something a bit more modern and capable. After a bit of searching, I decided on an [NVIDIA A10](https://www.nvidia.com/en-gb/data-center/products/a10-gpu/)

This guide covers the full homelab AI infrastructure build — This post is about getting the foundational infrastructure ready.

The first part will explain the steps and detail the Ansible configuration. The second part of this post goes into a full deployment utilising [SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/). My next post will go into more details on the Docker containers I am using for actually running the AI services, building on these foundations.

All of the code is referenced in my GitHub IAC [repository](https://github.com/jameskilbynet/iac/tree/main/ansible)

## Table of Contents

## GPU vs vGPU

For anyone not familiar, it may be worth giving an overview of the differences between GPU and vGPU. What I describe as “GPU” is where I am passing the entire Graphics PCI device through to a single VM within vSphere. Using this method has some advantages; firstly, it doesn’t require any special licences or drivers. The entire PCI card gets passed into the VM as is. However, it has some downsides.

The two most important ones for me are that it can only be presented to a single VM at a time and that VM cannot be snapshotted while it is turned on. This made backups convoluted. As I was changing configurations a lot this became tedious. I also wanted to be able to pass the card through to multiple VM’s

vGPU is only officially supported on “datacentre” cards from NVIDIA. It virtualises the graphics card and allows you to share it across multiple VMs in a similar way to what vSphere has done for compute virtualisation for years. It allows you to split the card into some predefined profiles that I have listed below and attach them to multiple virtual machines at the same time.

## Prerequisites

There are quite a lot of pre-reqs required to be in place to utilise all the attached deployment playbooks. So it’s worth ensuring that all of these are complete.

  * Obviously, you need a vSphere Host and vCentre server licensed at least at the enterprise level (I am using Enterprise Plus on 8.0u3)
  * An Ubuntu VM (Tested with 25.04) referred to as the vGPU VM
  * A NVIDIA datacenter Graphics card and associated Host and Guest drivers, I am using an A10 24GB and using driver version 535.247.0
  * NVIDIA vGPU licence. Trials are available [here](https://www.nvidia.com/en-gb/data-center/resources/vgpu-evaluation/) if needed
  * NFS Server (used for NVIDIA software deployment)
  * A Domain hosted with Cloudflare and an API [token](http://You can create one at: https://dash.cloudflare.com/profile/api-tokens) with Zone:DNS:Edit permissions.
  * SSH access to the vGPU VM with SUDO permission
  * Somewhere to run Ansible playbooks from.
  * Internal DNS Records created for 
    * vGPU VM
    * Traefik Dashboard
    * Test NGINX Server – Optional
    * NFS Server (Used for vGPU Software install)

## Host Setup

To make vGPU work successfully, there are three elements required. The ESXi Driver/VIB, the Guest driver and the NVIDIA licence for the Guest VM. For now, I’m using the ‘535’ version of the driver bundle, which is the LTS version.` The Driver bundle and licence must be obtained from NVIDIA however trials are available if you don’t have access. Once the software has been obtained, you need to copy the host driver to a VMware datastore. Then place the host in maintenance mode and install the driver using the command.
    
    
    esxcli software vib install -d /vmfs/volumes/02cb3d2b-457ccb84/nvidia/NVIDIA-GRID-vSphere-8.0-535.247.02-535.247.01-539.28.zip

📋 Copy

If it worked successfully, you should get a result like the one below
    
    
    Installation Result
       Message: Operation finished successfully.
       VIBs Installed: NVD_bootbank_NVD-VMware_ESXi_8.0.0_Driver_535.247.02-1OEM.800.1.0.20613240
       VIBs Removed: 
       VIBs Skipped: 
       Reboot Required: false
       DPU Results: 

📋 Copy

I always choose to restart the host after installing the driver. I have been bitten in the past where it says a reboot isn’t required, but it was.

Once the host has restarted, ssh into it and validate that the driver is talking to the GPU correctly. This can be done with the nvidia-smi command. This is executed on the ESXi host and will show something similar to the below if it’s working.
    
    
    +---------------------------------------------------------------------------------------+
    | NVIDIA-SMI 535.247.02             Driver Version: 535.247.02   CUDA Version: N/A      |
    |-----------------------------------------+----------------------+----------------------+
    | GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
    |                                         |                      |               MIG M. |
    |=========================================+======================+======================|
    |   0  NVIDIA A10                     On  | 00000000:03:00.0 Off |                    0 |
    |  0%   41C    P8              22W / 150W |  11200MiB / 23028MiB |      0%      Default |
    |                                         |                      |                  N/A |
    +-----------------------------------------+----------------------+----------------------+

📋 Copy

### vGPU Profiles

If everything is working correctly, you should now be able to see the vGPU profiles in vCentre.
    
    
    Select the VM you want to present the NVIDIA card to. Edit the VM settings and select add PCI device.
    
    
    
    
    
    ![Adding a PCI device for NVIDIA GPU passthrough in vSphere VM settings](https://jameskilby.co.uk/wp-content/uploads/2026/01/Add-PCI-Device-1-402x1024.png)
    
    
    
    
    
    
    
    You should then be presented with the available profiles from the NVIDIA GPU
    
    
    
    
    
    ![NVIDIA vGPU profile selection in vSphere for AI homelab workloads](https://jameskilby.co.uk/wp-content/uploads/2026/01/GPU-Profiles-1024x397.png)
    
    
    
    
    
    As can be seen, the NVIDIA A10 supports 18 different profiles. The nvidia_a10 part specifies the card (in case you have multiple), and the suffix determines how much vGPU RAM is allocated to the vGPU instance, along with the features that are exposed with it. I typically use either the a10-24q profile to allow the use of larger AI models. Although I do step this down to the 12q profile to allow support of multiple vm's for testing etc.
    
    
    
    
    
    
    
    The NVIDIA A10 supports four separate "Personalities" A, B, Q and C each of these come with different capabilities but also potentially different licensing requirements.
    
    
    
    
    
    Profile| Intended Use| Driver Feature Set| License Tier| Expected Workloads  
    ---|---|---|---|---  
    A-Series| App Streaming / RDSH| Basic Graphics no pro features| vAPPS| Many Users / Published Apps  
    B-Series| VDI Desktops| Standard Desktop Graphics| vPC| Knowledge Worker Desktops  
    C-Series| Compute Only| CUDA Only | vCompute Server| AI/ML Data Science  
    Q-Series| Full GFX Workstation| Full RTX| RTX vWS| CAD,3D Rendering   
    
    
    
    
    
    
    
    
    
    
    
    
    The keen-eyed amongst you might realise that I am using the wrong profile for AI workloads. I have chosen to use Q-based profiles rather than C-based ones. This is because the A, B and Q profiles are run from one ESXi driver VIB and the C profile requires a different VIB. Because I occasionally want to run a VDI based workload or media conversion in my lab. I have chosen to use the more graphics focused VIB and utilise the Q profile for my AI based workloads. I suspect this might have a performance impact, but it was a compromise I was willing to accept.
    
    
    
    
    
    
    
    ## Guest Setup
    
    
    
    
    
    
    
    To make the guest setup easier and more repeatable, I have built some Ansible playbooks.
    
    
    
    
    
    These perform a number of activities that make it MUCH easier to get the guest up and running for use with AI workloads and other containers. These have only been tested with Ubuntu but will probably work with other Linux distro's without a lot of changes. As a bonus if you want to utilise the Traefik setup I have built this can be used on its own, just with the Deploy Docker and Install Traefik playbooks. Once these playbooks have been run, you will be in a position to spin up any number of Docker containers with GPU access.
    
    
    
    
    
    
    
    At a high level, the four playbooks I have built:
    
    
    
    
    
    
    
    
    
      * [Deploy Docker ](https://github.com/jameskilbynet/iac/blob/main/ansible/docker/install_docker.yml)
    
    
    
    
    
      * [Install NVIDIA Guest drivers](https://github.com/jameskilbynet/iac/blob/main/ansible/vGPU/install_nvidia_drivers.yml)
    
    
    
    
    
      * [Install NVIDIA Container Toolkit](http://ansible/vGPU/install_nvidia_containertoolkit.yml)
    
    
    
    
    
      * [Install Traefik ](https://github.com/jameskilbynet/iac/blob/main/ansible/traefik/traefik_deploy.yml)
    
    
    
    
    
    
    
    
    ### Guest Configuration
    
    
    
    
    
    
    
    Before we get to the Ansible section, we obviously need to build the VM.
    
    
    
    
    
    There are a few key steps here as well. Firstly, it must be an EFI-based VM; BIOS won't work. Secondly, you need to allocate a decent amount of RAM to the workload. I usually run with at least 3x my GPU vRAM. Therefore, my main AI VM usually has 96GB allocated to it. It is also important to understand that vSphere will automatically reserve all of this memory. Also, make sure that you are not swapping to disk. This will dramatically slow down the system.
    
    
    
    
    
    
    
    The next step is to ensure that the VM has access to a lot of fast storage. I would recommend at least a few hundred GB, especially if you are going to be working with multiple models. The smallest models I typically use are around 8GB. Therefore loading these into memory even from an NVMe drive, can take a few seconds before anything can be processed. This will always give a slight delay when cold-starting compared to a commercial equivalent (Think ChatGPT, etc.) It is possible to configure Ollama to keep the models loaded.
    
    
    
    
    
    I have set this to 1 hour before it unloads them. This is due to higher power consumption on the graphics card when they are loaded.
    
    
    
    
    
    
    
    Please note that all of the testing has been done on Ubuntu 24 or 25
    
    
    
    
    
    
    
    ### Homelab AI Infrastructure: Ansible Automation
    
    
    
    
    
    
    
    I have kept these as separate playbooks for now. This hopefully makes it easier to follow and/or troubleshoot if needed. The playbooks are intended to be run in order. 
    
    
    
    
    
    
    
    I am using SemaphoreUI to handle the Ansible deployment but this isn't required. If you are familiar enough with Ansible to not use Semaphore, then you can easily modify these to suit your execution preferences.
    
    
    
    
    
    
    
    #### 1. Docker deployment
    
    
    
    
    
    
    
    <https://github.com/jameskilbynet/iac/blob/main/ansible/docker/install_docker.yml>
    
    
    
    
    
    
    
    I have covered the deployment of Docker already in [this](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/ "Managing my Homelab with SemaphoreUI") post.  No parameters are required to be set for the Docker deployment. Everything is set in the playbook.
    
    
    
    
    
    
    
    #### 2. Install NVIDIA Guest Drivers
    
    
    
    
    
    
    
    <https://github.com/jameskilbynet/iac/blob/main/ansible/vGPU/install_nvidia_drivers.yml>
    
    
    
    
    
    
    
    This playbook configures an NFS client on the Ubuntu server and then copies both the vGPU license file and the driver from my NFS storage before installing them. This, I felt was the best way to have a portable Ansible file without checking in my NVIDIA licence and driver files into Git.
    
    
    
    
    
    
    
    Before you use this playbook several variables need to be set in Semaphore. These should be done in the Variable Group section. I created a Variable Group called vGPU for this purpose.
    
    
    
    
    
    
    
    ##### NVIDIA Guest Driver Variables
    
    
    
    
    
    **Variable**|  **Default**|  **Description**  
    ---|---|---  
     nvidia_vgpu_driver_file| NVIDIA-Linux-x86_64-535.247.01-grid.run| Driver filename  
    nvidia_vgpu_licence_file| client_configuration_token_04-08-2025-16-54-19.tok| Token filename  
    nvidia_nfs_server| nas.jameskilby.cloud| NFS server hostname  
    nvidia_nfs_export_path| /mnt/pool1/ISO/nvidia| NFS export path  
    nvidia_nfs_mount_point| /mnt/iso/nvidia| Local mount point  
    
    
    
    
    
    
    To make your life easier, you can copy this json to Semaphore and just tweak what is needed.
    
    
    
    
    
    
    
    
    {
      "nvidia_vgpu_driver_file": "NVIDIA-Linux-x86_64-535.247.01-grid.run",
      "nvidia_vgpu_licence_file": "client_configuration_token_04-08-2025-16-54-19.tok",
      "nvidia_nfs_server": "nas.jameskilby.cloud",
      "nvidia_nfs_export_path": "/mnt/pool1/ISO/nvidia",
      "nvidia_nfs_mount_point": "/mnt/iso/nvidia",
    }

📋 Copy

If everything runs smoothly the last step of the Ansible playbook will show an export of the licence and vGPU configuration.
    
    
    TASK [Show vGPU license info] **************************************************
    9:18:47 PM
    ok: [blogtest.jameskilby.cloud] => 
    9:18:47 PM
      msg: |-
    9:18:47 PM
        ==============NVSMI LOG==============
    9:18:47 PM
      
    9:18:47 PM
        Timestamp                                 : Fri Feb  6 21:18:47 2026
    9:18:47 PM
        Driver Version                            : 535.247.01
    9:18:47 PM
        CUDA Version                              : 12.2
    9:18:47 PM
      
    9:18:47 PM
        Attached GPUs                             : 1
    9:18:47 PM
        GPU 00000000:03:00.0
    9:18:47 PM
            Product Name                          : NVIDIA A10-12Q
    9:18:47 PM
            Product Brand                         : NVIDIA RTX Virtual Workstation
    9:18:47 PM
            Product Architecture                  : Ampere
    9:18:47 PM
            Display Mode                          : Enabled
    9:18:47 PM
            Display Active                        : Disabled
    9:18:47 PM
            Persistence Mode                      : Enabled
    9:18:47 PM
            Addressing Mode                       : None
    9:18:47 PM
            MIG Mode
    9:18:47 PM
                Current                           : Disabled
    9:18:47 PM
                Pending                           : Disabled
    9:18:47 PM
            Accounting Mode                       : Disabled
    9:18:47 PM
            Accounting Mode Buffer Size           : 4000

📋 Copy

#### 3\. 
    
    
    Install NVIDIA Container Toolkit

📋 Copy

<https://github.com/jameskilbynet/iac/blob/main/ansible/vGPU/install_nvidia_containertoolkit.yml>

This playbook installs the NVIDIA container toolkit and validates it. It does this by running a Docker container and executing the nvidia-smi command from within the container. This sounds trivial but actually is one of the main reasons I made these playbooks. To get the GPU to work in the docker container you have to have a lot of things set up correctly. This requires the correct ESXi Driver, VM driver within the Ubuntu VM, Docker and the Docker container toolkit set up correctly.

The correct Kernel extensions, etc., and the licensing are working correctly

No additional parameters need to be set to execute it.

Below is the expected output showcasing nvidia-smi running from within a Docker container.

![nvidia-smi output confirming homelab AI infrastructure GPU is detected in Ubuntu](https://jameskilby.co.uk/wp-content/uploads/2026/01/nvidia-smi-1024x654.png)

#### 4\. Install Traefik

<https://github.com/jameskilbynet/iac/blob/main/ansible/traefik/traefik_deploy.yml>

For those unfamiliar with [Traefik](https://traefik.io) ( It's pronounced Traffic), it is a reverse proxy/ingress controller with automatic integrations to Docker and Kubernetes. I have it configured to leverage both Let's Encrypt and Cloudflare so that it will automatically obtain signed certificates for me. This is done with Docker labels in such a way that any container I spin up that has the correct Traefik labels will automatically mint a signed certificate and add it to the load balancer.

This has the added benefit that I just need to remember a URL IE openwebui.jameskilby.cloud configured in my internal DNS, rather than which VM and port the service is running on. It has the added benefit that it makes it very easy for me to expose services externally if needed. I just add the appropriate DNS record on my external DNS.

The labels look something like the following. These are added to the individual Docker containers and Traefik can see them through the Docker API. When the containers are started, it will autoconfigure the certificate generation and automatically configure the load balancer. If the container is removed or stopped, it will tidy up the configuration.
    
    
      labels:
          - "traefik.enable=true"
          - "traefik.http.routers.open-webui.rule=Host(`openwebui.jameskilby.cloud`)"
          - "traefik.http.routers.open-webui.entrypoints=websecure"
          - "traefik.http.routers.open-webui.tls=true"
          - "traefik.http.routers.open-webui.tls.certresolver=cloudflare"
          - "traefik.http.services.open-webui.loadbalancer.server.port=8080"

📋 Copy

With the above labels added to my OpenWebUI container, Traefik will request a certificate for openwebui.jameskilby.cloud and deploy this as a HTTPS service mapped to the OpenWebUI container on port 8080

I could probably do a whole post just on my setup of Traefik but for now here is an overview diagram.

![Ansible playbook configuring Traefik and Docker on the homelab AI VM](https://jameskilby.co.uk/wp-content/uploads/2025/01/Traefik-Docker-Setup-2-1024x342.png)

As part of the included playbook, I have added the option to deploy a simple nginx web server using this principle. If everything is configured correctly, you should be able to connect to this container post deployment and it will have a fully trusted certificate as seen below. (You may need to wait 1-2 minutes or so after deployment for this process to complete)

![Nginx TLS certificate verification via Traefik in the homelab setup](https://jameskilby.co.uk/wp-content/uploads/2026/01/nginx-cert-1024x997.png)

#### Traefik Dashboard

Traefik also has a nice dashboard that is very useful in troubleshooting.

![Traefik dashboard running in the homelab with Docker and Ansible](https://jameskilby.co.uk/wp-content/uploads/2026/01/TraefikDashboard-1024x478.png)

This is the dashboard from my testing configuration. My main server has over 40 "Routers"

#### Traefik Playbook Setup

Before running this playbook a lot of variables need to be configured as can be seen below. In most cases, the default is OK. I have just extended the vGPU Variable group to do this. When they are all input into Semaphore, it will look something like this.

![Traefik variable definitions in the Ansible playbook for the AI homelab](https://jameskilby.co.uk/wp-content/uploads/2026/01/Traefik-Variables-804x1024.png)

Rather than typing all of the values out you can copy the JSON below and then just tweak what you need to.
    
    
    {
      "nvidia_vgpu_driver_file": "NVIDIA-Linux-x86_64-535.247.01-grid.run",
      "nvidia_vgpu_licence_file": "client_configuration_token_04-08-2025-16-54-19.tok",
      "nvidia_nfs_server": "nas.jameskilby.cloud",
      "nvidia_nfs_export_path": "/mnt/pool1/ISO/nvidia",
      "nvidia_nfs_mount_point": "/mnt/iso/nvidia",
      "traefik_deploy_test_service": "true",
      "traefik_healthcheck_poll_retries": "12",
      "traefik_healthcheck_poll_delay": "5",
      "traefik_docker_image": "traefik:v3.6.4",
      "traefik_name": "traefik",
      "traefik_config_path": "/etc/traefik",
      "traefik_acme_path": "/etc/traefik/acme",
      "traefik_docker_network": "traefik",
      "traefik_http_port": "80",
      "traefik_https_port": "443",
      "acme_dns_delay": "10",
      "acme_dns_resolvers": "[\"1.1.1.1:53\", \"8.8.8.8:53\"]",
      "traefik_log_level": "info",
      "traefik_log_format": "json",
      "traefik_log_max_size": "10m",
      "traefik_log_max_files": "3",
      "traefik_healthcheck_interval": "30s",
      "traefik_healthcheck_timeout": "10s",
      "traefik_healthcheck_retries": "3",
      "traefik_healthcheck_start_period": "30s",
      "traefik_test_container": "nginx-test",
      "traefik_test_image": "nginx:alpine",
      "traefik_test_domain": "test.jameskilby.cloud",
      "traefik_dashboard_user": "admin",
      "wildcard_domain": "jameskilby.cloud"
    }

📋 Copy

##### Traefik Variable Definitions

 **Variable**|  **Default**|  **Description**  
---|---|---  
traefik_deploy_test_service| true| set to false to skip NGINX deployment  
traefik_healthcheck_poll_retries| 12| Number of health check poll attempts  
traefik_healthcheck_poll_delay| 5| Seconds between health check polls  
traefik_docker_image| 3.6.4| Traefik Docker Image and version  
traefik_name| traefik| Traefik Container Name  
traefik_config_path| /etc/traefik| Config Directory  
traefik_acme_path| /etc/traefik/acme| ACME/Cert Directory  
traefik_docker_network| traefik| Docker Network Name for Traefik  
traefik_http_port| 80| HTTP Port  
traefik_https_port| 443| HTTPS Port  
acme_dns_delay| 10| Seconds before DNS Check  
acme_dns_resolvers| 1.1.1.1:53, 8.8.8.8:53| DNS Resolvers  
traefik_log_level| info| Log Level  
traefik_log_format| json| Log Format  
traefik_log_max_size| 10m| Max Log Size  
traefik_log_max_files| 3| Max Log Files  
traefik_healthcheck_interval| 30s| Health Check Interval  
traefik_heakthcheck_timeout| 10s| Health Check Timeout  
traefik_healthcheck_retries| 3| Health Check Retries  
traefik_heathcheck_start_period| 30s| Health Check Grace Period  
traefik_test_container| nginx-test| Test Container Name  
traefik_test_image| nginx:alpine| Test Container Image  
traefik_test_domain| test.jameskilby.cloud| Test Service Domain  
traefik_dashboard_user| admin| Traefik Dashboard Username  
wildcard_domain| jameskilby.cloud| Traefik Wildcard Domain   
  
#### Ansible Secrets

The playbook also needs two values that should be considered sensitive.

These can be added to Semaphore as secrets. The two secrets are the Cloudflare API Token and the second is a hash of a password for the admin account used to access the Traefik dashboard. The Traefik dashboard is very useful for troubleshooting any SSL/connectivity issues.

![Ansible secrets configuration in Semaphore for secure homelab automation](https://jameskilby.co.uk/wp-content/uploads/2026/01/SemaphoreSecrets-1024x262.png)

The Cloudflare Token needs to be generated in the Cloudflare dashboard. 

To generate the hash for the admin dashboard password, the easiest way is with Docker. The below is an example that can be run on the command line 
    
    
    docker run --rm httpd:2   htpasswd -nbB '' 'your_password_here'

📋 Copy

It will download and execute the httpd container. The last line is the hash that you need.

![Apache httpd test response confirming Docker and Traefik are running correctly](https://jameskilby.co.uk/wp-content/uploads/2026/01/httpd-1024x383.png)

In this case, the hash is: $2y$05$nkQGI2UxnRY.7O.6k14naOJPjslbqOT5vpqZPmXMu4knhBOH1EUAq take the output from this output and add it to the Semaphore secure variable for "dashboard_admin_password_hash"

## Semaphore End-to-End Setup

Assuming you are going to use SemaphoreUI to execute the playbooks, these are the steps you will need to take. If you haven't already set it up, review my guide [here](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

### Repository

The first step is to point Semaphore at the Git repository. This is the location where the playbooks will be executed from. As my Git repo is public no authentication is required. You also need to specify the branch; in this case, I am using main.

![Adding a Git repository to Semaphore for Ansible homelab automation](https://jameskilby.co.uk/wp-content/uploads/2026/01/Semaphore_repo.png)

### Key Store

The next step is to add the Key Store items. This is used to define the authentication from Semaphore to the target workload or other systems. I do this in two parts. The first is standard authentication, which I do with an SSH key. The second part is defining the become password to allow Semaphore to execute SUDO commands. I do this with a password stored in the Key Store. I have called these two methods KeyAuth and PassAuth

![Creating a new SSH key in Semaphore for Ansible authentication](https://jameskilby.co.uk/wp-content/uploads/2026/01/NewKey-802x1024.png)

Once the Key authentication is added, the next step is to add a different key store item for when the playbook needs to "Become"

![Semaphore password authentication configuration for Ansible inventory access](https://jameskilby.co.uk/wp-content/uploads/2026/01/PassAuth.png)

An Alternative approach is to allow your user to elevate without confirmation.

### Inventory

Once the authentication methods are defined, the next step is to update the Semaphore Inventory.

I have created a new Inventory item called "vGPU' set the User credentials to be KeyAuth and the Sudo credentials as PassAuth as created above.

I've then added the specific VM in the inventory. For testing, I have called this blogtest.

![Ansible inventory file showing homelab host configuration in Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/01/blogtest_ansible_inventory-670x1024.png)

### Variable Group

The next step is to create a variable group and the required variables. 

Review the variable table above and set it to match your environment. This is what mine looks like:

![Semaphore variable group configuration for Ansible homelab automation](https://jameskilby.co.uk/wp-content/uploads/2026/01/VariableGroup-813x1024.png)

### Task Templates

The final step is to create the four task templates. These are the actual actions that Ansible will perform using the Inventory, Repository and Variable Groups we have just defined.

Select New Template from the "Task Templates" view. Ensure it is set to Ansible and configure as per below.

![Expanded Semaphore variable group showing all Ansible environment variables](https://jameskilby.co.uk/wp-content/uploads/2026/01/Variable-Group-1024x547.png)

You should end up with something looking like this

![Semaphore task templates for running Ansible playbooks in the homelab](https://jameskilby.co.uk/wp-content/uploads/2026/01/TaskTemplates-1024x263.png)

When they are all configured, press the play button to execute each of the given tasks against your inventory item. Semaphore will check out the Ansible playbook and execute it, showing the results in the window.

## Summary

When all the playbooks are run successfully, you should now have:

  * A vSphere host capable of passing through NVIDIA datacenter graphics
  * An Ubuntu VM with vGPU integrated with Docker

This is now ready for you to start deploying Docker-based AI workloads onto.

📋 Copy

## 📚 Related Posts

  * [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

## Similar Posts

  * [![VMware Cloud on AWS \(VMC\) resource hub](https://jameskilby.co.uk/wp-content/uploads/2022/11/iu-1-768x395.png)](https://jameskilby.co.uk/2020/07/i3en/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS i3en Host: Specs, Storage & Performance](https://jameskilby.co.uk/2020/07/i3en/)

By[James](https://jameskilby.co.uk)July 2, 2020April 16, 2026

VMware Cloud on AWS (VMC) has introduced a new host to its lineup the “i3en”. This is based on the i3en.

  * [![Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/wp-content/uploads/2024/06/Ubiquiti_Networks-Logo.wine_-768x512.png)](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Configure DHCP Option 43 for UniFi devices to enable remote adoption across subnets](https://jameskilby.co.uk/2024/06/unifi-dhcp-option-43/)

By[James](https://jameskilby.co.uk)June 26, 2024March 10, 2026

How to configure DHCP Option 43 for UniFi devices 

  * [![VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/wp-content/uploads/2025/02/Picture-1-e1768509620339-768x193.png)](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

[VMware Cloud on AWS](https://jameskilby.co.uk/category/vmware/vmware-cloud-on-aws/)

### [VMware Cloud on AWS Time Sync & NTP Configuration](https://jameskilby.co.uk/2025/12/time-in-a-vmc-environment/)

By[James](https://jameskilby.co.uk)December 8, 2025April 11, 2026

How to use the Amazon Time Sync Service in a VMC environment

  * [![Wa](https://jameskilby.co.uk/wp-content/uploads/2025/04/210902461-012e7273-413a-4ec7-be44-e854347f5a21-768x180.png)](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Warp – The intelligent terminal](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

By[James](https://jameskilby.co.uk)April 11, 2025April 16, 2026

How Warp is helping me run my homelab. 

  * [![Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/wp-content/uploads/2020/07/nutanix-logo-HI-REZ_reverse-w-carrier-768x196.jpg)](https://jameskilby.co.uk/2018/01/nutanix-ce/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Nutanix](https://jameskilby.co.uk/category/nutanix/)

### [Running Nutanix CE at Home: AHV Setup & First Impressions](https://jameskilby.co.uk/2018/01/nutanix-ce/)

By[James](https://jameskilby.co.uk)January 6, 2018April 16, 2026

I ran a Nutanix CE server at home for a little while when it first came out. However, due to the fairly high requirements, it didn’t make sense to me to continue running it at home.

  * [![How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/wp-content/uploads/2024/12/ZFS.jpg)](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

[TrueNAS Scale](https://jameskilby.co.uk/category/truenas-scale/) | [VMware](https://jameskilby.co.uk/category/vmware/) | [vSAN](https://jameskilby.co.uk/category/vmware/vsan-vmware/) | [vSphere](https://jameskilby.co.uk/category/vsphere/)

### [How to Run ZFS on VMware vSphere: Setup Guide and Best Practices](https://jameskilby.co.uk/2024/12/zfs-on-vmware/)

By[James](https://jameskilby.co.uk)December 18, 2024April 16, 2026

Introduction Copy on Write Disk IDs Trim Introduction I have run a number of systems using ZFS since the earliest days of my homelab using Nexenta, all the way back in 2010.