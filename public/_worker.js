/**
 * Cloudflare Pages Advanced Mode Worker
 *
 * This worker runs on ALL requests (including static files) to jameskilby.co.uk
 * Provides smart HTML caching with KV storage and selective purge
 *
 * Features:
 * - Smart TTL: 5min homepage, 15min recent posts, 1hr old posts
 * - Selective cache purge via /.purge endpoint
 * - Falls back to Cache API if KV unavailable
 * - Serves static assets from Pages
 * - Soft-404 guard: when the Pages project is in SPA mode, ASSETS returns
 *   index.html (200) for missing paths. We gate on a build-time manifest of
 *   real content paths and convert unknown paths into a real 404 so Bing /
 *   Google don't index ghost URLs.
 */

// Build-time substitution: scripts/generate_path_manifest.py replaces the
// placeholder below with an Array literal of all legitimate HTML paths
// before `cp _worker.template.js public/_worker.js` in the deploy workflow.
// If the placeholder is still present (local dev / template unchanged) the
// soft-404 guard is disabled — the worker behaves exactly as before.
const PATH_MANIFEST_RAW = /*__PATH_MANIFEST_START__*/["/","/2017/05/money-saving-uk-version","/2018/01/lab-storage","/2018/01/nutanix-ce","/2018/03/aws-for-beginners1","/2018/03/cloudflare","/2018/05/aws-status-page-monitoring-included","/2018/06/nutanix-command-reference-guide","/2018/10/and-now-for-something-completely-different","/2018/12/new-laptop","/2019/01/whats-in-my-backpack","/2019/02/lab-storage-2","/2019/12/aws-solution-architect-associate","/2019/12/monitoring-vmc-part-1","/2020/06/veeamon2020","/2020/07/i3en","/2020/07/nutanix-ncp","/2020/09/vmc-host-errors","/2020/09/vmware-certified-master-specialist-hci-2020","/2020/12/my-first-pull","/2021/01/hashicorp-packer","/2021/01/my-home-office-setup-upgrades","/2021/02/apple-content-caching","/2022/01/cloudflare-workers-limits-of-the-free-tier","/2022/01/lab-update-part-1-compute","/2022/01/lab-update-part-2-storage","/2022/01/lab-update-part-3-network","/2022/01/lab-update-part-5-desired-workloads","/2022/01/web-development","/2022/01/wrangler-and-node-versions","/2022/10/how-i-moved-my-wordpress-site-to-cloudflare-pages","/2022/10/starlink","/2022/11/homelab-bad-days-almost","/2022/12/100gb-s-in-my-homelab-sort-of","/2022/12/forcing-an-upgrade-to-vsphere-8","/2022/12/use-portainer-in-a-homelab-with-github","/2023/04/intel-optane","/2023/05/homelab-storage-refresh-part-1","/2023/05/how-to-take-a-wordpress-site-and-publish-it-as-a-static-site-on-cloudflare-pages","/2023/05/runecast-remediation-scripts","/2023/10/going-out-with-a-bang","/2023/10/vgpu-setup-in-my-homelab","/2023/11/advanced-deploy-vmware-vsphere-7-x-3v0-22-21n","/2023/11/analytics-in-a-privacy-focused-world","/2023/11/configuring-a-zen-internet-and-city-fibre-connection-with-a-3rd-party-router","/2023/11/truenas-scale-useful-commands","/2023/11/vsan-esa-and-the-improvements-it-brings-to-vmc","/2024/01/holodeck-cpu-fixes","/2024/01/multihost-holodeck-vcf","/2024/06/unifi-dhcp-option-43","/2024/07/new-nodes","/2024/09/can-you-really-squeeze-96tb-in-1u","/2024/09/home-network-upgrade","/2024/10/self-hosting-ai-stack-using-vsphere-docker-and-nvidia-gpu","/2024/12/zfs-on-vmware","/2025/01/how-i-migrated-from-pocket-to-hoarder-and-introduced-some-ai-along-the-way","/2025/04/warp-the-intelligent-terminal","/2025/05/vmc-quick-sizing-guide","/2025/08/vmc-host-deepdive","/2025/09/managing-my-homelab-with-semaphoreui","/2025/10/how-i-deploy-my-blog-as-a-static-website-with-github-actions-and-cloudflare","/2025/12/time-in-a-vmc-environment","/2025/12/ubuntu-disk-expansion-steps","/2025/12/vsan-cluster-shutdown","/2026/01/using-content-libraries-in-vmc-to-deploy-software-faster","/2026/01/web-development-improvements","/2026/02/automating-the-deployment-of-my-ai-homelab-and-other-improvements","/2026/03/my-self-hosted-ai-stack-a-technical-deep-dive","/2026/03/octopus-agile-battery-solar-calculator","/2026/04/automated-vcf-9-offline-depot","/2026/04/my-self-hosted-ai-stack-infrastructure-deep-dive-part-2","/2026/04/new-vmc-host-i7i-metal-24xl","/2026/04/packer-vsphere-golden-images","/2026/04/vsphere-power-management-driven-by-ansible","/2026/05/auto-documenting-mikrotik-switch-ports-with-ansible-and-lldp-neighbours","/404","/about-me","/category/ansible","/category/apple","/category/artificial-intelligence","/category/automation","/category/aws","/category/cloudflare","/category/consulting","/category/containers","/category/devops","/category/docker","/category/github","/category/homelab","/category/hosting","/category/kubernetes","/category/mikrotik","/category/money","/category/networking","/category/nutanix","/category/nvidia","/category/personal","/category/runecast","/category/storage","/category/synology","/category/traefik","/category/truenas-scale","/category/ubuntu","/category/veeam","/category/vexpert","/category/vmware","/category/vmware/vcf","/category/vmware/vmware-cloud-on-aws","/category/vmware/vsan-vmware","/category/vsphere","/category/wordpress","/changelog","/evs","/feed","/homelab-software","/lab","/media","/page/2","/page/3","/page/4","/page/5","/page/6","/page/7","/privacy-policy-2","/stats","/tag/account-setup","/tag/ai","/tag/analytics","/tag/ansible","/tag/apple","/tag/architecture","/tag/artificial-intelligence","/tag/automation","/tag/aws","/tag/bash","/tag/blog","/tag/blogging","/tag/brew","/tag/cache","/tag/certification","/tag/certifications","/tag/charity","/tag/city-fibre","/tag/cli","/tag/clickhouse","/tag/cloudflare","/tag/cloudflare-pages","/tag/comfyui","/tag/containers","/tag/content-library","/tag/cpu","/tag/desired-state","/tag/devops","/tag/dhcp","/tag/disk-expand","/tag/docker","/tag/energy","/tag/epic","/tag/failure","/tag/free","/tag/git","/tag/github","/tag/github-actions","/tag/hashicorp","/tag/hoarder","/tag/holodeck","/tag/homebrew","/tag/homelab","/tag/homeoffice","/tag/hosting","/tag/https","/tag/i7i","/tag/iac","/tag/infrastructure","/tag/ingress","/tag/intel","/tag/lambda","/tag/langfuse","/tag/lets-encrypt","/tag/lldp","/tag/macbook-air","/tag/mikrotik","/tag/minio","/tag/multihost","/tag/n8n","/tag/nas","/tag/networking","/tag/nginx","/tag/node","/tag/ntp","/tag/nutanix","/tag/nvidia","/tag/nvme","/vmc"]/*__PATH_MANIFEST_END__*/;
const PATH_MANIFEST = PATH_MANIFEST_RAW ? new Set(PATH_MANIFEST_RAW) : null;

