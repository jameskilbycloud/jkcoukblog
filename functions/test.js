/**
 * Simple test function to verify Pages Functions are working
 * Access at: https://jameskilby.co.uk/test
 */

export async function onRequest(context) {
  return new Response(JSON.stringify({
    message: 'Pages Functions are working!',
    timestamp: new Date().toISOString(),
    path: context.request.url
  }), {
    headers: {
      'Content-Type': 'application/json',
      'X-Function-Test': 'SUCCESS'
    }
  });
}
