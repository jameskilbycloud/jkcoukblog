# WordPress to Static Site Automation

🚀 **Automated WordPress to Static Site Generator** with AI spell-checking, SEO optimisations, Brotli+Gzip compression, AVIF/WebP image conversion, and Cloudflare Pages deployment via GitHub Actions.

📚 **[Complete Documentation Hub →](docs/README.md)**

## 🎯 Overview

This repository contains a complete automation pipeline that:

- ✅ **Connects to WordPress CMS** via REST API (supports Cloudflare Access protected sites)
- ✅ **Generates a static site** with all content, assets, and metadata — **incrementally** (only posts modified since last build are re-fetched)
- ✅ **Applies AI spell-checking** via Ollama (non-blocking, incremental)
- ✅ **Optimises images** to AVIF/WebP with `<picture>` elements and intelligent caching
- ✅ **Transforms HTML in a single pass** — SEO fixes, `<picture>` conversion, performance hints, critical CSS inlining, and minification in one parse cycle per file
- ✅ **Compresses assets** with Brotli (primary) + Gzip (fallback), pre-encoded at build time
- ✅ **Generates extras** — per-post Open Graph images, `llms.txt`, Markdown export + JSON API, subsetted heading font
- ✅ **Validates content** — SEO, accessibility, JSON-LD, og:image, security headers, plus Playwright UI smoke tests
- ✅ **Deploys to Cloudflare Pages** via git commit, with KV HTML cache purge after deploy
- ✅ **Submits to IndexNow** (and pings Google on new posts) so crawlers see fresh content immediately

## 🏗️ Architecture

```
WordPress CMS (Private)  →  Static Site Generator  →  GitHub Repository  →  Cloudflare Pages (Public)
wordpress.jameskilby.cloud  |                         |                      jameskilby.co.uk
(Behind Cloudflare Access)  |                         |                      (Public Static Site)
                             |                         |
                        Self-Hosted Runner        Auto-Deploy
                        (has CF Access token)     + Advanced Mode Worker (_worker.js)
                                                  + KV HTML Cache
```

## 📁 Repository Structure

