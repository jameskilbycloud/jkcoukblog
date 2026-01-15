#!/bin/bash
# Diagnostic script to check image optimization cache in GitHub Actions
set -euo pipefail

echo "=========================================="
echo "IMAGE OPTIMIZATION CACHE DIAGNOSTIC"
echo "=========================================="
echo ""

echo "1. CACHE DIRECTORY STATUS"
echo "--------------------------"
CACHE_DIR=".image_optimization_cache"
CACHE_FILE="$CACHE_DIR/optimization_cache.json"

if [ -d "$CACHE_DIR" ]; then
    echo "✓ Cache directory exists: $CACHE_DIR"
    ls -lah "$CACHE_DIR" | head -10
else
    echo "✗ Cache directory NOT found"
fi

echo ""
if [ -f "$CACHE_FILE" ]; then
    SIZE=$(wc -c < "$CACHE_FILE")
    echo "✓ Cache file exists: $CACHE_FILE"
    echo "  Size: $SIZE bytes"
    
    if [ "$SIZE" -gt 5 ]; then
        ENTRIES=$(python3 -c "import json; print(len(json.load(open('$CACHE_FILE'))))" 2>/dev/null || echo "ERROR")
        echo "  Entries: $ENTRIES"
        
        if [ "$ENTRIES" != "ERROR" ] && [ "$ENTRIES" -gt 0 ]; then
            echo "  ✓ Cache is populated"
            echo ""
            echo "  Sample entries:"
            python3 -c "import json; data=json.load(open('$CACHE_FILE')); import itertools; [print(f'    - {k}') for k in itertools.islice(data.keys(), 3)]" 2>/dev/null || echo "    ERROR reading entries"
        else
            echo "  ⚠️  Cache is empty"
        fi
    else
        echo "  ⚠️  Cache file is empty ({})"
    fi
else
    echo "✗ Cache file NOT found"
fi

echo ""
echo "2. OPTIMIZATION TOOLS"
echo "---------------------"
for tool in optipng jpegoptim avifenc cwebp; do
    if command -v $tool &> /dev/null; then
        VERSION=$($tool --version 2>&1 | head -1 || echo "unknown")
        echo "✓ $tool: $VERSION"
    else
        echo "✗ $tool: NOT INSTALLED"
    fi
done

echo ""
echo "3. GIT STATUS"
echo "-------------"
echo "Cache directory in git:"
git ls-files "$CACHE_DIR" 2>/dev/null || echo "  Not tracked"

echo ""
echo "Last commit touching cache:"
git --no-pager log --oneline -1 -- "$CACHE_DIR" 2>/dev/null || echo "  No commits found"

echo ""
echo "4. RECENT OPTIMIZATION RESULTS"
echo "-------------------------------"
if [ -f "optimization-results.json" ]; then
    echo "✓ optimization-results.json exists"
    OPTIMIZED=$(jq '[.[] | select(.was_cached == false)] | length' optimization-results.json 2>/dev/null || echo "ERROR")
    CACHED=$(jq '[.[] | select(.was_cached == true)] | length' optimization-results.json 2>/dev/null || echo "ERROR")
    echo "  Newly optimized: $OPTIMIZED"
    echo "  Cached (skipped): $CACHED"
else
    echo "⚠️  optimization-results.json not found (run optimization first)"
fi

echo ""
echo "=========================================="
echo "RECOMMENDATIONS"
echo "=========================================="

if [ ! -f "$CACHE_FILE" ] || [ "$(wc -c < "$CACHE_FILE")" -le 5 ]; then
    echo "⚠️  Cache is empty or missing"
    echo ""
    echo "This is expected if:"
    echo "  1. Cache was recently cleared"
    echo "  2. This is the first run"
    echo "  3. GitHub Actions cache expired (7 days unused)"
    echo ""
    echo "Next steps:"
    echo "  - Run the workflow once to populate cache"
    echo "  - Check GitHub Actions logs for optimization step"
    echo "  - Verify cache is committed to git after run"
else
    echo "✓ Cache appears healthy"
    echo ""
    echo "If images are still being re-optimized:"
    echo "  - Check GitHub Actions cache is being restored"
    echo "  - Verify cache key matches (build-cache-avif-v2-*)"
    echo "  - Check logs for 'Cache restored' message"
fi
