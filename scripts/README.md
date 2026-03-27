# Scripts Directory - Complete Inventory

This directory contains all automation scripts for the blog's static site generation pipeline. This document provides a comprehensive guide to understanding what each script does and when to use it.

## Quick Reference: Which Script Should I Use?

| Task | Script | Status |
|------|--------|--------|
| Generate static site from WordPress | `wp_to_static_generator.py` | ✅ CI/CD |
| Validate WordPress before generation | `validate_wordpress_source.py` | ✅ CI/CD |
| Spell check with AI | `ollama_spell_checker.py` | ✅ CI/CD |
| Spell check with auto-fix | `wp_spell_check_and_fix.py` | 🔧 Manual |
| Optimize images (AVIF/WebP) | `optimize_images.py` | ✅ CI/CD |
| Test live site manually | `test_live_site_formatting.py` | 🔧 Manual |
| Manage build cache | `manage_build_cache.py` | 🔧 Manual |
| Configure Cloudflare indexing | `archive/enable_cloudflare_indexing.py` | 🔧 One-time (archived) |
| Purge Cloudflare cache | `purge_static_cache.sh` | ✅ CI/CD |

## Legend

- ✅ **CI/CD** - Automatically runs in GitHub Actions workflow
- 🔧 **Manual** - Run manually when needed
- 📦 **Library** - Imported by other scripts, not run directly
- 🌐 **Frontend** - Client-side JavaScript

---

## CI/CD Pipeline Scripts (24 scripts)

These scripts run automatically as part of the `.github/workflows/deploy-static-site.yml` workflow.

### Core Generation & Validation

#### `wp_to_static_generator.py` ✅
**Purpose:** Main WordPress to static site converter
**What it does:** Fetches content from WordPress REST API and generates a complete static website
**Usage:** `python3 scripts/wp_to_static_generator.py ./output-directory`
**Key features:**
- Incremental builds (only regenerates changed content)
- Supports posts, pages, categories, tags
- Generates responsive images, sitemaps, RSS feeds
- Injects analytics, comments, and performance optimizations

#### `validate_wordpress_source.py` ✅
**Purpose:** Pre-generation WordPress health check
**What it does:** Validates WordPress source health BEFORE static site generation to catch issues early
**Usage:** `python3 scripts/validate_wordpress_source.py`
**Validates:**
- WordPress API accessibility and authentication
- No broken media references (featured images, embedded images)
- Valid category and tag assignments
- SEO readiness (titles, meta descriptions, featured images)
- Exits with code 1 if critical errors found, blocking deployment

#### `incremental_builder.py` 📦
**Purpose:** Incremental build system (library module)
**What it does:** Tracks content changes and enables incremental builds
**Usage:** Imported by `wp_to_static_generator.py`
**How it works:**
- Uses `.build-cache.json` to track content hashes
- Only rebuilds posts/pages that changed since last build
- Saves significant time on large sites

---

### Content Processing

#### `markdown_exporter.py` ✅
**Purpose:** Export posts to markdown with frontmatter
**What it does:** Converts HTML posts to markdown format for version control and portability
**Usage:** `python3 scripts/markdown_exporter.py <source-dir> <markdown-url>`
**Output:** Creates markdown files in `public/markdown/` with YAML frontmatter

#### `markdown_api.py` ✅
**Purpose:** Generate JSON API from markdown files
**What it does:** Creates a JSON API for programmatic access to blog content
**Usage:** `python3 scripts/markdown_api.py <markdown-dir> <api-dir>`
**Output:** Creates JSON files in `public/api/` for each post

---

### Image Optimization

#### `optimize_images.py` ✅
**Purpose:** Convert images to modern formats (AVIF/WebP)
**What it does:** Generates AVIF and WebP variants of all images using parallel processing
**Usage:** `python3 scripts/optimize_images.py`
**Key features:**
- Parallel processing for speed
- Caching to avoid re-processing
- Creates variants for responsive images
- Significant file size reduction

#### `convert_images_to_picture.py` ✅
**Purpose:** Convert img tags to picture elements
**What it does:** Replaces simple `<img>` tags with `<picture>` elements for modern image formats
**Usage:** `python3 scripts/convert_images_to_picture.py`
**Benefits:**
- Serves AVIF to supported browsers
- Falls back to WebP, then original format
- Improves page load performance

