---
title: "Changelog - James Kilby"
description: "Site improvements, deployments, and performance metrics for James Kilby's technical blog."
author: James Kilby
url: https://jameskilby.co.uk/changelog/
---

[← Back to Home](https://jameskilby.co.uk/)

# 📋 Changelog

Site improvements, deployments, and performance metrics

### Total Deployments

1169

Git commits

### Repository Age

198

Days active

### Contributors

3

Active contributors

### Last Deployment

2026-04-18

19:22:30

## 🚀 Lighthouse Performance Scores

Last checked: Estimated

95 

Performance

95 

Accessibility

100 

Best Practices

100 

SEO

## Recent Changes

2026-04-18 d54fdd3Fix

fix: stamp worker and manifest before brotli compression

Run generate_soft404_artefacts.py and stamp_worker_manifest.py against

2026-04-18 c94b6f0Improvement

Update SEO.md

2026-04-18 251c3aeFeature

Add soft-404 guard and manifest tooling

Introduce a soft-404 protection system to prevent SPA fallbacks from being indexed as real pages. Adds scripts to generate artefacts (scripts/generate_soft404_artefacts.py), stamp the worker with a build-time path manifest (scripts/stamp_worker_manifest.py), and perform a targeted KV purge (scripts/purge_soft404_kv_cache.py). The deploy workflow now runs generation and stamping before publishing the worker. Adds public/path-manifest.json, a minimal public/404.html, and appends idempotent legacy `/slug/ -> /YYYY/MM/slug/` redirects to public/_redirects. _worker.template.js and the staged public/_worker.js are updated to consult the manifest and refuse to serve or cache unknown paths (returning a real 404 with noindex headers). Docs (docs/SEO.md) were updated with rationale and a manual runbook (including a one-shot KV purge) to complete the rollout.

  

2026-04-17 6cbde77Improvement

refactor: remove view counting from Advanced Mode Worker

Analytics are handled by Plausible, so the KV-metadata view counter had no

2026-04-17 d8385c3Docs

docs: rewrite workers/README to match current state

The old README described the html-cache worker and a now-missing

2026-04-17 3273384Fix

fix: use Wrangler v4 kv key syntax for search index upload

Wrangler v4 removed the colon form `kv:key put` in favour of `kv key put`.

2026-04-17 a291f50Fix

fix: bump Node to 20 for Wrangler and correct KV upload success reporting

Wrangler requires Node 20+, so the Node 18 pin caused the KV search index

2026-04-17 6f31482Improvement

Update deploy-static-site.yml

  

2026-04-16 ba60ef5Other

Only install missing system dependencies

Change the workflow to probe for required system binaries and Python modules first, accumulating any missing packages into MISSING_PKGS. If nothing is missing, skip apt entirely; otherwise run apt-get update/install only for the missing items. This avoids unnecessary dpkg lock waits on long-lived self-hosted runners and speeds up the job startup. The script checks jq, bc, avifenc, optipng, jpegoptim, cwebp, python3-pip and python3-venv and still prints versions after installation.

2026-04-16 b4dc9ddImprovement

Update Claude settings and rotate indexnow key

Add new probes to .claude/settings.local.json (Bash(xxd) and WebFetch for www.bing.com) and update the stored IndexNow key in .indexnow_key (key rotated). These changes enable additional local checks and refresh the indexing key without altering other configuration.

2026-04-16 3a9b5caFeature

Add IndexNow keyLocation and WebFetch entry

Include a keyLocation field in IndexNow submission payload so the API knows where the verification key is hosted (scripts/submit_indexnow.py). Also add WebFetch(domain:www.indexnow.org) to local Claude settings to allow fetching IndexNow resources during analysis (.claude/settings.local.json).

2026-04-16 ba1761cOther

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-04-16 35fe94dFeature

Bump GitHub Action versions and add gh checks

Upgrade action usages across workflows to newer releases (actions/cache -> v5, actions/cache/restore/save -> v5, actions/upload-artifact/download-artifact -> v7, actions/setup-node -> v6, slackapi/slack-github-action -> v3.0.1) to keep CI tooling up-to-date and compatible. Also add Bash patterns for gh run/api to .claude/settings.local.json to include gh CLI checks in local scans.

2026-04-16 8c89ec4Other

Bump Actions checkout and setup-python versions

Upgrade GitHub Actions used in workflow files: actions/checkout@v4 -> actions/checkout@v5 across all workflows, and actions/setup-python@v4/@v5 -> actions/setup-python@v6 where present. Updated workflows: deploy-static-site.yml, enable-cloudflare-indexing.yml, quality-checks.yml, rollback-site.yml, secret-scan.yml, spell-check-consolidated.yml. No behavioral changes aside from using newer action releases; existing fetch-depth and Python version settings are preserved.

  

2026-04-15 5ea7e91Other

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-04-15 864fb0dImprovement

Update html_transformer.py

2026-04-15 7e61095Improvement

Update validate_deployment.py

2026-04-15 6b0c3dfOther

Escape HTML in changelog commit messages

2026-04-15 2af65f3Other

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-04-15 9b6dcf3Other

Exclude consolidated-inline-styles from critical CSS

Add 'consolidated-inline-styles' to the EXCLUDED tuple in scripts/extract_critical_css.py to prevent double-counting of inline noscript styles during critical CSS extraction, matching the handling of other excluded assets like 'brutalist-theme' and 'fonts.css'.

2026-04-15 51da4e0Improvement

Use single-pass HTML transformer; update CI & Makefile

Add a new scripts/html_transformer.py that performs SEO fixes, image-to-<picture> conversion, performance hints, critical CSS extraction/inlining, head deduplication and HTML minification in a single parse cycle per file. Update .github/workflows/deploy-static-site.yml to wait for dpkg locks during apt operations and to replace the previous multi-step image/SEO/perf/CSS/HTML pipeline with a streamlined CSS optimization step and a single-pass HTML transformer step. Simplify Makefile targets to call the new transformer and to consolidate the CSS pipeline (remove separate critical extraction step). These changes reduce repeated HTML parsing, simplify CI steps, and add robustness to runner package installs.

2026-04-15 1e365caImprovement

Refactor deploy workflow and staging URL handling

Rework the GitHub Actions deploy flow and staging URL conversion:

  

2026-04-14 a3debdaDocs

Updated Readme

2026-04-14 cf71416Feature

Add 'purge all' KV cache support

Replace selective file-based purge with a purge-all workflow step that POSTs /.purge?all=true and requires CACHE_PURGE_TOKEN; step name and GitHub summary fields updated and response count parsed with jq. Update worker handler to support the all=true query: iterate HTML_CACHE.list to delete KV keys and corresponding Cache API entries, return JSON with purged count and timestamp, and improve missing-parameter error and cache request origin handling.

  

2026-04-12 f405ac7Other

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-04-12 ef66c3eDocs

Improve taxonomy name extraction from title

Refine the regex used to extract taxonomy names from page titles. Use a non-greedy match for patterns like "Docker Archives - James Kilby" and add a fallback to the previous pattern when the 'Archives' token isn't present. Also update the comment/example. This prevents incorrect captures for taxonomy names that include hyphens or other characters.

Page generated: 2026-04-19 11:47:11 UTC  
Changelog powered by Git history and Lighthouse CI