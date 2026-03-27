/**
 * Cloudflare Worker for HTML Caching
 * 
 * This worker caches HTML pages at Cloudflare's edge to improve TTFB.
 * It converts cf-cache-status from DYNAMIC to HIT for cached content.
 * 
 * Features:
 * - Caches HTML responses for 5 minutes (300s)
 * - Respects cache-control headers from origin
 * - Adds cache status headers for debugging
 * - Handles cache purging via special header
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Only cache GET requests
    if (request.method !== 'GET') {
      return fetch(request);
    }
    
    // Don't cache admin/preview URLs
    if (url.pathname.includes('/wp-admin') || url.pathname.includes('/preview')) {
      return fetch(request);
    }
    
    // Cache API
    const cache = caches.default;
    
    // Create cache key (include query string for different variants)
    const cacheKey = new Request(url.toString(), request);
    
    // Check for cache purge header (for manual cache clearing)
    if (request.headers.get('X-Purge-Cache') === 'true') {
      await cache.delete(cacheKey);
      return new Response('Cache purged', { status: 200 });
    }
    
    // Try to get from cache first
    let response = await cache.match(cacheKey);
    
    if (response) {
      // Cache hit - add debug header
      const newHeaders = new Headers(response.headers);
      newHeaders.set('X-Worker-Cache', 'HIT');
      newHeaders.set('X-Cache-Age', Math.floor((Date.now() - new Date(response.headers.get('Date')).getTime()) / 1000));
      
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: newHeaders
      });
    }
    
    // Cache miss - fetch from origin
    response = await fetch(request);
    
    // Only cache successful HTML responses
    const contentType = response.headers.get('content-type') || '';
    const isHTML = contentType.includes('text/html');
    const isSuccess = response.status === 200;
    
    if (isSuccess && isHTML) {
      // Clone the response so we can cache it
      const responseToCache = response.clone();
      
      // Modify headers for caching
      const newHeaders = new Headers(responseToCache.headers);
      
      // Ensure cache-control is set properly
      // Use origin's cache-control or default to 5 minutes
      if (!newHeaders.has('Cache-Control')) {
        newHeaders.set('Cache-Control', 'public, max-age=300, s-maxage=300');
      }
      
      // Add debug headers
      newHeaders.set('X-Worker-Cache', 'MISS');
      newHeaders.set('X-Cache-Date', new Date().toISOString());
      
      // Create cached response
      const cachedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers: newHeaders
      });
      
      // Cache it asynchronously (doesn't block the response)
      ctx.waitUntil(cache.put(cacheKey, cachedResponse));
      
      // Return the original response with debug headers
      const finalHeaders = new Headers(response.headers);
      finalHeaders.set('X-Worker-Cache', 'MISS');
      finalHeaders.set('X-Cache-Date', new Date().toISOString());
      
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: finalHeaders
      });
    }
    
    // Don't cache non-HTML or error responses
    const bypassHeaders = new Headers(response.headers);
    bypassHeaders.set('X-Worker-Cache', 'BYPASS');
    
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: bypassHeaders
    });
  }
};
