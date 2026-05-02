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

739

Git commits

### Repository Age

211

Days active

### Contributors

3

Active contributors

### Last Deployment

2026-05-02

09:04:45

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

  

2026-04-16 07ffecdOther

Only install missing system dependencies

Change the workflow to probe for required system binaries and Python modules first, accumulating any missing packages into MISSING_PKGS. If nothing is missing, skip apt entirely; otherwise run apt-get update/install only for the missing items. This avoids unnecessary dpkg lock waits on long-lived self-hosted runners and speeds up the job startup. The script checks jq, bc, avifenc, optipng, jpegoptim, cwebp, python3-pip and python3-venv and still prints versions after installation.

2026-04-16 cbc3ac8Improvement

Update Claude settings and rotate indexnow key

Add new probes to .claude/settings.local.json (Bash(xxd) and WebFetch for www.bing.com) and update the stored IndexNow key in .indexnow_key (key rotated). These changes enable additional local checks and refresh the indexing key without altering other configuration.

2026-04-16 68ff088Feature

Add IndexNow keyLocation and WebFetch entry

Include a keyLocation field in IndexNow submission payload so the API knows where the verification key is hosted (scripts/submit_indexnow.py). Also add WebFetch(domain:www.indexnow.org) to local Claude settings to allow fetching IndexNow resources during analysis (.claude/settings.local.json).

2026-04-16 11b8890Feature

Bump GitHub Action versions and add gh checks

Upgrade action usages across workflows to newer releases (actions/cache -> v5, actions/cache/restore/save -> v5, actions/upload-artifact/download-artifact -> v7, actions/setup-node -> v6, slackapi/slack-github-action -> v3.0.1) to keep CI tooling up-to-date and compatible. Also add Bash patterns for gh run/api to .claude/settings.local.json to include gh CLI checks in local scans.

2026-04-16 5eec354Other

Bump Actions checkout and setup-python versions

Upgrade GitHub Actions used in workflow files: actions/checkout@v4 -> actions/checkout@v5 across all workflows, and actions/setup-python@v4/@v5 -> actions/setup-python@v6 where present. Updated workflows: deploy-static-site.yml, enable-cloudflare-indexing.yml, quality-checks.yml, rollback-site.yml, secret-scan.yml, spell-check-consolidated.yml. No behavioral changes aside from using newer action releases; existing fetch-depth and Python version settings are preserved.

  

2026-04-15 9c50f5bImprovement

Update html_transformer.py

2026-04-15 a9f7afeImprovement

Update validate_deployment.py

2026-04-15 69c1bdbOther

Escape HTML in changelog commit messages

2026-04-15 8218ee2Other

Exclude consolidated-inline-styles from critical CSS

Add 'consolidated-inline-styles' to the EXCLUDED tuple in scripts/extract_critical_css.py to prevent double-counting of inline noscript styles during critical CSS extraction, matching the handling of other excluded assets like 'brutalist-theme' and 'fonts.css'.

2026-04-15 84c366bImprovement

Use single-pass HTML transformer; update CI & Makefile

Add a new scripts/html_transformer.py that performs SEO fixes, image-to-<picture> conversion, performance hints, critical CSS extraction/inlining, head deduplication and HTML minification in a single parse cycle per file. Update .github/workflows/deploy-static-site.yml to wait for dpkg locks during apt operations and to replace the previous multi-step image/SEO/perf/CSS/HTML pipeline with a streamlined CSS optimization step and a single-pass HTML transformer step. Simplify Makefile targets to call the new transformer and to consolidate the CSS pipeline (remove separate critical extraction step). These changes reduce repeated HTML parsing, simplify CI steps, and add robustness to runner package installs.

2026-04-15 56393a0Improvement

Refactor deploy workflow and staging URL handling

Rework the GitHub Actions deploy flow and staging URL conversion:

  

2026-04-14 68d4346Docs

Updated Readme

2026-04-14 8082bdfFeature

Add 'purge all' KV cache support

Replace selective file-based purge with a purge-all workflow step that POSTs /.purge?all=true and requires CACHE_PURGE_TOKEN; step name and GitHub summary fields updated and response count parsed with jq. Update worker handler to support the all=true query: iterate HTML_CACHE.list to delete KV keys and corresponding Cache API entries, return JSON with purged count and timestamp, and improve missing-parameter error and cache request origin handling.

  

2026-04-12 93c5c25Docs

Improve taxonomy name extraction from title

Refine the regex used to extract taxonomy names from page titles. Use a non-greedy match for patterns like "Docker Archives - James Kilby" and add a fallback to the previous pattern when the 'Archives' token isn't present. Also update the comment/example. This prevents incorrect captures for taxonomy names that include hyphens or other characters.

2026-04-12 bdfd455Other

Deduplicate meta descriptions on paginated pages

Add fix_pagination_meta_description to detect /page/N/ URLs and append " - Page N" to meta description, og:description and twitter:description to avoid duplicate SEO content. The method strips trailing periods, truncates content to keep it within ~160 characters (adding ellipses if needed), and logs a brief message per modified page. Also call this new method during page processing so paginated archive pages get unique descriptions.

2026-04-12 0042adfFix

fix: exclude changelog/stats from Brotli reuse loop

These directories are regenerated by post-deploy scripts every build,

Page generated: 2026-05-02 09:28:57 UTC  
Changelog powered by Git history and Lighthouse CI