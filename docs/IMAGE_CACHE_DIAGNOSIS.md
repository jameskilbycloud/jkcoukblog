# Image Optimization Cache Diagnosis

## Issue Summary
The image optimization cache in the GitHub Actions workflow is not persisting between runs, causing all images to be re-optimized on every build instead of skipping unchanged images.

## Root Cause Analysis

### Current Cache Status (as of 2026-01-15)
- **Local cache file**: Empty (`{}`) - 2 bytes
- **Live site**: Working perfectly - AVIF images delivered with 90% savings
- **Local AVIF files**: 1,224 files present
- **GitHub Actions cache**: Configured but not effective

### The Problem
The cache was intentionally cleared on January 12, 2026 (commit 62bc9ff00: "Temporarily disable image optimization cache for troubleshooting"). Since then:

1. **GitHub Actions cache is restored** but finds an empty cache
2. **Images are optimized** but the cache remains empty
3. **Next run repeats step 1** - cache is still empty

### Why Cache Isn't Being Populated

The workflow steps are:
1. ✓ Restore cache from GitHub Actions cache
2. ✓ Run `optimize_images.py`
3. ⚠️  Cache should be saved by `optimize_images.py` at line 389
4. ❌ Cache file remains empty

**Possible causes:**
- Script exits before reaching `_save_cache()` call
- Exception during cache save is silently caught
- File permissions issue
- Cache directory path mismatch

## Verification Added to Workflow

### 1. Cache Restore Verification (Line 175-186)
```yaml
- name: Check cache status
  run: |
    echo "🔍 Checking cache restoration status..."
    echo "Cache hit: ${{ steps.cache-restore.outputs.cache-hit }}"
    echo "Cache matched key: ${{ steps.cache-restore.outputs.cache-matched-key }}"
    
    if [ -f ".image_optimization_cache/optimization_cache.json" ]; then
      ENTRIES=$(python3 -c "import json; print(len(json.load(open('.image_optimization_cache/optimization_cache.json'))))" 2>/dev/null || echo "0")
      echo "✓ Cache file exists with $ENTRIES entries"
    else
      echo "⚠️  Cache file not found (will be created on first run)"
    fi
```

### 2. Cache Update Verification (Line 476-498)
```yaml
- name: Verify cache was updated
  run: |
    echo "🔍 Verifying cache was updated after optimization..."
    
    if [ -f ".image_optimization_cache/optimization_cache.json" ]; then
      ENTRIES=$(python3 -c "import json; print(len(json.load(open('.image_optimization_cache/optimization_cache.json'))))" 2>/dev/null || echo "0")
      SIZE=$(wc -c < ".image_optimization_cache/optimization_cache.json")
      echo "✓ Cache file exists"
      echo "  Entries: $ENTRIES"
      echo "  Size: $SIZE bytes"
      
      if [ "$ENTRIES" -gt 0 ]; then
        echo "✓ Cache successfully populated"
        echo "  Sample entries:"
        python3 -c "import json; data=json.load(open('.image_optimization_cache/optimization_cache.json')); import itertools; [print(f'    - {k}') for k in itertools.islice(data.keys(), 3)]" 2>/dev/null || true
      else
        echo "⚠️  WARNING: Cache file is empty!"
        echo "  This means all images were skipped or optimization failed."
      fi
    else
      echo "❌ ERROR: Cache file was not created!"
      echo "  The optimization script may have failed to save the cache."
    fi
```

## Diagnostic Script

A diagnostic script `diagnose_cache.sh` has been created to help troubleshoot cache issues:

```bash
./diagnose_cache.sh
```

This script checks:
1. Cache directory and file status
2. Optimization tools installation
3. Git tracking of cache
4. Recent optimization results

## Expected Behavior

### First Run (Empty Cache)
```
🔍 Checking cache restoration status...
Cache hit: false
⚠️  Cache file not found (will be created on first run)

🖼️  Starting advanced image optimization with AVIF...
📊 Found 1223 images to process
   • Newly Optimized: 1223
   • Cached (Skipped): 0

🔍 Verifying cache was updated...
✓ Cache file exists
  Entries: 1223
  Size: 245678 bytes
✓ Cache successfully populated
```

