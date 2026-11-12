#!/usr/bin/env bash
# Encode AVIF/WebP for every image in ./static-output and report the counts.
#
# Run by the "Optimize images" step of .github/workflows/deploy-static-site.yml,
# which supplies the environment. Moved out of the workflow verbatim so it
# can be linted and tested.
set -eo pipefail   # the step declared `shell: bash`, which Actions runs as -eo pipefail

echo "🖼️  Starting advanced image optimization with AVIF..."

# Run the Python-based optimizer with parallel processing
# Uses 4 parallel workers, creates AVIF versions by default
# Cache is stored in .image_optimization_cache/ for persistence
# --skip-html: <picture> conversion is done once, by the single-pass
# HTML transformer. optimize_images.py's own HTML pass rewrote ~250
# pages per build for nothing — on the live build the transformer's
# output was byte-identical with and without it.
FORCE_FLAG=()
[ "$REENCODE_IMAGES" = "true" ] && FORCE_FLAG=(--force)
python3 scripts/optimize_images.py ./static-output \
  --workers 4 \
  --skip-html \
  "${FORCE_FLAG[@]}" \
  --json-output optimization-results.json \
  --cache-dir .image_optimization_cache || {
  echo "⚠️  Image optimization failed (non-blocking)"
  # Set defaults if optimization fails
  echo "PNG_COUNT=0" >> $GITHUB_ENV
  echo "JPG_COUNT=0" >> $GITHUB_ENV
  echo "OPTIMIZED_COUNT=0" >> $GITHUB_ENV
  echo "SKIPPED_COUNT=0" >> $GITHUB_ENV
  echo "SAVED_MB=0.0" >> $GITHUB_ENV
  exit 0
}

# Parse JSON results and extract metrics
if [ -f "optimization-results.json" ]; then
  # Count by format type
  PNG_COUNT=$(jq '[.[] | select(.format_type == "PNG")] | length' optimization-results.json)
  JPG_COUNT=$(jq '[.[] | select(.format_type == "JPEG")] | length' optimization-results.json)
  
  # Count optimized vs cached
  OPTIMIZED_COUNT=$(jq '[.[] | select(.was_cached == false)] | length' optimization-results.json)
  SKIPPED_COUNT=$(jq '[.[] | select(.was_cached == true)] | length' optimization-results.json)
  
  # Calculate total savings in MB
  SAVED_BYTES=$(jq '[.[] | .saved_bytes] | add // 0' optimization-results.json)
  SAVED_MB=$(echo "scale=2; $SAVED_BYTES / 1024 / 1024" | bc)
  
  # Calculate average optimization time for newly optimized images
  # Handle case where all images are cached (length = 0)
  AVG_TIME=$(jq '[.[] | select(.was_cached == false) | .duration_ms] | if length > 0 then (add / length | floor) else 0 end' optimization-results.json)
  
  # Count AVIF and WebP versions created
  AVIF_COUNT=$(jq '[.[] | select(.avif_created == true)] | length' optimization-results.json)
  WEBP_COUNT=$(jq '[.[] | select(.webp_created == true)] | length' optimization-results.json)
  
  echo "📊 Optimization Results:"
  echo "   • PNG Images: $PNG_COUNT"
  echo "   • JPEG Images: $JPG_COUNT"
  echo "   • Newly Optimized: $OPTIMIZED_COUNT"
  echo "   • Cached (Skipped): $SKIPPED_COUNT"
  echo "   • AVIF Created: $AVIF_COUNT"
  echo "   • WebP Created: $WEBP_COUNT"
  echo "   • Space Saved: ${SAVED_MB}MB"
  echo "   • Avg Time/Image: ${AVG_TIME}ms"
  
  # Save to environment for later steps
  echo "PNG_COUNT=$PNG_COUNT" >> $GITHUB_ENV
  echo "JPG_COUNT=$JPG_COUNT" >> $GITHUB_ENV
  echo "OPTIMIZED_COUNT=$OPTIMIZED_COUNT" >> $GITHUB_ENV
  echo "SKIPPED_COUNT=$SKIPPED_COUNT" >> $GITHUB_ENV
  echo "AVIF_COUNT=$AVIF_COUNT" >> $GITHUB_ENV
  echo "WEBP_COUNT=$WEBP_COUNT" >> $GITHUB_ENV
  echo "SAVED_MB=$SAVED_MB" >> $GITHUB_ENV
  echo "AVG_TIME=$AVG_TIME" >> $GITHUB_ENV
  
  # Add to GitHub Actions summary
  echo "" >> $GITHUB_STEP_SUMMARY
  echo "## 🖼️ Image Optimization Summary" >> $GITHUB_STEP_SUMMARY
  echo "" >> $GITHUB_STEP_SUMMARY
  echo "- **Total Images:** $((PNG_COUNT + JPG_COUNT))" >> $GITHUB_STEP_SUMMARY
  echo "  - PNG: $PNG_COUNT" >> $GITHUB_STEP_SUMMARY
  echo "  - JPEG: $JPG_COUNT" >> $GITHUB_STEP_SUMMARY
  echo "- **Newly Optimized:** $OPTIMIZED_COUNT" >> $GITHUB_STEP_SUMMARY
  echo "- **Already Optimized (Skipped):** $SKIPPED_COUNT" >> $GITHUB_STEP_SUMMARY
  echo "- **Modern Formats:**" >> $GITHUB_STEP_SUMMARY
  echo "  - AVIF: $AVIF_COUNT" >> $GITHUB_STEP_SUMMARY
  echo "  - WebP: $WEBP_COUNT" >> $GITHUB_STEP_SUMMARY
  echo "- **Space Saved:** ${SAVED_MB} MB" >> $GITHUB_STEP_SUMMARY
  echo "- **Avg Time per Image:** ${AVG_TIME} ms" >> $GITHUB_STEP_SUMMARY
  echo "- **Parallel Workers:** 4" >> $GITHUB_STEP_SUMMARY
else
  echo "⚠️  No optimization results found"
  echo "PNG_COUNT=0" >> $GITHUB_ENV
  echo "JPG_COUNT=0" >> $GITHUB_ENV
  echo "OPTIMIZED_COUNT=0" >> $GITHUB_ENV
  echo "SKIPPED_COUNT=0" >> $GITHUB_ENV
  echo "SAVED_MB=0.0" >> $GITHUB_ENV
fi

# Verify cache file was created and populated
echo ""
echo "💾 Cache file will be automatically saved by GitHub Actions"
if [ -f ".image_optimization_cache/optimization_cache.json" ]; then
  CACHE_ENTRIES=$(python3 -c "import json; print(len(json.load(open('.image_optimization_cache/optimization_cache.json'))))" 2>/dev/null || echo "0")
  echo "  ✅ Cache file exists with $CACHE_ENTRIES entries"
else
  echo "  ⚠️  Cache file not found (may be created on first optimization)"
fi
