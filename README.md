# WordPress to Static Site Automation

🚀 **Automated WordPress to Static Site Generator** with AI spell-checking, SEO optimisations, Brotli+Gzip compression, AVIF/WebP image conversion, and Cloudflare Pages deployment via GitHub Actions.

📚 **[Complete Documentation Hub →](docs/README.md)**

## 🎯 Overview

This repository contains a complete automation pipeline that:

- ✅ **Connects to WordPress CMS** via REST API (supports Cloudflare Access protected sites)
- ✅ **Generates a static site** with all content, assets, and metadata
- ✅ **Applies AI spell-checking** via Ollama (non-blocking, incremental)
- ✅ **Optimises images** to AVIF/WebP with `<picture>` elements and intelligent caching
- ✅ **Compresses assets** with Brotli (primary) + Gzip (fallback), pre-encoded at build time
- ✅ **Inlines critical CSS** for faster first paint
- ✅ **Validates content** — SEO, accessibility, JSON-LD, og:image, security headers
- ✅ **Deploys to Cloudflare Pages** via git commit, with selective KV cache purge
- ✅ **Submits to IndexNow** after deployment so crawlers see fresh content immediately

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
│   │   ├── quality-checks.yml             # Lighthouse + live site formatting tests
│   │   ├── spell-check-consolidated.yml   # AI spell checking (Ollama/Llama)
│   │   ├── spell-check-approval-handler.yml # Spell check approval flow
│   │   ├── secret-scan.yml                # Gitleaks secret scanning
│   │   ├── rollback-site.yml              # Deployment rollback
│   │   ├── issue-to-slack-improved.yml    # GitHub issue → Slack notifications
│   │   └── enable-cloudflare-indexing.yml # Cloudflare indexing setup
│   └── CODEOWNERS                         # Auto-assign PR reviewers
├── scripts/                               # Python & shell automation
│   ├── wp_to_static_generator.py          # Core WordPress → static converter
│   ├── incremental_builder.py             # BLAKE2b incremental build cache
│   ├── config.py                          # Centralised configuration
│   ├── optimize_images.py                 # AVIF/WebP generation (parallel, cached)
│   ├── convert_images_to_picture.py       # Wraps <img> in <picture> elements
│   ├── extract_critical_css.py            # Extracts and inlines above-fold CSS
│   ├── optimize_css.py                    # CSS optimisation and minification
│   ├── enhance_html_performance.py        # fetchpriority, lazy loading, preconnect
│   ├── fix_seo_issues.py                  # SEO auto-fixer (title, meta, H1)
│   ├── minify_html.py                     # HTML minification
│   ├── brotli_compress.py                 # Brotli + Gzip pre-encoding
│   ├── content_validator.py               # SEO, JSON-LD, accessibility, security
│   ├── validate_html.py                   # HTML structural validation
│   ├── validate_deployment.py             # Post-optimisation deployment checks
│   ├── validate_wordpress_source.py       # Pre-build WordPress health check
│   ├── test_csp.py                        # CSP validation (Utterances, Credly, Plausible)
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
│   ├── manage_build_cache.py              # Build cache management tool
│   ├── purge_static_cache.sh              # Cloudflare edge cache purge
│   ├── streamdeck-deploy.sh               # Stream Deck deployment trigger
│   └── archive/                           # Archived one-time setup scripts
├── functions/                             # Cloudflare Pages Functions
│   ├── _middleware.js                     # Request middleware (KV cache, view tracking)
│   ├── diagnostic.js                      # Cache diagnostic endpoint
│   ├── trace.js                           # Request tracing endpoint
│   └── test.js                            # Health check endpoint
├── _worker.template.js                    # Cloudflare Pages Advanced Mode Worker
│                                          #   → copied to public/_worker.js at deploy
│                                          #   KV cache, smart TTL, view tracking,
│                                          #   selective purge, security headers
├── docs/                                  # Documentation hub (20+ files)
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
│   └── archive/                           # Historical docs
├── public/                                # Generated static site (Cloudflare Pages)
├── workers/                               # Cloudflare Workers
│   ├── html-cache-kv.js                   # Active KV-backed HTML cache worker
│   ├── search-api.js                      # Search API endpoint
│   ├── slack-notification-handler.js      # Slack webhook handler
│   └── archive/                           # Superseded worker versions
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

The `deploy-static-site.yml` workflow runs these steps in order:

