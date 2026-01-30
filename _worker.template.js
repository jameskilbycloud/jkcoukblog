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
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // Only cache GET requests
    if (request.method !== 'GET') {
      return env.ASSETS.fetch(request);
    }
    
    // Handle purge requests
    if (path === '/.purge') {
      return handlePurge(request, env);
    }
    
    // Handle diagnostic endpoint
    if (path === '/diagnostic') {
      return handleDiagnostic(request, env);
    }
    
    // Handle trace endpoint
    if (path === '/trace') {
      return handleTrace(request, env);
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
      
      // Increment view count asynchronously (don't await)
      env.HTML_CACHE.put(cacheKey, cached.value, {
        expirationTtl: getTTL(path),
        metadata: { ...cached.metadata, views }
      });
      
      return new Response(cached.value, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'public, max-age=300',
          'X-Cache-Status': 'HIT',
          'X-Cache-Views': views.toString(),
          'X-Worker': 'advanced-worker-kv',
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
    const ttl = getTTL(path);
    
    // Store in KV (don't await to avoid blocking response)
    env.HTML_CACHE.put(cacheKey, html, {
      expirationTtl: ttl,
      metadata: { 
        views: 1,
        cached_at: new Date().toISOString(),
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
 * Determine if path should be cached
 */
function shouldCache(path) {
  if (path.includes('/wp-admin') || 
      path.includes('/preview') ||
      path.startsWith('/api/') || 
      path.startsWith('/.well-known/') ||
      path === '/diagnostic' ||
      path === '/trace' ||
      path === '/test' ||
      path.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|json|xml|txt|webp|avif|br)$/)) {
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
  
  // Recent posts - 15 minutes
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const pathMatch = path.match(/^\/(\d{4})\/(\d{2})\//);  
  if (pathMatch) {
    const year = parseInt(pathMatch[1]);
    const month = parseInt(pathMatch[2]);
    
    if (year === currentYear && month >= currentMonth - 1) {
      return 900; // 15 minutes
    }
  }
  
  // Older content - 1 hour
  return 3600;
}

/**
 * Handle selective cache purge
 */
async function handlePurge(request, env) {
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
  const cacheKey = new Request(`https://jameskilby.co.uk${path}`);
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
 * Handle diagnostic endpoint
 */
async function handleDiagnostic(request, env) {
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
 * Handle trace endpoint
 */
async function handleTrace(request, env) {
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
      has_file_extension: testPath.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|json|xml|txt|webp|avif|br)$/) !== null
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
