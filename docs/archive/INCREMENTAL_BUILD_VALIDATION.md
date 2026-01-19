# Validating Incremental Builds - Quick Reference

## 6 Ways to Validate Incremental Builds

### 1. ✅ Build Output Messages

**First Build (creating cache):**
```
🚀 WordPress to Static Site Generator
Mode: Full build (creating cache)
📋 Discovering content from WordPress REST API...
   🔍 Fetching posts page 1...
⬇️  Processing 156 URLs...
📦 Build Cache:
   Cached posts: 145
   Cached pages: 8
💾 Build cache saved to .build-cache.json
Duration: 12.3 seconds
```

**Incremental Build:**
```
🚀 WordPress to Static Site Generator
Mode: Incremental (cache has 153 entries)
📋 Discovering content (incremental mode)...
🔄 Incremental build - checking posts modified since 2026-01-14T15:30:00
📊 Incremental build: 2 changed posts
   📄 Changed post: My Updated Post
⬇️  Processing 2 URLs...
📦 Build Cache:
   Cached posts: 145
   Cached pages: 8
   ⚡ Time saved vs full build: ~75%
Duration: 3.2 seconds
```

### 2. 📊 Cache Statistics

```bash
# Before build
$ python3 manage_build_cache.py stats
📊 Build Cache Statistics
============================================================
Posts cached:      145
Pages cached:      8
Assets cached:     0
Total entries:     153
Last build:        2026-01-14 15:30:45 (2 hours ago)
Last full build:   2026-01-14 08:00:12
============================================================

# After incremental build
$ python3 manage_build_cache.py stats
📊 Build Cache Statistics
============================================================
Posts cached:      145    # Same or increased
Pages cached:      8      # Same or increased
Last build:        2026-01-14 17:45:12 (just now)  # UPDATED!
Last full build:   2026-01-14 08:00:12              # Unchanged
============================================================
```

### 3. ⏱️ Build Time Comparison

```bash
# Time both builds
$ time python3 wp_to_static_generator.py ./public

# First build output:
real    0m12.345s   # ~12 seconds

# Second build (no changes) output:
real    0m2.567s    # ~2-3 seconds - 75-80% FASTER!
```

### 4. 🗂️ Cache File Verification

```bash
# Check cache exists
$ ls -lh .build-cache.json
-rw-r--r--  1 user  staff   45K Jan 14 15:30 .build-cache.json

# View cache structure
$ cat .build-cache.json | python3 -m json.tool | head -30
{
  "posts": {
    "/2024/01/my-post/": {
      "hash": "abc123def456",
      "modified": "2024-01-14T15:30:00",
      "processed": "2024-01-14T15:35:22"
    },
    ...
  },
  "pages": {
    "/about/": {
      "hash": "xyz789ghi012",
      "modified": "2024-01-10T12:00:00",
      "processed": "2024-01-14T15:35:25"
    }
  },
  "last_build_time": "2024-01-14T15:35:30",
  "last_full_build": "2024-01-14T08:00:00"
}
```

### 5. 🔄 Force Full Build Test

```bash
# Clear cache and rebuild
$ python3 manage_build_cache.py clear
🗑️  Build cache cleared - next build will be full

$ time python3 wp_to_static_generator.py ./public
# Should take ~12 seconds and show "Mode: Full build (creating cache)"

# Alternative: Use --no-incremental flag
$ time python3 wp_to_static_generator.py ./public --no-incremental
```

### 6. 🔍 Inspect Detailed Cache

```bash
$ python3 manage_build_cache.py inspect
🔍 Detailed Cache Contents
============================================================

📝 Recent Posts (145 total):
  • /2024/01/latest-post/
    Processed: 2026-01-14 15:35
    Hash: abc123def456...
  • /2024/01/another-post/
    Processed: 2026-01-14 15:35
    Hash: def456ghi789...
  ...

📄 Recent Pages (8 total):
  • /about/
    Processed: 2026-01-14 15:35
  • /contact/
    Processed: 2026-01-14 15:35
  ...
============================================================
```

## Running Automated Tests

```bash
# Run all incremental build tests
$ python3 test_incremental_build.py

🧪 Incremental Build System Tests
============================================================
  Test 1: Cache Operations
  ✅ Cache operations test passed!

  Test 2: Cache Persistence
  ✅ Cache persistence test passed!

  Test 3: Archive Rebuild Logic
  ✅ Archive rebuild logic test passed!
  
✅ All tests passed!
```

## Expected Behavior Summary

| Scenario | URLs Processed | Duration | Cache Updated |
|----------|----------------|----------|---------------|
| First build (no cache) | ~156 URLs | ~12s | ✅ Created |
| No changes | 0-3 URLs (archives only) | ~2-3s | ✅ Updated timestamp |
| 2 posts edited | 2 posts + archives | ~3-4s | ✅ Updated hashes |
| 10 posts added | 10 posts + archives | ~5-6s | ✅ Added entries |
| Full rebuild forced | ~156 URLs | ~12s | ✅ Recreated |

## Troubleshooting

### ❌ "Mode: Full build" every time
**Cause:** Cache not persisting
```bash
# Check if cache file exists
$ ls -la .build-cache.json

# If missing, check for errors in output
$ python3 wp_to_static_generator.py ./public 2>&1 | grep -i cache
```

### ❌ Build still takes ~12 seconds
**Possible causes:**
1. First build (creating cache) - normal
2. Many posts changed - check output for "X changed posts"
3. Cache cleared or corrupted
4. Using `--no-incremental` flag

**Verify:**
```bash
python3 manage_build_cache.py stats
# Check when last build was
```

### ❌ Changes not showing up
**Causes:**
1. WordPress `modified` date not updated
2. Archive pages rebuilt daily (might be old)

**Solution:**
```bash
# Force full rebuild to sync everything
python3 manage_build_cache.py clear
python3 wp_to_static_generator.py ./public
```

## Quick Start Validation

```bash
# 1. Clear any existing cache
python3 manage_build_cache.py clear

# 2. First build (should take ~12s)
time python3 wp_to_static_generator.py ./public
# Look for: "Mode: Full build (creating cache)"

# 3. Check cache was created
python3 manage_build_cache.py stats

# 4. Second build immediately (should take ~2-3s)
time python3 wp_to_static_generator.py ./public
# Look for: "Mode: Incremental (cache has X entries)"

# 5. Verify time savings shown
# Look for: "⚡ Time saved vs full build: ~75%"
```

## Success Indicators

✅ Cache file `.build-cache.json` exists and grows  
✅ Second build is 75-80% faster  
✅ Build output shows "Mode: Incremental"  
✅ Only changed URLs are processed  
✅ `manage_build_cache.py stats` shows recent timestamps  
✅ Time savings percentage is displayed  

If you see all of these, **incremental builds are working perfectly!** 🎉