---

### CSS & HTML Optimization

#### `extract_critical_css.py` ✅
**Purpose:** Extract and inline above-the-fold CSS
**What it does:** Identifies critical CSS for above-the-fold content and inlines it
**Usage:** `python3 scripts/extract_critical_css.py`
**Benefits:**
- Improves First Contentful Paint (FCP)
- Reduces render-blocking CSS
- Better Core Web Vitals scores

#### `optimize_css.py` ✅
**Purpose:** Remove unused CSS + minification
**What it does:** Two modes - remove unused CSS selectors and minify
**Usage:**
- `python3 scripts/optimize_css.py --remove-unused` (remove unused CSS)
- `python3 scripts/optimize_css.py --minify` (minify CSS)

#### `minify_html.py` ✅
**Purpose:** HTML minification
**What it does:** Removes whitespace, comments, and unnecessary characters from HTML
**Usage:** `python3 scripts/minify_html.py`
**Benefits:** Reduces HTML file size by 10-30%

#### `enhance_html_performance.py` ✅
**Purpose:** Add lazy loading, async/defer, preconnect
**What it does:** Adds performance optimizations to HTML
**Enhancements:**
- Lazy loading for images below the fold
- `async`/`defer` for non-critical JavaScript
- DNS prefetch and preconnect for external resources

#### `fix_seo_issues.py` ✅
**Purpose:** Fix common SEO problems
**What it does:** Automatically fixes SEO issues in HTML
**Fixes:**
- Missing or duplicate title tags
- Missing or short meta descriptions
- Missing canonical URLs
- Multiple H1 tags
- Missing image alt attributes

---

### Compression & Validation

#### `brotli_compress.py` ✅
**Purpose:** Brotli pre-compression for static files
**What it does:** Creates `.br` compressed versions of HTML, CSS, JS files
**Usage:** `python3 scripts/brotli_compress.py`
**Benefits:**
- Cloudflare serves pre-compressed files
- 20-30% better compression than gzip
- Faster page loads

#### `validate_html.py` ✅
**Purpose:** Final HTML validation post-optimization
**What it does:** Validates HTML structure and links after all optimizations
**Usage:** `python3 scripts/validate_html.py`
**Checks:**
- Broken internal links
- Missing image assets
- Missing alt attributes
- HTML structure validity

#### `validate_deployment.py` ✅
**Purpose:** Comprehensive post-optimization validation
**What it does:** Validates all build artifacts before deployment
**Usage:** `python3 scripts/validate_deployment.py <site-directory>`
**Validates:**
- Brotli compression integrity
- Image format variants (AVIF/WebP)
- Picture element structure
- Minification success
- Critical CSS injection
- Utterances comment integration
- Plausible Analytics integration

#### `content_validator.py` ✅
**Purpose:** Content quality validation (non-blocking)
**What it does:** Checks content quality without blocking deployment
**Usage:** `python3 scripts/content_validator.py`
**Checks:**
- Broken links
- Missing alt text
- SEO basics (titles, descriptions)
- Performance issues
- Accessibility concerns

---

### Security & Analytics Testing

#### `test_csp.py` ✅
**Purpose:** Consolidated CSP validation for all third-party services
**What it does:** Tests that Content Security Policy headers allow Utterances, Credly, and Plausible
**Usage:**
- `python3 scripts/test_csp.py` — Test all providers
- `python3 scripts/test_csp.py utterances` — Test one provider
- `python3 scripts/test_csp.py credly plausible` — Test specific providers
**Validates:** script-src, frame-src, and connect-src for each provider's required domains

---

### Quality Assurance

#### `ollama_spell_checker.py` ✅
**Purpose:** Two-stage spell checking (pyspellchecker + AI)
**What it does:** Sophisticated spell checking using AI (Ollama)
**Usage:** `python3 scripts/ollama_spell_checker.py`
**How it works:**
1. First pass: pyspellchecker for common misspellings
2. Second pass: Ollama AI for context-aware corrections
3. Generates spell check report (non-blocking)

---

### URL & Metadata

