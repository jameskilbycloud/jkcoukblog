# HTML Cache Worker Documentation

## Overview

The HTML Cache Worker caches HTML pages at Cloudflare's edge to dramatically improve Time To First Byte (TTFB). This converts `cf-cache-status: DYNAMIC` responses to `cf-cache-status: HIT` for cached content.

**Expected Impact:**
- TTFB: 320ms → ~30-50ms (90% improvement for cached requests)
- Total page load: 665ms → ~150-200ms
- Reduced load on origin (Cloudflare Pages)

## Features

- ✅ Caches HTML responses for 5 minutes (300 seconds)
- ✅ Only caches successful GET requests (200 status)
- ✅ Respects existing cache-control headers
- ✅ Adds debug headers for monitoring (`X-Worker-Cache`, `X-Cache-Age`)
- ✅ Excludes admin/preview URLs from caching
- ✅ Supports manual cache purging
- ✅ Non-blocking cache writes (uses `ctx.waitUntil`)

## Deployment Options

### Option 1: Cloudflare Pages Function (Recommended)

Deploy as a Pages Function to automatically intercept all requests:

1. **Create the Functions directory:**
   ```bash
   mkdir -p functions
   ```

2. **Copy the worker as middleware:**
   ```bash
   cp workers/html-cache.js functions/_middleware.js
   ```

3. **Commit and push:**
   ```bash
   git add functions/_middleware.js
   git commit -m "feat: Add HTML caching via Pages Function"
   git push
   ```

4. **Automatic deployment:**
   Cloudflare Pages will automatically deploy the function on the next push.

**Pros:**
- ✅ No additional configuration needed
- ✅ Automatically applies to all Pages deployments
- ✅ No separate worker management

**Cons:**
- ⚠️ Pages Functions are in beta (but stable)

---

### Option 2: Standalone Cloudflare Worker with Route

Deploy as a separate worker with a route to your domain:

1. **Deploy the worker:**
   ```bash
   npx wrangler deploy workers/html-cache.js --name jkcoukblog-html-cache
   ```

2. **Add route in Cloudflare Dashboard:**
   - Go to: Workers & Pages → Overview → jkcoukblog-html-cache → Settings → Triggers
   - Add Route: `jameskilby.co.uk/*`
   - Zone: `jameskilby.co.uk`
   - Save

**Pros:**
- ✅ More control over deployment
- ✅ Can use separate monitoring/logs
- ✅ Easy to disable without redeployment

**Cons:**
- ⚠️ Requires manual route configuration
- ⚠️ Separate worker management

---

### Option 3: Deploy via Wrangler (Automated)

Use the existing `wrangler.toml` configuration:

```bash
# Deploy the cache worker
npx wrangler deploy --config wrangler.toml --name jkcoukblog-html-cache

# Then add the route manually in Cloudflare Dashboard
# Or add to wrangler.toml:
# routes = [{ pattern = "jameskilby.co.uk/*", zone_name = "jameskilby.co.uk" }]
```

---

## Testing

### 1. Test Cache Miss (First Request)

```bash
curl -I https://jameskilby.co.uk/ | grep -i "x-worker-cache\|x-cache"
```

**Expected output:**
```
X-Worker-Cache: MISS
X-Cache-Date: 2026-01-01T23:00:00.000Z
```

### 2. Test Cache Hit (Second Request)

```bash
curl -I https://jameskilby.co.uk/ | grep -i "x-worker-cache\|x-cache"
```

**Expected output:**
```
X-Worker-Cache: HIT
X-Cache-Age: 15
```

### 3. Test Different Pages

```bash
# Test homepage
curl -sI https://jameskilby.co.uk/ | grep "X-Worker-Cache"

# Test a blog post
curl -sI https://jameskilby.co.uk/2025/10/some-post/ | grep "X-Worker-Cache"

# Test category page
curl -sI https://jameskilby.co.uk/category/vmware/ | grep "X-Worker-Cache"
```

