#!/usr/bin/env bash
# Generate the site into ./static-output, seeded from the previous build when the incremental cache exists.
#
# Run by the "Generate static site" step of .github/workflows/deploy-static-site.yml,
# which supplies the environment. Moved out of the workflow verbatim so it
# can be linted and tested.
set -e   # same as a default Actions run: step (bash -e)

# Ensure we're in the right directory
echo "📁 Working from: $(pwd)"
if [ ! -f "scripts/wp_to_static_generator.py" ]; then
  echo "❌ scripts/wp_to_static_generator.py not found!"
  ls -la scripts/
  exit 1
fi

# Incremental build: if a previous build cache exists, seed ./static-output/
# from public/ so unchanged posts stay in place, then let the generator
# fetch only posts modified since the last run (WP REST API modified_after).
# On first run (no cache) the generator detects an empty cache and fetches
# all posts automatically — no --no-incremental flag needed.
if [ -f ".build-cache.json" ] && [ -d "public" ]; then
  echo "⚡ Incremental build cache found — seeding static-output from previous build..."
  mkdir -p ./static-output
  # Copy all files except Brotli/Gzip variants (regenerated after post-processing)
  rsync -a --exclude='*.br' --exclude='*.gz' public/ ./static-output/
  SEEDED_FILES=$(find ./static-output -type f | wc -l | xargs)
  LAST_BUILD=$(python3 -c "import json; d=json.load(open('.build-cache.json')); print(d.get('last_build_time','unknown'))" 2>/dev/null || echo "unknown")
  echo "✅ Seeded $SEEDED_FILES files — last build: $LAST_BUILD"
  echo ""

  # Overlay the raw (pre-transform) HTML/CSS captured at the end of the
  # previous run. public/ holds the *post-processed* copies, and the
  # optimisation passes are not idempotent over their own output — see
  # the "Restore raw pre-transform HTML snapshot" step for the detail.
  # Overlaying here (before the generator runs) means anything the
  # generator itself rewrites this run still wins.
  if [ -d ".raw-html-snapshot" ]; then
    RAW_FILES=$(find .raw-html-snapshot -type f | wc -l | xargs)
    rsync -a .raw-html-snapshot/ ./static-output/
    echo "🧼 Overlaid $RAW_FILES raw pre-transform files (HTML + CSS) over the seed"
  else
    echo "⚠️  No raw snapshot to overlay — seeding HTML from post-processed public/."
    echo "   Post-processing will re-run over already-transformed HTML, so this run"
    echo "   may still produce a whole-site diff. The snapshot captured at the end"
    echo "   of this run makes the next one clean."
  fi
  echo ""
  # Restore absolute URLs in seeded HTML so the HTML validator sees the same
  # URL format as a full build (convert_to_staging.py runs AFTER validation,
  # converting absolute → relative; seeded files already have relative URLs).
  # Without this, old posts linking to deleted tags (e.g. /tag/storage/) would
  # fail link validation when seeded — but pass in a full build (absolute URLs
  # are treated as external and skipped by the validator).
  python3 scripts/restore_seeded_urls.py ./static-output
  echo "🔄 Running incremental generation (only WordPress posts modified since $LAST_BUILD will be re-fetched)..."
else
  echo "🔨 No incremental cache — first run will fetch all posts and create the cache..."
fi
# Always run in incremental mode: the generator handles first-run (empty cache)
# by fetching all posts and saving .build-cache.json for future incremental runs.
python3 scripts/wp_to_static_generator.py ./static-output

# Count generated files for summary
HTML_COUNT=$(find ./static-output -name "*.html" -type f 2>/dev/null | wc -l | xargs)
TOTAL_SIZE=$(du -sh ./static-output 2>/dev/null | cut -f1)
echo "📊 Generated $HTML_COUNT HTML files, total size: $TOTAL_SIZE"

# Guard: fail fast rather than running all optimisation steps on empty output
if [ "${HTML_COUNT:-0}" -eq 0 ]; then
  echo "❌ ERROR: No HTML files generated — WordPress may be unreachable or returned empty"
  exit 1
fi