```
├── .github/
│   ├── workflows/
│   │   ├── deploy-static-site.yml         # Main build + deploy pipeline
│   │   ├── force-full-deploy.yml          # Full (non-incremental) rebuild trigger
│   │   ├── quality-checks.yml             # Lighthouse + live site formatting tests (daily)
│   │   ├── lighthouse-pr.yml              # Lighthouse audit on pull requests
│   │   ├── spell-check-consolidated.yml   # AI spell checking (Ollama/Llama)
│   │   ├── spell-check-approval-handler.yml # Spell check approval flow
│   │   ├── apply-typo-patches.yml         # Apply approved typo fixes to WordPress
│   │   ├── apply-alt-patches.yml          # Apply approved image alt-text fixes
│   │   ├── wordpress-backup.yml           # WordPress backup (1st + 15th of month)
│   │   ├── secret-scan.yml                # Gitleaks secret scanning (weekly)
│   │   ├── rollback-site.yml              # Deployment rollback
│   │   ├── issue-to-slack-improved.yml    # GitHub issue → Slack notifications
│   │   └── enable-cloudflare-indexing.yml # Cloudflare indexing setup
│   └── CODEOWNERS                         # Auto-assign PR reviewers
├── scripts/                               # Python & shell automation
│   ├── wp_to_static_generator.py          # Core WordPress → static converter
│   ├── incremental_builder.py             # BLAKE2b incremental build cache
│   ├── config.py                          # Centralised configuration
│   ├── optimize_images.py                 # AVIF/WebP generation (parallel, cached)
│   ├── optimize_css.py                    # CSS unused-selector removal + minification
│   ├── html_transformer.py                # Single-pass HTML transformer (SEO, <picture>,
│   │                                      #   perf hints, critical CSS, minify)
│   ├── convert_images_to_picture.py       # <picture> conversion (used by transformer)
│   ├── extract_critical_css.py            # Critical CSS extraction (used by transformer)
│   ├── enhance_html_performance.py        # Performance hints (used by transformer)
│   ├── fix_seo_issues.py                  # SEO auto-fixer (used by transformer)
│   ├── minify_html.py                     # HTML minification (used by transformer)
│   ├── brotli_compress.py                 # Brotli + Gzip pre-encoding
│   ├── generate_og_images.py              # Per-post Open Graph image generation
│   ├── generate_llms_txt.py               # llms.txt generation for AI crawlers
│   ├── generate_soft404_artefacts.py      # Soft-404 detection artefacts
│   ├── stamp_worker_manifest.py           # Stamps Advanced Mode Worker manifest
│   ├── subset_fonts.py                    # Subsets heading font to used characters
│   ├── rewrite_vendored_urls.py           # Rewrites stale vendored-CDN URLs
│   ├── content_validator.py               # SEO, JSON-LD, accessibility, security
│   ├── validate_html.py                   # HTML structural validation
│   ├── validate_deployment.py             # Post-optimisation deployment checks
│   ├── validate_seo.py                    # SEO validation
│   ├── validate_wordpress_source.py       # Pre-build WordPress health check
│   ├── test_csp.py                        # CSP validation (Utterances, Credly, Plausible)
│   ├── test_interactive_ui.py             # Playwright interactive UI smoke tests
│   ├── test_live_site_formatting.py       # Live site formatting + performance tests
│   ├── markdown_exporter.py               # Exports content as Markdown
│   ├── markdown_api.py                    # Generates /api/ JSON endpoints
│   ├── submit_indexnow.py                 # Submits changed URLs to IndexNow
│   ├── generate_changelog.py              # Generates changelog page
│   ├── generate_stats_page.py             # Generates Plausible stats embed page
│   ├── generate_build_report.py           # Build metrics reporting
│   ├── convert_to_staging.py              # Converts URLs for staging deployment
│   ├── ollama_spell_checker.py            # AI spell checker (Ollama/Llama)
│   ├── wp_spell_check_and_fix.py          # WordPress spell check + auto-fix
│   ├── apply_typo_patches.py              # Applies approved typo patches to WordPress
│   ├── apply_alt_patches.py               # Applies approved alt-text patches
│   ├── manage_build_cache.py              # Build cache management tool
│   ├── purge_html_kv_cache.py             # Bulk-delete html:* entries from KV
│   ├── purge_soft404_kv_cache.py          # Ad-hoc soft-404 KV purge
│   ├── restore_seeded_urls.py             # Restore seeded URLs after build
│   ├── fix_duplicate_resource_hints.py    # Deduplicate preconnect/prefetch hints
│   ├── purge_static_cache.sh              # Cloudflare edge cache purge
│   └── streamdeck-deploy.sh               # Stream Deck deployment trigger
├── _worker.template.js                    # Cloudflare Pages Advanced Mode Worker
│                                          #   → copied to public/_worker.js at deploy
│                                          #   KV cache, smart TTL, view tracking,
│                                          #   security headers, /markdown/ + /api/ routing
├── docs/                                  # Documentation hub
│   ├── README.md                          # Documentation index
│   ├── DEPLOYMENT.md                      # Deployment guide
│   ├── OPTIMIZATION.md                    # Performance optimisation reference
│   ├── FEATURES.md                        # Feature documentation
│   ├── SEO.md                             # SEO implementation details
│   ├── IMAGE_OPTIMIZATION.md              # Image optimisation guide
│   ├── DEVELOPMENT.md                     # Local development guide
│   ├── TESTING.md                         # Testing procedures
│   ├── CHANGELOG.md                       # Version history
│   ├── PAGES_KV_SETUP.md                  # Cloudflare KV setup
│   ├── BUILD_AND_DEPLOY_DOCUMENTATION.md  # Build system reference
│   ├── STREAMDECK_DEPLOY_SETUP.md         # Stream Deck integration
│   ├── STREAMDECK_QUICK_REFERENCE.md      # Stream Deck quick reference card
│   ├── STREAMDECK_README.md               # Stream Deck overview
│   └── ADDITIONAL_PERFORMANCE_RECOMMENDATIONS.md  # Extra performance tips
├── public/                                # Generated static site (Cloudflare Pages)
├── workers/                               # Cloudflare Workers (deployed independently)
│   ├── search-api.js                      # Search API endpoint
│   └── slack-notification-handler.js      # Slack webhook handler
├── assets/fonts/                          # Font assets
├── Makefile                               # Build pipeline targets (make help)
├── CONTRIBUTING.md                        # Contribution guidelines
├── wrangler.toml                          # Cloudflare Wrangler configuration
├── _headers                               # Cloudflare Pages HTTP header rules
└── README.md                              # This file
```

