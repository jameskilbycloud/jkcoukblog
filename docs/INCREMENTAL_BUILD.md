# Incremental Build System

The incremental build system dramatically speeds up static site generation by only regenerating content that has changed since the last build.

## Overview

Instead of regenerating the entire site on every build (which can take 12+ seconds and process 150+ URLs), the incremental builder:

- ✅ Tracks what's already been built using a cache file
- ✅ Queries WordPress for only modified content
- ✅ Skips unchanged posts, pages, and assets
- ✅ Reduces build time from 12s to ~2-5s for typical updates
- ✅ Saves bandwidth and API requests

## How It Works

### 1. Build Cache
The system maintains a `.build-cache.json` file that tracks:
- Every post/page URL that's been processed
- Content hash for each item
- Last modified timestamp
- Last build time
- Last full build time

### 2. Change Detection
On each build, the system:
1. Queries WordPress API with `modified_after` parameter
2. Compares content hashes for changed items
3. Only regenerates what's actually changed
4. Rebuilds archive pages (home, categories, tags) when needed

### 3. Smart Rebuilding
- **Individual posts**: Only regenerate if modified
- **Archive pages**: Rebuild daily or when posts change
- **Assets**: Track by hash, skip if unchanged
- **Full rebuild**: Once per day to ensure consistency

## Usage

### Standard Build (with Incremental)
The incremental builder is automatically used by the generator:

```bash
# First build - processes everything
python3 wp_to_static_generator.py ./public

# Subsequent builds - only changed content
python3 wp_to_static_generator.py ./public
```

### Force Full Build
To force a complete rebuild (ignoring cache):

```bash
# Clear the cache first
python3 manage_build_cache.py clear

# Then build
python3 wp_to_static_generator.py ./public
```

### Check Cache Status
View what's cached and when:

```bash
# Show statistics
python3 manage_build_cache.py stats

# Show detailed contents
python3 manage_build_cache.py inspect
```

## Performance Benefits

### Before (Full Build)
```
📋 Discovering content: 156 URLs
⬇️  Processing 156 URLs...
⏱️  Duration: ~12 seconds
```

### After (Incremental Build)
```
🔄 Incremental build: 2 changed posts
⬇️  Processing 2 URLs...
⏱️  Duration: ~2-3 seconds
```

**Time savings: 75-80% reduction for typical updates**

## Cache Management Commands

### View Statistics
```bash
python3 manage_build_cache.py stats
```

Output:
```
📊 Build Cache Statistics
============================================================
Posts cached:      145
Pages cached:      8
Assets cached:     0
Total entries:     153
Last build:        2026-01-14 15:30:45 (2 hours ago)
Last full build:   2026-01-14 08:00:12
============================================================
```

### Inspect Cache
```bash
python3 manage_build_cache.py inspect
```

Shows detailed info about cached items including URLs, hashes, and processing timestamps.

### Clear Cache
```bash
python3 manage_build_cache.py clear
```

Removes all cached data - next build will be a full rebuild.

## Cache File Format

The `.build-cache.json` file structure:

```json
{
  "posts": {
    "/2024/01/my-post/": {
      "hash": "abc123def456",
      "modified": "2024-01-14T15:30:00",
      "processed": "2024-01-14T15:35:22"
    }
  },
  "pages": {
    "/about/": {
      "hash": "xyz789ghi012",
      "modified": "2024-01-10T12:00:00",
      "processed": "2024-01-14T15:35:25"
    }
  },
  "assets": {},
  "last_build_time": "2024-01-14T15:35:30",
  "last_full_build": "2024-01-14T08:00:00"
}
```

## Integration with CI/CD

The cache file should be committed to your repository to enable incremental builds in GitHub Actions:

```yaml
# In .github/workflows/deploy-static-site.yml

- name: Generate static site (incremental)
  run: |
    # Cache is automatically loaded from .build-cache.json
    python3 wp_to_static_generator.py ./public
  env:
    WP_AUTH_TOKEN: ${{ secrets.WP_AUTH_TOKEN }}

- name: Commit cache and public directory
  run: |
    git add .build-cache.json public/
    git commit -m "Update site (incremental build)"
```

## When to Force Full Rebuild

You should clear the cache and force a full rebuild when:

- ❌ Theme or layout changes (affects all pages)
- ❌ Global configuration changes
- ❌ Search index needs complete regeneration
- ❌ Sitemap or RSS feed issues
- ❌ Cache corruption suspected
- ❌ Major WordPress updates

For normal content updates (new posts, edits), incremental builds are perfect.

## Archive Page Rebuilding

Archive pages (home, categories, tags) are rebuilt:
- When any post changes
- Once per day (even with no changes)
- When cache is cleared

This ensures lists stay up-to-date while minimizing unnecessary work.

## Troubleshooting

### Cache Not Working
Check if `.build-cache.json` exists and is readable:
```bash
ls -la .build-cache.json
python3 manage_build_cache.py stats
```

### Builds Still Slow
- First build is always full (creates cache)
- Check how many items show as "changed" in output
- Verify WordPress API is returning correct `modified_after` results

### Content Not Updating
- WordPress `modified` timestamp must change
- Archive pages rebuild daily automatically
- Force full rebuild if needed: `python3 manage_build_cache.py clear`

## API Usage

You can also use the incremental builder programmatically:

```python
from incremental_builder import IncrementalBuilder

# Initialize
builder = IncrementalBuilder('.build-cache.json')

# Get changed posts
changed_posts = builder.get_changed_posts(session, wp_url)

# Check if specific content changed
if builder.has_changed(url, content_hash, modified_date):
    # Regenerate this content
    process_content(url)
    
    # Mark as processed
    builder.mark_processed(url, content_hash, modified_date)

# Finalize
builder.finalize_build(is_full_build=True)
```

## Benefits Summary

✅ **Faster builds**: 75-80% time reduction
✅ **Lower bandwidth**: Fewer API calls and downloads
✅ **Reduced load**: Less work for WordPress server
✅ **CI/CD friendly**: Faster deploys in GitHub Actions
✅ **Smart caching**: Automatic detection of stale content
✅ **Transparent**: Works without configuration changes

The incremental builder makes frequent site updates practical and efficient!
