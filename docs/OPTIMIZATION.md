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
- **Graceful Degradation**: Build continues even if individual tools are missing

### Tools Used

| Format | Tool | Settings |
|--------|------|----------|
| PNG optimisation | `optipng` | `-o2` |
| JPEG optimisation | `jpegoptim` | `--max=85 --strip-all` |
| WebP conversion | `cwebp` | `-q 80` |
| AVIF conversion | `avifenc` | default |

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

The image optimisation cache is preserved across GitHub Actions runs via `actions/cache@v4`:

```yaml
- uses: actions/cache@v4
  with:
    path: |
      .image_optimization_cache
      .last_spell_check_timestamp
      .build-cache.json
    key: build-cache-avif-v3-${{ github.sha }}
    restore-keys: |
      build-cache-avif-v3-
```

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
3. Inlines those rules directly into `<head>` as a `<style>` block.
4. Changes the original `<link rel="stylesheet">` to load asynchronously via `media="print" onload="this.media='all'"` — a well-known non-blocking CSS pattern.

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

---

## DNS Prefetch & Preconnect

**Script:** `scripts/enhance_html_performance.py` — `add_resource_hints()`

Resource hints warm up connections to external domains before they are needed.

### What is added

**DNS prefetch** (added for all detected external domains):
```html
<link rel="dns-prefetch" href="//plausible.jameskilby.cloud">
```

**Preconnect** (stronger; added only for critical domains that are actually used on the page):
```html
<link rel="preconnect" href="https://plausible.jameskilby.cloud">
```

### Performance Impact

Without resource hints, loading the Plausible script involves serial DNS → TCP → TLS → HTTP steps (~400–900 ms on cold connections). With preconnect, steps 1–3 happen in parallel with page parsing.

**Typical saving:** 200–600 ms on first load.

---

## Performance Monitoring

### Lighthouse CI

**File:** `.github/workflows/quality-checks.yml`

Runs automatically on push to main and daily at 03:00 UTC.

#### Pages tested
1. Homepage — `https://jameskilby.co.uk`
2. Category page — `https://jameskilby.co.uk/category/`
3. Recent posts archive

#### Performance budgets

| Metric | Budget |
|--------|--------|
| First Contentful Paint (FCP) | ≤ 2000 ms |
| Largest Contentful Paint (LCP) | ≤ 2500 ms |
| Time to Interactive (TTI) | ≤ 3500 ms |
| Cumulative Layout Shift (CLS) | ≤ 0.1 |
| Total Blocking Time (TBT) | ≤ 300 ms |

#### Resource budgets

| Resource | Budget |
|----------|--------|
| HTML | 50 KB |
| CSS | 100 KB |
| JS | 200 KB |
| Images | 500 KB |
| Fonts | 100 KB |
| **Total** | **1 MB** |

Budgets exceeded → Slack alert + workflow failure.

### Viewing Reports

```bash
# List recent Lighthouse runs
gh run list --workflow=quality-checks.yml

# Download report artifacts
gh run download <run-id>
```

Reports are retained for **30 days**.

---

## Related Documentation
- [Main README](../README.md)
- [FEATURES.md](FEATURES.md)
- [SEO.md](SEO.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md)
