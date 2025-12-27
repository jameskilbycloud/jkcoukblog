# Two-Stage Spell Checker Update

## Summary

The spell checker has been upgraded to use a **two-stage approach** for significantly better performance:

### Stage 1: Fast Traditional Check ⚡
- Uses `pyspellchecker` library for instant dictionary lookup
- Scans all text in milliseconds
- Identifies potentially misspelled words

### Stage 2: AI Validation 🤖
- **Only if** Stage 1 finds candidates
- Batches ALL sections together (title + excerpt + content)
- Single Ollama API call per post (vs 10-20+ previously)
- AI validates with full context

## Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API calls per post | 10-20+ | 1 | 10-20x fewer |
| Processing speed | Slow | Fast | ~10-20x faster |
| Context awareness | Per-section | Full post | Better accuracy |

## Changes Made

### Code Changes
1. **`ollama_spell_checker.py`**
   - Added `fast_spell_check()` method using `pyspellchecker`
   - Added `check_with_ollama_batched()` method for single API call
   - Refactored `check_post()` to use two-stage approach
   - Added `format: json` to Ollama API calls for better reliability
   - Increased timeout to 90s for batched content

2. **`requirements.txt`**
   - Added `pyspellchecker` dependency

3. **Workflow files updated:**
   - `.github/workflows/spell-check-and-fix.yml`
   - `.github/workflows/spell-check.yml`

4. **Documentation updated:**
   - `docs/SPELL_CHECK_AND_FIX.md` - Added two-stage explanation

### New Files
- `test_spell_checker.py` - Test script to verify setup
- `SPELL_CHECKER_UPDATE.md` - This file

## Installation

### On GitHub Runner (Ubuntu)

The GitHub Actions workflows now automatically install the new dependency:

```bash
pip install requests beautifulsoup4 pyspellchecker
```

No additional configuration needed - it will work automatically on the next workflow run.

### Local Development (macOS)

If you want to test locally on your Mac:

```bash
# Option 1: Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./test_spell_checker.py

# Option 2: Using system packages (if allowed)
pip3 install --break-system-packages pyspellchecker
```

Note: Local installation is **optional** - the spell checker runs on the GitHub runner, not locally.

## Usage

No changes to usage - workflows work exactly the same:

```bash
# Check 5 most recent posts
gh workflow run spell-check-and-fix.yml

# Check 10 posts
gh workflow run spell-check-and-fix.yml -f post_count=10

# Check only modified posts
gh workflow run spell-check-and-fix.yml -f check_modified=true
```

## What You'll See

When the spell checker runs, you'll see new output:

```
📄 Checking post ID: 123
   Title: My Blog Post
   URL: https://wordpress.jameskilby.cloud/my-post/
   Found 15 text sections
   ⚡ Stage 1: Fast spell check...
   🔍 Stage 2: Validating 3 candidates with Ollama...
      ⚠️  spelling: teh → the (in title)
   ⚠️  Found 1 confirmed errors
```

## Benefits

✅ **10-20x faster** - Single Ollama call instead of many  
✅ **Better context** - AI sees full post, not isolated sections  
✅ **More accurate** - Fewer false positives on technical terms  
✅ **Same workflow** - No changes to GitHub Actions usage  
✅ **Backward compatible** - Gracefully handles missing dependencies

## Testing

To verify the update works:

```bash
# On the GitHub runner, this will work automatically
./test_spell_checker.py
```

The test will verify:
- All dependencies are installed
- Traditional spell checker works correctly
- Whitelisted terms are excluded
- Known errors are detected

## Rollback

If needed, you can rollback by reverting these commits. The old version will continue to work (just slower).

## Technical Details

### Why pyspellchecker?

- Pure Python (no system dependencies)
- Fast dictionary lookups
- Easy to customize dictionary
- Works on all platforms (Ubuntu runner, macOS)

### Whitelisted Terms

The spell checker automatically whitelists these technical terms:

```python
vmware, vsphere, vsan, vmc, kubernetes, homelab,
cloudflare, github, ansible, terraform, docker,
postgres, nginx, linux, ubuntu, api, json, yaml,
cli, devops, cicd, nvme, pcie, gb, tb, cpu, gpu,
ram, ssd, nas, iscsi, nfs, vlan, acast, plausible,
indexnow, netlify, vimeo, srcset, iframe, jpegoptim,
optipng, fuse
```

More can be added to the `whitelist` set in `ollama_spell_checker.py`.

## Questions?

See the full documentation in `docs/SPELL_CHECK_AND_FIX.md` for detailed workflow information.
