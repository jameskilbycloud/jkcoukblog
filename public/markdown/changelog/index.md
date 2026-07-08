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

1023

Git commits

### Repository Age

275

Days active

### Contributors

5

Active contributors

### Last Deployment

2026-07-03

08:30:32

## 🚀 Lighthouse Performance Scores

Last checked: 2026-07-03 06:40:06 UTC

92 

Performance

96 

Accessibility

100 

Best Practices

100 

SEO

## Recent Changes

2026-07-03 3597940Fix

perf: fix stale-image reuse, browser cache TTLs, and build waste (#120)

Stale images (audit finding #1):

2026-07-03 3859fc8Other

chore(lighthouse): record scores P92/A96/BP100/S100

2026-07-03 022f7afFix

fix(incremental): stamp watermark at build start in UTC, not build end (#122)

A post edited in WordPress during the 10-40 min build was older than

2026-07-03 b576082Other

chore(deps): Bump actions/cache/restore from 6.0.0 to 6.1.0 (#116)

Bumps [actions/cache/restore](https://github.com/actions/cache) from 6.0.0 to 6.1.0.

2026-07-03 f06c923Other

chore(deps): Bump actions/cache from 6.0.0 to 6.1.0 (#118)

Bumps [actions/cache](https://github.com/actions/cache) from 6.0.0 to 6.1.0.

2026-07-03 6ba12bbOther

chore(deps): Bump pillow from 12.2.0 to 12.3.0 (#119)

Bumps [pillow](https://github.com/python-pillow/Pillow) from 12.2.0 to 12.3.0.

2026-07-03 84a7eceOther

chore(deps): Bump actions/cache/save from 6.0.0 to 6.1.0 (#117)

Bumps [actions/cache/save](https://github.com/actions/cache) from 6.0.0 to 6.1.0.

2026-07-03 84ec0d3Other

perf(critical-css): only inline from async sheets, not inline styles (#115)

The build was warning "Critical CSS over 15000B cap: dropped 198/289 rules

2026-07-03 8e34b25Fix

fix(theme): raise body-text contrast to WCAG AA (#121)

\--gray-light colours all article body copy (.entry-content p,

  

2026-07-02 a4c0ccdOther

chore(lighthouse): record scores P92/A96/BP100/S100

  

2026-07-01 8f4ca80Other

chore(lighthouse): record scores P92/A96/BP100/S100

  

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

Page generated: 2026-07-05 08:14:40 UTC  
Changelog powered by Git history and Lighthouse CI