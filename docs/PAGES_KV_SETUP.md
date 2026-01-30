# Cloudflare Pages KV Bindings Setup

## Problem
The Worker caching system isn't executing because jameskilby.co.uk is served by Cloudflare Pages, not a traditional Worker. Pages has priority over Worker routes, so your standalone Worker never runs.

## Solution
Use **Pages Functions** with KV bindings instead of standalone Workers.

## Current Status
✅ Pages Function middleware updated (`functions/_middleware.js`)  
❌ KV bindings not configured in Pages project  

## Setup Instructions

### 1. Bind KV Namespaces to Pages Project

You need to add the HTML_CACHE and SEARCH_INDEX KV namespaces to your Pages project:

#### Option A: Via Cloudflare Dashboard (Easiest)

1. Go to https://dash.cloudflare.com
2. Navigate to **Workers & Pages** > **jkcoukblog** (your Pages project)
3. Click **Settings** tab
4. Scroll to **Functions** section
5. Under **KV namespace bindings**, click **Add binding**
6. Add two bindings:
   
   **Binding 1:**
   - Variable name: `HTML_CACHE`
   - KV namespace: Select "HTML_CACHE" (ID: `5528672ccf0644c9bd65e7de8b629189`)
   
   **Binding 2:**
   - Variable name: `SEARCH_INDEX`  
   - KV namespace: Select "SEARCH_INDEX" (ID: `da75861d372642d4979c8611b4856ab0`)

7. Click **Save**

#### Option B: Via Wrangler CLI

```bash
# Bind HTML_CACHE
npx wrangler pages deployment tail jkcoukblog --environment production

# Note: KV bindings for Pages must be set via dashboard or wrangler.toml
```

Actually, for Pages you need to add a `wrangler.toml` at the root with Pages-specific config:

### 2. Add Environment Variable for PURGE_TOKEN

Still in Settings > Functions:

1. Under **Environment variables**, click **Add variable**
2. Add:
   - Variable name: `PURGE_TOKEN`
   - Value: `0484ed947a4c4473fe9bdb751d47135ed22b65db8e31eb07d0067a5df39d31b0`
   - Type: **Encrypted** (important!)
   - Environment: **Production**

### 3. Deploy Updated Function

The Pages Function will automatically deploy when you commit and push `functions/_middleware.js`:

```bash
git add functions/_middleware.js
git commit -m "Update Pages Function with KV caching"
git push origin main
```

Cloudflare Pages will detect the change and redeploy automatically.

### 4. Verify It's Working

Wait 1-2 minutes for deployment, then test:

```bash
# First request (should be MISS)
curl -I https://jameskilby.co.uk/

# Look for these headers:
# X-Cache-Status: MISS (or HIT on subsequent requests)
# X-Worker: pages-function-kv (if KV working)
# X-Worker: pages-function-cache-api (if KV not bound, fallback active)
# X-Cache-Views: 1 (view count, only with KV)

# Second request (should be HIT)
curl -I https://jameskilby.co.uk/
```

## How It Works Now

1. **Request arrives** → Cloudflare Pages receives it
2. **Pages Function runs** → `functions/_middleware.js` intercepts ALL requests
3. **Checks KV cache**:
   - ✅ KV bound → Uses `handleKVCache()` with smart TTL and view tracking
   - ❌ KV not bound → Falls back to `handleCacheAPI()` (Cache API)
4. **Returns cached response** or fetches from Pages assets

## Key Differences: Pages vs Workers

| Feature | Standalone Worker | Pages Function |
|---------|------------------|----------------|
| Configuration | `wrangler.toml` | Dashboard bindings |
| Deployment | `wrangler deploy` | Auto-deploy on push |
| Route priority | Low (Pages wins) | High (runs first) |
| KV binding | In `wrangler.toml` | In Dashboard |

## Fallback Behavior

The updated `_middleware.js` includes a **graceful fallback**:

- **If KV is bound**: Uses KV with view tracking and smart TTL
- **If KV not bound**: Uses Cache API (still functional, just without advanced features)

This means the caching will work immediately (with Cache API) even before you bind KV. You'll see:
- `X-Worker: pages-function-cache-api` (fallback mode)

After binding KV, you'll see:
- `X-Worker: pages-function-kv` (full KV mode)
- `X-Cache-Views: 1` (view count tracking)

## Cleanup: Remove Standalone Worker Route

Once Pages Functions are working, you can remove the standalone Worker route to avoid confusion:

```bash
# This route is now redundant since Pages has priority
npx wrangler triggers deploy
# Or just leave it - it won't execute anyway
```

## Next Steps

1. [ ] Bind KV namespaces in Dashboard (5 min)
2. [ ] Add PURGE_TOKEN environment variable (2 min)
3. [ ] Commit and push `functions/_middleware.js` (done)
4. [ ] Wait for Pages deployment (2 min)
5. [ ] Test with curl (1 min)

**Total time: ~10 minutes**
