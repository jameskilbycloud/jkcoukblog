#!/usr/bin/env bash
# Wait for the Pages deployment of the pushed site commit, then purge the changed pages from the KV HTML cache.
#
# Run by the "Purge changed HTML from KV cache" step of .github/workflows/deploy-static-site.yml,
# which supplies the environment. Moved out of the workflow verbatim so it
# can be linted and tested.
set -e   # same as a default Actions run: step (bash -e)

echo "🗑️ Purging changed HTML entries from Workers KV cache..."

if [ -z "$CACHE_PURGE_TOKEN" ]; then
  echo "ℹ️  CACHE_PURGE_TOKEN not set, skipping KV cache purge"
  echo "   To enable: Add CACHE_PURGE_TOKEN to repository secrets"
  exit 0
fi

if [ -z "$PUSHED_SHA" ]; then
  # Nothing was committed, so every KV entry is still byte-identical
  # to what Pages serves — purging would only force cold-cache MISSes.
  # (If a previous run's purge failed and you need a manual flush:
  # scripts/purge_html_kv_cache.py, or POST /.purge?all=true.)
  echo "ℹ️  No new commit was pushed — public/ unchanged, skipping KV purge."
  exit 0
fi

if [ -n "$CLOUDFLARE_API_TOKEN" ] && [ -n "$CLOUDFLARE_ACCOUNT_ID" ]; then
  echo "⏳ Waiting for Cloudflare Pages deployment of ${PUSHED_SHA:0:7} to complete..."
  # 5s poll, same 180s ceiling. The deployment consistently becomes
  # ready between the 3rd and 4th poll, so a 10s interval spent up to
  # 9s per deploy waiting on a state that had already changed — 33s of
  # the step's 49s on the 2026-08-09 17:34 run. Halving the interval
  # keeps the same worst case and returns most of that.
  MAX_ATTEMPTS=36   # 36 × 5s = 180s max
  ATTEMPT=0
  DEPLOY_STATUS="pending"
  DEPLOY_RESP=""
  while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    DEPLOY_RESP=$(curl -s \
      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
      "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects/jkcoukblog/deployments?per_page=10")
    DEPLOY_STATUS=$(printf '%s' "$DEPLOY_RESP" \
      | jq -r --arg sha "$PUSHED_SHA" \
          '[.result[]? | select(.deployment_trigger.metadata.commit_hash == $sha)] | .[0].latest_stage.status // "pending"' \
      2>/dev/null || echo "pending")
    echo "   Deployment status: $DEPLOY_STATUS (attempt $((ATTEMPT+1))/$MAX_ATTEMPTS)"
    case "$DEPLOY_STATUS" in
      success)
        echo "✅ Deployment complete — waiting 15s for global propagation..."
        sleep 15
        break
        ;;
      failure|canceled)
        echo "❌ Pages deployment $DEPLOY_STATUS — skipping purge"
        exit 0
        ;;
    esac
    ATTEMPT=$((ATTEMPT+1))
    sleep 5
  done
  if [ "$DEPLOY_STATUS" != "success" ]; then
    echo "⚠️  Deployment for ${PUSHED_SHA:0:7} did not reach 'success' within timeout"
    echo "   Diagnosing — these are the bits the previous debug block silently swallowed:"
    echo
    echo "   [a] CF API success flag + error array:"
    printf '%s' "$DEPLOY_RESP" \
      | jq '{success, errors, messages, result_count: (.result | length? // 0)}' \
          2>&1 | sed 's/^/       /'
    echo
    echo "   [b] First 3 deployments returned (id / status / commit / created):"
    printf '%s' "$DEPLOY_RESP" \
      | jq -r '
          .result[0:3][]? as $d
          | "       - \($d.id[:8]) / \($d.latest_stage.name // "?"):\($d.latest_stage.status // "?") / \($d.deployment_trigger.metadata.commit_hash[:7] // "?") / \($d.created_on // "?")"
        ' 2>&1
    echo
    echo "   [c] Did *any* returned deployment match $PUSHED_SHA?"
    printf '%s' "$DEPLOY_RESP" \
      | jq -r --arg sha "$PUSHED_SHA" \
          '[.result[]? | select(.deployment_trigger.metadata.commit_hash == $sha)] | "       matches: \(length)"' \
          2>&1
    echo
    echo "   [d] Raw response preview (first 600 chars):"
    printf '%s' "${DEPLOY_RESP:0:600}" | sed 's/^/       /'
    echo
    echo "   Continuing with a 30s safety buffer before purge..."
    sleep 30
  fi