/**
 * Is this path a known content URL?
 *
 * Returns true if the manifest is missing (fail-open during local dev), or
 * if the path matches one of the valid HTML paths baked at build time. A
 * path is normalised by stripping the trailing slash except for '/' itself
 * so '/about-me' and '/about-me/' both resolve.
 */
function isKnownContentPath(path) {
  if (!PATH_MANIFEST) return true;
  if (path === '/' || path === '/index.html') return true;
  const normalised = path.length > 1 && path.endsWith('/') ? path.slice(0, -1) : path;
  return PATH_MANIFEST.has(normalised) || PATH_MANIFEST.has(normalised + '/');
}

/**
 * Build a 404 response. Tries to serve /404.html from ASSETS; falls back to
 * a tiny inline body if that file isn't present.
 */
async function buildNotFoundResponse(env, hostname) {
  try {
    const notFoundReq = new Request('https://internal/404.html');
    const r = await env.ASSETS.fetch(notFoundReq);
    if (r.ok) {
      const body = await r.text();
      return new Response(body, {
        status: 404,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'public, max-age=60, must-revalidate',
          'X-Cache-Status': 'SOFT404-FIXED',
          'X-Worker': 'advanced-worker',
          'X-Robots-Tag': 'noindex',
          ...getSecurityHeaders(hostname)
        }
      });
    }
  } catch (_) {
    // fall through to inline body
  }
  return new Response(
    '<!doctype html><meta charset=utf-8><title>Not Found</title><h1>404 Not Found</h1>',
    {
      status: 404,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'public, max-age=60, must-revalidate',
        'X-Cache-Status': 'SOFT404-FIXED',
        'X-Worker': 'advanced-worker',
        'X-Robots-Tag': 'noindex',
        ...getSecurityHeaders(hostname)
      }
    }
  );
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // ── www → non-www redirect (301 permanent) ───────────────────────────────
    // Must be first — _redirects is ignored in Advanced Mode Worker deployments.
    // Fixes Googlebot crawl errors on www.jameskilby.co.uk (GSC: "Problems last week").
    if (url.hostname === 'www.jameskilby.co.uk') {
      return Response.redirect(`https://jameskilby.co.uk${url.pathname}${url.search}`, 301);
    }
    // ────────────────────────────────────────────────────────────────────────

    // ── Admin / diagnostic endpoints ────────────────────────────────────────
    // These must be checked BEFORE the GET-only guard so POST purges work,
    // and BEFORE shouldCache so they are never accidentally cached.

    // Handle purge requests — requires POST + valid token (#18)
    if (path === '/.purge') {
      return handlePurge(request, env);
    }

    // Handle diagnostic endpoint — gated by PURGE_TOKEN (#17)
    if (path === '/diagnostic') {
      return handleDiagnostic(request, env);
    }

    // Handle trace endpoint — gated by PURGE_TOKEN (#17)
    if (path === '/trace') {
      return handleTrace(request, env);
    }

    // Block indexing of the Cloudflare Pages preview domain. Serve a
    // disallow-all robots.txt so crawlers that honour robots.txt never fetch
    // any URL on pages.dev. HTML responses on this host also get
    // X-Robots-Tag: noindex via getSecurityHeaders() below.
    if (url.hostname === 'jkcoukblog.pages.dev' && path === '/robots.txt') {
      return new Response('User-agent: *\nDisallow: /\n', {
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'Cache-Control': 'public, max-age=3600',
          'X-Robots-Tag': 'noindex, nofollow'
        }
      });
    }
    // ────────────────────────────────────────────────────────────────────────

    // Only cache GET requests
    if (request.method !== 'GET') {
      return env.ASSETS.fetch(request);
    }
    
    // Handle test endpoint
    if (path === '/test') {
      return new Response(JSON.stringify({
        message: 'Pages Functions are working!',
        timestamp: new Date().toISOString(),
        path: request.url,
        mode: 'advanced-worker'
      }), {
        headers: {
          'Content-Type': 'application/json',
          'X-Function-Test': 'SUCCESS',
          'X-Worker-Mode': 'advanced'
        }
      });
    }
    
    // Don't cache assets or special paths
    if (!shouldCache(path)) {
      return env.ASSETS.fetch(request);
    }
    
    // Try KV cache if available (with fallback to Cache API)
    if (env.HTML_CACHE) {
      return handleKVCache(request, env, ctx, path, url.hostname);
    }

    // Fallback to Cache API if KV not bound
    return handleCacheAPI(request, env, ctx, path, url.hostname);
  }
};

