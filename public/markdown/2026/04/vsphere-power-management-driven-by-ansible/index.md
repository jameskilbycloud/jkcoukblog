---
title: "Automating vSphere Power Management driven by Ansible and SemaphoreUI"
description: "Learn how to automate vSphere power management using Ansible and SemaphoreUI, scheduling ESXi host shutdowns based on Octopus Agile energy tariffs to cut costs."
date: 2026-04-15T21:36:41+00:00
modified: 2026-06-01T21:07:22+00:00
author: James Kilby
categories:
  - Ansible
  - Automation
  - Homelab
  - Networking
  - VCF
  - VMware
  - Storage
  - Synology
  - AWS
  - Veeam
tags:
  - #Ansible
  - #Homelab
  - #Semaphore
  - #VMware
url: https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/
image: https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible.png
---

![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible.png)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

# Automating vSphere Power Management driven by Ansible and SemaphoreUI

By[James](https://jameskilby.co.uk) April 15, 2026 · Updated June 1, 2026 • 📖7 min read(1,465 words)

📅**Published:** April 15, 2026•**Updated:** June 01, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. 

## Table of Contents

## Introduction

One of the larger costs of running my [homelab ](https://jameskilby.co.uk/lab/)is the electricity. I have previously talked about my supplier Octopus Energy and how they operate an innovative tariff called [Agile](https://jameskilby.co.uk/2026/03/octopus-agile-battery-solar-calculator/). With this tariff the price I pay changes every 30 minutes based on the demand on the grid. This is greatly influenced by a number of factors including the external temperature and time of day.

The supply side also has a significant impact to the pricing. A sunny and windy day can lead to an excess of electricity in the grid where the pricing can occasionally go negative. Below is the pricing I will be paying for today (15th April) as you can see the afternoon rate drops almost to zero and then from 1600-1900hrs it is more expensive as that is the largest demand on the grid. This profile is typical especially the 1600-1900hrs peak.

![Octopus Agile electricity price rates dashboard showing half-hourly pricing](https://jameskilby.co.uk/wp-content/uploads/2026/04/AgileRates-1024x707.png)

Octopus also published a graph on the carbon intensity of the grid

![Octopus Energy carbon intensity graph showing grid demand over time](https://jameskilby.co.uk/wp-content/uploads/2026/04/OctopusGreen-1024x259.png)

To try and optimise the costs for my lab and also improve my green credentials I wanted to try and reduce the usage during those peak hours. I wanted to see if vSphere Power Management driven by Ansible could help me change the vSphere power management profile from balanced to low on a schedule. Initially this will be a fixed schedule going to low at 1600 every day and back to balanced at 1900hrs. I will probably enable the low power mode overnight as well.

As I have been using Ansible a lot lately, I decided to create two playbooks that I could use to achieve this and then use SemaphoreUI to schedule and run them for me.

## How vSphere Power Management driven by Ansible Works

vSphere’s default power policy is “**Balanced** ,” which leverages P-states aggressively that govern frequency and voltage scaling, while preserving turbo boost and fast ramp-up behaviour. With C-states enabled which govern idle sleep states, the CPU can opportunistically run at higher frequencies during bursts, processing workloads more quickly.

**Low Power** mode tells vSphere to choose efficiency over speed. The CPU spends more time in deep C-states when idle, sits at lower P-states when active, and is far less willing to ramp up frequency or engage turbo boost. The result is reduced power draw and heat output, at the cost of slower response to sudden workload spikes.

On my HP Z840 which is my box that stays on 24×7 and contains 2x Xeon E5-2673v3 I am expecting an approximate 30w difference between the two modes. (I will likely try and measure this in the future.) The average price I’ve paid over the 1600-1900hrs time period for the last year is 33.10p/kWh. This gives me an approximate saving of £11.00 a year. Nothing huge, but I often will have 3 more additional vSphere servers on at the same time. I will use this setting globally. It’s nice to save some money and be a bit greener at the same time. 

Manually changing these settings across multiple hosts through the vSphere client is tedious — and who wants to do that? By automating you get a repeatable process that runs in seconds regardless of how many hosts you manage.

## The Playbooks

This needed a lot of AI help to get right due to the way that Semaphore executes the playbooks. Hence the bootstrap wrappers described below.

The solution uses four playbooks: two bootstrap wrappers that handle dependency installation, and two core playbooks that apply the power policy. The bootstrap wrappers are needed because `community.vmware` does not officially support Ansible 2.18, so the collection must be installed and patched at runtime. The wrappers also install the required `PyVmomi` Python library.

Both core playbooks use the `community.vmware.vmware_host_powermgmt_policy` module with the `cluster_name` parameter, which applies the policy to **all hosts in the specified cluster**. They also support multiple clusters by accepting a list via `cluster_names`.

These can be found in my Infrastructure as Code Github [Repo](https://github.com/jameskilbynet/iac/tree/3033a9d1b41208a48a75f30e8ccf395d4828dca5/ansible/powermanagement)

### run_set_power_low.yml (Bootstrap Wrapper)

This is the playbook you point Semaphore at. It installs `PyVmomi`, installs the `community.vmware` collection to a temporary path, patches the Ansible version constraint, then launches the core playbook as a subprocess with the correct collection path configured:
    
    
    ---
    - name: Bootstrap and run power management playbook
      hosts: localhost
      gather_facts: no
      tasks:
        - name: Install PyVmomi Python library
          ansible.builtin.pip:
            name: PyVmomi
            state: present
        - name: Install collection and patch compatibility
          ansible.builtin.shell: |
            ansible-galaxy collection install community.vmware --force -p /tmp/vmware_collections 2>&1
            MANIFEST="/tmp/vmware_collections/ansible_collections/community/vmware/MANIFEST.json"
            if [ -f "$MANIFEST" ]; then
              sed -i 's/"requires_ansible": ".*"/"requires_ansible": ">=2.15.0"/' "$MANIFEST"
            fi
            META="/tmp/vmware_collections/ansible_collections/community/vmware/meta/runtime.yml"
            if [ -f "$META" ]; then
              sed -i 's/requires_ansible: .*/requires_ansible: ">=2.15.0"/' "$META"
            fi
        - name: Write extra vars file
          ansible.builtin.copy:
            content: |
              vcenter_host: "{{ vcenter_host }}"
              vcenter_user: "{{ vcenter_user }}"
              vcenter_pass: "{{ vcenter_pass }}"
              cluster_names: {{ cluster_names | to_json }}
            dest: /tmp/.powermgmt_vars.yml
            mode: "0600"
          no_log: true
        - name: Run Set Power Low playbook
          ansible.builtin.shell: |
            cat > /tmp/ansible_vmware.cfg << 'EOF'
            [defaults]
            collections_path = /tmp/vmware_collections
            collections_scan_sys_path = false
            EOF
            export ANSIBLE_CONFIG=/tmp/ansible_vmware.cfg
            ansible-playbook {{ playbook_dir }}/set_power_low.yml -e @/tmp/.powermgmt_vars.yml 2>&1
          register: playbook_result
        - name: Clean up temp files
          ansible.builtin.file:
            path: "{{ item }}"
            state: absent
          loop:
            - /tmp/.powermgmt_vars.yml
            - /tmp/ansible_vmware.cfg
        - name: Show playbook output
          ansible.builtin.debug:
            msg: "{{ playbook_result.stdout_lines }}"

📋 Copy

### set_power_low.yml

This is the core playbook that sets all hosts in the specified clusters to **Low Power** mode:
    
    
    ---
    - name: Set vSphere host power management policy to Low Power
      hosts: localhost
      gather_facts: no
      collections:
        - community.vmware
    
      vars:
        vcenter_hostname: "{{ vcenter_host }}"
        vcenter_username: "{{ vcenter_user }}"
        vcenter_password: "{{ vcenter_pass }}"
        validate_certs: false
    
      tasks:
        - name: Set power management policy to Low Power on all hosts in cluster
          community.vmware.vmware_host_powermgmt_policy:
            hostname: "{{ vcenter_hostname }}"
            username: "{{ vcenter_username }}"
            password: "{{ vcenter_password }}"
            validate_certs: "{{ validate_certs }}"
            cluster_name: "{{ item }}"
            policy: low-power
          loop: "{{ cluster_names if cluster_names is iterable and cluster_names is not string else [cluster_names] }}"
          register: power_results
    
        - name: Display results
          ansible.builtin.debug:
            msg: "{{ item.item }}: {{ 'changed' if item.changed else 'ok' }}"
          loop: "{{ power_results.results }}"

📋 Copy

### set_power_balanced.yml

This playbook switches all hosts in the specified clusters back to **Balanced** , restoring the default trade-off between performance and power consumption:
    
    
    ---
    - name: Set vSphere host power management policy to Balanced
      hosts: localhost
      gather_facts: no
      collections:
        - community.vmware
    
      vars:
        vcenter_hostname: "{{ vcenter_host }}"
        vcenter_username: "{{ vcenter_user }}"
        vcenter_password: "{{ vcenter_pass }}"
        validate_certs: false
    
      tasks:
        - name: Set power management policy to Balanced on all hosts in cluster
          community.vmware.vmware_host_powermgmt_policy:
            hostname: "{{ vcenter_hostname }}"
            username: "{{ vcenter_username }}"
            password: "{{ vcenter_password }}"
            validate_certs: "{{ validate_certs }}"
            cluster_name: "{{ item }}"
            policy: balanced
          loop: "{{ cluster_names if cluster_names is iterable and cluster_names is not string else [cluster_names] }}"
          register: power_results
    
        - name: Display results
          ansible.builtin.debug:
            msg: "{{ item.item }}: {{ 'changed' if item.changed else 'ok' }}"
          loop: "{{ power_results.results }}"

📋 Copy

## Variables

Each playbook expects the following variables to be passed in via Semaphore:

  * **vcenter_host** — the FQDN or IP of your vCenter Server
  * **vcenter_user** — a vCenter user with host configuration privileges
  * **vcenter_pass** — the password for the above user (mark as secret in Semaphore)
  * **cluster_names** — the vSphere cluster(s) to target, either a single name (e.g. `"GPU"`) or a list (e.g. `["GPU", "Compute"]`)

These can be set in the Semaphore task template as variables. Semaphore injects them at runtime, so you never need to store sensitive vCenter credentials alongside your playbook code.

## Running the Playbooks

From Semaphore, point your task template at `run_set_power_low.yml` or `run_set_power_balanced.yml` (the bootstrap wrappers). These handle installing the `community.vmware` collection and `PyVmomi` automatically, then launch the core playbook. If you prefer the command line:
    
    
    ansible-playbook run_set_power_low.yml -e "vcenter_host=vcsa.local vcenter_user=administrator@vsphere.local vcenter_pass=YourPassword cluster_names=MyCluster"

📋 Copy

If everything is working as expected you should see the task pop like

![vSphere Power Management driven by Ansible changing ESXi host power policy from Balanced to Low Power](https://jameskilby.co.uk/wp-content/uploads/2026/04/vSphereChangePower-1024x90.png)

## Scheduling

For now I am just using fixed time based schedules in SemaphoreUI setting low power at 1600 and balanced at 1900. The next iteration will be to integrate with Home Assistant as that can already see Octopus Agile pricing via the Octopus API. I would like to set a cost threshold where if the electricity price is above this then low power mode is triggered. The likelihood is this will also take care of the 1600-1900 window.

## Prerequisites

Before running these playbooks, make sure you have the following in place:

  * Ansible 2.15 or later installed
  * The bootstrap wrapper playbooks handle installing the `community.vmware` collection and `PyVmomi` automatically — no manual setup needed
  * A vCenter Server user account with permission to change host power management settings
  * Network connectivity from the Ansible control node (or Semaphore runner) to the vCenter Server

## 📚 Related Posts

  * [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [ ![UniFi UDM Beast 1U rack-mount gateway shown front-on, with two 3.5-inch drive bays, a bank of RJ45 and SFP network ports, and dimension labels.](https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast-768x219.webp) ](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Networking](https://jameskilby.co.uk/category/networking/)

### [Unleashing the Beast](https://jameskilby.co.uk/2026/06/ubiquiti-udm-beast/)

By[James](https://jameskilby.co.uk) June 20, 2026 · Updated July 11, 2026

Retiring my ageing WatchGuard M200, I swap in the UniFi UDM Beast — a hardware tour, first iperf and WAN tests, the BGP/FRR setup, and the homelab services I’m consolidating onto it.

  * [ ![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png) ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk) September 2, 2025 · Updated June 5, 2026

An intro on how I use SemaphoreUI to manage my Homelab

  * [ ![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg) ](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk) January 18, 2024 · Updated June 1, 2026

How to deploy Holodeck with Legacy CPU’s

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [My First Homelab Storage Setup: HP Gen8 & Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below.

  * [ ![Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/wp-content/uploads/2023/10/IMG_1107-768x403-1.jpg) ](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Nvidia Tesla P4 vGPU Setup in VMware Homelab: Full Guide](https://jameskilby.co.uk/2023/10/vgpu-setup-in-my-homelab/)

By[James](https://jameskilby.co.uk) October 23, 2023 · Updated July 11, 2026

Card Stats Install steps VM Provisioning Folding@Home A little while ago I decided to play with vGPU in my homelab.

  * [ ![Monitoring VMware Cloud on AWS: Tools & Approaches \(Part 1\)](https://jameskilby.co.uk/wp-content/uploads/2026/03/VMConAWS.png.webp) ](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

[VMware](https://jameskilby.co.uk/category/vmware/) | [AWS](https://jameskilby.co.uk/category/aws/) | [Veeam](https://jameskilby.co.uk/category/veeam/)

### [Monitoring VMware Cloud on AWS: Tools & Approaches (Part 1)](https://jameskilby.co.uk/2019/12/monitoring-vmc-part-1/)

By[James](https://jameskilby.co.uk) December 17, 2019 · Updated June 5, 2026

As previously mentioned I have been working a lot with VMware Cloud on AWS and one of the questions that often crops up is around an approach to monitoring.