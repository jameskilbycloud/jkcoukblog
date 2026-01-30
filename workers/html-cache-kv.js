/**
 * Enhanced HTML Cache Worker with Workers KV
 * 
 * Features:
 * - Smart TTL based on URL patterns
 * - View count tracking per page
 * - Selective cache purging
 * - Metadata storage
 * - Better cache hit ratio
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Handle purge requests
    if (url.pathname === '/.purge') {
      return this.handlePurge(request, env);
    }
    
    // Only cache GET requests for HTML
    if (request.method !== 'GET') {
      return fetch(request);
    }
    
    // Don't cache admin/preview URLs
    if (url.pathname.includes('/wp-admin') || 
        url.pathname.includes('/preview') ||
        url.pathname.includes('/wp-login')) {
      return fetch(request);
    }
    
    const cacheKey = url.pathname;
    
    // Try KV first (faster than Cache API)
    try {
      const cachedStr = await env.HTML_CACHE.get(cacheKey);
      
      if (cachedStr) {
        const cached = JSON.parse(cachedStr);
        
        // Check if still valid
        if (Date.now() - cached.timestamp < cached.ttl) {
          // Increment view count asynchronously (don't block response)
          ctx.waitUntil(this.incrementViews(env, cacheKey, cached));
          
          return new Response(cached.html, {
            status: 200,
            headers: {
              'Content-Type': 'text/html; charset=utf-8',
              'X-Cache-Status': 'HIT',
              'X-Cache-Age': Math.floor((Date.now() - cached.timestamp) / 1000),
              'X-Cache-Views': (cached.views || 0).toString(),
              'Cache-Control': `public, max-age=${Math.floor(cached.ttl / 1000)}`,
              'X-KV-Cache': 'true'
            }
          });
        }
      }
    } catch (error) {
      // KV error - fall through to origin
      console.error('KV read error:', error);
    }
    
    // Cache miss - fetch from origin
    const response = await fetch(request);
    
    // Only cache successful HTML responses
    const contentType = response.headers.get('content-type') || '';
    const isHTML = contentType.includes('text/html');
    const isSuccess = response.status === 200;
    
    if (isSuccess && isHTML) {
      const html = await response.text();
      
      // Determine TTL based on URL pattern
      const ttl = this.getTTL(url.pathname);
      
      // Store in KV
      const cacheData = {
        html,
        timestamp: Date.now(),
        ttl,
        views: 0,
        path: url.pathname,
        contentLength: html.length
      };
      
      // Store asynchronously (don't block response)
      ctx.waitUntil(
        env.HTML_CACHE.put(cacheKey, JSON.stringify(cacheData), {
          expirationTtl: Math.floor(ttl / 1000)
        }).catch(err => console.error('KV write error:', err))
      );
      
      return new Response(html, {
        status: response.status,
        headers: {
          'Content-Type': contentType,
          'X-Cache-Status': 'MISS',
          'X-Cache-TTL': Math.floor(ttl / 1000).toString(),
          'Cache-Control': `public, max-age=${Math.floor(ttl / 1000)}`,
          'X-KV-Cache': 'true'
        }
      });
    }
    
    // Don't cache non-HTML or error responses
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...Object.fromEntries(response.headers),
        'X-Cache-Status': 'BYPASS'
      }
    });
  },
  
  getTTL(pathname) {
    // Homepage: 5 minutes (frequently updated)
    if (pathname === '/' || pathname === '') {
      return 5 * 60 * 1000;
    }
    
    // Recent posts (2026): 15 minutes
    if (pathname.match(/^\/2026\//)) {
      return 15 * 60 * 1000;
    }
    
    // Older posts (2017-2025): 1 hour (stable content)
    if (pathname.match(/^\/(2017|2018|2019|2020|2021|2022|2023|2024|2025)\//)) {
      return 60 * 60 * 1000;
    }
    
    // Category/tag pages: 10 minutes (updated when new posts added)
    if (pathname.match(/^\/(category|tag)\//)) {
      return 10 * 60 * 1000;
    }
    
    // About pages and static content: 1 hour
    if (pathname.match(/^\/(about|lab|homelab|media|vmc|evs)\//)) {
      return 60 * 60 * 1000;
    }
    
    // Default: 15 minutes
    return 15 * 60 * 1000;
  },
  
  async incrementViews(env, cacheKey, cached) {
    try {
      cached.views = (cached.views || 0) + 1;
      await env.HTML_CACHE.put(cacheKey, JSON.stringify(cached), {
        expirationTtl: Math.floor(cached.ttl / 1000)
      });
    } catch (error) {
      console.error('Error incrementing views:', error);
    }
  },
  
  async handlePurge(request, env) {
    const url = new URL(request.url);
    const path = url.searchParams.get('path');
    const token = request.headers.get('X-Purge-Token');
    const all = url.searchParams.get('all') === 'true';
    
    // Validate token
    if (!token || token !== env.PURGE_TOKEN) {
      return new Response('Unauthorized', { 
        status: 401,
        headers: { 'Content-Type': 'text/plain' }
      });
    }
    
    try {
      if (all) {
        // Purge all cache (use with caution)
        // Note: KV doesn't have a "delete all" operation
        // This would need to be implemented with a list of keys
        return new Response('Purge all not implemented - use Cloudflare Dashboard', { 
          status: 501,
          headers: { 'Content-Type': 'text/plain' }
        });
      } else if (path) {
        // Purge specific path
        await env.HTML_CACHE.delete(path);
        return new Response(`Purged: ${path}`, { 
          status: 200,
          headers: { 'Content-Type': 'text/plain' }
        });
      } else {
        return new Response('Missing path or all parameter', { 
          status: 400,
          headers: { 'Content-Type': 'text/plain' }
        });
      }
    } catch (error) {
      console.error('Purge error:', error);
      return new Response(`Purge error: ${error.message}`, { 
        status: 500,
        headers: { 'Content-Type': 'text/plain' }
      });
    }
  }
};
