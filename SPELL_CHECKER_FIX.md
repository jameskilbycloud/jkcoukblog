# Spell Checker Fix - December 5, 2025

## Issue Fixed

**Problem**: Spell checker was finding "0 text sections to check" for all posts.

**Root Cause**: The `extract_text_from_html()` function was designed to parse full HTML pages, but the WordPress REST API only returns the post content HTML (not the full page with title, meta tags, etc.).

## Solution

Updated `extract_text_from_html()` to:

1. **Accept title and excerpt from API** as parameters
2. **Decode HTML entities** (e.g., `&#8211;` → `–`)
3. **Extract content directly from API response** instead of looking for page structure
4. **Parse paragraphs and headings** from the content HTML

## Changes Made

### Modified Function Signature
```python
# Before
def extract_text_from_html(self, html_content: str)

# After  
def extract_text_from_html(self, html_content: str, post_title: str = '', post_excerpt: str = '')
```

### What Gets Checked Now

1. **Title** - From API `title.rendered` field (HTML entities decoded)
2. **Excerpt** - From API `excerpt.rendered` field (HTML stripped)
3. **Paragraphs** - All `<p>` tags in content (>20 chars)
4. **Headings** - All `<h1>`, `<h2>`, `<h3>`, `<h4>` tags (>5 chars)

### What's Excluded

- Code blocks (`<pre>`, `<code>`)
- Scripts and styles
- Very short paragraphs (<20 chars)
- Very short headings (<5 chars)

## Test It Now

```bash
# Set your token
export WP_AUTH_TOKEN="your_token"

# Test on 1 post
./ollama_spell_checker.py 1
```

## Expected Output

```
🔍 Checking 1 most recent posts...
📄 Checking post ID: 7127
   Title: How I upgraded my blog as a Static Website with GitHub Actions...
   URL: https://wordpress.jameskilby.cloud/2025/10/...
   Found 25 text sections to check
   🔍 Checking title...
   🔍 Checking excerpt...
   🔍 Checking paragraph_1...
   🔍 Checking paragraph_2...
   🔍 Checking heading_1...
   ...
```

## Files Modified

- ✅ `ollama_spell_checker.py` - Fixed text extraction logic
- ✅ `SPELL_CHECKER_FIX.md` - This documentation

## How It Works Now

```
WordPress REST API
├── /wp-json/wp/v2/posts/{id}
│   ├── title.rendered → Extracted directly
│   ├── excerpt.rendered → Extracted directly  
│   └── content.rendered → Parsed for paragraphs & headings
└── Returns JSON (not full HTML page)
```

## Why It Failed Before

The original code expected:
- `<h1 class="entry-title">` for title
- `<meta name="description">` for description
- `<div class="entry-content">` wrapper

But WordPress REST API returns:
- Just the post content HTML
- No page wrapper
- No meta tags
- Title and excerpt as separate JSON fields

## Verification

After the fix, you should see text sections being extracted:

```bash
# Before fix
Found 0 text sections to check

# After fix
Found 25 text sections to check
```

## Note About Cloudflare Access

The WordPress site is behind Cloudflare Access, but that's **not a problem** because:
- We authenticate via WordPress REST API (using `WP_AUTH_TOKEN`)
- We never fetch the actual URLs directly
- All content comes from REST API responses
- Cloudflare Access doesn't protect the REST API when using proper authentication

## Integration Status

- ✅ Script works locally
- ✅ GitHub Actions workflow configured
- ✅ Ready for automated checks
