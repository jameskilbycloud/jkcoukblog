/**
 * Cloudflare Pages Advanced Mode Worker
 * 
 * This worker runs on ALL requests (including static files) to jameskilby.co.uk
 * Provides smart HTML caching with KV storage, view tracking, and selective purge
 * 
 * Features:
 * - Smart TTL: 5min homepage, 15min recent posts, 1hr old posts
 * - View count tracking in KV metadata
 * - Selective cache purge via /.purge endpoint
 * - Falls back to Cache API if KV unavailable
 * - Serves static assets from Pages
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

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
      return handleKVCache(request, env, path);
    }
    
    // Fallback to Cache API if KV not bound
    return handleCacheAPI(request, env, path);
  }
};

/**
 * Handle caching with KV (preferred method)
 */
async function handleKVCache(request, env, path) {
  try {
    const cacheKey = `html:${path}`;
    const cached = await env.HTML_CACHE.getWithMetadata(cacheKey, { type: 'text' });

    if (cached && cached.value) {
      const views = parseInt(cached.metadata?.views || 0) + 1;
      const ttl = getTTL(path); // E: compute once, reuse below

      // L: preserve the original absolute expiry so view-count updates don't
      //    keep resetting the TTL — deleted/renamed pages expire naturally.
      const absExpiry = cached.metadata?.abs_expiry
        || Math.floor(Date.now() / 1000) + ttl;

      // Increment view count asynchronously — ctx.waitUntil ensures the put
      // completes even after the response is returned (#21)
      ctx.waitUntil(env.HTML_CACHE.put(cacheKey, cached.value, {
        expiration: absExpiry, // L: absolute, not relative
        metadata: { ...cached.metadata, views }
      }));

      return new Response(cached.value, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': `public, max-age=${ttl}`, // E: reuse ttl
          'X-Cache-Status': 'HIT',
          'X-Cache-Views': views.toString(),
          'X-Worker': 'advanced-worker-kv',
          ...getSecurityHeaders()
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

    // Store in KV (don't await to avoid blocking response)
    env.HTML_CACHE.put(cacheKey, html, {
      expiration: absExpiry, // L: absolute expiry — KV evicts after ttl seconds
      metadata: {
        views: 1,
        cached_at: new Date(nowSec * 1000).toISOString(),
        abs_expiry: absExpiry, // L: persisted so HIT path can reuse it
        path: path
      }
    });

    // Return with our headers
    return new Response(html, {
      status: response.status,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': `public, max-age=${ttl}`,
        'X-Cache-Status': 'MISS',
        'X-Cache-TTL': ttl.toString(),
        'X-Worker': 'advanced-worker-kv',
        ...getSecurityHeaders()
      }
    });
  } catch (error) {
    // If KV fails, fall back to Cache API
    console.error('KV cache error:', error);
    return handleCacheAPI(request, env, path);
  }
}

/**
 * Fallback: Cache API (if KV unavailable)
 */
async function handleCacheAPI(request, env, path) {
  const cache = caches.default;
  const cacheKey = new Request(request.url, request);
  
  let response = await cache.match(cacheKey);
  
  if (response) {
    const newHeaders = new Headers(response.headers);
    newHeaders.set('X-Cache-Status', 'HIT');
    newHeaders.set('X-Worker', 'advanced-worker-cache-api');
    
    // Add security headers
    const securityHeaders = getSecurityHeaders();
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
    const securityHeaders = getSecurityHeaders();
    Object.entries(securityHeaders).forEach(([key, value]) => {
      newHeaders.set(key, value);
    });
    
    const cachedResponse = new Response(responseToCache.body, {
      status: responseToCache.status,
      headers: newHeaders
    });
    
    // Cache asynchronously
    await cache.put(cacheKey, cachedResponse);
    
    return new Response(response.body, {
      status: response.status,
      headers: newHeaders
    });
  }
  
  return response;
}

/**
 * Get security headers for all responses
 */
function getSecurityHeaders() {
  return {
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' plausible.io plausible.jameskilby.cloud https://utteranc.es; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' plausible.io plausible.jameskilby.cloud https://api.github.com; frame-src 'self' plausible.jameskilby.cloud https://utteranc.es https://www.youtube.com https://youtube.com https://embed.acast.com;",
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
  };
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
  
  const path = url.searchParams.get('path');
  
  if (!path) {
    return new Response('Missing path parameter', { status: 400 });
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
