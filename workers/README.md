# Cloudflare Workers

This directory contains Cloudflare Workers for the jkcoukblog static site.

## Workers

### 1. `html-cache.js` - HTML Caching Worker

**Purpose:** Caches HTML pages at Cloudflare's edge to dramatically improve TTFB.

**Impact:**
- TTFB: 320ms → ~50ms (85% improvement)
- Total load: 665ms → ~200ms (70% improvement)

**Features:**
- ✅ Caches HTML for 5 minutes
- ✅ Adds debug headers (X-Worker-Cache, X-Cache-Age)
- ✅ Supports manual cache purging
- ✅ Excludes admin/preview URLs

**Quick Deploy:**
```bash
# Option 1: Pages Function (recommended)
./deploy-cache-worker.sh pages

# Option 2: Standalone Worker
./deploy-cache-worker.sh worker
```

**Full Documentation:** [`docs/HTML_CACHE_WORKER.md`](../docs/HTML_CACHE_WORKER.md)

---

### 2. `slack-notification-handler.js` - Slack Webhook Handler

**Purpose:** Handles Slack notifications from GitHub Actions workflows.

**Status:** Already deployed

**Configuration:** See `wrangler.toml`

---

### 3. `slack-notification-handler-improved.js` - Enhanced Slack Handler

**Purpose:** Improved version of Slack notification handler with better formatting.

**Status:** Development/testing

---

## Quick Reference

| Worker | Purpose | Status | Docs |
|--------|---------|--------|------|
| html-cache.js | Edge HTML caching | ✅ Ready | [HTML_CACHE_WORKER.md](../docs/HTML_CACHE_WORKER.md) |
| slack-notification-handler.js | Slack alerts | ✅ Deployed | - |
| slack-notification-handler-improved.js | Enhanced Slack | 🚧 Testing | - |

## Deployment

All workers are configured in `wrangler.toml` and can be deployed via:

```bash
# Deploy specific worker
npx wrangler deploy workers/<worker-name>.js --name <worker-name>

# Or use the helper script
./deploy-cache-worker.sh [pages|worker]
```

## Testing

Test the HTML cache worker after deployment:

```bash
# Test cache miss (first request)
curl -I https://jameskilby.co.uk/ | grep X-Worker-Cache

# Test cache hit (second request)
curl -I https://jameskilby.co.uk/ | grep X-Worker-Cache

# Verify performance
curl -w "\nTTFB: %{time_starttransfer}s\n" -o /dev/null -s https://jameskilby.co.uk/
```

## Monitoring

View worker metrics in Cloudflare Dashboard:
- Workers & Pages → [worker-name] → Metrics
- Analytics → Traffic (for cache hit ratio)

Tail logs in real-time:
```bash
npx wrangler tail <worker-name>
```

## Related Documentation

- [`wrangler.toml`](../wrangler.toml) - Worker configurations
- [`docs/HTML_CACHE_WORKER.md`](../docs/HTML_CACHE_WORKER.md) - HTML cache documentation
- [`deploy-cache-worker.sh`](../deploy-cache-worker.sh) - Deployment script
