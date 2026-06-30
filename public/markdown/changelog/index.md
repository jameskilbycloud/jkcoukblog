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

1009

Git commits

### Repository Age

270

Days active

### Contributors

5

Active contributors

### Last Deployment

2026-06-30

11:03:15

## 🚀 Lighthouse Performance Scores

Last checked: 2026-06-30 07:03:19 UTC

93 

Performance

96 

Accessibility

100 

Best Practices

100 

SEO

## Recent Changes

2026-06-30 1f53652Other

style(search): dark brutalist theme for the search field + results (#114)

The JS-injected search UI still used light-theme inline styles (#fafafa

2026-06-30 a2b6accOther

feat(chrome): JK favicon + real header search button (#113)

Two cosmetic finishes flagged after the logo/footer work.

2026-06-30 241528eOther

chore(lighthouse): record scores P93/A96/BP100/S100

2026-06-30 8b03017Other

feat(chrome): JK monogram logo lockup + relocate footer socials to header (#112)

The footer's Kadence "filled" social icons (X/LinkedIn/GitHub) sat centred

2026-06-30 76eff16Fix

fix(build): deploy brutalist-theme.css by content, not mtime (#111)

CSS-only edits to scripts/brutalist-theme.css could silently fail to ship.

  

2026-06-29 f45154bFix

fix(css): collapse the wasted-space archive hero on tag/category pages (#110)

Kadence styles the archive title band with `min-height:200px` + a centred

2026-06-29 c31d3ebFix

fix(homepage): editorial headline + canonical SEO h1; reliable lighthouse stat (#109)

Follow-ups to the top-band ribbon (#108), after seeing it live.

2026-06-29 066b346Other

feat(homepage): top band → status ribbon (Option B) (#108)

Implements PATCH-top-band-ribbon.md from the JK Blog design project.

2026-06-29 91893f6Other

chore(deps-dev): Bump ruff from 0.15.17 to 0.15.20 (#105)

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.15.17 to 0.15.20.

2026-06-29 987e6ccOther

chore(lighthouse): record scores P94/A96/BP100/S100

2026-06-29 87c2c56Other

chore(lighthouse): record scores P96/A96/BP100/S100

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

Page generated: 2026-06-30 11:07:26 UTC  
Changelog powered by Git history and Lighthouse CI