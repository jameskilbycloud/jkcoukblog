---
title: "How I Migrated from Pocket to Hoarder with AI Integration"
description: "How I migrated my saved articles from Pocket to Hoarder (now Karakeep), self-hosted it with Docker, and added AI tagging to organise everything."
date: 2025-01-29T23:31:56+00:00
modified: 2026-06-05T18:46:47+00:00
author: James Kilby
categories:
  - Artificial Intelligence
  - Docker
  - Hosting
  - Homelab
  - Ansible
  - Storage
  - vExpert
  - Synology
tags:
  - #AI
  - #Docker
  - #Hoarder
  - #Homelab
  - #Ollama
url: https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/
image: https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.30.47-1024x547.png
---

![](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.30.47.png)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Hosting](https://jameskilby.co.uk/category/hosting/)

# How I Migrated from Pocket to Hoarder with AI Integration

By[James](https://jameskilby.co.uk) January 29, 2025 · Updated June 5, 2026 • 📖5 min read(1,004 words)

📅**Published:** January 29, 2025•**Updated:** June 05, 2026

Update: Hoarder has now been renamed to Karakeep due to a trademark issue

I’ve been on a mission recently to regain control of my data. I haven’t yet faced the humongous task of moving my main email from Gmail, but I have had some successes with other cloud services and a win is a win….

One of them is my bookmark manager. Up until now, I used Pocket since way back in the day when it was originally called “Read it Later”. I wanted to bring it away from a cloud service and host it locally. I also had the opportunity to add a little AI magic to go with it.

## Table of Contents

## What is Hoarder?

Taken from the Hoarder website, it’s an App that can do all of this….

  * 🔗 Bookmark links, take simple notes and store images and pdfs.
  * ⬇️ Automatic fetching for link titles, descriptions and images.
  * 📋 Sort your bookmarks into lists.
  * 🔎 Full text search of all the content stored.
  * ✨ AI-based (aka chatgpt) automatic tagging. With support for local models using Ollama!
  * 🎆 OCR for extracting text from images.
  * 🔖 [Chrome plugin](https://chromewebstore.google.com/detail/hoarder/kgcjekpmcjjogibpjebkhaanilehneje) and [Firefox addon](https://addons.mozilla.org/en-US/firefox/addon/hoarder/) for quick bookmarking.
  * 📱 An [iOS app](https://apps.apple.com/us/app/hoarder-app/id6479258022), and an [Android app](https://play.google.com/store/apps/details?id=app.hoarder.hoardermobile&pcampaignid=web_share).
  * 📰 Auto hoarding from RSS feeds.
  * 🔌 REST API.
  * 🌐 Multi-language support.
  * 🖍️ Mark and store highlights from your hoarded content.
  * 🗄️ Full page archival (using [monolith](https://github.com/Y2Z/monolith)) to protect against link rot. Auto video archiving using [youtube-dl](https://github.com/marado/youtube-dl).
  * ☑️ Bulk actions support.
  * 🔐 SSO support.
  * 🌙 Dark mode support.
  * 💾 Self-hosting first.

The main use for me is having a website and mobile app for saving pages useful to me that I found when I’m usually down a tech rabbit hole. 

## Hoarder Architecture

I have chosen to run this within my home infrastructure and connected it to my existing Ollama [setup ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/) This means that Hoarder can call Ollama for AI text/image clarification using the setup and models I have already created.

The deployment is all within Docker and I have added extracts from my Docker Compose files below.

![Hoarder App](https://jameskilby.co.uk/wp-content/uploads/2025/01/HoarderApp-1024x491.png)

## Hoarder Install

Snippet from my docker-compose.yml
    
    
    Hoarder
      hoarder:
        image: ghcr.io/hoarder-app/hoarder:${HOARDER_VERSION:-release}
        restart: unless-stopped
        networks:
          - traefik
        volumes:
          - ./data:/data
        env_file:
          - .env
        environment:
          MEILI_ADDR: http://meilisearch:7700
          BROWSER_WEB_URL: http://chrome:9222
          DATA_DIR: /data
        labels:
          - "com.example.description=hoarder"
          - "traefik.enable=true"
          - "traefik.http.routers.hoarder.rule=Host(`hoarder.jameskilby.cloud`)"
          - "traefik.http.routers.hoarder.entrypoints=https"
          - "traefik.http.routers.hoarder.tls=true"
          - "traefik.http.routers.hoarder.tls.certresolver=cloudflare"
          - "traefik.http.services.hoarder.loadbalancer.server.port=3000"
    
      chrome:
        image: gcr.io/zenika-hub/alpine-chrome:123
        restart: unless-stopped
        networks:
          - traefik
        command:
          - --no-sandbox
          - --disable-gpu
          - --disable-dev-shm-usage
          - --remote-debugging-address=0.0.0.0
          - --remote-debugging-port=9222
          - --hide-scrollbars
      meilisearch:
        image: getmeili/meilisearch:v1.11.1
        restart: unless-stopped
        networks:
          - traefik
        env_file:
          - .env
        environment:
          MEILI_NO_ANALYTICS: "true"
        volumes:
          - ./meilisearch:/meili_data

📋 Copy

.env snippet file
    
    
    OLLAMA_BASE_URL=http://ollama:11434
    INFERENCE_TEXT_MODEL=llama3.1:8b
    INFERENCE_IMAGE_MODEL=llava
    

📋 Copy

## Export from Pocket

Luckily, Pocket has an export function that will dump all of your saved URL’s and tags into a single file. This can be run by navigating to https://getpocket.com/export when logged in.

## Import to Hoarder

Once you have this file, you can input it straight into Hoarder. This is done by navigating to the user settings section and then selecting import/export.

Hoarder supports several file formats from other tools

![How I Migrated from Pocket to Hoarder with AI Integration Screenshot](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-22.52.45-1024x124.png)

## Hoarder In Action

When the URLs are loaded, Hoarder passes the URL’s into a headless Chrome to gather the data from that page. It then indexes the contents and then passes the contents to Ollama to apply appropriate tags.

### AI Prompt

You can tweak the AI prompt that is sent over to Ollama. In my case I have just used the default as it looked like a good starting point. The prompt is
    
    
    You are a bot in a read-it-later app and your responsibility is to help with automatic tagging.
    Please analyze the text between the sentences "CONTENT START HERE" and "CONTENT END HERE" and suggest relevant tags that describe its key themes, topics, and main ideas. The rules are:
    - Aim for a variety of tags, including broad categories, specific keywords, and potential sub-genres.
    - The tags language must be in english.
    - If it's a famous website you may also include a tag for the website. If the tag is not generic enough, don't include it.
    - The content can include text for cookie consent and privacy policy, ignore those while tagging.
    - Aim for 3-5 tags.
    - If there are no good tags, leave the array empty.
    
    CONTENT START HERE
    
    <CONTENT_HERE>
    
    CONTENT END HERE
    You must respond in JSON with the key "tags" and the value is an array of string tags.

📋 Copy

The process of gathering all the web pages, indexing them and analysing with AI took around an hour with my setup. I believe that Hoarder has some internal throttles to try and avoid tripping anti-bot tools.

You can monitor this process in the admin section. I was also keen to see the stats on my graphics card while this was running so I ran NVTOP on the VM while some AI processing was running.

![How I Migrated from Pocket to Hoarder with AI Integration Screenshot](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.00.23-1024x329.png)

## Finished Result

At the end of the process, I ended up with a little over 750 bookmarks imported and fully indexed and displayed in a very appealing nature.

![How I Migrated from Pocket to Hoarder with AI Integration Screenshot](https://jameskilby.co.uk/wp-content/uploads/2025/01/Screenshot-2025-01-29-at-23.21.32-1024x590.png)

## Post Install Tasks

### Tag Merge

The AI process is mightily impressive but one of the issues that can occur is that it generates similar tags. Hoarder has the ability to allow you to merge them. 

This is done in the cleanups section under your username. In my case it suggested 150 tags that may need merging. At the moment I am glad this has manual oversight as some should definitely be merged like “Motherboard” and “Motherboards” but some are totally different like “NAS” and “NASA”

### Broken Links

I was quite surprised by how many of the links I had were broken links. These were for a few reasons, ranging from company takeovers, to sites being dead. Sadly, in one case the author is no longer with us. In a few cases, the broken link was because the URL I had saved led to a URL shortener that no longer exists. I need to revisit the remaining links in the list and ensure that they point to the end state.

## 📚 Related Posts

  * [My Self-Hosted AI Stack: Infrastructure Deep Dive (Part 2)](https://jameskilby.co.uk/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2/)
  * [My Self-Hosted AI Stack: Architecture Overview (Part 1)](https://jameskilby.co.uk/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive/)
  * [Automating the Deployment of my Homelab AI Infrastructure](https://jameskilby.co.uk/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements/)

## Similar Posts

  * [ ![What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/wp-content/uploads/2020/06/iu-2-768x229.png) ](https://jameskilby.co.uk/2018/03/cloudflare/)

[Hosting](https://jameskilby.co.uk/category/hosting/)

### [What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained](https://jameskilby.co.uk/2018/03/cloudflare/)

By[James](https://jameskilby.co.uk) March 27, 2018 · Updated June 1, 2026

Cloudflare – What is it and why would I care? I have been using Cloudflare for a long time.

  * [ ![Wa](https://jameskilby.co.uk/wp-content/uploads/2025/04/210902461-012e7273-413a-4ec7-be44-e854347f5a21-768x180.png) ](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Warp – The intelligent terminal](https://jameskilby.co.uk/2025/04/warp-the-intelligent-terminal/)

By[James](https://jameskilby.co.uk) April 11, 2025 · Updated June 1, 2026

How Warp is helping me run my homelab. 

  * [ ![Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/wp-content/uploads/2025/07/semaphore-768x768.png) ](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

[Ansible](https://jameskilby.co.uk/category/ansible/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Managing my Homelab with SemaphoreUI](https://jameskilby.co.uk/2025/09/managing-my-homelab-with-semaphoreui/)

By[James](https://jameskilby.co.uk) September 2, 2025 · Updated June 5, 2026

An intro on how I use SemaphoreUI to manage my Homelab

  * [ ![Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/wp-content/uploads/2023/04/intel_optane_ssd_900p_series_aic_-_right_angle_575px.png) ](https://jameskilby.co.uk/2023/04/intel-optane/)

[Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [vExpert](https://jameskilby.co.uk/category/vexpert/)

### [Using Intel Optane NVMe in a VMware Homelab: Setup & Results](https://jameskilby.co.uk/2023/04/intel-optane/)

By[James](https://jameskilby.co.uk) April 17, 2023 · Updated June 1, 2026

I have been a VMware vExpert for many years and it has brought me many benefits over the years.

  * [ ![Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/wp-content/uploads/2024/10/pexels-tara-winstead-8386440-768x512.jpg) ](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

[Artificial Intelligence](https://jameskilby.co.uk/category/artificial-intelligence/) | [Docker](https://jameskilby.co.uk/category/docker/) | [Homelab](https://jameskilby.co.uk/category/homelab/)

### [Self Hosting AI Stack using vSphere, Docker and NVIDIA GPU](https://jameskilby.co.uk/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu/)

By[James](https://jameskilby.co.uk) October 11, 2024 · Updated June 1, 2026

Artificial intelligence is all the rage at the moment, It’s getting included in every product announcement from pretty much every vendor under the sun.

  * [Homelab](https://jameskilby.co.uk/category/homelab/) | [Storage](https://jameskilby.co.uk/category/storage/) | [Synology](https://jameskilby.co.uk/category/synology/)

### [My First Homelab Storage Setup: HP Gen8 & Xpenology](https://jameskilby.co.uk/2018/01/lab-storage/)

By[James](https://jameskilby.co.uk) January 6, 2018 · Updated June 1, 2026

I have been meaning to post around some of the lab setup for a while. Although it changes frequently at present it’s as below.