/**
 * Handle caching with KV (preferred method)
 *
 * `ctx` MUST be passed in so we can use ctx.waitUntil() for KV writes.
 * Referencing `ctx` from the enclosing scope would throw ReferenceError
 * because this is a module-top-level function, not a closure inside fetch().
 */
async function handleKVCache(request, env, ctx, path, hostname) {
  try {
    // Soft-404 guard: unknown content paths must never be cached or served
    // as 200. Runs BEFORE the KV lookup so poisoned historical entries
    // (written before this guard existed) stop bleeding through. See
    // scripts/purge_soft404_kv_cache.py for a one-shot cleanup of the
    // existing poisoned keys.
    if (!isKnownContentPath(path)) {
      return buildNotFoundResponse(env, hostname);
    }

    const cacheKey = `html:${path}`;
    const cached = await env.HTML_CACHE.get(cacheKey, { type: 'text' });

    if (cached) {
      const ttl = getTTL(path);

      return new Response(cached, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': `public, max-age=${ttl}`,
          'X-Cache-Status': 'HIT',
          'X-Worker': 'advanced-worker-kv',
          ...getSecurityHeaders(hostname)
        }
      });
    }

    // Fetch from Pages assets
    const response = await env.ASSETS.fetch(request);

    // Don't cache non-successful responses
    if (!response.ok) {
      return response;
    }

    // Only cache HTML
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('text/html')) {
      return response;
    }

    // Clone before reading body
    const html = await response.text();
    const ttl = getTTL(path); // E: compute once
    const nowSec = Math.floor(Date.now() / 1000);
    const absExpiry = nowSec + ttl; // L: fixed absolute expiry stored in metadata

    // Store in KV without blocking the response. ctx.waitUntil keeps the
    // worker alive until the put completes — a bare fire-and-forget can be
    // aborted by the runtime when the response is sent.
    ctx.waitUntil(
      env.HTML_CACHE.put(cacheKey, html, {
        expiration: absExpiry, // L: absolute expiry — KV evicts after ttl seconds
        metadata: {
          cached_at: new Date(nowSec * 1000).toISOString(),
          path: path
        }
      }).catch(err => console.error('KV cache write failed:', err))
    );

    // Return with our headers
    return new Response(html, {
      status: response.status,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': `public, max-age=${ttl}`,
        'X-Cache-Status': 'MISS',
        'X-Cache-TTL': ttl.toString(),
        'X-Worker': 'advanced-worker-kv',
        ...getSecurityHeaders(hostname)
      }
    });
  } catch (error) {
    // If KV fails, fall back to Cache API
    console.error('KV cache error:', error);
    return handleCacheAPI(request, env, ctx, path, hostname);
  }
}

