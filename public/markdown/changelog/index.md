---
title: "Changelog - James Kilby"
description: "Site improvements, deployments, and performance metrics for James Kilby's technical blog."
author: James Kilby
url: https://jameskilby.co.uk/changelog/
---

[← Back to Home](https://jameskilby.co.uk/)

# 📋 Changelog

Site improvements, deployments, and performance metrics

[ ![Quality Checks workflow status](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml/badge.svg) ](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml)

### Total Deployments

763

Git commits

### Repository Age

217

Days active

### Contributors

3

Active contributors

### Last Deployment

2026-05-08

09:21:49

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

2026-05-08 3072236Feature

Update Generate to add quality checks

2026-05-08 c658884Improvement

Update Quality Checks

2026-05-08 dab649fOther

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-05-08 9dcfce7Improvement

update quality check URL

  

2026-05-06 50f9025Other

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-05-06 e856596Other

Tweaked the cache mechanisms

2026-05-06 93ff447Improvement

Theme Updates

2026-05-06 3f49588Other

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-05-06 02279bbOther

Tidy Up

2026-05-06 d510762Improvement

Update wp_to_static_generator.py

2026-05-06 a3c67dcImprovement

Update Validation

2026-05-06 ccbf4a6Other

Theme Tweak

  

2026-05-02 b18967fOther

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-05-02 b123552Improvement

update CSP

2026-05-02 9990e9aFeature

ADD Google Ping

2026-05-02 509c002Fix

Fix IndexNow submission

2026-05-02 46b7ff8Other

Merge branch 'main' of https://github.com/jameskilbynet/jkcoukblog

2026-05-02 b38b2afImprovement

Update Robots

2026-05-02 8635d80Fix

fix: source-level SEO fixes in generator and post-processor

wp_to_static_generator.py:

2026-05-02 5732865Fix

fix: SEO pipeline — og:site_name, stylesheet artefact, category indexing, crawl budget

scripts/fix_seo_issues.py (pipeline post-processor):

  

2026-04-30 f046ae2Fix

fix: skip post-validation paths in HTML link checker

/changelog/ and /stats/ are generated after validate_html.py runs,

2026-04-30 042a943Removal

chore: restore build artifacts after history rewrite; remove dead code

History rewritten with git filter-repo to strip public/ and

  

2026-04-18 eb86271Fix

fix: stamp worker and manifest before brotli compression

Run generate_soft404_artefacts.py and stamp_worker_manifest.py against

2026-04-18 aec8d46Improvement

Update SEO.md

2026-04-18 cc2f575Feature

Add soft-404 guard and manifest tooling

Introduce a soft-404 protection system to prevent SPA fallbacks from being indexed as real pages. Adds scripts to generate artefacts (scripts/generate_soft404_artefacts.py), stamp the worker with a build-time path manifest (scripts/stamp_worker_manifest.py), and perform a targeted KV purge (scripts/purge_soft404_kv_cache.py). The deploy workflow now runs generation and stamping before publishing the worker. Adds public/path-manifest.json, a minimal public/404.html, and appends idempotent legacy `/slug/ -> /YYYY/MM/slug/` redirects to public/_redirects. _worker.template.js and the staged public/_worker.js are updated to consult the manifest and refuse to serve or cache unknown paths (returning a real 404 with noindex headers). Docs (docs/SEO.md) were updated with rationale and a manual runbook (including a one-shot KV purge) to complete the rollout.

  

2026-04-17 7905391Improvement

refactor: remove view counting from Advanced Mode Worker

Analytics are handled by Plausible, so the KV-metadata view counter had no

2026-04-17 98e9e4aDocs

docs: rewrite workers/README to match current state

The old README described the html-cache worker and a now-missing

2026-04-17 9f24734Fix

fix: use Wrangler v4 kv key syntax for search index upload

Wrangler v4 removed the colon form `kv:key put` in favour of `kv key put`.

2026-04-17 563dff0Fix

fix: bump Node to 20 for Wrangler and correct KV upload success reporting

Wrangler requires Node 20+, so the Node 18 pin caused the KV search index

2026-04-17 406245aImprovement

Update deploy-static-site.yml

Page generated: 2026-05-08 08:23:13 UTC  
Changelog powered by Git history and Lighthouse CI