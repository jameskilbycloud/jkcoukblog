/**
 * Cloudflare Pages Function - Advanced HTML Caching with KV
 * 
 * This middleware runs on ALL requests to jameskilby.co.uk
 * Provides smart TTL caching, view tracking, and selective purge
 * 
 * Features:
 * - Smart TTL: 5min homepage, 15min recent posts, 1hr old posts
 * - View count tracking in KV metadata
 * - Selective cache purge via /.purge endpoint
 * - Falls back to Cache API if KV unavailable
 */

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Only cache GET requests
  if (request.method !== 'GET') {
    return next();
  }
  
  // Handle purge requests
  if (path === '/.purge') {
    return handlePurge(request, env);
  }
  
  // Don't cache assets or special paths
  if (!shouldCache(path)) {
    return next();
  }
  
  // Try KV cache if available (with fallback to Cache API)
  if (env.HTML_CACHE) {
    return handleKVCache(request, env, next, path);
  }
  
  // Fallback to Cache API if KV not bound
  return handleCacheAPI(request, next, path);
}

/**
 * Handle caching with KV (preferred method)
 */
async function handleKVCache(request, env, next, path) {
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
          'X-Worker': 'pages-function-kv',
        }
      });
    }
    
    // Fetch from Pages
    const response = await next();
    
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
    const clonedResponse = response.clone();
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
    const newHeaders = new Headers(clonedResponse.headers);
    newHeaders.set('Content-Type', 'text/html; charset=utf-8');
    newHeaders.set('Cache-Control', `public, max-age=${ttl}`);
    newHeaders.set('X-Cache-Status', 'MISS');
    newHeaders.set('X-Cache-TTL', ttl.toString());
    newHeaders.set('X-Worker', 'pages-function-kv');
    
    return new Response(html, {
      status: clonedResponse.status,
      headers: newHeaders
    });
  } catch (error) {
    // If KV fails, fall back to Cache API
    console.error('KV cache error:', error);
    return handleCacheAPI(request, next, path);
  }
}

/**
 * Fallback: Cache API (if KV unavailable)
 */
async function handleCacheAPI(request, next, path) {
  const cache = caches.default;
  const cacheKey = new Request(request.url, request);
  
  let response = await cache.match(cacheKey);
  
  if (response) {
    const newHeaders = new Headers(response.headers);
    newHeaders.set('X-Cache-Status', 'HIT');
    newHeaders.set('X-Worker', 'pages-function-cache-api');
    
    return new Response(response.body, {
      status: response.status,
      headers: newHeaders
    });
  }
  
  response = await next();
  
  if (response.ok && response.headers.get('content-type')?.includes('text/html')) {
    const responseToCache = response.clone();
    const newHeaders = new Headers(responseToCache.headers);
    
    if (!newHeaders.has('Cache-Control')) {
      newHeaders.set('Cache-Control', `public, max-age=${getTTL(path)}`);
    }
    
    newHeaders.set('X-Cache-Status', 'MISS');
    newHeaders.set('X-Worker', 'pages-function-cache-api');
    
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