/**
 * Fallback: Cache API (if KV unavailable, or if handleKVCache throws).
 *
 * `ctx` is required so the cache.put on a MISS can run via waitUntil
 * instead of blocking the response.
 */
async function handleCacheAPI(request, env, ctx, path, hostname = '') {
  // Mirror the KV-path soft-404 guard so the Cache-API fallback path (when
  // HTML_CACHE binding is missing) also refuses to serve ghost URLs.
  if (!isKnownContentPath(path)) {
    return buildNotFoundResponse(env, hostname);
  }

  const cache = caches.default;
  const cacheKey = new Request(request.url, request);

  let response = await cache.match(cacheKey);

  if (response) {
    const newHeaders = new Headers(response.headers);
    newHeaders.set('X-Cache-Status', 'HIT');
    newHeaders.set('X-Worker', 'advanced-worker-cache-api');

    // Add security headers
    const securityHeaders = getSecurityHeaders(hostname);
    Object.entries(securityHeaders).forEach(([key, value]) => {
      newHeaders.set(key, value);
    });

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders
    });
  }

  response = await env.ASSETS.fetch(request);

  if (response.ok && response.headers.get('content-type')?.includes('text/html')) {
    const responseToCache = response.clone();
    const newHeaders = new Headers(responseToCache.headers);

    if (!newHeaders.has('Cache-Control')) {
      newHeaders.set('Cache-Control', `public, max-age=${getTTL(path)}`);
    }

    newHeaders.set('X-Cache-Status', 'MISS');
    newHeaders.set('X-Worker', 'advanced-worker-cache-api');

    // Add security headers
    const securityHeaders = getSecurityHeaders(hostname);
    Object.entries(securityHeaders).forEach(([key, value]) => {
      newHeaders.set(key, value);
    });
    
    const cachedResponse = new Response(responseToCache.body, {
      status: responseToCache.status,
      headers: newHeaders
    });

    // Write to the edge cache without blocking the response. The previous
    // `await cache.put(...)` made every MISS pay the put latency before the
    // user got their HTML.
    ctx.waitUntil(
      cache.put(cacheKey, cachedResponse)
        .catch(err => console.error('Cache API write failed:', err))
    );

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders
    });
  }
  
  return response;
}

