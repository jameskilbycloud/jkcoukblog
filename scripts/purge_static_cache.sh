#!/bin/bash
# Purge static asset cache from Cloudflare CDN.
#
# Covers files whose URL stays stable across deploys but whose content
# may change — and whose `_headers` Cache-Control marks them as long-
# lived, so the CF edge cache holds an old copy until manually purged:
#
#   - Favicon set / site.webmanifest (manual edits)
#   - Self-hosted woff2 fonts (subset_fonts.py rewrites them on every
#     build with the glyphs actually used in this build's HTML)
#
# Keep the URL list here in sync with the change-detection regex in
# .github/workflows/deploy-static-site.yml (search for STATIC_ASSET_PATTERN).

set -e

CLOUDFLARE_ZONE_ID="${CLOUDFLARE_ZONE_ID:-}"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"

if [ -z "$CLOUDFLARE_ZONE_ID" ] || [ -z "$CLOUDFLARE_API_TOKEN" ]; then
  echo "⚠️  CLOUDFLARE_ZONE_ID or CLOUDFLARE_API_TOKEN not set"
  echo "   Skipping static asset cache purge"
  exit 0
fi

echo "🗑️  Purging static assets from Cloudflare cache..."

# Files to purge. Keep in sync with STATIC_ASSET_PATTERN in
# .github/workflows/deploy-static-site.yml.
URLS_TO_PURGE='[
  "https://jameskilby.co.uk/favicon.ico",
  "https://jameskilby.co.uk/favicon-16x16.png",
  "https://jameskilby.co.uk/favicon-32x32.png",
  "https://jameskilby.co.uk/apple-touch-icon.png",
  "https://jameskilby.co.uk/site.webmanifest",
  "https://jameskilby.co.uk/assets/fonts/anton-v27-latin-400.woff2",
  "https://jameskilby.co.uk/assets/fonts/jetbrainsmono-v24-latin-400.woff2",
  "https://jameskilby.co.uk/assets/fonts/jetbrainsmono-v24-latin-700.woff2",
  "https://jameskilby.co.uk/assets/fonts/spacegrotesk-v22-latin-400.woff2",
  "https://jameskilby.co.uk/assets/fonts/spacegrotesk-v22-latin-500.woff2",
  "https://jameskilby.co.uk/assets/fonts/spacegrotesk-v22-latin-700.woff2"
]'

# Purge using Cloudflare API
RESPONSE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
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
