---
title: "Changelog - James Kilby"
description: "Site improvements, deployments, and performance metrics for James Kilby's technical blog. Site improvements, deployments, and performance metrics"
author: James Kilby
url: https://jameskilby.co.uk/changelog/
---

[← Back to Home](https://jameskilby.co.uk/)

# 📋 Changelog

Site improvements, deployments, and performance metrics

[![Quality Checks workflow status](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml)

### Total Deployments

780

Git commits

### Repository Age

235

Days active

### Contributors

3

Active contributors

### Last Deployment

2026-05-26

14:50:14

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

2026-05-26 1846ed9Other

ci: KV-purge now polls for the *pushed* commit, not the trigger commit

Follow-up to #31. The 26-May post-merge deploy still spent 210s in the

2026-05-26 d58a9a9Fix

ci: trim 4.5 min of waste + fix log noise + plausible coverage

Four fixes informed by reviewing the 26-May deploy logs.

2026-05-26 6348006Feature

perf: address GTmetrix HAR audit findings

Performance pass driven by a 26-May HAR audit of jameskilby.co.uk.

2026-05-26 602002bOther

chore: bump slackapi/slack-github-action from v3.0.1 to v3.0.3

Clears the DEP0169 url.parse() deprecation warning emitted from the

  

2026-05-15 2183c69Improvement

Repo Cleanup

  

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

Page generated: 2026-05-26 14:58:27 UTC  
Changelog powered by Git history and Lighthouse CI