/**
 * Get security headers for all responses.
 * Pass hostname to automatically add X-Robots-Tag: noindex on the Pages preview domain.
 */
function getSecurityHeaders(hostname = '') {
  const headers = {
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' plausible.io plausible.jameskilby.cloud https://utteranc.es cdn.credly.com cdn.youracclaim.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' plausible.io plausible.jameskilby.cloud https://api.github.com; frame-src 'self' plausible.jameskilby.cloud https://utteranc.es https://www.youtube.com https://youtube.com https://embed.acast.com https://www.credly.com https://www.youracclaim.com;",
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
  };

  // Prevent the Cloudflare Pages preview domain from appearing in search results
  if (hostname === 'jkcoukblog.pages.dev') {
    headers['X-Robots-Tag'] = 'noindex, nofollow';
  }

  return headers;
}

/**
 * Determine if path should be cached
 */
function shouldCache(path) {
  if (path.includes('/wp-admin') ||
      path.includes('/preview') ||
      path.startsWith('/api/') ||       // JSON post data for search
      path.startsWith('/markdown/') ||  // Raw markdown source files (#19)
      path.startsWith('/.well-known/') ||
      path === '/diagnostic' ||
      path === '/trace' ||
      path === '/test' ||
      path.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|json|xml|txt|webp|avif|br|gz)$/)) {
    return false;
  }

  return true;
}

/**
 * Smart TTL based on URL pattern
 */