## 🚀 Quick Start

### GitHub Actions (Recommended)

1. **Set up a self-hosted GitHub runner** (required for Cloudflare Access):
   ```bash
   # Settings → Actions → Runners → New self-hosted runner
   ```

2. **Add repository secrets:**
   - `WP_AUTH_TOKEN` — WordPress Basic Auth token (required)
   - `SLACK_WEBHOOK_URL` — Slack notifications (optional)
   - `OLLAMA_API_CREDENTIALS` — AI spell check (optional)
   - `CACHE_PURGE_TOKEN` — KV cache purge (optional)
   - `CLOUDFLARE_API_TOKEN` — Cloudflare API (optional, for cache purge + KV)
   - `CLOUDFLARE_ACCOUNT_ID` — Account ID for KV operations (optional)
   - `CLOUDFLARE_ZONE_ID` — Zone ID for static asset purge (optional)
   - `KV_SEARCH_INDEX_ID` — KV namespace for search index (optional)
   - `PLAUSIBLE_SHARE_LINK` — Plausible stats page (optional)

3. **Trigger a build:**
   ```bash
   gh workflow run deploy-static-site.yml
   ```

### Manual Generation

```bash
export WP_AUTH_TOKEN="your_wordpress_auth_token_here"

# Using Make
make build          # Full pipeline: generate + optimize + validate
make generate       # Generate only
make help           # Show all targets

# Or directly
python3 scripts/wp_to_static_generator.py ./static-output
```

## 🔄 Build Pipeline

The `deploy-static-site.yml` workflow runs a non-blocking spell-check job, then the main build job:

| # | Step | Notes |
|---|------|-------|
| 0 | AI spell check | Separate job, Ollama/Llama, `continue-on-error` — never blocks the build |
| 1 | Validate environment variables | Fails fast on missing secrets |
| 2 | Restore build caches | `actions/cache` — image cache + incremental build cache + spell-check timestamp |
| 3 | Install system + Python dependencies | apt packages (`avifenc`, `optipng`, `jpegoptim`, `jq`, `bc`) + `pip install -r requirements.txt` |
| 4 | Validate CSP (Utterances, Plausible, Credly) | `test_csp.py` — fails build if the CSP would block them |
| 5 | Validate WordPress source health | Pre-flight check before generation |
| 6 | Generate static site | `wp_to_static_generator.py` — incremental (WP `modified_after`) or full build; HTML, assets, sitemap, search index |
| 7 | Export to Markdown + Markdown API | `markdown_exporter.py`, `markdown_api.py` — `/markdown/` and `/api/` paths |
| 8 | Generate llms.txt | `generate_llms_txt.py` |
| 9 | Content quality validation | `content_validator.py` — non-blocking |
| 10 | Optimise images | AVIF + WebP, 4 parallel workers, BLAKE2b cache |
| 11 | Optimise CSS | Remove unused selectors + minify |
| 12 | Single-pass HTML transformer | `html_transformer.py` — SEO fixes, `<img>` → `<picture>`, performance hints, critical CSS inlining, and HTML minification in one parse cycle per file |
| 13 | Soft-404 artefacts + worker stamp | `generate_soft404_artefacts.py`, `stamp_worker_manifest.py` |
| 14 | Generate per-post Open Graph images | `generate_og_images.py` |
| 15 | Subset heading font | `subset_fonts.py` — Anton subset to characters used in headings |
| 16 | Rewrite stale vendored-CDN URLs | `rewrite_vendored_urls.py` |
| 17 | Brotli + Gzip compression | `.br` (primary) + `.gz` (fallback) for all text assets |
| 18 | Interactive UI smoke tests | Playwright (`test_interactive_ui.py`) |
| 19 | Validate HTML + deployment | `validate_html.py` + `validate_deployment.py` in parallel — Brotli integrity, AVIF/WebP presence, picture structure |
| 20 | Prepare output + changelog/stats | Copies to `public/`, generates changelog and stats pages, recompresses |
| 21 | Commit and push to git | Triggers Cloudflare Pages auto-deploy |
| 22 | Upload search index to Workers KV | `wrangler kv key put` |
| 23 | Purge all HTML from KV cache | Waits for the Pages deploy of the pushed commit, then wipes `html:*` entries |
| 24 | Purge static assets from Cloudflare | Edge cache purge via Cloudflare API |
| 25 | Submit URLs to IndexNow | Runs after deployment so crawlers see fresh content |
| 26 | Ping Google sitemap | Only when a new post was published |
| 27 | Notify Slack | Success or failure notification |
| 28 | Clean up on failure | Removes `./static-output` if build failed |

