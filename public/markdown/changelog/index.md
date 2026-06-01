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

860

Git commits

### Repository Age

241

Days active

### Contributors

3

Active contributors

### Last Deployment

2026-06-01

12:00:56

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

2026-06-01 6149740Fix

fix(deploy): sweep stale vendored-CDN URLs from cached HTML each build

The WP→static generator is incremental: posts whose source content hasn't

2026-06-01 0828198Fix

fix(search): vendor fuse.js and splide.js, drop jsdelivr dependency

Site search broke because /js/fuse.min.js

  

2026-05-30 d94cbffFix

fix(ci): skip interactive UI tests when chromium fails to launch (#57)

The smoke-test step in deploy-static-site.yml is wrapped in

2026-05-30 60ee29dFix

fix(ci): declare workflow GITHUB_TOKEN permissions for org defaults (#56)

After moving the repo into an organization, GITHUB_TOKEN defaults to

  

2026-05-29 ea56802Fix

fix(seo): strip wordpress.jameskilby.cloud leakage from generated HTML (#55)

Post-#54 audit found three residual references to the private WordPress

2026-05-29 b346016Fix

fix(seo): enrich Person/E-E-A-T schema (sameAs + jobTitle + knowsAbout + award) (#54)

After auditing what Google actually leverages for ranking in 2026:

2026-05-29 92c6a5cFeature

fix(seo): add twitter:site + twitter:creator attribution (#53)

Rank Math's default doesn't include twitter:site or twitter:creator, so

2026-05-29 b83e72eFix

fix(seo): dedupe TechArticle in @graph + inject dates + tighten title cap (#52)

Three follow-ups from the post-#51 SEO audit:

2026-05-29 5be7f93Fix

fix(seo): bake noindex,follow into changelog + stats templates (#51)

Post-PR-#50 verification showed /stats/ still serving `index, follow`

2026-05-29 7d5e77eFix

fix(seo): noindex,follow on thin category/tag/archive pages (#50)

Live audit (post-PR-#49 status check) showed multiple pages in the

2026-05-29 8e56ecaFeature

fix(seo): add If-Modified-Since 304 handling, drop ETag debug (#49)

PR #48's X-ETag-Echo diagnostic confirmed the hypothesis: Cloudflare

2026-05-29 d8e3670Fix

fix(seo): move /feed/ 301 into the worker + diag ETag stripping (#48)

PR #46 added /feed/ -> /feed/index.xml as a 301! rule in _redirects.

2026-05-29 5be4876Fix

fix(seo): wire fix_homepage_title into html_transformer orchestrator (#47)

The previous PR added Config.HOMEPAGE_TITLE + SEOFixer.fix_homepage_title

2026-05-29 d35c0c3Feature

fix(seo): drop /404/ + /feed/ from sitemap, lock homepage title, add ETag/304 (#46)

Audit against the live site surfaced three issues GSC would flag and a few

2026-05-29 8c2ed77Feature

fix(seo): restore truncated meta descriptions + add SEO build validator

Two changes that ship together:

2026-05-29 8edf2fbFix

fix(seo): stop truncating titles with literal '...' + restore broken ones

42 of 72 post pages had their <title> brutally chopped at 57 chars

2026-05-29 14535e9Other

ci: recalibrate Lighthouse thresholds for CI mobile variance

The previous threshold tightening (perf-tighten commit) failed the

2026-05-29 cd67d11Other

ci: tighten Lighthouse budgets + start actually enforcing them

The budget JSONs had a `tolerance` property on every timing entry,

2026-05-29 34a1a34Fix

fix: handle absolute URLs in picture responsive srcset derivation

Lighthouse mobile was flagging UbuntuExpand.avif as wasting 178 KiB

2026-05-29 4eeffcbFix

debug: surface exact paths that picture-repair couldn't find in CI

Last build reported "594 skipped — missing AVIF/WebP variant on disk"

2026-05-29 91615fbFeature

perf: add late-pass picture <source> srcset repair + diagnostics

Lighthouse mobile flagged UbuntuExpand.avif as wasting 178 KiB because

2026-05-29 2d30e3bOther

perf: drop consolidated WP CSS and hide noise overlay on mobile

Two more mobile FCP/LCP wins:

Page generated: 2026-06-01 11:53:22 UTC  
Changelog powered by Git history and Lighthouse CI