function getTTL(path) {
  // Homepage - 5 minutes
  if (path === '/' || path === '/index.html') {
    return 300;
  }

  // Recent posts - 15 minutes (this month or last month)
  const now = new Date(); // F: create Date once
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1; // 1-12
  const pathMatch = path.match(/^\/(\d{4})\/(\d{2})\//);
  if (pathMatch) {
    const year = parseInt(pathMatch[1]);
    const month = parseInt(pathMatch[2]);

    // Express "post age" in whole months to handle the January→December
    // boundary correctly.  When currentMonth=1, currentMonth-1 would be 0,
    // making month >= 0 always true (all posts "recent") — using the age
    // formula avoids that bug.
    const postAgeMonths = (currentYear - year) * 12 + (currentMonth - month);
    if (postAgeMonths <= 1) {
      return 900; // 15 minutes
    }
  }

  // Older content - 1 hour
  return 3600;
}

/**
 * Handle selective cache purge — POST only (#18)
 */
async function handlePurge(request, env) {
  // Require POST — GET would be idempotent-safe but purge is destructive (#18)
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed — use POST', {
      status: 405,
      headers: { Allow: 'POST' }
    });
  }

  const url = new URL(request.url);
  const purgeToken = request.headers.get('X-Purge-Token');

  if (!env.PURGE_TOKEN || purgeToken !== env.PURGE_TOKEN) {
    return new Response('Unauthorized', { status: 401 });
  }

  const all = url.searchParams.get('all');
  const path = url.searchParams.get('path');

  // Purge all: iterate the KV namespace and delete every cached HTML entry
  if (all === 'true') {
    let purgedCount = 0;
    const cache = caches.default;

    if (env.HTML_CACHE) {
      let cursor = undefined;
      do {
        const list = await env.HTML_CACHE.list({ cursor });
        const deletes = list.keys.map(async (key) => {
          await env.HTML_CACHE.delete(key.name);
          // Also clear corresponding Cache API entry
          if (key.name.startsWith('html:')) {
            const cachePath = key.name.slice(5); // strip "html:" prefix
            await cache.delete(new Request(`${url.origin}${cachePath}`));
          }
        });
        await Promise.all(deletes);
        purgedCount += list.keys.length;
        cursor = list.list_complete ? undefined : list.cursor;
      } while (cursor);
    }

    return new Response(JSON.stringify({
      success: true,
      purged: 'all',
      count: purgedCount,
      timestamp: new Date().toISOString()
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  if (!path) {
    return new Response('Missing path or all parameter', { status: 400 });
  }

  // Delete from KV if available
  if (env.HTML_CACHE) {
    const cacheKey = `html:${path}`;
    await env.HTML_CACHE.delete(cacheKey);
  }

  // Also clear from Cache API
  const cache = caches.default;
  const cacheKey = new Request(`${url.origin}${path}`); // use request origin, not hardcoded domain
  await cache.delete(cacheKey);

  return new Response(JSON.stringify({
    success: true,
    purged: path,
    timestamp: new Date().toISOString()
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}

/**
 * Handle diagnostic endpoint — gated by PURGE_TOKEN (#17)
 */
async function handleDiagnostic(request, env) {
  const token = request.headers.get('X-Purge-Token');
  if (!env.PURGE_TOKEN || token !== env.PURGE_TOKEN) {
    return new Response('Unauthorized', { status: 401 });
  }

  const diagnostics = {
    timestamp: new Date().toISOString(),
    url: request.url,
    method: request.method,
    mode: 'advanced-worker',
    bindings: {
      HTML_CACHE: env.HTML_CACHE ? 'BOUND' : 'NOT BOUND',
      SEARCH_INDEX: env.SEARCH_INDEX ? 'BOUND' : 'NOT BOUND',
      PURGE_TOKEN: env.PURGE_TOKEN ? 'SET' : 'NOT SET',
      ASSETS: env.ASSETS ? 'BOUND' : 'NOT BOUND'
    },
    cache_api: typeof caches !== 'undefined' ? 'AVAILABLE' : 'NOT AVAILABLE'
  };
  
  // Try to test KV if bound
  if (env.HTML_CACHE) {
    try {
      const testKey = 'diagnostic:test';
      const testValue = 'test-value';
      
      await env.HTML_CACHE.put(testKey, testValue, { expirationTtl: 60 });
      const retrieved = await env.HTML_CACHE.get(testKey);
      
      diagnostics.kv_test = {
        status: retrieved === testValue ? 'WORKING' : 'FAILED',
        written: testValue,
        retrieved: retrieved
      };
      
      await env.HTML_CACHE.delete(testKey);
    } catch (error) {
      diagnostics.kv_test = {
        status: 'ERROR',
        error: error.message
      };
    }
  }
  
  return new Response(JSON.stringify(diagnostics, null, 2), {
    headers: {
      'Content-Type': 'application/json',
      'X-Diagnostic': 'SUCCESS',
      'X-Worker-Mode': 'advanced',
      'Cache-Control': 'no-store'
    }
  });
}

/**
 * Handle trace endpoint — gated by PURGE_TOKEN (#17)
 */
async function handleTrace(request, env) {
  const token = request.headers.get('X-Purge-Token');
  if (!env.PURGE_TOKEN || token !== env.PURGE_TOKEN) {
    return new Response('Unauthorized', { status: 401 });
  }

  const url = new URL(request.url);
  const testPath = url.searchParams.get('path') || '/';
  
  const trace = {
    test_path: testPath,
    method: 'GET',
    mode: 'advanced-worker',
    should_cache: shouldCache(testPath),
    ttl: getTTL(testPath),
    checks: {
      has_wp_admin: testPath.includes('/wp-admin'),
      has_preview: testPath.includes('/preview'),
      starts_with_api: testPath.startsWith('/api/'),
      starts_with_well_known: testPath.startsWith('/.well-known/'),
      has_file_extension: testPath.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|json|xml|txt|webp|avif|br|gz)$/) !== null
    },
    kv_status: env.HTML_CACHE ? 'BOUND' : 'NOT BOUND',
    middleware_decision: null
  };
  
  if (trace.should_cache) {
    if (env.HTML_CACHE) {
      trace.middleware_decision = 'Would use KV cache (handleKVCache)';
    } else {
      trace.middleware_decision = 'Would use Cache API (handleCacheAPI)';
    }
  } else {
    trace.middleware_decision = 'Would skip caching (serve from ASSETS)';
  }
  
  return new Response(JSON.stringify(trace, null, 2), {
    headers: {
      'Content-Type': 'application/json',
      'X-Trace': 'SUCCESS',
      'X-Worker-Mode': 'advanced',
      'Cache-Control': 'no-store'
    }
  });
}