#### `convert_to_staging.py` ✅
**Purpose:** Convert absolute to relative URLs
**What it does:** Replaces absolute URLs with relative URLs for staging environments
**Usage:** `python3 scripts/convert_to_staging.py`
**Use case:** Testing on staging domain without breaking links

#### `generate_changelog.py` ✅
**Purpose:** Generate changelog page
**What it does:** Creates a changelog page with deployment statistics
**Usage:** `python3 scripts/generate_changelog.py`
**Output:** Generates `/changelog/` page with build history

#### `generate_stats_page.py` ✅
**Purpose:** Generate stats page with Plausible embed
**What it does:** Creates a statistics page with embedded Plausible Analytics dashboard
**Usage:** `PLAUSIBLE_SHARE_LINK=<token> python3 scripts/generate_stats_page.py`
**Output:** Generates `/stats/` page with analytics iframe

---

### SEO & Search

#### `submit_indexnow.py` ✅
**Purpose:** Submit URLs to IndexNow (Bing/Yandex)
**What it does:** Submits changed URLs to search engines via IndexNow API
**Usage:** `INDEXNOW_KEY=<key> python3 scripts/submit_indexnow.py`
**Benefits:** Faster search engine indexing of new/updated content

---

### Cache Management

#### `purge_static_cache.sh` ✅
**Purpose:** Purge Cloudflare cache for static assets
**What it does:** Clears Cloudflare cache after deployment
**Usage:** `bash scripts/purge_static_cache.sh`
**Environment variables required:**
- `CLOUDFLARE_ZONE_ID`
- `CLOUDFLARE_API_TOKEN`

---

## Development & Utility Scripts (3 scripts)

These scripts are for manual use during development or debugging.

### Manual Testing

#### `test_live_site_formatting.py` 🔧
**Purpose:** Comprehensive live site testing
**What it does:** Tests the deployed live site for various issues
**Usage:** `python3 scripts/test_live_site_formatting.py`
**Tests:**
- HTML structure and validity
- CSS loading and formatting
- JavaScript functionality
- SEO metadata presence
- Analytics tracking (Plausible)
- Comment system (Utterances)
- Responsive images
- Performance headers

**When to use:** Manual verification after deployment or when debugging issues on the live site

---

### Alternative Tools

#### `wp_spell_check_and_fix.py` 🔧
**Purpose:** Spell checker with auto-fix capability
**What it does:** Alternative spell checker that can automatically correct misspellings in WordPress
**Usage:** `python3 scripts/wp_spell_check_and_fix.py`
**Key difference from ollama_spell_checker.py:**
- **Auto-fix:** Writes corrections back to WordPress
- **Simpler:** Uses only pyspellchecker (no AI)
- **Manual:** Not in automated workflow

**When to use:** When you want to quickly auto-correct common misspellings in WordPress posts

**Note:** For automated spell checking in CI/CD, use `ollama_spell_checker.py` instead.

---

### Cache Management

#### `manage_build_cache.py` 🔧
**Purpose:** Manage incremental builder cache
**What it does:** View, clear, or get stats about the incremental build cache
**Usage:**
- `python3 scripts/manage_build_cache.py view` - View cache contents
- `python3 scripts/manage_build_cache.py clear` - Clear cache
- `python3 scripts/manage_build_cache.py stats` - Show cache statistics

**When to use:**
- Debugging incremental build issues
- Forcing a full rebuild
- Understanding what's cached

---

## Support & Configuration (3 scripts)

### Configuration

#### `config.py` 📦
**Purpose:** Centralized configuration for all scripts
**What it does:** Defines WordPress URL, target domain, and other settings
**Usage:** Imported by other scripts
**Key settings:**
- `WP_URL` - WordPress source URL
- `TARGET_DOMAIN` - Target static site domain
- `PLAUSIBLE_URL` - Plausible Analytics instance URL

---

### Triggers

#### `streamdeck-deploy.sh` 🔧
**Purpose:** Stream Deck integration for manual workflow trigger
**What it does:** Triggers GitHub Actions workflow via Stream Deck button
**Usage:** Configure as Stream Deck shell command
**Requires:**
- GitHub Personal Access Token
- Stream Deck software

