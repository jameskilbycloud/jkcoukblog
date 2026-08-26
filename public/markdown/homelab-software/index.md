---
title: "Homelab – Software"
description: "HomeLab - Software offers a comprehensive suite of applications for media, AI, security, and more. Optimize your digital environment today."
date: 2023-11-11T21:51:49+00:00
modified: 2026-06-16T20:56:10+00:00
author: James Kilby
tags:
  - See related posts →
url: https://jameskilby.co.uk/homelab-software/
image: https://jameskilby.co.uk/wp-content/uploads/2025/12/ChatGPT-Image-Dec-17-2025-at-09_03_10-PM.png
---

My homelab runs a broad software stack spanning media, AI, monitoring, networking, and self-hosted productivity. Everything below runs as Docker containers unless noted otherwise. For the hardware this runs on, see the [Homelab Hardware page →](https://jameskilby.co.uk/lab/)

This page will continue to grow — config posts and write-ups are linked where they exist.

## Media

  * [Plex](https://www.plex.tv/) — media server for streaming my film, TV, and music library to any device.
  * [Tautulli](https://tautulli.com/) — Plex monitoring and statistics: who’s watching, what, and when.

## AI & Automation

  * [Ollama](https://ollama.com/) — run large language models locally; backed by the Ampere A10 GPU on the Z840.
  * [Open WebUI](https://openwebui.com/) — polished browser-based chat interface for Ollama and other LLM backends.
  * [n8n](https://n8n.io/) — self-hosted workflow automation; connects services without needing to write full code.
  * [SearXNG](https://searxng.github.io/searxng/) — privacy-respecting meta search engine that aggregates results from multiple sources.
  * [DeepStack](https://deepstack.cc/) — self-hosted AI image recognition API used for object detection in camera feeds.

## Networking & Access

  * [Traefik](https://traefik.io/) — reverse proxy and ingress controller that automatically handles routing and TLS for containers.
  * [Cloudflared](https://github.com/cloudflare/cloudflared) — Cloudflare Tunnel daemon providing secure public access to internal services without open firewall ports.
  * [Pi-hole](https://pi-hole.net/) — network-wide DNS-based ad and tracker blocking.
  * [UniFi Controller](https://ui.com/) — management for the Ubiquiti access points and network devices.

## Monitoring & Observability

  * [Grafana](https://grafana.com/) — dashboarding and visualisation platform; the front end for most of my metrics.
  * [Prometheus](https://prometheus.io/) — time-series metrics collection and alerting, feeding Grafana.
  * [Netdata](https://www.netdata.cloud/) — real-time per-host performance monitoring with automatic anomaly detection.
  * [Uptime Kuma](https://github.com/louislam/uptime-kuma) — self-hosted uptime and status monitoring with notifications.
  * [Beszel](https://beszel.dev/) — lightweight server and container resource monitoring with a clean UI.
  * [Homepage](https://gethomepage.dev/) — customisable dashboard that aggregates status and links for all running services.

## Photography & Files

  * [Immich](https://immich.app/) — self-hosted photo and video backup and management; Google Photos replacement.
  * [Nextcloud](https://nextcloud.com/) — self-hosted file sync, sharing, and collaboration platform.
  * [Paperless-ngx](https://docs.paperless-ngx.com/) — document management system with OCR; turns scanned paperwork into a searchable archive.
  * [Hoarder](https://hoarder.app/) — AI-powered bookmarking and read-it-later app. [Read my migration post →](https://jameskilby.co.uk/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way/)

## Home & Life

  * [Home Assistant](https://www.home-assistant.io/) — home automation hub connecting smart devices, automations, and integrations.
  * [Airtrail](https://github.com/johanbook/airtrail) — flight logging and travel history tracker.

## Dev & IT Tools

  * [CyberChef](https://gchq.github.io/CyberChef/) — browser-based tool for encoding, decoding, encryption, and data transformation.
  * [phpIPAM](https://phpipam.net/) — open-source IP address management for tracking subnets and address allocations.
  * [Excalidraw](https://excalidraw.com/) — virtual whiteboard for hand-drawn-style diagrams and architecture sketches.
  * [SemaphoreUI](https://semaphoreui.com/) — modern web UI for Ansible playbook execution and scheduling. [See related posts →](https://jameskilby.co.uk/tag/semaphore/)
  * [VS Code Server](https://github.com/coder/code-server) — browser-based VS Code for editing code from anywhere without a local install.
  * [JDownloader](https://jdownloader.org/) — automated download manager supporting a wide range of file hosting sites.

## Hosting

  * [WordPress](https://wordpress.org/) — powers this site, The authoring site is self-hosted on the lab however live content is served direct from Cloudflare.
  * [Plausible](https://plausible.io/) — privacy-first, cookieless web analytics as an alternative to Google Analytics.

## Storage & Infrastructure

  * [MinIO](https://min.io/) — S3-compatible object storage server; used for application backups and bulk data.