### Subsequent Runs (With Cache)
```
🔍 Checking cache restoration status...
Cache hit: true
Cache matched key: build-cache-avif-v2-abc123...
✓ Cache file exists with 1223 entries

🖼️  Starting advanced image optimization with AVIF...
📊 Found 1223 images to process
   • Newly Optimized: 0
   • Cached (Skipped): 1223

🔍 Verifying cache was updated...
✓ Cache file exists
  Entries: 1223
  Size: 245678 bytes
✓ Cache successfully populated
```

## How the Cache Works

### Cache Flow
```
┌─────────────────────────────────────────────────────┐
│ 1. GitHub Actions: Restore Cache                    │
│    - Restores .image_optimization_cache/            │
│    - Key: build-cache-avif-v2-{sha}                │
│    - Restore keys: build-cache-avif-v2-*            │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│ 2. Load Cache (optimize_images.py line 70-78)      │
│    - Reads optimization_cache.json                  │
│    - Loads MD5 hashes of optimized images          │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│ 3. Process Images (line 322-391)                   │
│    - For each image:                                │
│      * Calculate MD5 hash                           │
│      * Check if hash exists in cache                │
│      * If match: skip optimization                  │
│      * If no match: optimize and update cache       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│ 4. Save Cache (line 389)                           │
│    - Writes updated cache to optimization_cache.json│
│    - Includes all processed images                  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│ 5. Commit to Git (workflow line 607)               │
│    - git add .image_optimization_cache/             │
│    - Commits with site files                        │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│ 6. GitHub Actions: Save Cache (automatic)          │
│    - Saves .image_optimization_cache/ directory     │
│    - Available for next workflow run                │
└─────────────────────────────────────────────────────┘
```

### Cache Storage
- **GitHub Actions Cache**: Temporary, 7-day retention if unused
- **Git Repository**: Permanent, committed with each deployment
- **Both used**: Git for long-term, Actions cache for speed

## Testing the Fix

### Next Steps
1. **Commit the diagnostic changes**:
   ```bash
   git add .github/workflows/deploy-static-site.yml diagnose_cache.sh docs/IMAGE_CACHE_DIAGNOSIS.md
   git commit -m "Add cache diagnostics to image optimization workflow"
   git push
   ```

2. **Trigger a manual workflow run**:
   ```bash
   gh workflow run deploy-static-site.yml
   ```

3. **Monitor the workflow logs** for:
   - "Cache hit: true/false" message
   - Number of entries after restoration
   - Number of newly optimized vs cached images
   - Cache file size after optimization

4. **Check next run** - should see:
   - Cache hit: true
   - Most images cached (skipped)
   - Build time reduced by 30-40 seconds

## Performance Impact

### Without Cache (Current)
- **All images optimized**: ~1200 images
- **Time**: 30-45 seconds
- **Every build**: Same time

### With Cache (Expected)
- **First run**: 30-45 seconds (populate cache)
- **Subsequent runs**: 2-5 seconds (cache hits)
- **Changed images only**: Incremental optimization
- **Build speedup**: 75-80% faster

## Related Files
- `.github/workflows/deploy-static-site.yml` - Workflow configuration
- `optimize_images.py` - Image optimization script
- `.image_optimization_cache/optimization_cache.json` - Cache file
- `diagnose_cache.sh` - Diagnostic script
- `docs/archive/IMAGE_OPTIMIZATION.md` - Original documentation

## Troubleshooting

### If cache still doesn't work after this fix:

1. **Check if tools are installed**:
   ```bash
   ./diagnose_cache.sh
   ```

2. **Look for Python exceptions**:
   - Check workflow logs for "Could not save cache" warning
   - Check if `_save_cache()` is reached

3. **Verify file permissions**:
   - Cache directory should be writable
   - Runner should have permission to create/update files

4. **Check GitHub Actions cache**:
   - Go to repo → Actions → Caches
   - Verify "build-cache-avif-v2-*" entries exist
   - Check cache size and last used date

5. **Force cache refresh**:
   ```bash
   # Clear local cache and commit
   echo '{}' > .image_optimization_cache/optimization_cache.json
   git add .image_optimization_cache/optimization_cache.json
   git commit -m "Reset image optimization cache"
   git push
   ```

## Success Criteria

✓ Cache file populated after first run (>1000 entries)  
✓ Subsequent runs show "Cache hit: true"  
✓ Most images show "was_cached: true"  
✓ Build time reduced by 75-80%  
✓ Cache committed to git  
✓ No re-optimization of unchanged images  
