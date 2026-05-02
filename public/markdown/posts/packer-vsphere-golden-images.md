---
title: "Automating vSphere Golden Images with Packer and GitHub Actions"
description: "Automate your Packer vSphere golden-image pipeline: build 6 Ubuntu LTS templates (22.04, 24.04, 26.04) server & desktop flavours with GitHub Actions."
date: 2026-04-30T17:22:19+00:00
modified: 2026-05-01T17:48:05+00:00
author: James Kilby
categories:
  - Automation
  - Github
  - Homelab
  - Storage
  - vExpert
  - VCF
  - VMware
  - Artificial Intelligence
  - Docker
  - NVIDIA
  - Traefik
  - Runecast
  - Ansible
  - Hosting
  - Kubernetes
tags:
  - #Automation
  - #Devops
  - #github-actions
  - #Homelab
  - #packer
  - #Ubuntu
  - #vsphere
url: https://jameskilby.co.uk/2026/04/packer-vsphere-golden-images/
image: https://jameskilby.co.uk/wp-content/uploads/2026/04/packer-github-actions-vsphere-pipeline.png
---

![Packer Github Actions Vsphere Pipeline](https://jameskilby.co.uk/wp-content/uploads/2026/04/packer-github-actions-vsphere-pipeline.png)

[Automation](https://jameskilby.co.uk/category/automation/) | [Github](https://jameskilby.co.uk/category/github/)

# Automating vSphere Golden Images with Packer and GitHub Actions

By[James](https://jameskilby.co.uk)April 30, 2026May 1, 2026 • 📖9 min read(1,819 words)

📅 **Published:** April 30, 2026• **Updated:** May 01, 2026

Building VM templates by hand is slow, error-prone, and impossible to audit. This post walks through how I built this Packer vSphere pipeline to automate golden-image deployment for my homelab using [HashiCorp Packer](https://www.packer.io/) and GitHub Actions — from downloading Ubuntu ISOs right through to a finished, fully-provisioned vSphere template, with no manual steps after the initial setup.

The result is six production-ready Ubuntu LTS templates (22.04, 24.04, and 26.04 — each in server and desktop flavours) rebuilt automatically on every push to `main`, on a weekly schedule, or on demand from the GitHub Actions UI.

* * *

## What the Pipeline Builds

Each run produces up to six vSphere templates:

Ubuntu Version| Server| Desktop  
---|---|---  
22.04 LTS (Jammy)| 2 vCPU / 2 GB / 40 GB| 4 vCPU / 4 GB / 60 GB  
24.04 LTS (Noble)| 2 vCPU / 2 GB / 40 GB| 4 vCPU / 4 GB / 60 GB  
26.04 LTS (Plucky)| 2 vCPU / 2 GB / 40 GB| 4 vCPU / 4 GB / 60 GB  
  
All templates use EFI firmware, pvscsi storage, vmxnet3 networking, thin-provisioned LVM disks, and ship with open-vm-tools, SSH hardening, and zeroed free space for compact storage. Hardware sizes are fully configurable via variables.

* * *

## How the Packer vSphere Pipeline Works

The pipeline has three logical stages:
    
    
    Upload ISOs ──► packer init ──► packer build ──► vSphere Template
    (upload-isos.sh)                (vsphere-iso)    (ready to clone)

📋 Copy

### 1\. ISO Management

Ubuntu ISOs are downloaded from `releases.ubuntu.com`, SHA256-verified, and imported into a vSphere Content Library named `Packer-ISOs`. This is a one-time setup step (or re-run when a new point release drops). The script is idempotent — if an ISO already exists in the library it is skipped, so it is safe to re-run after a partial failure.

### 2\. Unattended OS Install via Cloud-Init

Rather than hosting an HTTP server for the autoinstall seed (which requires network routing from the VM back to the build machine), Packer mounts the cloud-init configuration as a small ISO image labelled `cidata` directly in vSphere. The Ubuntu installer finds it automatically with `ds=nocloud` and runs fully unattended.

The autoinstall user-data is templated at build time using HCL’s `templatefile()` function, so credentials are injected from variables rather than baked into static files. Key autoinstall steps include: LVM storage layout, SSH server enabled, passwordless sudo for the build user, SSH host key removal (regenerated on first clone boot), and a `datasource_list: [None]` cloud-init config written to `/etc/cloud/cloud.cfg.d/` via `late-commands`. This neutralises cloud-init on deployed VMs without disabling its systemd units — a subtle but important distinction: `cloud-init.disabled` breaks the network on Ubuntu 24.04 because cloud-init’s boot units sit in the dependency chain for network bring-up. Setting `datasource_list: [None]` makes cloud-init a no-op (no user-data, no key or user management) while still letting its units complete normally, so netplan brings the network up correctly on every clone.

The network configuration in the autoinstall user-data uses a `vmxnet3` driver match rather than a hardcoded interface name. Instead of specifying `ens192` (which varies by hardware and vSphere version), the netplan config uses `match: driver: vmxnet3` to target the vmxnet3 adapter generically. This makes the same user-data template portable across any ESXi host or vSphere version without modification.

### 3\. Shell Provisioners

Two shell scripts run after the OS install completes:

  *  **setup.sh** — full `apt upgrade`, installs common utilities, disables swap, removes SSH host keys, appends SSH hardening config (`PermitRootLogin no` etc.), and zeroes free disk space to minimise template storage footprint, and optionally creates a named admin account and imports its SSH public keys from GitHub via `ssh-import-id-gh` (controlled by the `admin_username` and `admin_github_user` variables).
  *  **vmtools.sh** — verifies or installs open-vm-tools (and the desktop variant if a display manager is detected), enables the service, and reports the running version.

### 4\. Template Conversion

Once provisioning completes, Packer converts the finished VM to a vSphere template in-place. The template is named `ubuntu-<version>-<type>-<YYYYMMDD>` (e.g. `ubuntu-2404-server-20260429`) and placed in the folder specified by the `vsphere_folder` variable. A build manifest JSON is written to `manifests/` recording the template name and metadata.

* * *

## GitHub Actions CI/CD

Three workflows cover the full pipeline. The only step that runs locally is the one-time `make secrets` to push credentials to GitHub — everything else is automated.
    
    
    Local (one-time)                GitHub Actions (automated)
    ────────────────                ──────────────────────────────────────
    1. Fill in pkrvars file
    2. make secrets              ─► secrets stored in GitHub
    
                                    PR opened
                                    └─► validate.yml
                                        fmt check + packer validate
    
                                    Merge to main / weekly cron / manual
                                    └─► build-templates.yml
                                        packer build → vSphere template
    
    3. Trigger upload-isos.yml   ─► upload-isos.yml
       from Actions UI               govc → Content Library (manual only)

📋 Copy

### Workflow 1: Validate

 **Trigger:** Every pull request touching `.pkr.hcl` files, templates, or provisioner scripts. Also runs on push to `main`.

 **Runner:** `ubuntu-latest` (GitHub-hosted) — no self-hosted runner or real secrets needed, because `packer validate` checks syntax and variable references only; it never contacts vSphere. Placeholder values are passed for required variables.

 **What it does:**

  1. Installs Packer via direct binary download (avoids APT codename issues with pre-release Ubuntu versions on the runner)
  2. Downloads the vSphere plugin via `packer init`
  3. Runs `packer fmt --check` — fails the PR if any file needs reformatting
  4. Runs `packer validate` across all six builds — catches undefined variables, bad HCL, and broken `templatefile()` references before anything reaches `main`

Fast feedback in under two minutes with zero infrastructure cost.

### Workflow 2: Build Templates

 **Trigger:** Push to `main` (when `.pkr.hcl` files or scripts change), weekly cron (every Sunday at 02:00 UTC to pick up security updates), or manual dispatch.

 **Runner:** Self-hosted — required because GitHub-hosted runners live on the public internet and cannot reach a private vCenter. A self-hosted runner installed on a VM inside the vSphere network dials out to GitHub on port 443 to pick up jobs, so no inbound firewall rules are needed.

 **Matrix strategy:** A `resolve-targets` job converts the trigger input (e.g. `all-servers`, `2404-desktop`, or `all`) into a build matrix, then each template runs as a parallel job — up to six simultaneous builds.

 **Key steps in each matrix job:**

  1.  **Pre-flight secrets check** — fails immediately with a clear list of any missing secrets before any tools are installed, rather than letting Packer produce cryptic connection errors
  2.  **Install Packer** — fetches the latest binary directly from HashiCorp releases (codename-independent, works on any Ubuntu version)
  3.  **Install xorriso** — required for Packer to create the cloud-init CD image
  4.  **Install govc & resolve ISO paths** — queries the Content Library via the vSphere SDK to get the exact datastore path for each ISO (Content Library items live under `contentlib-{lib-uuid}/{item-uuid}/` — not guessable without the API)
  5.  **Write variables file** — assembles a temporary `runner.pkrvars.hcl` from GitHub Secrets, so no secret values appear in command-line arguments
  6.  **Packer validate → Packer build** — with `PACKER_LOG=1` for full debug output and `-on-error=cleanup` to destroy VMs on failure
  7.  **Upload artifacts** — Packer log and build manifest uploaded as workflow artifacts (retained 30 and 90 days respectively)
  8.  **Orphan VM cleanup** — runs on cancellation or failure; finds any VM matching the build name pattern that was not converted to a template and destroys it, keeping vSphere clean
  9.  **Always delete credentials file** — `runner.pkrvars.hcl` is removed even on failure

The workflow also supports a **dry-run mode** (validate only, no build) triggerable from the Actions UI — useful for testing workflow changes without waiting 60-90 minutes for a full build.

### Workflow 3: Upload ISOs

 **Trigger:** Manual only — run once during initial setup or when Ubuntu releases a new point version.

 **What it does:** Runs `scripts/upload-isos.sh` on the self-hosted runner, downloading ISOs from `releases.ubuntu.com` with SHA256 verification and importing them into the vSphere Content Library via govc. Installs govc automatically if not present. Configurable via workflow inputs: versions to upload, library name, whether to keep local downloads, and whether to skip checksum verification.

* * *

## Concurrency and Safety

The build workflow uses a `concurrency` group (`packer-build`) with `cancel-in-progress: false`, so a queued run waits for the current one to finish rather than being cancelled. This prevents two jobs from racing to create VMs with the same name in vSphere — a subtle but important detail when builds are triggered by both push events and the weekly schedule.

* * *

## Secrets Management

All vSphere credentials, build credentials, and ISO paths are stored as GitHub Actions Secrets. A helper script (`scripts/set-github-secrets.sh`) reads the local `variables.pkrvars.hcl` file and pushes every value to GitHub in one step via the GitHub CLI:
    
    
    make secrets

📋 Copy

Re-run any time a value changes — existing secrets are overwritten. The local vars file is covered by `.gitignore` so credentials are never committed.

Two optional secrets control admin account creation in the template: `ADMIN_USERNAME` sets a persistent named account to create (leave empty to skip), and `ADMIN_GITHUB_USER` sets the GitHub username whose public SSH keys are imported into that account via `ssh-import-id-gh`. If these secrets are absent or empty, no admin account is created — the build still completes normally.

* * *

## Project Structure
    
    
    packer/
    |-- packer.pkr.hcl              # Plugin requirements (vsphere >= 1.3.0)
    |-- variables.pkr.hcl           # All variable declarations
    |-- locals.pkr.hcl              # Shared locals: build_date, build_timestamp
    |-- ubuntu-2204.pkr.hcl         # 22.04 server + desktop sources and builds
    |-- ubuntu-2404.pkr.hcl         # 24.04 server + desktop sources and builds
    |-- ubuntu-2604.pkr.hcl         # 26.04 server + desktop sources and builds
    |-- templates/
    |   |-- server-user-data.pkrtpl # Cloud-init autoinstall config -- server
    |   `-- desktop-user-data.pkrtpl
    |-- scripts/
    |   |-- upload-isos.sh          # Download ISOs to Content Library
    |   |-- setup.sh                # Post-install: upgrade, SSH hardening
    |   `-- vmtools.sh              # Verify / install open-vm-tools
    |-- Makefile                    # Convenience build targets
    `-- .github/workflows/
        |-- validate.yml
        |-- build-templates.yml
        `-- upload-isos.yml

📋 Copy

* * *

## Running Builds Locally

The Makefile wraps the most common Packer invocations:
    
    
    # Build a single template
    make 2404-server
    
    # Build all six images sequentially
    make build-all
    
    # Validate without building
    make validate

📋 Copy

Under the hood each target calls:
    
    
    packer build -var-file=variables.pkrvars.hcl -only='*.vsphere-iso.ubuntu-2404-server' .

📋 Copy

The glob prefix (`*.`) is required because Packer’s full source reference format is `<build-label>.<source-type>.<source-name>` — omitting the label causes “No builds to run”.

* * *

## Why Bother?

A few things this pipeline gives you that manual template builds don’t:

  *  **Reproducibility** — every template is built from the same HCL source, the same provisioner scripts, and the same Ubuntu ISO. No “I think I installed that manually last time.”
  *  **Up-to-date templates** — the weekly cron rebuild means templates always include the latest security patches from `apt upgrade`, without any manual effort.
  *  **Auditability** — every build is tied to a git commit. The Packer log and manifest are retained as workflow artifacts. You can see exactly what changed and when.
  *  **PR validation** — format and syntax checks on every pull request mean broken HCL never reaches `main`.
  *  **No local tooling required day-to-day** — after the one-time `make secrets` setup, builds run entirely in the cloud. Useful if you work across multiple machines.

* * *

The full source is available on [GitHub](https://github.com/w20kilja/packer). Feedback and PRs welcome.

## 📚 Related Posts

  * [Auto-Documenting MikroTik Switch Ports with Ansible and LLDP Neighbours](https://jameskilby.co.uk/2026/05/auto-documenting-mikrotik-switch-ports-with-ansible-and-lldp-neighbours/)
  * [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)
  * [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

## Similar Posts

  * [![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png)](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk)April 17, 2023April 16, 2026

I have been a VMware vExpert for many years and it has brought me many many benefits over the years.

  * [![VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/wp-content/uploads/2024/01/40oOd8IipPvtrPJs-1198788743-768x737.jpg)](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

[VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [VMware Holodeck on Older CPUs: Fixing Compatibility Issues](https://jameskilby.co.uk/2024/01/holodeck-cpu-fixes/)

By[James](https://jameskilby.co.uk)January 18, 2024April 11, 2026

How to deploy Holodeck with Legacy CPU’s

  * [![Self-hosted AI stack operations architecture — Ansible automation, Uptime Kuma monitoring, Open WebUI backup, and container orchestration with Docker and Traefik](https://jameskilby.co.uk/wp-content/uploads/2026/03/ai-stack-featured-768x403.png)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)

By[James](https://jameskilby.co.uk)April 4, 2026April 16, 2026

Part 2 of my self-hosted AI stack series. I cover container resource sizing, dual-network isolation via Traefik and Cloudflare Tunnels, and every database powering the stack — PostgreSQL, ClickHouse, Redis, Qdrant, MinIO, MongoDB, SQLite, Prometheus, and Jaeger — plus the backup strategy for each.

  * [![Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/wp-content/uploads/2023/05/Runecast-Solutions-Ltd.png)](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

[Runecast](https://jameskilby.co.uk/category/runecast/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Runecast Remediation Scripts: Auto-Fix VMware Storage Issues](https://jameskilby.co.uk/2023/05/runecast-remediation-scripts/)

By[James](https://jameskilby.co.uk)May 16, 2023April 16, 2026

I am a huge fan of the Runecast product and luckily as a vExpert they give out NFR licences for my lab.

  * [![vSphere Power Management Ansible Playbooks with Semaphore](https://jameskilby.co.uk/wp-content/uploads/2026/04/vsphere-power-management-ansible-768x403.png)](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/)

### [Automating vSphere Power Management driven by Ansible and SemaphoreUI](https://jameskilby.co.uk/2026/04/vsphere-power-management-driven-by-ansible/)

By[James](https://jameskilby.co.uk)April 15, 2026April 19, 2026

In this post I’ll walk through how I use vSphere Power Management driven by Ansible and SemaphoreUI to automatically reduce ESXi host electricity consumption — saving real money on my Octopus Agile tariff by toggling hosts between Low Power and Balanced policies. Introudction One of the larger costs of running my homelab is the electricity….

  * [![Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/wp-content/uploads/2022/12/22225832.png)](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

[Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Kubernetes](https://jameskilby.co.uk/category/kubernetes/)

### [Use Portainer in a Homelab with GitHub](https://jameskilby.co.uk/2022/12/use-portainer-in-a-homelab-with-github/)

By[James](https://jameskilby.co.uk)December 9, 2022April 16, 2026

Late to the party or not, I have been using containers in my lab more and more and that has led me to Portainer ….