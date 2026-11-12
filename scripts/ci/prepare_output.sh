#!/usr/bin/env bash
# Move ./static-output to ./public and add the files only the deploy needs (IndexNow key, security.txt, relative URLs).
#
# Run by the "Prepare output for deployment" step of .github/workflows/deploy-static-site.yml,
# which supplies the environment. Moved out of the workflow verbatim so it
# can be linted and tested.
set -e   # same as a default Actions run: step (bash -e)

# Configure git
git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"

# Preserve the populated cache before reset. .image_optimization_cache
# is git-tracked, so the `git reset --hard origin/main` below would
# otherwise clobber this build's freshly-optimized entries with the
# older committed copy. Back it up, then restore after the reset so the
# "Commit and push" step commits the up-to-date cache.
echo "💾 Preserving optimization cache before reset..."
if [ -f ".image_optimization_cache/optimization_cache.json" ]; then
  CACHE_ENTRIES=$(python3 -c "import json; print(len(json.load(open('.image_optimization_cache/optimization_cache.json'))))" 2>/dev/null || echo "0")
  echo "  Cache has $CACHE_ENTRIES entries before reset"
  cp -r .image_optimization_cache /tmp/preserved_cache_$$
  echo "  ✓ Cache backed up to /tmp/preserved_cache_$$"
fi

# Ensure we're on the latest version of main
echo "🔄 Syncing with remote repository..."
git fetch origin
git reset --hard origin/main

# Restore the cache after reset
if [ -d "/tmp/preserved_cache_$$" ]; then
  cp -r /tmp/preserved_cache_$$/optimization_cache.json .image_optimization_cache/
  echo "  ✓ Cache restored"
  rm -rf /tmp/preserved_cache_$$
fi

# Move static output to public/
rm -rf public/
mv ./static-output public/

# Copy IndexNow key file
if [ -f ".indexnow_key" ]; then
  INDEXNOW_KEY=$(cat .indexnow_key)
  cp .indexnow_key "public/${INDEXNOW_KEY}.txt"
  echo "✅ IndexNow key file copied to public/${INDEXNOW_KEY}.txt"
fi

# soft-404 artefacts and the stamped _worker.js are generated in the
# "Generate soft-404 artefacts and stamp Advanced Mode Worker" step
# above (before Brotli compression + validation), so they already live
# inside public/ at this point alongside their .br/.gz sidecars.

# Generate security.txt (RFC 9116) with a rolling 1-year expiry
mkdir -p public/.well-known
SECURITY_TXT_EXPIRES=$(date -u -d '+365 days' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v+365d '+%Y-%m-%dT%H:%M:%SZ')
cat > public/.well-known/security.txt <<EOF
Contact: mailto:security@jameskilby.cloud
Expires: ${SECURITY_TXT_EXPIRES}
Preferred-Languages: en
Canonical: https://jameskilby.co.uk/.well-known/security.txt
EOF
cp public/.well-known/security.txt public/security.txt
echo "✅ security.txt written (expires ${SECURITY_TXT_EXPIRES})"

# Convert absolute URLs to relative for staging compatibility
# (preserves absolute URLs in canonical, OG/Twitter meta, and JSON-LD)
echo "🔄 Converting URLs for staging compatibility..."
python3 scripts/convert_to_staging.py
