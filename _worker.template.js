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
const PATH_MANIFEST_RAW = /*__PATH_MANIFEST_START__*/null/*__PATH_MANIFEST_END__*/;
const PATH_MANIFEST = PATH_MANIFEST_RAW ? new Set(PATH_MANIFEST_RAW) : null;

// Build-time substitution: scripts/stamp_worker_manifest.py reads the
// Content-Security-Policy line from the repo-root `_headers` file and
// replaces the placeholder below with that string literal. `_headers`
// stays the single source of truth — the worker just consumes it so
// CSP ships on every worker-built Response (Pages does NOT layer
// `_headers` rules over Response objects returned by `_worker.js`;
// only `env.ASSETS.fetch()` responses get them). If the placeholder
// is still `null` (template unchanged, local dev) CSP is omitted —
// same as before, fail-open.
const CSP_FROM_HEADERS = /*__CSP_FROM_HEADERS_START__*/null/*__CSP_FROM_HEADERS_END__*/;

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

    // ── /feed/ → /feed/index.xml (301 permanent) ────────────────────────────
    // _redirects is ignored in Advanced Mode Worker mode, so the redirect must
    // live here. Without this, /feed/ would 404 (the meta-refresh HTML shim
    // was deleted because Google read it as a soft redirect when listed in
    // the sitemap).
    if (path === '/feed' || path === '/feed/') {
      return Response.redirect('https://jameskilby.co.uk/feed/index.xml', 301);
    }
    // ────────────────────────────────────────────────────────────────────────

    // ── /YYYY/MM/DD/<slug>/ → /YYYY/MM/<slug>/ (301 permanent) ──────────────
    // Legacy WordPress permalink format included the day. The static
    // generator emits /YYYY/MM/<slug>/ only, so day-format URLs from old
    // backlinks, archived snapshots and shared social-card links 404 with
    // no recovery. Rewrite to the monthly canonical so link equity isn't
    // lost. Matches /<4-digit>/<2-digit>/<2-digit>/<rest> only — won't
    // collide with /wp-content/... or other top-level paths.
    const dayPermalinkMatch = path.match(/^\/(\d{4})\/(\d{2})\/\d{2}\/(.+)$/);
    if (dayPermalinkMatch) {
      const [, year, month, rest] = dayPermalinkMatch;
      return Response.redirect(
        `https://jameskilby.co.uk/${year}/${month}/${rest}${url.search}`,
        301
      );
    }
    // ────────────────────────────────────────────────────────────────────────

    // ── /about-me/ → /about-james-kilby-solution-architect/ (301 permanent) ─
    // The About Me page slug was renamed in WordPress (probably via a
    // Rank Math / permalink-manager rewrite); the old URL now 404s,
    // breaking external backlinks, social-card shares and historical mentions.
    // Preserve link equity with a permanent redirect to the new slug.
    if (path === '/about-me' || path === '/about-me/') {
      return Response.redirect(
        `https://jameskilby.co.uk/about-james-kilby-solution-architect/${url.search}`,
        301
      );
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

    // ── Soft-404 fix for the bare 404 page ───────────────────────────────────
    // /404.html exists in the static output (Cloudflare Pages uses it as the
    // SPA fallback), but a direct GET to /404 or /404.html previously returned
    // 200 with 404-styled content — a soft-404 that Google flags as
    // "Discovered – currently not indexed". Force the proper 404 status here.
    if (path === '/404' || path === '/404/' || path === '/404.html') {
      return buildNotFoundResponse(env, url.hostname);
    }
    // ────────────────────────────────────────────────────────────────────────

    // ── Plausible Analytics proxy ────────────────────────────────────────────
    // Serve script.js and /api/event from the same origin so:
    //  - ad blockers don't recognise the third-party host
    //  - the script is edge-cached at Cloudflare, not fetched from the VM
    //  - one fewer TLS handshake on the visitor's first paint
    // Must run before the GET-only guard below — /api/event is a POST.
    if (path === '/js/script.js' && request.method === 'GET') {
      return handlePlausibleScript(request);
    }
    if (path === '/api/event' && request.method === 'POST') {
      return handlePlausibleEvent(request);
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
    const cachedRes = await env.HTML_CACHE.getWithMetadata(cacheKey, { type: 'text' });
    const cached = cachedRes && cachedRes.value;
    const cachedMeta = (cachedRes && cachedRes.metadata) || {};

    if (cached) {
      const ttl = getTTL(path);
      const etag = await computeETag(cached);
      const lastModified = cachedMeta.cached_at
        ? new Date(cachedMeta.cached_at).toUTCString()
        : new Date().toUTCString();

      // 304 Not Modified — Googlebot honours this and skips downloading the
      // body, which cuts our crawl-budget cost on pages that haven't changed.
      // If-Modified-Since is the path that actually fires for Googlebot (CF
      // Pages strips ETag on text/html 200, so crawlers never capture it for
      // If-None-Match). Both checks are wired so any client that does have
      // an ETag still gets a 304.
      if (matchesIfNoneMatch(request, etag) ||
          matchesIfModifiedSince(request, lastModified)) {
        return new Response(null, {
          status: 304,
          headers: {
            'ETag': etag,
            'Last-Modified': lastModified,
            'Cache-Control': `public, max-age=${ttl}`,
            'X-Cache-Status': 'HIT-304',
            'X-Worker': 'advanced-worker-kv',
            ...getSecurityHeaders(hostname)
          }
        });
      }

      return new Response(cached, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': `public, max-age=${ttl}`,
          'ETag': etag,
          'Last-Modified': lastModified,
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

    // Return with our headers (plus ETag/Last-Modified for crawl efficiency).
    const etag = await computeETag(html);
    const lastModified = new Date(nowSec * 1000).toUTCString();
    if (matchesIfNoneMatch(request, etag) ||
        matchesIfModifiedSince(request, lastModified)) {
      return new Response(null, {
        status: 304,
        headers: {
          'ETag': etag,
          'Last-Modified': lastModified,
          'Cache-Control': `public, max-age=${ttl}`,
          'X-Cache-Status': 'MISS-304',
          'X-Worker': 'advanced-worker-kv',
          ...getSecurityHeaders(hostname)
        }
      });
    }
    return new Response(html, {
      status: response.status,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': `public, max-age=${ttl}`,
        'ETag': etag,
        'Last-Modified': lastModified,
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
  // Key on the path only, mirroring the KV path's pathname-based keys —
  // otherwise ?utm_source=… style tracking params fragment the cache into
  // unlimited per-query copies that each go stale on their own clock.
  const cacheKeyUrl = new URL(request.url);
  cacheKeyUrl.search = '';
  const cacheKey = new Request(cacheKeyUrl.toString(), { method: 'GET' });

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

    // Always apply our smart TTL (Cache-Control) to HTML, overriding any
    // upstream default. The previous `if (!has(...))` guard was meant to
    // respect the `_headers /*.html` rule (max-age=300), but that rule only
    // matches literal `.html` paths — pretty-URL post permalinks like
    // `/2017/05/foo/` skipped it entirely and inherited Cloudflare Pages'
    // `max-age=0, must-revalidate` default, leaving browsers unable to
    // soft-cache repeat visits. Aligning the browser cache with the smart
    // KV TTL gives readers proper local caching without violating the
    // "absolute-expiry, view-counts don't reset the clock" invariant
    // (browser cache is a separate clock from the KV cache).
    newHeaders.set('Cache-Control', `public, max-age=${getTTL(path)}`);

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
 *
 * Content-Security-Policy: stamped in from the repo-root `_headers` file at
 * build time (see CSP_FROM_HEADERS above and scripts/stamp_worker_manifest.py).
 * `_headers` remains the single source of truth — but Cloudflare Pages only
 * applies its rules to responses fetched via `env.ASSETS.fetch()`. Brand-new
 * `Response` objects returned by `_worker.js` (e.g. the KV-cached HTML path)
 * don't get `_headers` layered on, so the worker must emit CSP itself.
 * Validation lives in scripts/test_csp.py.
 *
 * Pass hostname to automatically add X-Robots-Tag: noindex on the Pages preview domain.
 */
function getSecurityHeaders(hostname = '') {
  const headers = {
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    // Keep in sync with the Permissions-Policy line in _headers — the worker
    // emits headers for cache HITs, _headers covers direct ASSETS responses.
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()'
  };

  if (CSP_FROM_HEADERS) {
    headers['Content-Security-Policy'] = CSP_FROM_HEADERS;
  }

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
      path.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|json|xml|txt|webp|avif|br|gz|webmanifest)$/)) {
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
 * Compute a weak ETag for an HTML body. SHA-1 hex of the bytes, prefixed
 * with W/ — the response may be served from KV cache, so the byte-for-byte
 * "strong" guarantee doesn't quite hold.
 *
 * NOTE: Cloudflare Pages strips the ETag header from text/html 200 responses
 * (it auto-generates its own per static asset, which collides). Empirically
 * verified — see PR #48. Pages does NOT strip ETag on 304 responses, so the
 * If-None-Match path still works for any client that captured the ETag
 * out-of-band. The primary revalidation mechanism Googlebot can actually
 * use here is If-Modified-Since against our Last-Modified header, which
 * Pages does NOT strip.
 */
async function computeETag(text) {
  const buf = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest('SHA-1', buf);
  const hex = Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
  return `W/"${hex}"`;
}

/**
 * Return true iff the request's If-None-Match header matches the given ETag.
 * Tolerates the weak-prefix and quoted/unquoted variants clients may send.
 */
function matchesIfNoneMatch(request, etag) {
  const header = request.headers.get('if-none-match');
  if (!header) return false;
  const normalize = s => s.replace(/^W\//, '').replace(/^"|"$/g, '');
  const wanted = normalize(etag);
  return header.split(',').some(t => normalize(t.trim()) === wanted);
}

/**
 * Return true iff the request's If-Modified-Since is at or after the
 * response's Last-Modified date. This is what Googlebot uses in practice
 * for HTML revalidation. Granularity is one second — the HTTP spec rounds
 * to whole-second precision for both headers.
 */
function matchesIfModifiedSince(request, lastModifiedHttpDate) {
  const header = request.headers.get('if-modified-since');
  if (!header) return false;
  const since = Date.parse(header);
  const lm = Date.parse(lastModifiedHttpDate);
  if (Number.isNaN(since) || Number.isNaN(lm)) return false;
  return Math.floor(lm / 1000) <= Math.floor(since / 1000);
}

// ── Plausible proxy ────────────────────────────────────────────────────────
// Upstream Plausible CE instance. Hostname-only; the proxy always targets
// /js/script.js and /api/event so there's no path templating.
const PLAUSIBLE_ORIGIN = 'https://plausible.jameskilby.cloud';

/**
 * Proxy GET /js/script.js → Plausible. Edge-cached so the VM only sees a
 * trickle of requests per PoP per hour.
 */
async function handlePlausibleScript(request) {
  const upstream = await fetch(`${PLAUSIBLE_ORIGIN}/js/script.js`, {
    method: 'GET',
    cf: { cacheEverything: true, cacheTtl: 3600 }
  });

  // Strip hop-by-hop headers; force a sane cache policy for the browser.
  const headers = new Headers();
  headers.set('Content-Type', upstream.headers.get('Content-Type') || 'application/javascript');
  headers.set('Cache-Control', 'public, max-age=86400, stale-while-revalidate=3600');
  headers.set('X-Worker', 'plausible-proxy');

  return new Response(upstream.body, { status: upstream.status, headers });
}

/**
 * Proxy POST /api/event → Plausible. Forwards the visitor IP via
 * X-Forwarded-For (Plausible needs it for GeoIP + unique-visitor hashing)
 * and the User-Agent (needed for the same hash). Never cached.
 */
async function handlePlausibleEvent(request) {
  const headers = new Headers();
  headers.set('Content-Type', request.headers.get('Content-Type') || 'application/json');
  const ua = request.headers.get('User-Agent');
  if (ua) headers.set('User-Agent', ua);
  const clientIp = request.headers.get('CF-Connecting-IP');
  if (clientIp) headers.set('X-Forwarded-For', clientIp);

  const upstream = await fetch(`${PLAUSIBLE_ORIGIN}/api/event`, {
    method: 'POST',
    headers,
    body: request.body
  });

  const respHeaders = new Headers();
  respHeaders.set('Cache-Control', 'no-store');
  respHeaders.set('X-Worker', 'plausible-proxy');
  const ct = upstream.headers.get('Content-Type');
  if (ct) respHeaders.set('Content-Type', ct);

  return new Response(upstream.body, { status: upstream.status, headers: respHeaders });
}
// ───────────────────────────────────────────────────────────────────────────

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
