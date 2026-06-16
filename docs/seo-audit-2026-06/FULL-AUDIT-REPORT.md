# Full SEO Audit — jameskilby.co.uk

**Audit date:** 2026-06-03
**Crawler:** claude-seo full audit (inline subagent execution)
**Sample size:** 78 sitemap URLs (homepage + 72 posts + 5 static pages) — 100% of indexable URLs were inspected for meta-tag checks; static pages were skipped from the bulk meta sweep.

---

## Executive Summary

### SEO Health Score: **74 / 100**

| Category | Weight | Score | Weighted |
|---|---|---|---|
| Technical SEO | 22% | 92 | 20.2 |
| Content Quality (meta/OG consistency) | 23% | 55 | 12.7 |
| On-Page SEO | 20% | 78 | 15.6 |
| Schema / Structured Data | 10% | 88 | 8.8 |
| Performance (CWV) | 10% | 75¹ | 7.5 |
| AI Search Readiness | 10% | 50 | 5.0 |
| Images | 5% | 90 | 4.5 |
| **Total** | **100%** | | **74.3** |

¹ Lab CWV not measured this run — PageSpeed Insights API quota exhausted. Score is an estimate derived from header inspection (Brotli + HTTP/3 + critical-CSS inlining + AVIF/WebP all present, all of which are known LCP/CLS positives). Validate with a fresh PSI run or CrUX field data before acting on this number.

### Business type detected
- **Single-author technical blog** — VMware, homelab, cloud infrastructure
- Author: James Kilby (vExpert)
- Schema correctly models the site as a `Blog` / `Person` / `Organization` triplet, not a Local Service business → local-SEO checks correctly skipped.

### Top 5 critical findings

1. **OG description mismatches meta description on 44 / 72 posts (61%).** The OG description appears to be AI-generated marketing copy ("Unlock smart banking strategies to save more now!"), while the meta description is the actual opening sentence of the article. Social shares (LinkedIn, X, Slack, Discord) will surface clickbait that doesn't match the post.
2. **OG title mismatches `<title>` on 13 / 72 posts (18%).** Same pattern — `<title>` is the SEO-optimised version; `og:title` is unrelated marketing copy. Hurts brand consistency and click-through from social.
3. **`<title>` > 70 chars on 32 / 72 posts (44%).** Google truncates around 50–60 chars on mobile. The trailing `" - James Kilby"` suffix is the main offender; for already-long descriptive titles, the brand suffix should be dropped.
4. **`llms.txt` and `llms-full.txt` are 404.** No declared AI ingestion policy and no curated index for LLM crawlers. With GPTBot/ChatGPT-User/PerplexityBot all currently allowed, you are getting AI ingestion but not steering it.
5. **Duplicate `BreadcrumbList` JSON-LD on at least one sample post.** Two separate `<script type="application/ld+json">` blocks both include a `BreadcrumbList`. Schema.org allows multiple graphs but duplicate BreadcrumbList is a known cause of "Breadcrumbs item not specified" warnings in Search Console. Worth verifying across the corpus.

### Top 5 quick wins

1. **Replace `og:title` and `og:description` with `<title>` / `meta[name=description]`** by default. The custom AI copy isn't adding value over the SEO-tuned text. ~1 hour of script work; fixes 57 mismatches in a single deploy.
2. **Drop `" - James Kilby"` suffix from `<title>` when title body > 55 chars.** Adjust in `fix_seo_issues.py` / `html_transformer.py`. ~30 min; fixes 32 truncated titles.
3. **Add `/llms.txt`.** A 30-line file at site root listing your top pages and citation preferences. Generate as a build-pipeline step alongside the sitemap.
4. **De-duplicate `BreadcrumbList` JSON-LD.** Pick one block (the per-page generator), strip the other.
5. **Run PSI / CrUX for real CWV.** Quota was hit on this audit; the `claude-seo:seo-google` skill can pull authoritative field data once Search Console / CrUX credentials are wired up.