## ✨ Features

### 🖼️ Image Optimisation
- AVIF + WebP generation with `<picture>` elements for browser-native selection
- BLAKE2b-based caching — skips unchanged images across runs
- 4 parallel workers for fast processing
- `fetchpriority="high"` on the first `<main>`/`<article>` image (LCP candidate)
- `loading="lazy"` + `decoding="async"` on all other images
- Per-post Open Graph images generated at build time

### 🗜️ Compression
- **Brotli** (quality 11, `MODE_TEXT` for HTML/CSS/JS, `MODE_GENERIC` for JSON/SVG/XML)
- **Gzip** fallback (level 9) for clients that don't support Brotli
- Pre-encoded at build time — zero runtime CPU cost
- Minimum 5% size reduction threshold before writing compressed file

### ⚡ Performance
- Single-pass HTML transformer — one BeautifulSoup parse/serialise cycle per file instead of 5–6 separate passes
- Critical CSS extracted and inlined for zero render-blocking on first paint
- Heading font subsetted to only the characters actually used
- DNS prefetch + preconnect for Plausible Analytics
- Cloudflare KV HTML cache with smart TTL (5 min homepage, 15 min recent posts, 1 hr older)
- KV TTL uses absolute expiry — view-count updates do not reset the cache clock

### 🔍 SEO & Content Quality
- `og:image` validation — checks presence and absolute HTTPS URL
- JSON-LD structured data validation — checks presence, valid JSON, required Article fields
- Meta description expansion scoped to `<article>`/`<main>` (not nav or footer)
- Canonical URL warnings
- H1 deduplication
- `llms.txt` for AI crawlers
- IndexNow submission after deployment + Google sitemap ping on new posts

### 🔒 Security
- Content Security Policy headers (via `_worker.template.js`)
- Inline script detection in content validator
- Mixed content detection
- Gitleaks secret scanning (pre-commit hook + weekly workflow)

### 📊 Analytics & Monitoring
- **Plausible Analytics** auto-injected on every page
- **Utterances** comments (GitHub Issues backed, dark theme)
- **Slack notifications** on success and failure
- **GitHub Actions summary** with per-step metrics
- **Playwright UI smoke tests** before every deploy

## ⚙️ Configuration

All URLs and domains are centralised in `scripts/config.py`:
- `WP_URL`: `https://wordpress.jameskilby.cloud`
- `TARGET_DOMAIN`: `https://jameskilby.co.uk`
- `STAGING_DOMAIN`: `jkcoukblog.pages.dev`
- `OLLAMA_URL`: `https://ollama.jameskilby.cloud`
- `PLAUSIBLE_DOMAIN`: `plausible.jameskilby.cloud`