else
  echo "⚠️  CF API credentials not set — sleeping 30s to allow deployment propagation..."
  sleep 30
fi

# Selective purge: only pages whose rendered bytes changed in the
# pushed commit need purging — every other KV entry is still
# byte-identical to what Pages now serves (KV values are raw HTML
# bodies; worker headers/TTLs are applied at serve time, so even a
# worker change doesn't invalidate them). Previously every deploy
# wiped the whole namespace, forcing a cold MISS for every page's
# next visitor. Above MAX_SELECTIVE changed pages (site-wide CSS/
# template rewrites) purge-all is fewer requests, so fall back.
MAX_SELECTIVE=30
# The site commit is parentless, so diff it against the one it replaced.
CHANGED_HTML=$(git diff --name-only "${PREV_SITE_SHA:-$(git hash-object -t tree /dev/null)}" "$PUSHED_SHA" -- public/ | grep '\.html$' || true)
CHANGED_COUNT=$(printf '%s' "$CHANGED_HTML" | grep -c . || true)

PURGE_METHOD="selective"
PURGED_COUNT=0
if [ "$CHANGED_COUNT" -eq 0 ]; then
  echo "ℹ️  No HTML files changed in ${PUSHED_SHA:0:7} — nothing to purge."
  PURGE_METHOD="none"
elif [ "$CHANGED_COUNT" -gt "$MAX_SELECTIVE" ]; then
  echo "ℹ️  $CHANGED_COUNT HTML files changed (> $MAX_SELECTIVE) — using purge-all."
  PURGE_METHOD="all"
fi

if [ "$PURGE_METHOD" = "selective" ]; then
  echo "🎯 Selectively purging $CHANGED_COUNT changed HTML page(s)..."
  OK=0
  FAILED=0
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    rel="${f#public/}"
    # The worker keys the KV cache on the raw request pathname, and
    # isKnownContentPath accepts both slash forms — so a page can be
    # cached under /dir and /dir/. Purge both variants.
    case "$rel" in
      index.html)   paths="/ /index.html" ;;
      */index.html) d="/${rel%/index.html}"; paths="$d $d/" ;;
      *)            paths="/$rel" ;;
    esac
    for p in $paths; do
      CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "https://jameskilby.co.uk/.purge?path=$p" \
        -H "X-Purge-Token: $CACHE_PURGE_TOKEN")
      if [ "$CODE" = "200" ]; then
        OK=$((OK + 1))
      else
        echo "   ⚠️  Purge failed for $p (HTTP $CODE)"
        FAILED=$((FAILED + 1))
      fi
    done
  done <<< "$CHANGED_HTML"
  PURGED_COUNT=$OK
  echo "✅ Purged $OK path variant(s), $FAILED failed"
  if [ "$FAILED" -gt 0 ]; then
    echo "⚠️  Some selective purges failed — falling back to purge-all for safety."
    PURGE_METHOD="all"
  fi
fi

if [ "$PURGE_METHOD" = "all" ]; then
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "https://jameskilby.co.uk/.purge?all=true" \
    -H "X-Purge-Token: $CACHE_PURGE_TOKEN")

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | sed '$d')

  if [ "$HTTP_CODE" = "200" ]; then
    PURGED_COUNT=$(echo "$BODY" | jq -r '.count // 0')
    echo "✅ Purged $PURGED_COUNT entries from KV cache"
  else
    echo "⚠️  Purge-all failed (HTTP $HTTP_CODE): $BODY"
  fi
fi

# Add to summary
echo "" >> $GITHUB_STEP_SUMMARY
echo "## 🗑️ KV Cache Purged" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "- **Entries Purged:** ${PURGED_COUNT:-unknown}" >> $GITHUB_STEP_SUMMARY
echo "- **Method:** $PURGE_METHOD ($CHANGED_COUNT HTML files changed)" >> $GITHUB_STEP_SUMMARY