---

## Technical SEO — 92/100

### Headers and transport

| Item | Status |
|---|---|
| HTTPS (TLS) | ✓ |
| HSTS preload-ready (`max-age=63072000; includeSubDomains; preload`) | ✓ |
| HTTP/2 + HTTP/3 (alt-svc) | ✓ |
| Brotli content-encoding (verified on a post page) | ✓ |
| `Content-Security-Policy` with explicit allow-list for Utterances / Plausible / Credly / Cloudflare Insights | ✓ |
| `Permissions-Policy` zero-trust defaults (geolocation, microphone, camera, payment, USB) | ✓ |
| `Referrer-Policy: strict-origin-when-cross-origin` | ✓ |
| `X-Content-Type-Options: nosniff` | ✓ |
| `X-Frame-Options: SAMEORIGIN` | ✓ |
| `report-to` / `NEL` configured | ✓ |
| `cache-control` on homepage: `max-age=300, must-revalidate` (aligns with worker's 5-min TTL for `/`) | ✓ |
| `cache-control` on post: `max-age=0, must-revalidate` | ⚠ Browser-side caching disabled — relies entirely on edge cache + KV. Worth confirming this is intentional vs. an unintended consequence of the worker; setting `max-age=60`+ would let modern browsers benefit from soft-cache on revisits. |

### robots.txt

- Allow-all for crawl, `Disallow: /*/feed/` and `Disallow: /api/` — both correct (feed redirects collapse to the canonical `index.xml`; `/api/` is non-indexable JSON).
- Sitemap correctly declared.
- No GPTBot / ClaudeBot / PerplexityBot block — intentional given the GEO strategy (see AI Search Readiness below), but worth deciding *deliberately*, not by default.

### Sitemap

| Item | Status |
|---|---|
| Total URLs | 78 (1 homepage + 72 posts + 5 static pages) |
| Category / tag / author / paged archives | Correctly excluded |
| Image extensions (`image:image`) | ✓ Present where applicable, with descriptive `image:title` and `image:caption` |
| `lastmod` on every URL | ✓ |
| `priority` weighted (1.0 home, 0.7 posts) | ✓ |

### Other endpoints

| Endpoint | Status |
|---|---|
| `/robots.txt` | 200 ✓ |
| `/sitemap.xml` | 200 ✓ |
| `/feed/` → `/feed/index.xml` | 301 ✓ |
| `/feed/index.xml` | 200 ✓ |
| `/.well-known/security.txt` | 200 ✓ (contact, expiry 2027-06, en, canonical declared) |
| `/llms.txt` | **404** |
| `/llms-full.txt` | **404** |
| `/humans.txt` | 404 (minor; optional) |

---

## Content & Meta Quality — 55/100

This is the category dragging the score down.

### Title tags

- 32 / 72 posts (44%) have `<title>` > 70 chars
- The `" - James Kilby"` suffix is the consistent overflow trigger
- Worst offenders go up to 80 chars
- All other title-related checks pass: no duplicate titles within the sitemap sample, no missing titles, no `<title>` shorter than 30 chars

### Meta descriptions

- 0 too short (<70), 0 too long (>160) — length policy is well-enforced
- BUT the description content frequently has no relationship to the actual post topic on older posts (see "OG description mismatch" below — same root cause)

### Open Graph / Twitter Card consistency

| Issue | Affected | Notes |
|---|---|---|
| `og:title` vs `<title>` divergence (<35% word overlap) | 13 / 72 (18%) | `og:title` looks like LLM-generated marketing copy |
| `og:description` vs `meta[name=description]` divergence (<30% word overlap) | **44 / 72 (61%)** | Same root cause — `og:description` is AI marketing copy, `meta description` is the real article opener |
| `twitter:card` present | 72 / 72 ✓ | |
| `og:image` present | 72 / 72 ✓ | All point to `/wp-content/uploads/og/<slug>.png`, sized 1200×630 |
| Homepage OG image renders (32985 bytes, image/png) | ✓ | |

**Examples of mismatch:**

| URL | `<title>` (SEO) | `og:title` (clickbait) |
|---|---|---|
| `/2017/05/money-saving-uk-version/` | "UK Money Saving Tips: Banking, Rewards & Travel Cards" | "Maximize Your Savings with UK Banking Tips" |
| `/2018/03/cloudflare/` | "What Is Cloudflare? Free CDN, WAF & DDoS Protection Explained" | "Boost Your Site with Cloudflare" |
| `/2024/09/can-you-really-squeeze-96tb-in-1u/` | "Can you really squeeze 96TB in 1U ?" | "Unlock 96TB in a 1U Server" |
| `/2025/04/warp-the-intelligent-terminal/` | "Warp – The intelligent terminal" | "Elevate Your Homelab with Warp Terminal" |

The SEO titles are *good*; the OG titles dilute them.

### Author / E-E-A-T signals

- Strong: `Person` schema declares `jobTitle: "Cloud / Infrastructure Architect"`, `award: "VMware vExpert"`, `knowsAbout: [VMware vSphere, VMware Cloud on AWS, Homelab Infrastructure, Cloudflare, AWS, Ansible, Kubernetes, Storage, Self-hosted AI, Network Automation]`, `sameAs: [github, x]`
- Author byline confirmed in RSS (`<author>James</author>`)
- An `/about-james-kilby-solution-architect/` page exists in sitemap
- Could be strengthened: add `LinkedIn` to `Person.sameAs` (it's only in `Organization.sameAs` currently — both should match)

---

## On-Page SEO — 78/100

| Item | Status |
|---|---|
| Homepage `<title>` (62 chars) | ✓ |
| Homepage `<meta description>` (150 chars) | ✓ |
| Homepage single `<h1>` ("James Kilby") | ⚠ Minimal — could be more descriptive given the site is content-heavy. Consider "James Kilby — VMware, Homelab & Cloud Infrastructure Notes" or similar |
| Single `<h1>` per post page | ✓ (sampled, all clean) |
| Internal linking (homepage = 119 internal vs 3 external) | ✓ Healthy ratio |
| Canonical present on every post sampled | ✓ |
| Canonical missing on category/tag archives | ⚠ Acceptable because they are `noindex,follow` — not a real issue |
| HTML `lang="en-GB"` | ✓ |
| Viewport meta | ✓ |
| Hreflang | N/A (single-locale site) |

---

## Schema & Structured Data — 88/100

### Homepage `@graph`
- `Person` (James Kilby, vExpert, jobTitle, knowsAbout array of 10 expertise areas, sameAs github+x)
- `WebSite` with `SearchAction` potentialAction → enables SERP search box
- `CollectionPage` for the homepage
- `Organization` with logo and sameAs github+linkedin

### Post pages `@graph` (sampled)
- `WebPage`, `TechArticle`, `BreadcrumbList`, `Person`, `Organization`, `ImageObject` (multiple)
- Plus a *second* `<script type="application/ld+json">` block also containing a `BreadcrumbList` — **duplicate**, see Action Plan
- `TechArticle` is the correct sub-type for technical tutorials (better than generic `Article` or `BlogPosting`)

### Gaps
- No `FAQPage` schema on posts that have Q&A-style sub-headings — Google deprecated rich-result eligibility for most sites in mid-2023 but it still helps AI Overviews citation
- No `HowTo` schema on step-by-step guides (e.g., the VCF 9 offline depot, vSphere power-management, AI-stack posts) — same caveat re: rich results, but useful for AI extraction
- `Organization.sameAs` and `Person.sameAs` should be aligned (currently inconsistent — `Person` has github+x, `Organization` has github+linkedin)

---

## Performance / Core Web Vitals — 75/100 (estimate)

Lab data not collected this run — PageSpeed Insights API daily quota was exhausted.

What is verifiable from headers and HTML:

| Signal | Status | LCP/INP/CLS impact |
|---|---|---|
| Brotli (q11) pre-compression | ✓ | Smaller transfer → faster LCP |
| HTTP/3 (alt-svc) | ✓ | Faster handshake → faster TTFB / FCP |
| Critical CSS inlined in `<head>` | ✓ | Eliminates render-blocking → faster FCP/LCP |
| Font preload (`as="font" crossorigin`) for Space Grotesk + Anton | ✓ | Removes FOIT/FOUT → CLS positive |
| AVIF + WebP sources via `<picture>` (11 picture / 12 AVIF / 11 WebP on homepage) | ✓ | Smaller LCP image candidate |
| `fetchpriority` / lazy-loading (per CLAUDE.md pipeline) | ✓ (configured) | LCP + bandwidth |
| Worker-driven KV HTML cache (5min home / 15min recent / 1h older) | ✓ | TTFB |

**Action:** Re-run PSI tomorrow (quota resets daily) or wire `seo-google` with GSC + CrUX credentials to get authoritative field data.

---

## AI Search Readiness (GEO) — 50/100

### Strengths
- Markdown export and JSON API (`/markdown/`, `/api/`) already exposed via the worker — high citability format for LLM crawlers
- Rich `Person`/`Organization` schema gives AI engines strong author-attribution signals
- Clean semantic HTML with proper headings, AVIF imagery, and descriptive alt text helps passage extraction
- GPTBot / ChatGPT-User / PerplexityBot all currently *allowed* in robots.txt (no Disallow)

### Gaps
- **No `/llms.txt`** — the emerging Anthropic-proposed standard for declaring site-level LLM ingestion policy and curated content index. With your `/markdown/` mirror already built, `/llms.txt` could be auto-generated in <50 lines as a pipeline step
- **No `/llms-full.txt`** — the fuller variant containing full content of your highest-priority pages, for direct LLM ingestion
- **No author byline schema on posts** (`Person` is referenced at the site level, but post pages don't explicitly link the article to the author via `author: { @id: "#person" }`)
- **No `Article.about` / `Article.mentions`** for explicit topic tagging beyond `knowsAbout`

### AI crawler accessibility
- `GPTBot` allowed: ✓ (no robots block)
- `ChatGPT-User` allowed: ✓
- `PerplexityBot`: not explicitly checked, but no block in robots.txt
- `ClaudeBot`: not explicitly checked, but no block in robots.txt

---

## Images — 90/100

- All 12 `<img>` tags on the homepage have alt text ✓
- `<picture>` with AVIF + WebP fallbacks on all content images ✓
- Image extensions in sitemap with descriptive `image:title`/`image:caption` ✓
- Per-post OG images at 1200×630 — correctly sized ✓
- No oversized images flagged in this audit (file-size deep dive not in scope without PSI quota)

Remaining concerns: none identified at the markup level. A file-size sweep (`scripts/optimize_images.py --report-only` if such a flag existed) could surface oversized originals.

---

## What was NOT audited this run

| Skill | Why skipped |
|---|---|
| `seo-google` (CrUX, GSC, GA4 field data) | No API credentials configured in this environment |
| `seo-backlinks` | No Moz / Bing Webmaster credentials; Common Crawl deferred |
| `seo-dataforseo` | DataForSEO MCP extension not detected |
| `seo-maps`, `seo-local` | Not a local business — correctly skipped per business-type detection |
| `seo-ecommerce` | Not an e-commerce site — correctly skipped |
| `seo-drift` | No baseline file present at `python scripts/drift_history.py <url>` — recommend creating one as part of the post-fix verification |
| `seo-cluster` | Skipped — would require keyword corpus the audit doesn't yet have |
| Lab PageSpeed run | Quota exhausted (retry tomorrow) |
| Playwright screenshots | Not run this audit |

See `ACTION-PLAN.md` for the prioritised fix list.
