# Deployment Documentation

## Table of Contents
- [GitHub Actions Workflow](#github-actions-workflow)
- [Build Steps Reference](#build-steps-reference)
- [Cloudflare Pages Advanced Mode Worker](#cloudflare-pages-advanced-mode-worker)
- [KV Cache](#kv-cache)
- [Build Cache Persistence](#build-cache-persistence)
- [Deployment Options](#deployment-options)
- [Environment Variables & Secrets](#environment-variables--secrets)
- [Troubleshooting](#troubleshooting)

---

## GitHub Actions Workflow

**File:** `.github/workflows/deploy-static-site.yml`

**Triggers:**
- Manual (`workflow_dispatch`)
- Webhook (`repository_dispatch` — sent by WordPress plugin on publish)

**Runner:** Self-hosted (required to reach WordPress behind Cloudflare Access)

**Concurrency:** `cancel-in-progress: false` — concurrent runs queue rather than cancel, so no deployment is skipped.

**Manual trigger:**
```bash
gh workflow run deploy-static-site.yml
```

---

## Build Steps Reference

| # | Step | Script / Tool | Blocking? |
|---|------|--------------|-----------|
| 1 | Validate env vars | bash | ✅ Yes |
| 2 | Checkout repository | `actions/checkout@v4` | ✅ Yes |
| 3 | Restore build cache | `actions/cache@v4` | ✅ Yes |
| 4 | Install system dependencies | apt-get | ✅ Yes |
| 5 | Install Python dependencies | pip | ✅ Yes |
| 6 | Validate WordPress source | `validate_wordpress_source.py` | ✅ Yes |
| 7 | Generate static site | `wp_to_static_generator.py` | ✅ Yes |
| 8 | Export to Markdown | `markdown_exporter.py` | ⚠️ Non-blocking |
| 9 | Generate Markdown API | `markdown_api.py` | ⚠️ Non-blocking |
| 10 | Validate CSP (Utterances) | `test_csp_utterances.py` | ✅ Yes |
| 11 | Validate CSP (Plausible) | `test_plausible_analytics.py` | ✅ Yes |
| 12 | Content quality validation | `content_validator.py` | ⚠️ Non-blocking |
| 13 | Optimise images | `optimize_images.py` | ⚠️ Non-blocking |
| 14 | Convert `<img>` → `<picture>` | `convert_images_to_picture.py` | ⚠️ Non-blocking |
| 15 | Optimise CSS | `optimize_css.py` | ⚠️ Non-blocking |
| 16 | Apply SEO fixes | `fix_seo_issues.py` | ⚠️ Non-blocking |
| 17 | Extract and inline critical CSS | `extract_critical_css.py` | ⚠️ Non-blocking |
| 18 | Apply performance enhancements | `enhance_html_performance.py` | ⚠️ Non-blocking |
| 19 | Minify CSS | `optimize_css.py --minify-only` | ⚠️ Non-blocking |
| 20 | Minify HTML | `minify_html.py` | ⚠️ Non-blocking |
| 21 | Brotli + Gzip compression | `brotli_compress.py` | ⚠️ Non-blocking |
| 22 | Validate final HTML | `validate_html.py` | ✅ Yes |
| 23 | Comprehensive deployment validation | `validate_deployment.py` | ✅ Yes |
| 24 | Commit and push to git | git | ✅ Yes |
| 25 | Upload search index to KV | `wrangler kv:key put` | ⚠️ Non-blocking |
| 26 | Selective KV cache purge | `/.purge` endpoint | ⚠️ Non-blocking |
| 27 | Purge Cloudflare static cache | `purge_static_cache.sh` | ⚠️ Non-blocking |
| 28 | Submit URLs to IndexNow | `submit_indexnow.py` | ⚠️ Non-blocking |
| 29 | Notify Slack | `slackapi/slack-github-action` | ⚠️ Non-blocking |
| 30 | Clean up on failure | bash `rm -rf ./static-output` | On failure only |

> **Why IndexNow runs last:** It fires after both Cloudflare cache purge steps so search engine crawlers arrive to find the fresh, correctly-served content rather than a cached stale version.

---

## Cloudflare Pages Advanced Mode Worker

**Source:** `_worker.template.js` (tracked in git)
**Deployed as:** `public/_worker.js` (copied during the "Commit and push" step)

When `_worker.js` is present in the Pages deployment root, Cloudflare Pages activates **Advanced Mode** — the worker intercepts every request, including static file requests.

### Features

| Feature | Detail |
|---------|--------|
| KV HTML cache | Caches rendered HTML in `HTML_CACHE` KV namespace |
| Smart TTL | Homepage 5 min, recent posts 15 min, older content 1 hour |
| Absolute KV expiry | Expiry is set as an absolute Unix timestamp on first cache write; view-count updates reuse the original expiry and do not reset the TTL clock |
| View count tracking | Incremented asynchronously on each cache hit (stored in KV metadata) |
| Selective purge | `/.purge?path=<url>` endpoint — requires `X-Purge-Token` header |
| Security headers | CSP, HSTS, X-Frame-Options, Referrer-Policy, Permissions-Policy |
| Cache API fallback | Falls back to the Cache API if KV is unavailable |
| Static asset bypass | `.js`, `.css`, `.br`, `.gz`, `.avif`, `.webp`, etc. are served directly without KV caching |

### KV Bindings Required

| Binding | Purpose |
|---------|---------|
| `HTML_CACHE` | HTML page cache |
| `SEARCH_INDEX` | Search index storage |
| `PURGE_TOKEN` | Secret for `/.purge` endpoint |
| `ASSETS` | Cloudflare Pages static asset binding (automatic) |

### Diagnostic Endpoints

> These are **currently public** — see open issue #17.

| Path | Purpose |
|------|---------|
| `/diagnostic` | Reports binding status, KV test |
| `/trace?path=<url>` | Shows caching decision for any path |
| `/test` | Confirms Advanced Mode is active |

---

## KV Cache

### TTL Logic

```
/ or /index.html     → 300 s  (5 min)
/YYYY/MM/ paths      → 900 s  (15 min) if year+month ≥ current month − 1
everything else      → 3600 s (1 hour)
```

### Expiry Behaviour

When a page is first cached, the worker stores:
- `expiration` — absolute Unix timestamp (`now + ttl`)
- `abs_expiry` — same value, persisted in KV metadata

On subsequent cache hits (view count updates), `expiration: abs_expiry` is reused — the TTL is **not** extended. This means:
- Popular pages expire on the same schedule as unpopular ones
- Deleted or renamed pages are naturally evicted from KV within their TTL window

### Selective Purge

Changed HTML files are purged from KV automatically after each deployment:

```bash
curl -X GET "https://jameskilby.co.uk/.purge?path=/2026/01/my-post/" \
  -H "X-Purge-Token: $CACHE_PURGE_TOKEN"
```

> **Note:** The purge endpoint currently uses GET — see open issue #18.

---

## Build Cache Persistence

The `actions/cache@v4` step saves and restores:

| Path | Purpose |
|------|---------|
| `.image_optimization_cache/` | BLAKE2b image hashes — skips unchanged images |
| `.last_spell_check_timestamp` | ISO timestamp for incremental spell checking |
| `.build-cache.json` | Incremental build cache (post/page content hashes) |

**Cache key:** `build-cache-avif-v3-${{ github.sha }}`
**Restore keys:** `build-cache-avif-v3-` (partial match — uses most recent cache)

> The key was bumped from v2 → v3 when MD5 hashing was replaced with BLAKE2b. A v2 cache contains MD5 hashes that no longer match the BLAKE2b hashes produced by the current code, which would cause every post to be treated as changed.

---

## Deployment Options

### 1. Cloudflare Pages (Primary)

Automatic deployment from the `public/` directory in the git repository.

**Setup:**
1. Connect Cloudflare Pages to this GitHub repository
2. Set publish directory: `public/`
3. No build command — site is pre-built by GitHub Actions
4. Custom domain: `jameskilby.co.uk`

### 2. Manual (Wrangler)

```bash
npx wrangler pages publish ./public --project-name=jameskilby-co-uk
```

### 3. Git Commit (What GitHub Actions does)

```bash
git add public/
git commit -m "🚀 Auto-update static site - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main
```

---

## Environment Variables & Secrets

### Required

| Secret | Purpose |
|--------|---------|
| `WP_AUTH_TOKEN` | WordPress Basic Auth token for REST API |

### Optional

| Secret | Purpose |
|--------|---------|
| `OLLAMA_API_CREDENTIALS` | `username:password` for AI spell checker |
| `SLACK_WEBHOOK_URL` | Slack notifications on success/failure |
| `CACHE_PURGE_TOKEN` | Token for `/.purge` KV cache endpoint |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API — static asset cache purge + KV upload |
| `CLOUDFLARE_ZONE_ID` | Zone ID for static asset cache purge |
| `KV_SEARCH_INDEX_ID` | KV namespace ID for search index |
| `PLAUSIBLE_SHARE_LINK` | Plausible Analytics share link for stats page |

### Environment Variables (set in workflow)

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_URL` | `https://ollama.jameskilby.cloud` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.1:8b` | Model for spell checking |

---

## Troubleshooting

### Build fails at "Validate WordPress Source"

```bash
# Check WordPress API is reachable from the runner
curl -H "Authorization: Basic $WP_AUTH_TOKEN" https://wordpress.jameskilby.cloud/wp-json/wp/v2/posts?per_page=1
```

### Images not converting to AVIF

- Check `avifenc` is installed: `avifenc --version`
- Review the "Optimise images" step logs for per-image errors
- Verify the image cache hasn't incorrectly marked files as up to date: delete `.image_optimization_cache/optimization_cache.json` and re-run

### Build cache not surviving between runs

- Confirm the `actions/cache@v4` step shows "Cache restored" in the logs
- Check the cache key: `build-cache-avif-v3-` prefix should match between save and restore
- GitHub cache has a 10 GB limit per repository — old caches are evicted automatically

### Cloudflare Pages shows old content after deploy

1. Check the "Selective KV cache purge" step — did it purge the affected URLs?
2. Manually purge via: `curl -X GET "https://jameskilby.co.uk/.purge?path=/your-path/" -H "X-Purge-Token: $TOKEN"`
3. Check the Cloudflare Pages deployment list to confirm the commit was picked up

### Python dependency errors

```bash
pip install -r requirements.txt --break-system-packages
```

### Git push conflicts

The workflow attempts rebase before force-push. If you see `[force-resolved]` in a commit message, the rebase failed and the site was regenerated from scratch without optimisations applied — see open issue #13.

### Viewing workflow logs

```bash
gh run list --workflow=deploy-static-site.yml
gh run view <run-id> --log
gh run rerun <run-id> --failed
```

---

## Related Documentation
- [Main README](../README.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
- [FEATURES.md](FEATURES.md)
- [PAGES_KV_SETUP.md](PAGES_KV_SETUP.md)
