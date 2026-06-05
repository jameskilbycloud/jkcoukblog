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

918

Git commits

### Repository Age

244

Days active

### Contributors

3

Active contributors

### Last Deployment

2026-06-04

21:45:36

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

2026-06-04 2fd0f8bFix

fix(seo): bundle small audit items — homepage h1, /llms*.txt cache, AI crawler doc (#68)

Closes three audit items in one PR to keep the deploy queue short.

2026-06-04 e3087d4Improvement

refactor(headers): make repo-root _headers the single source of truth (#67)

Until now `_headers` lived in two places that could drift:

2026-06-04 9b261adFeature

fix(generator): add /2* rule to public/_headers for pretty-URL post cache-control (#66)

Real fix for audit action M2. The repo-root `_headers` file edited in

2026-06-04 879a693Fix

fix(headers): set max-age=300 on pretty-URL post pages (#65)

The previous attempt (PR #64) edited _worker.template.js but the worker

2026-06-04 cd9579fFix

fix(worker): apply smart-TTL Cache-Control to all HTML, including pretty-URLs (#64)

Posts at pretty permalinks like /2017/05/foo/ were returning

2026-06-04 dc5d1bbFix

fix(seo): align Person.sameAs and Organization.sameAs to a single canonical list (#63)

Person and Organization currently emit mismatched sameAs lists — Person

  

2026-06-03 a3723b0Other

feat(seo): generate /llms.txt and /llms-full.txt for AI crawlers (#62)

Adds an llmstxt.org-format index of site content for LLM ingestion.

2026-06-03 957318bFix

fix(seo): drop " - James Kilby" suffix from <title> on long posts (#61)

Google truncates the <title> tag in mobile SERPs around 55–60 chars.

2026-06-03 b74bf99Fix

Merge pull request #60 from jameskilbycloud/fix/og-meta-alignment-and-breadcrumb-dedupe

fix(seo): align og/twitter meta with canonical; dedupe BreadcrumbList

2026-06-03 7fdc093Fix

fix(seo): align og/twitter meta with canonical title+description; dedupe BreadcrumbList JSON-LD

Rank Math emits LLM-generated marketing copy in og:title/og:description

2026-06-03 249482bFix

feat(alt-patches): tooling for WP media alt-text fixes + About Me entry

The image-alt issue from the v2 audit (~25 pages with filename-shaped

2026-06-03 4214d5dFix

chore(docs): sync typo-patches docs to current state; fix static-pages list

\- Regenerate typo-patches.md from the current typo-patches.json so the

2026-06-03 ed86a3eOther

feat(worker): 301 /about-me/ → /about-james-kilby-solution-architect/

The About Me page slug was renamed in WordPress (Rank Math /

  

2026-06-02 da6a7cdFix

fix(homepage hero): remove the <li> wrapper, not just the <article>

Kadence wraps each archive card in <li class="entry-list-item">. The hero

2026-06-02 fa3e6d2Feature

ci(deploy): add Force Full Deploy workflow that purges GH Actions caches

Adds .github/workflows/force-full-deploy.yml. Manual-trigger workflow that

2026-06-02 958e7ccFeature

feat(homepage): featured hero, drop archive byline + modified date

Three changes from design_handoff_homepage_refresh (Jun 2026, DirectionA mock):

2026-06-02 5e5cae1Fix

fix(byline): separator + 'Updated' label between published and modified dates

WordPress + Kadence renders entry-meta as two adjacent <time> elements with

  

2026-06-01 5058ce5Fix

fix(typo-patches): narrow about-me grammar find to skip <a>vExpert</a> link

First apply attempt failed because the original find string

2026-06-01 1f792f7Fix

fix(typo-patches): re-route /about-me/ → /about-james-kilby-solution-architect/

The About Me page slug was renamed in WP to about-james-kilby-solution-architect

2026-06-01 7163f34Feature

fix(apply-typo-patches): add --debug + status-list fallback in link-match

Live-site verification showed 16 recent posts (2024/12 onwards) couldn't be

2026-06-01 fbfea95Fix

fix(apply-typo-patches): link-match fallback for slug-override pages

First real apply pass landed 5 of 6 patches on /lab/ — good — but /about-me/

2026-06-01 7f3ab89Fix

fix(apply-typo-patches): bridge wptexturize gap + slug fallbacks

The first dry-run revealed 146 of 148 skips were "find string not in raw

2026-06-01 91c4542Fix

fix(apply-typo-patches): pip --user --break-system-packages (no venv)

The runner's Python 3.14 has ensurepip/venv stripped (Debian's

2026-06-01 5056709Fix

fix(apply-typo-patches): install deps into a venv (PEP 668)

Previous fix used `pip install --user` on the system python3, but the

2026-06-01 bd61cdcFix

fix(apply-typo-patches): use system python3 + opt into Node.js 24

The self-hosted runner is on Ubuntu 26.04 and actions/setup-python@v6 has no

2026-06-01 58d939aFix

chore(audit): site audit reports + WordPress typo-patch tooling

\- Two site-audit reports in repo root: v1 (WebFetch-based, contains false

Page generated: 2026-06-04 20:51:09 UTC  
Changelog powered by Git history and Lighthouse CI