---

## Frontend (1 file)

#### `search.js` 🌐
**Purpose:** Client-side search UI using Fuse.js
**What it does:** Powers the `/search/` page with fuzzy search functionality
**Technology:** Fuse.js (client-side fuzzy search library)
**Usage:** Loaded automatically on search page

---

## One-Time Setup (1 script)

#### `archive/enable_cloudflare_indexing.py` 🔧
**Purpose:** Enable search engine indexing via Cloudflare
**What it does:** Configures Cloudflare to allow search engine crawlers
**Usage:** `CLOUDFLARE_API_TOKEN=<token> CLOUDFLARE_ZONE_ID=<id> python3 scripts/archive/enable_cloudflare_indexing.py`
**When to use:** Run once during initial blog setup
**Status:** Archived — one-time setup script, already executed

---

## Script Categories Summary

| Category | Count | Purpose |
|----------|-------|---------|
| CI/CD Pipeline | 24 | Automated build, optimization, and deployment |
| Development Tools | 3 | Manual testing and utilities |
| Support/Config | 3 | Configuration and external triggers |
| Frontend | 1 | Client-side functionality |
| One-Time Setup | 1 | Initial configuration |
| **Total** | **32** | All Python scripts |

Plus 2 shell scripts and 1 JavaScript file = **40 total files**

---

## Workflow Integration

All ✅ CI/CD scripts are called in `.github/workflows/deploy-static-site.yml` in this order:

1. **Pre-Generation:**
   - `validate_wordpress_source.py` - Validate WordPress health

2. **Generation:**
   - `wp_to_static_generator.py` - Generate static site
   - `markdown_exporter.py` - Export to markdown
   - `markdown_api.py` - Generate JSON API

3. **CSP Testing:**
   - `test_csp.py` - Validate CSP for all providers (Utterances, Credly, Plausible)

4. **Content Validation:**
   - `content_validator.py` - Quality checks (non-blocking)

5. **Image Optimization:**
   - `optimize_images.py` - Generate AVIF/WebP
   - `convert_images_to_picture.py` - Update HTML

6. **SEO & Performance:**
   - `fix_seo_issues.py` - Fix SEO issues
   - `extract_critical_css.py` - Extract critical CSS
   - `enhance_html_performance.py` - Add lazy loading, async/defer

7. **CSS Optimization:**
   - `optimize_css.py --remove-unused` - Remove unused CSS
   - `optimize_css.py --minify` - Minify CSS

8. **HTML Optimization:**
   - `minify_html.py` - Minify HTML

9. **Compression:**
   - `brotli_compress.py` - Pre-compress static files

10. **Validation:**
    - `validate_html.py` - Validate HTML
    - `validate_deployment.py` - Final validation

11. **Metadata:**
    - `convert_to_staging.py` - Convert URLs (if needed)
    - `generate_changelog.py` - Generate changelog
    - `generate_stats_page.py` - Generate stats page

12. **SEO:**
    - `submit_indexnow.py` - Submit to search engines

13. **Cache:**
    - `purge_static_cache.sh` - Purge Cloudflare cache

14. **Spell Check (Separate Job):**
    - `ollama_spell_checker.py` - AI spell checking

---

## Common Tasks

### "I want to test changes without deploying"
1. Run `wp_to_static_generator.py` locally
2. Run `test_live_site_formatting.py` (after deploying to staging)

### "I want to force a full rebuild"
1. Run `manage_build_cache.py clear`
2. Trigger workflow

### "I want to check WordPress health"
```bash
export WP_AUTH_TOKEN="your_token"
python3 scripts/validate_wordpress_source.py
```

### "I want to test CSP for third-party services"
```bash
python3 scripts/test_csp.py                # All providers
python3 scripts/test_csp.py plausible      # Plausible only
```

### "I want to auto-fix spelling mistakes"
```bash
python3 scripts/wp_spell_check_and_fix.py
```

---

## Maintainers

For questions or issues with these scripts, refer to:
- GitHub repository: https://github.com/jameskilbynet/jkcoukblog
- Workflow file: `.github/workflows/deploy-static-site.yml`
- Plan files: `.claude/plans/`

Last updated: 2026-02-16
