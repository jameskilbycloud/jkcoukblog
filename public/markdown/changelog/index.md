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

988

Git commits

### Repository Age

269

Days active

### Contributors

5

Active contributors

### Last Deployment

2026-06-29

15:46:05

## 🚀 Lighthouse Performance Scores

Last checked: 2026-06-29 14:40:45 UTC

94 

Performance

96 

Accessibility

100 

Best Practices

100 

SEO

## Recent Changes

2026-06-29 5684aaaOther

chore(lighthouse): record scores P94/A96/BP100/S100

2026-06-29 d21dc70Fix

fix(stats): wire real Lighthouse scores into changelog/stats history (#107)

The /stats/ and /changelog/ Lighthouse sections were showing hardcoded

2026-06-29 c017314Other

chore(deps): Bump actions/checkout from 6 to 7 (#104)

Bumps [actions/checkout](https://github.com/actions/checkout) from 6 to 7.

2026-06-29 0d0edd4Other

chore(deps): Bump actions/cache from 5.0.5 to 6.0.0 (#103)

Bumps [actions/cache](https://github.com/actions/cache) from 5.0.5 to 6.0.0.

2026-06-29 36ab35aOther

chore(deps-dev): Bump pytest from 9.1.0 to 9.1.1 (#106)

Bumps [pytest](https://github.com/pytest-dev/pytest) from 9.1.0 to 9.1.1.

  

2026-06-18 c5d5cd3Feature

fix(seo): wire 3 dead SEOFixer passes into the pipeline + add sync-guard test (#102)

The deploy pipeline runs html_transformer.py, whose _apply_seo_fixes() is a

2026-06-18 b265965Fix

fix(seo): wire fix_jsonld_headline_brand_suffix into the html_transformer orchestrator (#101)

PR #99 added fix_jsonld_headline_brand_suffix to SEOFixer and registered it in

  

2026-06-17 4d6eed5Other

chore(ci): run force-full-deploy weekly to backfill back-catalogue schema (#100)

Incremental builds skip unchanged posts, so generator-stage-only SEO/schema

2026-06-17 fbc122eFix

fix(seo): dead wp-json links, JSON-LD headline, twitter:image:alt, canonical validation (#99)

* fix(seo): trustworthy sitemap lastmod, drop dead SearchAction, sort RSS, harden validator

2026-06-17 a5a43d1Fix

fix(seo): trustworthy sitemap lastmod, drop dead SearchAction, sort RSS, harden validator (#98)

Five SEO fixes surfaced by the content/code review.

2026-06-17 163a69bFix

fix(ci): pin actions to commit SHAs and gate redundant pip installs (#97)

#2 Supply-chain hardening: pin every action in the deploy workflow to a full

2026-06-17 1aaa68eOther

chore(deps-dev): Bump ruff from 0.15.16 to 0.15.17 (#94)

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.16 to 0.15.17.

2026-06-17 ac36887Fix

fix(ci): correct compression ordering, drop dead Google ping, prune redundant cache (#96)

Four fixes to the WordPress→static deploy workflow:

2026-06-17 b65b302Other

chore(deps-dev): Bump pytest from 9.0.3 to 9.1.0 (#95)

Bumps [pytest](https://github.com/pytest-dev/pytest) from 9.0.3 to 9.1.0.

2026-06-17 614e44dOther

chore(deps): Bump treosh/lighthouse-ci-action from 11 to 12 (#93)

Bumps [treosh/lighthouse-ci-action](https://github.com/treosh/lighthouse-ci-action) from 11 to 12.

  

2026-06-16 122445eOther

feat(seo): CrUX field metrics, drift baseline, JSON-LD entity enrichment (H3/M4/M1/L3) (#92)

* feat(seo): link article author to Person @id + topic about/mentions entities

2026-06-16 aa7f754Feature

Add Style Guide and checlist

2026-06-16 e6d8d47Other

feat: auto-inject FAQPage JSON-LD for posts with FAQ sections (#91)

Implements the "Add FAQ schema markup" item from the SEO checklist

  

2026-06-15 47bbb77Removal

chore: remove dead workflow and trigger cruft (#90)

* fix(seo): noindex markdown/JSON mirrors to stop crawl-budget waste

  

2026-06-14 a760ed2Fix

fix(seo): noindex markdown/JSON mirrors to stop crawl-budget waste (#89)

Google Search Console flagged ~80 /markdown/*.md mirror files under

  

2026-06-10 7c002deFix

feat: review round 3 — docs sync, session migration, stamp validation, picture query fix, more tests, hygiene (#88)

1\. Docs/Makefile: CLAUDE.md no longer claims there is no pytest suite;

2026-06-10 4d666baFix

feat: shared WP session module, exception logging, worker cache fixes, pytest+ruff CI (#87)

Fix 7 — shared module + config enforcement:

2026-06-10 c2f365eOther

chore(deps): Bump html2text from 2020.1.16 to 2025.4.15 (#82)

Bumps [html2text](https://github.com/Alir3z4/html2text) from 2020.1.16 to 2025.4.15.

2026-06-10 2cb7035Other

chore(deps): Bump gitleaks/gitleaks-action from 2 to 3 (#79)

Bumps [gitleaks/gitleaks-action](https://github.com/gitleaks/gitleaks-action) from 2 to 3.

2026-06-10 a3bd318Other

chore(deps): Bump actions/upload-artifact from 4 to 7 (#81)

Bumps [actions/upload-artifact](https://github.com/actions/upload-artifact) from 4 to 7.

2026-06-10 9928939Other

chore(deps): Bump actions/download-artifact from 7 to 8 (#83)

Bumps [actions/download-artifact](https://github.com/actions/download-artifact) from 7 to 8.

2026-06-10 d2249d8Other

chore(deps): Bump actions/github-script from 7 to 9 (#84)

Bumps [actions/github-script](https://github.com/actions/github-script) from 7 to 9.

2026-06-10 de845c0Other

chore(deps): Bump actions/checkout from 5 to 6 (#78)

Bumps [actions/checkout](https://github.com/actions/checkout) from 5 to 6.

2026-06-10 2c6cc8bOther

chore(deps): Bump pyyaml from 6.0.1 to 6.0.3 (#80)

Bumps [pyyaml](https://github.com/yaml/pyyaml) from 6.0.1 to 6.0.3.

2026-06-10 94ad7d9Fix

fix: surface non-blocking CI failures, thread-safe caches, config-aware cache invalidation (#85)

\- deploy-static-site.yml: give all 13 continue-on-error steps ids and add a

Page generated: 2026-06-29 16:28:04 UTC  
Changelog powered by Git history and Lighthouse CI