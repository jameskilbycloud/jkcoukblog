#!/bin/bash
# Purge static asset cache from Cloudflare CDN
# Used after deploying new favicon files or other static assets

set -e

CLOUDFLARE_ZONE_ID="${CLOUDFLARE_ZONE_ID:-}"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"

if [ -z "$CLOUDFLARE_ZONE_ID" ] || [ -z "$CLOUDFLARE_API_TOKEN" ]; then
  echo "⚠️  CLOUDFLARE_ZONE_ID or CLOUDFLARE_API_TOKEN not set"
  echo "   Skipping static asset cache purge"
  exit 0
fi

echo "🗑️  Purging static assets from Cloudflare cache..."

# Files to purge
URLS_TO_PURGE='[
  "https://jameskilby.co.uk/favicon.ico",
  "https://jameskilby.co.uk/favicon-16x16.png",
  "https://jameskilby.co.uk/favicon-32x32.png",
  "https://jameskilby.co.uk/apple-touch-icon.png",
  "https://jameskilby.co.uk/site.webmanifest"
]'

# Purge using Cloudflare API
RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "{\"files\": ${URLS_TO_PURGE}}")

# Check if successful
if echo "$RESPONSE" | grep -q '"success":true'; then
  echo "✅ Successfully purged static asset cache"
  echo "$RESPONSE" | jq -r '.result.id' 2>/dev/null || echo "   Purge request submitted"
else
  echo "❌ Failed to purge cache"
  echo "$RESPONSE"
  exit 1
fi
