/**
 * Diagnostic endpoint to check KV binding and middleware status
 * Access at: https://jameskilby.co.uk/diagnostic
 */

export async function onRequest(context) {
  const { env, request } = context;
  
  const diagnostics = {
    timestamp: new Date().toISOString(),
    url: request.url,
    method: request.method,
    bindings: {
      HTML_CACHE: env.HTML_CACHE ? 'BOUND' : 'NOT BOUND',
      SEARCH_INDEX: env.SEARCH_INDEX ? 'BOUND' : 'NOT BOUND',
      PURGE_TOKEN: env.PURGE_TOKEN ? 'SET' : 'NOT SET'
    },
    cache_api: typeof caches !== 'undefined' ? 'AVAILABLE' : 'NOT AVAILABLE'
  };
  
  // Try to test KV if bound
  if (env.HTML_CACHE) {
    try {
      const testKey = 'diagnostic:test';
      const testValue = 'test-value';
      
      // Write test
      await env.HTML_CACHE.put(testKey, testValue, { expirationTtl: 60 });
      
      // Read test
      const retrieved = await env.HTML_CACHE.get(testKey);
      
      diagnostics.kv_test = {
        status: retrieved === testValue ? 'WORKING' : 'FAILED',
        written: testValue,
        retrieved: retrieved
      };
      
      // Cleanup
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
      'Cache-Control': 'no-store'
    }
  });
}