# Save to environment file for use in later steps
echo "HTML_COUNT=$HTML_COUNT" >> $GITHUB_ENV
echo "TOTAL_SIZE=$TOTAL_SIZE" >> $GITHUB_ENV

# Capture the raw HTML/CSS *before* any optimisation pass runs. This is
# the fixed starting point the next incremental build seeds from, so
# that post-processing never re-runs over its own output. Everything
# after this line in the pipeline mutates static-output in place.
echo "📸 Capturing raw pre-transform snapshot..."
rm -rf .raw-html-snapshot
mkdir -p .raw-html-snapshot
rsync -a --prune-empty-dirs \
  --include='*/' --include='*.html' --include='*.css' --exclude='*' \
  ./static-output/ .raw-html-snapshot/
RAW_SNAPSHOT_FILES=$(find .raw-html-snapshot -type f | wc -l | xargs)
RAW_SNAPSHOT_SIZE=$(du -sh .raw-html-snapshot 2>/dev/null | cut -f1)
echo "✅ Snapshot: $RAW_SNAPSHOT_FILES files, $RAW_SNAPSHOT_SIZE"

# Reuse already-optimized AVIF/WebP from the previous build in public/
# rsync --ignore-existing skips files that already exist in static-output
# so freshly generated conversions are never overwritten.
if [ -d "public/wp-content/uploads" ] && [ -d "./static-output/wp-content/uploads" ]; then
  echo "📋 Copying already-optimized modern formats via rsync..."
  AVIF_BEFORE=$(find ./static-output/wp-content/uploads -type f -name "*.avif" | wc -l | xargs)
  WEBP_BEFORE=$(find ./static-output/wp-content/uploads -type f -name "*.webp" | wc -l | xargs)

  rsync -a --ignore-existing \
    --include='*/' --include='*.avif' --include='*.webp' \
    --exclude='*' \
    public/wp-content/uploads/ ./static-output/wp-content/uploads/

  AVIF_AFTER=$(find ./static-output/wp-content/uploads -type f -name "*.avif" | wc -l | xargs)
  WEBP_AFTER=$(find ./static-output/wp-content/uploads -type f -name "*.webp" | wc -l | xargs)
  echo "✅ Copied $((AVIF_AFTER - AVIF_BEFORE)) AVIF and $((WEBP_AFTER - WEBP_BEFORE)) WebP files from previous build"

  # NOTE: originals are intentionally NOT copied from the previous
  # build. Nothing in the pipeline recompresses originals in place,
  # so a size difference between public/ and static-output can only
  # mean the image was replaced in WordPress under the same filename
  # — copying the old (smaller) file back served stale content and
  # the rsynced derivatives above then never regenerated.

  # Count how many images still need modern formats.
  #
  # Was TOTAL_IMAGES minus a bare count of every .avif on disk, which
  # is not a subset of TOTAL_IMAGES — derivatives whose source is a
  # format we don't count (or no longer present) inflate it, so the
  # arithmetic went negative and the step reported "-300 of 1852".
  # Ask the real question instead: which sources have no .avif sibling.
  TOTAL_IMAGES=$(find ./static-output/wp-content/uploads -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | wc -l | xargs)
  NEED_CONVERSION=$(find ./static-output/wp-content/uploads -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) \
    | while read -r img; do [ -f "${img%.*}.avif" ] || echo "$img"; done | wc -l | xargs)
  echo "📊 Images needing AVIF/WebP conversion: $NEED_CONVERSION of $TOTAL_IMAGES"
fi

# Add generation summary to GitHub Actions UI
echo "## 📊 Site Generation Summary" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "- **HTML Pages:** $HTML_COUNT" >> $GITHUB_STEP_SUMMARY
echo "- **Total Size:** $TOTAL_SIZE" >> $GITHUB_STEP_SUMMARY
# Backticks must be escaped: unescaped, bash treats them as command
# substitution and tries to execute the directory, which is where the
# stray "./static-output: Is a directory" error in every run came from.
echo "- **Output Directory:** \`./static-output\`" >> $GITHUB_STEP_SUMMARY
