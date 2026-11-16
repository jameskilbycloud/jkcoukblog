# Optimisation Documentation

Performance optimisations applied by the static site build pipeline.

## Table of Contents
- [Image Optimisation](#image-optimisation)
- [Image Lazy Loading & LCP Priority](#image-lazy-loading--lcp-priority)
- [Brotli + Gzip Compression](#brotli--gzip-compression)
- [Critical CSS Inlining](#critical-css-inlining)
- [CSS Preload Hints](#css-preload-hints)
- [DNS Prefetch & Preconnect](#dns-prefetch--preconnect)
- [Performance Monitoring](#performance-monitoring)

---

## Image Optimisation

### Overview
Advanced image optimisation using Python-based parallel processing with intelligent **BLAKE2b**-based caching.

### Features
- **Parallel Processing**: 4 concurrent workers
- **Intelligent Caching**: BLAKE2b (digest size 16) hashing — unchanged images are skipped across runs
- **AVIF + WebP**: Modern formats generated alongside originals; `<picture>` elements inserted so browsers pick the best format
- **`fetchpriority="high"`**: Applied to the first image inside `<main>`/`<article>` (the likely LCP element)
- **Detailed Metrics**: JSON output with per-image statistics
- **Graceful Degradation**: a failed encode is logged and the build continues

### Tools Used

Everything is encoded by Pillow in `optimize_images.py`; no external image CLIs are used. Originals are served as-is (not recompressed).

| Output | Encoder | Settings |
|--------|---------|----------|
| WebP | Pillow | `quality=85`, `method=6` |
| AVIF | Pillow (built-in AVIF, >= 11.2) | `quality=85`, `speed=4` |
| 480 px variants | Pillow | same settings, for `srcset` |

### Caching System

Cache directory: `.image_optimization_cache/optimization_cache.json`

**Cache Entry Structure:**
```json
{
  "/path/to/image.png": {
    "hash": "blake2b_hex...",
    "optimized_size": 12345,
    "timestamp": 1703012345.678
  }
}
```

> **Note:** The cache previously used MD5 hashing; it was migrated to BLAKE2b (`hashlib.blake2b(content, digest_size=16)`) for improved collision resistance. The build cache key was bumped (v2→v3) to force a clean rebuild after this change.

### Cache Persistence

`.image_optimization_cache/optimization_cache.json` is committed to `main` by the deploy workflow whenever it changes, so it is restored by the checkout. The AVIF/WebP files themselves come back with the previous build, restored from the `site` branch. The incremental build cache and raw HTML snapshot live in the Actions cache — see [DEPLOYMENT.md](DEPLOYMENT.md#caches-between-runs).

### Performance

**Typical timings (≈150 images):**

| Workers | Time | Speedup |
|---------|------|---------|
| 1 | ~120 s | 1.0× |
| 2 | ~65 s | 1.8× |
| 4 | ~35 s | 3.4× |
| 8 | ~30 s | ~4.0× |

*Diminishing returns above 4 workers due to I/O bottleneck.*

---

## Image Lazy Loading & LCP Priority

**Script:** `scripts/enhance_html_performance.py` — `optimize_images()`

### Strategy

The enhancer identifies the **single most likely LCP element** rather than using a fixed count:

1. Find the content root — `<main>` or `<article>` element.
2. The **first `<img>`** inside that root gets `fetchpriority="high"` (and no `loading` attribute so the browser fetches it immediately).
3. **All other images** throughout the page get `loading="lazy"` and `decoding="async"`.

This prevents layout-irrelevant images (logos, nav icons, sidebar thumbnails) from receiving `fetchpriority="high"`.

### Before / After

```html
<!-- Before -->
<img src="hero.jpg" alt="Hero image">
<img src="photo.jpg" alt="Photo">

<!-- After -->
<img src="hero.jpg" alt="Hero image" fetchpriority="high" decoding="async">
<img src="photo.jpg" alt="Photo" loading="lazy" decoding="async">
```

---

## Brotli + Gzip Compression

**Script:** `scripts/brotli_compress.py`

Pre-compression runs at build time so Cloudflare Pages can serve `.br` or `.gz` files directly — zero runtime CPU cost.

### Compression Modes

Brotli exposes two modes relevant to web assets:

| Mode | Used for | Rationale |
|------|----------|-----------|
| `MODE_TEXT` | `.html`, `.css`, `.js`, `.md`, `.txt` | Optimised entropy model for UTF-8 prose and code |
| `MODE_GENERIC` | `.json`, `.svg`, `.xml`, `.csv`, `.rss`, `.atom` | Structured/binary data; `MODE_TEXT` provides no benefit here |

### Gzip Fallback

A second compression pass produces `.gz` alongside every `.br` file, ensuring compatibility with clients that don't support Brotli (legacy browsers, some CDN edge nodes, curl without `--compressed-br`).

```
asset.html      ← original, served if neither encoding accepted
asset.html.br   ← Brotli, primary (served to modern browsers)
asset.html.gz   ← Gzip, fallback (served to legacy clients)
```

### Quality Settings

| Algorithm | Quality | Notes |
|-----------|---------|-------|
| Brotli | 11 (default) | Maximum compression; slower build but zero runtime cost |
| Gzip | 9 | Maximum compression |

Both passes skip files where compression saves less than **5%** of the original size.

### Minimum Size Threshold

Files under **1 KB** are skipped — the header overhead of Brotli/Gzip outweighs any savings for tiny files.

---

## Critical CSS Inlining

**Script:** `scripts/extract_critical_css.py`

### What it does

1. Parses each page's external stylesheets.
2. Identifies CSS rules that apply to elements in the **above-the-fold** viewport (approximately the first screenful of content).
3. Inlines those rules as a `<style data-critical-for>` block placed right before that sheet's `<link>`, so the cascade order matches the final page. The inlined CSS is capped at 16 KB.
4. Changes the original `<link rel="stylesheet">` to `<link rel="preload" as="style" onload="this.onload=null;this.rel='stylesheet'">`, with a `<noscript>` fallback link. The theme stylesheet stays synchronous because it carries the `@font-face` rules.

### Result

The browser renders the initial viewport immediately using the inlined CSS without waiting for external stylesheets to download, eliminating **render-blocking CSS** as a Lighthouse issue.

### CSS Parser

The rule parser uses a **brace-depth tokeniser** rather than a simple regex, correctly handling:
- Nested at-rules (`@media`, `@supports`, `@layer`)
- Comment stripping before parse
- `@keyframes` and `@font-face` (skipped from critical extraction)
- `@import` and `@charset` (semicolon-terminated, no brace block)

---

## CSS Preload Hints

**Script:** `scripts/enhance_html_performance.py` — `add_preload_hints()`

### What is preloaded

A `<link rel="preload" as="style">` hint is added for the **primary stylesheet** — the one most likely to be render-critical. Only stylesheets whose **filename** exactly matches one of these patterns are preloaded:

| Pattern | Examples matched |
|---------|-----------------|
| `critical.css` / `critical.min.css` | Explicit critical CSS files |
| `main.css` / `main.min.css` | Primary theme stylesheet |
| `styles.css` / `styles.min.css` | Common alternative naming |

Any other stylesheet (e.g. `bootstrap-styles.css`, `theme-stylesheet.css`) is **not** preloaded. Preloading too many stylesheets defeats the purpose by competing for bandwidth.

The match is applied to the filename portion of the href only (not the full path), so `/assets/css/main.css` is matched but `/assets/main-content.css` is not.

### Other preloads

- **LCP image:** the first image in `<main>`/`<article>` gets `<link rel="preload" as="image" fetchpriority="high">`. When the image sits in a `<picture>`, the hint points at its first AVIF/WebP `<source>` (with `imagesrcset`/`imagesizes`), so the browser doesn't download two formats.
- **Fonts:** only the body font (Space Grotesk 400) and the heading font (Anton) are preloaded. The other four files rely on `font-display: optional`.

---

## DNS Prefetch & Preconnect

**Script:** `scripts/enhance_html_performance.py` — `add_resource_hints()`

This pass currently adds nothing. Plausible used to be its only critical domain, but the script is now served same-origin (`/js/script.js`, proxied by the Worker), so the list of critical domains is empty. `add_plausible_analytics()` also removes old `dns-prefetch`/`preconnect` hints to the Plausible host from pages. The pass stays in place for any future third-party domain that is on the critical path.

---

## Performance Monitoring

### Lighthouse CI

**File:** `.github/workflows/quality-checks.yml`

Dispatched by the deploy workflow after every deploy, and daily at 03:00 UTC.

#### Pages tested
The homepage (`https://jameskilby.co.uk`) only, three runs each on desktop and mobile settings.

#### Performance budgets

From `.github/lighthouse/budget.json` (desktop) and `budget-mobile.json` (mobile):

| Metric | Desktop | Mobile |
|--------|---------|--------|
| First Contentful Paint (FCP) | ≤ 1500 ms | ≤ 5500 ms |
| Largest Contentful Paint (LCP) | ≤ 2500 ms | ≤ 7000 ms |
| Time to Interactive (TTI) | ≤ 3000 ms | ≤ 8000 ms |
| Speed Index | ≤ 1500 ms | ≤ 5500 ms |
| Total Blocking Time (TBT) | ≤ 300 ms | ≤ 400 ms |
| Cumulative Layout Shift (CLS) | ≤ 0.05 | ≤ 0.05 |

#### Resource budgets

Same on desktop and mobile:

| Resource | Budget |
|----------|--------|
| HTML | 30 KB |
| CSS | 30 KB |
| JS | 40 KB |
| Images | 450 KB |
| Fonts | 600 KB |
| Third-party | 30 KB |
| **Total** | **1,100 KB** |

The budgets also cap request counts (5 stylesheets, 6 scripts, 18 images, 6 fonts, 3 third-party). Every run posts its scores to Slack.

### Viewing Reports

```bash
# List recent Lighthouse runs
gh run list --workflow=quality-checks.yml

# Download report artifacts
gh run download <run-id>
```

Reports are uploaded as workflow artifacts (kept for the repository's artifact retention period) and to Lighthouse's temporary public storage.

---

## Related Documentation
- [Main README](../README.md)
- [FEATURES.md](FEATURES.md)
- [SEO.md](SEO.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md)
