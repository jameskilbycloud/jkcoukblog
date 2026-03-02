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
├── .github/workflows/
│   ├── deploy-static-site.yml        # Main build + deploy workflow
│   └── quality-checks.yml            # Lighthouse + formatting tests
├── scripts/                          # Python automation scripts
│   ├── wp_to_static_generator.py     # Core WordPress → static converter
│   ├── optimize_images.py            # Image optimisation (AVIF/WebP, parallel)
│   ├── convert_images_to_picture.py  # Wraps <img> in <picture> elements
│   ├── brotli_compress.py            # Brotli (primary) + Gzip (fallback) compression
│   ├── extract_critical_css.py       # Extracts and inlines above-fold CSS
│   ├── optimize_css.py               # CSS optimisation and minification
│   ├── enhance_html_performance.py   # fetchpriority, lazy loading, preconnect, preload
│   ├── fix_seo_issues.py             # SEO auto-fixer (title length, meta description, H1)
│   ├── minify_html.py                # HTML minification
│   ├── content_validator.py          # Content quality checks (SEO, JSON-LD, security)
│   ├── validate_html.py              # HTML structural validation
│   ├── validate_deployment.py        # Post-optimisation deployment validation
│   ├── validate_wordpress_source.py  # Pre-build WordPress source health check
│   ├── markdown_exporter.py          # Exports content as Markdown
│   ├── markdown_api.py               # Generates Markdown API endpoints
│   ├── submit_indexnow.py            # Submits changed URLs to IndexNow
│   ├── generate_changelog.py         # Generates changelog page
│   ├── generate_stats_page.py        # Generates Plausible stats embed page
│   ├── incremental_builder.py        # Incremental build cache (BLAKE2b hashing)
│   ├── convert_to_staging.py         # Converts absolute URLs to relative for staging
│   ├── purge_static_cache.sh         # Purges Cloudflare edge cache for static assets
│   ├── test_csp_utterances.py        # Validates CSP allows Utterances
│   ├── test_plausible_analytics.py   # Validates CSP allows Plausible Analytics
│   ├── ollama_spell_checker.py       # AI spell checker (Ollama/Llama)
│   ├── wp_spell_check_and_fix.py     # WordPress spell check + fix
│   └── config.py                     # Centralised configuration
├── _worker.template.js               # Cloudflare Pages Advanced Mode Worker (source)
│                                     #   → copied to public/_worker.js at deploy time
│                                     #   Provides: KV HTML cache, smart TTL, view tracking,
│                                     #             selective purge, security headers
├── docs/                             # Documentation
│   ├── README.md                     # Documentation hub
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── OPTIMIZATION.md               # Performance optimisation reference
│   ├── FEATURES.md                   # Feature documentation
│   ├── SEO.md                        # SEO implementation details
│   ├── IMAGE_OPTIMIZATION.md         # Image optimisation guide
│   ├── DEVELOPMENT.md                # Development guide
│   └── archive/                      # Historical docs
├── public/                           # Generated static site (deployed by Cloudflare Pages)
│   └── _worker.js                    # Compiled from _worker.template.js at deploy time
├── workers/                          # Legacy Cloudflare Workers scripts
├── wrangler.toml                     # Cloudflare Wrangler configuration
└── README.md                         # This file
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
| 9 | Validate CSP (Utterances + Plausible) | Fails build if CSP would block them |
| 10 | Content quality validation | `content_validator.py` — non-blocking |
| 11 | Optimise images | AVIF + WebP, 4 parallel workers, BLAKE2b cache |
| 12 | Convert `<img>` → `<picture>` | Adds AVIF/WebP sources with fallbacks |
| 13 | Optimise CSS | Remove unused selectors |
| 14 | Apply SEO fixes | Title length, meta description scoped to article, H1 deduplication |
| 15 | Extract and inline critical CSS | Above-fold CSS inlined in `<head>` |
| 16 | Apply performance enhancements | `fetchpriority` for LCP image, lazy loading, preconnect, CSS preload |
| 17 | Minify CSS | Minification pass |
| 17 | Minify HTML | `minify_html.py` |
| 18 | Brotli + Gzip compression | `.br` (primary) + `.gz` (fallback) for all text assets |
| 19 | Validate final HTML | Structural validation |
| 20 | Comprehensive deployment validation | Brotli integrity, AVIF/WebP presence, picture structure |
| 21 | Commit and push to git | Triggers Cloudflare Pages auto-deploy |
| 22 | Upload search index to Workers KV | `wrangler kv:key put` |
| 23 | Selective KV cache purge | Purges only changed HTML pages |
| 24 | Purge static assets from Cloudflare | Edge cache purge via Cloudflare API |
| 25 | Submit URLs to IndexNow | Runs after deployment so crawlers see fresh content |
| 26 | Notify Slack | Success or failure notification |
| 27 | Clean up on failure | Removes `./static-output` if build failed |

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
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Workflow steps, secrets, troubleshooting |
| [docs/OPTIMIZATION.md](docs/OPTIMIZATION.md) | Compression, image, CSS, and JS optimisations |
| [docs/FEATURES.md](docs/FEATURES.md) | Analytics, search, RSS, comments |
| [docs/SEO.md](docs/SEO.md) | SEO implementation details |
| [docs/IMAGE_OPTIMIZATION.md](docs/IMAGE_OPTIMIZATION.md) | Image optimisation deep-dive |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Local development guide |
| [docs/PAGES_KV_SETUP.md](docs/PAGES_KV_SETUP.md) | Cloudflare KV setup |

---

**Automating WordPress → Static since 2025** 🎉
