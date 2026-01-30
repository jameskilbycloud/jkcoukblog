/**
 * Trace endpoint to debug middleware execution
 * Access at: https://jameskilby.co.uk/trace?path=/
 */

export async function onRequest(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const testPath = url.searchParams.get('path') || '/';
  
  // Replicate shouldCache logic
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
  
  // Replicate getTTL logic
  function getTTL(path) {
    if (path === '/' || path === '/index.html') {
      return 300;
    }
    
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
    
    return 3600; // 1 hour
  }
  
  const trace = {
    test_path: testPath,
    method: 'GET',
    should_cache: shouldCache(testPath),
    ttl: getTTL(testPath),
    checks: {
      has_wp_admin: testPath.includes('/wp-admin'),
      has_preview: testPath.includes('/preview'),
      starts_with_api: testPath.startsWith('/api/'),
      starts_with_well_known: testPath.startsWith('/.well-known/'),
      has_file_extension: testPath.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|json|xml|txt|webp|avif|br)$/) !== null,
      extension_match: testPath.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|json|xml|txt|webp|avif|br)$/)
    },
    kv_status: env.HTML_CACHE ? 'BOUND' : 'NOT BOUND',
    middleware_decision: null
  };
  
  // Determine what middleware would do
  if (trace.should_cache) {
    if (env.HTML_CACHE) {
      trace.middleware_decision = 'Would use KV cache (handleKVCache)';
    } else {
      trace.middleware_decision = 'Would use Cache API (handleCacheAPI)';
    }
  } else {
    trace.middleware_decision = 'Would skip caching (call next())';
  }
  
  return new Response(JSON.stringify(trace, null, 2), {
    headers: {
      'Content-Type': 'application/json',
      'X-Trace': 'SUCCESS',
      'Cache-Control': 'no-store'
    }
  });
}