| # | Step | Notes |
|---|------|-------|
| 1 | Validate environment variables | Fails fast on missing secrets |
| 2 | Restore build cache | `actions/cache@v4` — image cache + build cache + spell-check timestamp |
| 3 | Install system dependencies | apt packages: `avifenc`, `optipng`, `jpegoptim`, `jq`, `bc` |
| 4 | Install Python dependencies | `pip install -r requirements.txt` |
| 5 | Validate WordPress source health | Pre-flight check before generation |
| 6 | Generate static site | `wp_to_static_generator.py` — HTML, assets, sitemap, search index |
| 7 | Export to Markdown | `markdown_exporter.py` |
| 8 | Generate Markdown API | `markdown_api.py` |
| 9 | Validate CSP (Utterances, Plausible, Credly) | `test_csp.py` — fails build if CSP would block them |
| 10 | Content quality validation | `content_validator.py` — non-blocking |
| 11 | Optimise images | AVIF + WebP, 4 parallel workers, BLAKE2b cache |
| 12 | Convert `<img>` → `<picture>` | Adds AVIF/WebP sources with fallbacks |
| 13 | Optimise CSS | Remove unused selectors |
| 14 | Apply SEO fixes | Title length, meta description scoped to article, H1 deduplication |
| 15 | Extract and inline critical CSS | Above-fold CSS inlined in `<head>` |
| 16 | Apply performance enhancements | `fetchpriority` for LCP image, lazy loading, preconnect, CSS preload |
| 17 | Minify CSS | Minification pass |
| 18 | Minify HTML | `minify_html.py` |
| 19 | Brotli + Gzip compression | `.br` (primary) + `.gz` (fallback) for all text assets |
| 20 | Validate final HTML | Structural validation |
| 21 | Comprehensive deployment validation | Brotli integrity, AVIF/WebP presence, picture structure |
| 22 | Commit and push to git | Triggers Cloudflare Pages auto-deploy |
| 23 | Upload search index to Workers KV | `wrangler kv:key put` |
| 24 | Selective KV cache purge | Purges only changed HTML pages |
| 25 | Purge static assets from Cloudflare | Edge cache purge via Cloudflare API |
| 26 | Submit URLs to IndexNow | Runs after deployment so crawlers see fresh content |
| 27 | Notify Slack | Success or failure notification |
| 28 | Clean up on failure | Removes `./static-output` if build failed |

## ✨ Features

### 🖼️ Image Optimisation
- AVIF + WebP generation with `<picture>` elements for browser-native selection
- BLAKE2b-based caching — skips unchanged images across runs
- 4 parallel workers for fast processing
- `fetchpriority="high"` on the first `<main>`/`<article>` image (LCP candidate)
- `loading="lazy"` + `decoding="async"` on all other images

### 🗜️ Compression
- **Brotli** (quality 11, `MODE_TEXT` for HTML/CSS/JS, `MODE_GENERIC` for JSON/SVG/XML)
- **Gzip** fallback (level 9) for clients that don't support Brotli
- Pre-encoded at build time — zero runtime CPU cost
- Minimum 5% size reduction threshold before writing compressed file

### ⚡ Performance
- Critical CSS extracted and inlined for zero render-blocking on first paint
- CSS preload hints for primary stylesheet (exact filename match: `critical.css`, `main.css`, `styles.css`)
- DNS prefetch + preconnect for Plausible Analytics
- Cloudflare KV HTML cache with smart TTL (5 min homepage, 15 min recent posts, 1 hr older)
- KV TTL uses absolute expiry — view-count updates do not reset the cache clock

### 🔍 SEO & Content Quality
- `og:image` validation — checks presence and absolute HTTPS URL
- JSON-LD structured data validation — checks presence, valid JSON, required Article fields
- Meta description expansion scoped to `<article>`/`<main>` (not nav or footer)
- Canonical URL warnings
- H1 deduplication
- IndexNow submission after deployment

### 🔒 Security
- Content Security Policy headers (via `_worker.template.js`)
- Inline script detection in content validator
- Mixed content detection
- `/markdown/` and `/api/` path handling in the worker

### 📊 Analytics & Monitoring
- **Plausible Analytics** auto-injected on every page
- **Utterances** comments (GitHub Issues backed, dark theme)
- **Slack notifications** on success and failure
- **GitHub Actions summary** with per-step metrics

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

[![Deploy Static Site](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml)
[![Quality Checks](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml)
[![Secret Scan](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/secret-scan.yml)

| Workflow | Purpose |
|----------|---------|
| `deploy-static-site.yml` | Main 28-step build + deploy pipeline |
| `quality-checks.yml` | Lighthouse audits + live site formatting tests (daily) |
| `spell-check-consolidated.yml` | AI spell checking via Ollama/Llama |
| `spell-check-approval-handler.yml` | PR-based spell correction approval |
| `secret-scan.yml` | Gitleaks secret scanning |
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

---

**Automating WordPress → Static since 2025** 🎉
