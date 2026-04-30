---
title: "How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare"
description: "I wanted to automate the publishing of my blog from the authoring side to the public side. These are some of the improvements I made."
date: 2025-10-06T15:57:06+00:00
modified: 2026-04-16T22:01:41+00:00
author: James Kilby
categories:
  - Cloudflare
  - Devops
  - Github
  - Wordpress
  - Hosting
  - Ansible
  - Artificial Intelligence
  - Containers
  - Homelab
  - NVIDIA
  - Traefik
  - VMware
  - Automation
  - Docker
  - VCF
  - Personal
tags:
  - #Blog
  - #Cloudflare
  - #Cloudflare Pages
  - #github
  - #Runners
  - #Wordpress
url: https://jameskilby.co.uk/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare/
image: https://jameskilby.co.uk/wp-content/uploads/2025/10/Github-Actions.webp
---

![Github Actions](https://jameskilby.co.uk/wp-content/uploads/2025/10/Github-Actions.webp)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Github](https://jameskilby.co.uk/category/github/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

# How I upgraded my blog as a Static Website with GitHub Actions and Cloudflare

By[James](https://jameskilby.co.uk)October 6, 2025April 16, 2026 • 📖7 min read(1,380 words)

📅 **Published:** October 06, 2025• **Updated:** April 16, 2026

I wanted to automate the publishing of my blog from the authoring side to the public side. These are some of the improvements I made.

## Table of Contents

## What I started with

My previous setup, involved a locally hosted WordPress instance. This runs in my homelab in an Ubuntu VM. This I will refer to as the authoring instance. Within this WordPress instance I have the “[Simply Static](https://simplystatic.com)” Plugin. When I have finished writing a post or making changes, I then hit “Generate” within the plugin. It will then scan the entire site, creating an entire copy that’s made available as a Zip download. The benefits of this setup I have discussed [previously](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

I then take this export and copy it to a public Github repo called “WordPress”. When the code is checked in, this triggers a process within Cloudflare to publish it as a static site in Cloudflare’s CDN. I have previously written about the Cloudflare part.

## What I finished with

![Wordpress Authoring](https://jameskilby.co.uk/wp-content/uploads/2025/10/Wordpress-Authoring-2-1024x677.png)

The new setup is conceptually similar in that I have maintained the authoring WordPress instance. The major difference is how the data gets from the authoring WordPress instance to GitHub. The GitHub to Cloudflare part remains unchanged.

I have introduced a GitHub runner that runs alongside the WordPress Instance. This runner has permissions to query the WordPress API to get data. Now when I have finished updating my site, I can start the runner. It then scans the site making a local copy of it and performs an automated check-in to Github.

 **Disclaime** r: I used a fair bit of AI to help with some of the python and API calls. It also wrote the documentation for me.

## How I got there

First things first, I created a new GitHub repo so that if I messed anything up, I could point Cloudflare back to the previous WordPress Repo.

### WordPress API

The next step was to enable the WordPress API. This was to allow a GitHub runner to communicate directly with WordPress. I chose to do this with a plugin called [REST API Authentication for WP](https://en-gb.wordpress.org/plugins/wp-rest-api-authentication/)

I then created a simple basic authentication token. This is then stored in the GitHub repo as an action secret. This allows me to have a public repo but without leaking the key.

This is done by navigating to the GitHub repo > Settings then navigate to the Security section and select “Secrets & Variables” Then create a “New Repository Secret” called WP_AUTH_TOKEN add your API token.

### GitHub Runner

The next step was to deploy a runner. These can either be a GitHub-hosted runner or a local runner. I am using a local GitHub runner running on an Ubuntu machine in my lab to perform this function as the WordPress instance isn’t available publicly and therefore for the GitHub-hosted runner.

To set this up, first you need to navigate to the Actions section within your GitHub Repo and select the “Runners” section. 

Ensure you have the Self-hosted runners tab selected.

GitHub then gives you easy instructions to set up the runner. First, you select the Architecture I am using Ubuntu and therefore selected Linux. GitHub then gives you great instructions.
    
    
    # Create a folder
    $ mkdir actions-runner && cd actions-runner
    # Download the latest runner package
    $ curl -o actions-runner-osx-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-osx-x64-2.329.0.tar.gz
    # Optional: Validate the hash
    $ echo "c5a14e84b358c72ca83bf14518e004a8ad195cc440322fbca2a4fec7649035c7  actions-runner-osx-x64-2.329.0.tar.gz" | shasum -a 256 -c
    # Extract the installer
    $ tar xzf ./actions-runner-osx-x64-2.329.0.tar.gz

📋 Copy

Then configure the runner 
    
    
    # Create the runner and start the configuration experience
    $ ./config.sh --url https://github.com/jameskilbynet/jkcoukblog --token AFPWGXXXXXXXXXVHXXI7D7DM
    # Last step, run it!
    $ ./run.sh

📋 Copy

### Python

The runner is then executing a number of Python scripts as can be seen in the GitHub repo.

At a high level these:

  * Discover all posts, pages, categories and tags
  * Fetches the media library assets 
  * Replaces all WordPress URL’s as relative
  * Converts WordPress Embed blocks to iframes
  * Removes WordPress specific elements that are not required in the static site.

This grabs a copy of the site and then stores it in the Public directory within the GitHub Repo and issues a Git Commit and Git Push command.

When I have finished making changes in WordPress I can trigger the GitHub runner manually ( It also runs on a Cron schedule)

It typically takes about 1 minute 20 to process my site.

In that time it:

  * Set’s up the job on a runner
  * Check’s Out the repo
  * Sets up the Python environment
  * Install any relevant dependencies 
  * Test’s the runner environment
  * Generates the Static Site files
  * Commit and Pushes the Static Site
  * Notifies Slack 
  * Executes Python cleanup
  * Executes other cleanups

## Build Notifications

I didn’t want to have to login to GitHub or Cloudflare to monitor progress of the runner, so I added notifications to Slack.

### Create a Slack Webhook URL

First, you’ll need to create a Slack webhook. Here’s how:

  1. Go to your Slack workspace
  2. Navigate to Apps: Click on your workspace name → Settings & administration → Manage apps
  3. Search for “Incoming Webhooks” and add it to your workspace
  4. Create a webhook:  
◦ Choose the channel where you want notifications (e.g., #deployments, #general) I created a web channel  
◦ Click “Add Incoming Webhooks Integration”  
◦ Copy the Webhook URL (looks like: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXX

#### GitHub Notifications

In GitHub, navigate to the secrets actions section of your repo

Add a new secret Called SLACK_WEBHOOK_URL

This will automatically get triggered by the workflow in the repo

#### Cloudflare Notifications

In Cloudflare, go to the Notifications settings and select Destinations.

Create a Webhook using the Webhook URL created above with an appropriate name.

Then navigate to the “Workers & Pages” section and select your static pages site. Then navigate to the settings of your workers and select the notification events that you want, and select the Webhook name created above.

While testing, I have all notifications turned on.

![Cloudflare Events](https://jameskilby.co.uk/wp-content/uploads/2025/10/Cloudflare-Events-1024x214.png)

When I trigger the runner, I get 3 Slack notifications in my Web channel. The first is the Commit to GitHub, I then get one when Cloudflare starts building the Static site and one when it completes. One useful feature is that it gives you the preview URL so you can’t instantly view your changes without having any DNS propagation issues.
    
    
    incoming-webhook
    APP  10:27 PM
    :white_check_mark: Succeeded GitHub Actions
    
    8398a7@action-slack
    repo
    jameskilbynet/jkcoukblog
    commit
    4761df3f
    10:27
    Slack
    :zap: Cloudflare Pages: A production deployment has started for jkcoukblog :zap:
    Build Link: https://dash.cloudflare.com/c9bb9919eaab3686694017fa604070dd/pages/view/jkcoukblog/aeacb2b5-03c8-4771-a252-cf48b2c86da0
    Commit Hash: b72489f574a14dc6aacad7c2fa1fbd874ed7fed4
    Environment: ENVIRONMENT_PRODUCTION
    Timestamp: 2025-10-09T21:27:53.399259Z
    Cloudflare | Oct 9th
    10:28
    Slack
    :white_check_mark: Cloudflare Pages: A production deployment has succeeded for jkcoukblog :white_check_mark:
    Build Link: https://dash.cloudflare.com/c9bb9919eaab3686694017fa604070dd/pages/view/jkcoukblog/aeacb2b5-03c8-4771-a252-cf48b2c86da0
    Commit Hash: b72489f574a14dc6aacad7c2fa1fbd874ed7fed4
    Preview URL: https://aeacb2b5.jkcoukblog.pages.dev
    Branch Alias URL:
    Project URL: https://jkcoukblog.pages.dev
    Show more
    Cloudflare | Oct 9th

📋 Copy

## Using Utterance for Comments

I wanted to add a comment mechanism to my pages, but as it’s a static site that needs a little bit of planning as the traditional WordPress mechanisms won’t work. After a little bit of research I decided to use [Utterance](https://utteranc.es).

Utterance is lightweight javascript code that integrates with GitHub issues. To enable it, I enabled Issues on the repo I have been using for all of my Web stuff and then edited the WordPress theme using the built-in theme editor.

Within WordPress changed comments.php to the following
    
    
    <?php
    /**
     * Utterances-only comments template.
     *
     * @package Infinity Blog
     */
    
    if (post_password_required()) {
        return;
    }
    ?>
    
    <div id="comments" class="comments-area">
        <div class="pb-30">
            
            <section id="utterances-comments">
                <script src="https://utteranc.es/client.js"
                    repo="jameskilbynet/jkcoukblog"
                    issue-term="pathname"
                    theme="github-light"
                    crossorigin="anonymous"
                    async>
                </script>
            </section>
        </div>
    </div>

📋 Copy

I also wanted a Slack notification if anyone posted comments on one of my pages. Unfortunately the payload Slack is expecting is a JSON payload in a specific format that GitHub doesn’t do by default. I therefore created a new GitHub Action to trigger the notification

###  **Use GitHub Actions**

You can trigger Slack messages directly via GitHub Actions:

  1. Create a GitHub Action workflow `.github/workflows/issue-to-slack.yml`:

    
    
    name: Notify Slack on Issue Creation
    
    on:
      issues:
        types: [opened]
    
    jobs:
      notify-slack:
        runs-on: ubuntu-latest
        steps:
          - name: Send Slack Notification
            uses: slackapi/slack-github-action@v1.23.0
            with:
              payload: |
                {
                  "text": "New Comment Created: <${{ github.event.issue.html_url }}|${{ github.event.issue.title }}> by ${{ github.event.issue.user.login }}"
                }
            env:
              SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    

📋 Copy

I am using the same SLACK_WEBHOOK_URL as defined previously so these get posted in my existing web channel.

## 📚 Related Posts

  * [Blog Performance &#038; SEO Improvements: Cloudflare, Privacy &#038; More](https://jameskilby.co.uk/2026/01/web-development-improvements/)
  * [WordPress Hosting with Cloudflare Pages](https://jameskilby.co.uk/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages/)
  * [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

## Similar Posts

  * [![What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png)](https://jameskilby.co.uk/2018/03/cloudflare/)

[Hosting](https://jameskilby.co.uk/category/hosting/)

### [What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/2018/03/cloudflare/)

By[James](https://jameskilby.co.uk)March 27, 2018April 16, 2026

Cloudflare – What is it and why would I care? I have been using Cloudflare for a long time.

  * [![Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/wp-content/uploads/2026/01/VMware-NVIDIA-logos_ee2f18dc-615d-4c9e-8f11-9c3c2ce2bf37-prv-768x432.png)](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Containers](https://jameskilby.co.uk/category/containers/) | [Devops](https://jameskilby.co.uk/category/devops/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [NVIDIA](https://jameskilby.co.uk/category/nvidia/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

By[James](https://jameskilby.co.uk)February 9, 2026April 16, 2026

Learn how to use Ansible to configure an Ubuntu VM for use with NVIDIA based AI workloads in vSphere

  * [![Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/wp-content/uploads/2026/01/Website-Optimisations-768x560.png)](https://jameskilby.co.uk/2026/01/web-development-improvements/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Blog Performance & SEO Improvements: Cloudflare, Privacy & More](https://jameskilby.co.uk/2026/01/web-development-improvements/)

By[James](https://jameskilby.co.uk)January 15, 2026April 16, 2026

I have spent the Christmas break making some improvements to this blog.

  * [![Automated VCF 9 Offline Depot architecture diagram showing Traefik reverse proxy and Nginx file server stack](https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png)](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Automation](https://jameskilby.co.uk/category/automation/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/) | [Traefik](https://jameskilby.co.uk/category/traefik/) | [VCF](https://jameskilby.co.uk/category/vmware/vcf/) | [VMware](https://jameskilby.co.uk/category/vmware/)

### [Automated VCF 9 Offline Depot](https://jameskilby.co.uk/2026/04/automated-vcf-9-offline-depot/)

By[James](https://jameskilby.co.uk)April 10, 2026April 16, 2026

One Bash script turns a fresh Ubuntu VM into a VCF 9 Offline Depot: Traefik, Nginx, basic auth, and Let’s Encrypt wildcard certs via Cloudflare DNS.

  * [![Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/wp-content/uploads/2022/10/iu-768x450.jpeg)](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

[Cloudflare](https://jameskilby.co.uk/category/cloudflare/) | [Hosting](https://jameskilby.co.uk/category/hosting/) | [Wordpress](https://jameskilby.co.uk/category/wordpress/)

### [Static WordPress hosting using Cloudflare](https://jameskilby.co.uk/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages/)

By[James](https://jameskilby.co.uk)October 20, 2022April 16, 2026

For a while now I have been running this site directly from Cloudflare utilising their excellent worker’s product.

  * [![Analytics in a privacy focused world](https://jameskilby.co.uk/wp-content/uploads/2023/11/plausible-analytics-icon-top.png)](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

[Hosting](https://jameskilby.co.uk/category/hosting/) | [Personal](https://jameskilby.co.uk/category/personal/)

### [Analytics in a privacy focused world](https://jameskilby.co.uk/2023/11/analytics-in-a-privacy-focused-world/)

By[James](https://jameskilby.co.uk)November 10, 2023April 16, 2026

I recently helped my friend Dean Lewis @veducate with some hosting issues. As part of the testing of this he kindly gave me a login to his WordPress instance.