### 4. Verify Performance Improvement

```bash
# Before deployment (DYNAMIC)
curl -w "\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" -o /dev/null -s https://jameskilby.co.uk/

# After deployment (HIT)
curl -w "\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" -o /dev/null -s https://jameskilby.co.uk/
```

**Expected improvement:**
- TTFB: 320ms → ~50ms (for cached requests)
- Total: 665ms → ~200ms

---

## Cache Management

### Manual Cache Purge

Purge a specific URL from cache:

```bash
curl -X GET https://jameskilby.co.uk/ -H "X-Purge-Cache: true"
```

**Response:**
```
Cache purged
```

### Automatic Cache Invalidation

The cache automatically expires after **5 minutes (300 seconds)**. After a new deployment:

1. Wait 5 minutes for automatic expiration, OR
2. Use the purge command above for immediate invalidation

### Full Cache Purge (via Cloudflare Dashboard)

1. Go to: Caching → Configuration
2. Click "Purge Everything"
3. Confirm

**Note:** This purges ALL cached content, not just HTML.

---

## Monitoring

### Check Cache Status

View cache performance in Cloudflare Dashboard:

1. **Analytics → Traffic:**
   - Cache hit ratio
   - Bandwidth saved
   - Requests served from cache

2. **Workers & Pages → jkcoukblog-html-cache → Metrics:**
   - Request count
   - CPU time
   - Success rate

### Debug Headers

The worker adds helpful headers for monitoring:

| Header | Description | Example |
|--------|-------------|---------|
| `X-Worker-Cache` | Cache status | `HIT`, `MISS`, or `BYPASS` |
| `X-Cache-Age` | Seconds since cached | `45` (for HIT only) |
| `X-Cache-Date` | When cached | `2026-01-01T23:00:00.000Z` (for MISS) |

### View Logs (Real-time)

```bash
# Tail worker logs
npx wrangler tail jkcoukblog-html-cache

# Filter for specific patterns
npx wrangler tail jkcoukblog-html-cache --format pretty
```

---

## Configuration

### Adjust Cache Duration

Edit `workers/html-cache.js` line 74:

```javascript
// Change from 300 seconds (5 minutes) to desired value
newHeaders.set('Cache-Control', 'public, max-age=300, s-maxage=300');

// Example: 10 minutes
newHeaders.set('Cache-Control', 'public, max-age=600, s-maxage=600');
```

**Recommendations:**
- **5 minutes (300s):** Good balance for frequently updated content
- **15 minutes (900s):** Better performance for stable content
- **1 hour (3600s):** Maximum for mostly static blogs

### Exclude Additional Paths

Edit `workers/html-cache.js` line 24:

```javascript
// Add more exclusions
if (url.pathname.includes('/wp-admin') || 
    url.pathname.includes('/preview') ||
    url.pathname.includes('/staging') ||
    url.pathname.startsWith('/api/')) {
  return fetch(request);
}
```

### Cache Additional Content Types

Edit `workers/html-cache.js` line 61:

```javascript
// Add JSON caching
const isHTML = contentType.includes('text/html');
const isJSON = contentType.includes('application/json');
const isCacheable = isHTML || (isJSON && url.pathname.includes('/search-index'));
```

---

## Troubleshooting

### Cache Not Working

**Symptom:** Always seeing `X-Worker-Cache: MISS`

**Solutions:**

1. **Check worker is deployed:**
   ```bash
   npx wrangler deployments list --name jkcoukblog-html-cache
   ```

2. **Verify route is active:**
   - Dashboard → Workers & Pages → jkcoukblog-html-cache → Settings → Triggers
   - Ensure route matches your domain

3. **Check cache-control headers:**
   ```bash
   curl -I https://jameskilby.co.uk/ | grep -i cache-control
   ```
   Should show: `Cache-Control: public, max-age=300, must-revalidate`

### High Cache Miss Rate

**Symptom:** Low cache hit ratio in Analytics