Secrets (tokens, credentials) remain in environment variables and GitHub Secrets.

## 📋 Prerequisites

- Python 3.11+
- `pip install -r requirements.txt`
- System tools: `avifenc`, `optipng`, `jpegoptim`, `cwebp`, `jq`, `bc`
- Self-hosted GitHub runner (for Cloudflare Access authentication)
- `WP_AUTH_TOKEN` environment variable

## 🤖 GitHub Actions Workflows

### Workflow Status Badges

[![Deploy Static Site](https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/deploy-static-site.yml/badge.svg)](https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/deploy-static-site.yml)
[![Quality Checks](https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/quality-checks.yml)
[![Secret Scan](https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/secret-scan.yml)

| Workflow | Purpose |
|----------|---------|
| `deploy-static-site.yml` | Main build + deploy pipeline |
| `force-full-deploy.yml` | Force a full (non-incremental) rebuild |
| `quality-checks.yml` | Lighthouse audits + live site formatting tests (daily, 03:00 UTC) |
| `lighthouse-pr.yml` | Lighthouse audit on pull requests |
| `spell-check-consolidated.yml` | AI spell checking via Ollama/Llama |
| `spell-check-approval-handler.yml` | PR-based spell correction approval |
| `apply-typo-patches.yml` | Apply approved typo fixes back to WordPress |
| `apply-alt-patches.yml` | Apply approved image alt-text fixes |
| `wordpress-backup.yml` | WordPress backup (1st + 15th of month) |
| `secret-scan.yml` | Gitleaks secret scanning (weekly) |
| `rollback-site.yml` | Deployment rollback |
| `issue-to-slack-improved.yml` | GitHub issue → Slack notifications |

### Useful Commands

```bash
# Trigger a build
gh workflow run deploy-static-site.yml

# List recent runs
gh run list --limit 10

# Watch a live run
gh run watch

# View logs for a specific run
gh run view <run-id> --log

# Re-run only failed jobs
gh run rerun <run-id> --failed
```

## 📚 Documentation

| File | Contents |
|------|----------|
| [docs/README.md](docs/README.md) | Documentation hub |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Workflow steps, secrets, troubleshooting |
| [docs/OPTIMIZATION.md](docs/OPTIMIZATION.md) | Compression, image, CSS, and JS optimisations |
| [docs/FEATURES.md](docs/FEATURES.md) | Analytics, search, RSS, comments |
| [docs/SEO.md](docs/SEO.md) | SEO implementation details |
| [docs/IMAGE_OPTIMIZATION.md](docs/IMAGE_OPTIMIZATION.md) | Image optimisation deep-dive |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Local development guide |
| [docs/TESTING.md](docs/TESTING.md) | Testing procedures and live site checks |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Version history and improvements |
| [docs/PAGES_KV_SETUP.md](docs/PAGES_KV_SETUP.md) | Cloudflare KV setup |
| [docs/BUILD_AND_DEPLOY_DOCUMENTATION.md](docs/BUILD_AND_DEPLOY_DOCUMENTATION.md) | Build system reference |
| [docs/STREAMDECK_DEPLOY_SETUP.md](docs/STREAMDECK_DEPLOY_SETUP.md) | Stream Deck integration |
| [docs/STREAMDECK_QUICK_REFERENCE.md](docs/STREAMDECK_QUICK_REFERENCE.md) | Stream Deck quick reference |
| [docs/STREAMDECK_README.md](docs/STREAMDECK_README.md) | Stream Deck overview |
| [docs/ADDITIONAL_PERFORMANCE_RECOMMENDATIONS.md](docs/ADDITIONAL_PERFORMANCE_RECOMMENDATIONS.md) | Additional performance recommendations |

---

**Automating WordPress → Static since 2025** 🎉