**Possible causes:**

1. **Query strings:** Different query params = different cache keys
2. **Short TTL:** 5 minutes might be too short for your traffic pattern
3. **Low traffic:** Not enough requests within the 5-minute window
4. **Cookies:** Request cookies affect cache keys

**Solution:** Increase cache duration to 15 minutes (900s) or normalize cache keys.

### Worker Errors

**Check logs:**
```bash
npx wrangler tail jkcoukblog-html-cache
```

**Common errors:**
- `TypeError: response.clone is not a function` → Ensure using correct fetch API
- `Cache.match is not a function` → Using Workers cache API correctly

---

## Performance Metrics

### Before Deployment

```
DNS:     1.6ms
Connect: 85ms
TLS:     194ms
TTFB:    320ms ⚠️
Total:   665ms
```

### After Deployment (Cache Hit)

```
DNS:     1.6ms
Connect: 85ms
TLS:     194ms
TTFB:    50ms  ✅ (85% improvement)
Total:   200ms ✅ (70% improvement)
```

### After Deployment (Cache Miss)

```
DNS:     1.6ms
Connect: 85ms
TLS:     194ms
TTFB:    320ms (same as before)
Total:   665ms
```

**Expected cache hit ratio:** 80-95% for typical blog traffic

---

## Cost Considerations

**Cloudflare Workers Pricing:**

- **Free tier:** 100,000 requests/day
- **Paid tier:** $5/month for 10 million requests

**Estimate for jameskilby.co.uk:**

Assuming 10,000 page views/day:
- **Daily requests:** 10,000
- **Monthly requests:** 300,000
- **Cost:** $0 (within free tier)

Even at 100,000 page views/day (3M/month), you're well within the free tier.

---

## Rollback Procedure

If you need to disable the worker:

### Pages Function Method:
```bash
git rm functions/_middleware.js
git commit -m "rollback: Disable HTML cache worker"
git push
```

### Standalone Worker Method:
1. Dashboard → Workers & Pages → jkcoukblog-html-cache
2. Settings → Triggers → Remove route
3. Or disable the worker entirely

---

## Best Practices

1. **Start with 5-minute cache:** Monitor and adjust based on content update frequency
2. **Use debug headers:** Keep them enabled to verify caching behavior
3. **Monitor cache hit ratio:** Aim for >80% in Cloudflare Analytics
4. **Purge after deployments:** Ensure fresh content after GitHub Actions deploy
5. **Test in staging first:** If using `jkcoukblog.pages.dev` for staging

---

## Integration with GitHub Actions

Add cache purging to `.github/workflows/deploy-static-site.yml`:

```yaml
- name: Purge Cloudflare cache
  if: success()
  run: |
    # Purge specific paths or entire cache
    curl -X POST "https://api.cloudflare.com/client/v4/zones/${{ secrets.CLOUDFLARE_ZONE_ID }}/purge_cache" \
      -H "Authorization: Bearer ${{ secrets.CLOUDFLARE_API_TOKEN }}" \
      -H "Content-Type: application/json" \
      --data '{"purge_everything":true}'
```

Or use Cloudflare's Wrangler:

```yaml
- name: Deploy worker and purge cache
  run: |
    npx wrangler deploy workers/html-cache.js --name jkcoukblog-html-cache
```

---

## Related Documentation

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/functions/)
- [Cache API Documentation](https://developers.cloudflare.com/workers/runtime-apis/cache/)
- `PERFORMANCE_REPORT.md` - Current performance baseline
- `IMPROVEMENTS_AND_IMPLEMENTATIONS.md` - All site improvements

---

## Questions?

For issues or questions:
1. Check worker logs: `npx wrangler tail jkcoukblog-html-cache`
2. Verify deployment: `npx wrangler deployments list`
3. Review Cloudflare Analytics for cache performance

---

**Created:** 2026-01-01  
**Version:** 1.0.0  
**Expected TTFB Improvement:** 85% (320ms → 50ms)
