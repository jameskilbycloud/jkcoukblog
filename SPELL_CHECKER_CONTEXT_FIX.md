# Spell Checker Context Fix

## Problem

The spell checker was finding errors that **don't exist in the published post** on your live site.

### Root Cause

The spell checker was using `context=edit` when fetching posts from WordPress REST API. This context returns:

1. ❌ **Draft content** - Unpublished changes you're working on
2. ❌ **Revision history** - Old versions of the post stored by WordPress
3. ❌ **Raw editable content** - Including shortcodes and markup

So if you had:
- A typo in a draft that wasn't published yet
- An old spelling error that was fixed 3 versions ago (but still in revisions)
- Content you edited but didn't save

The spell checker would flag all of these, even though they're not on the live site!

## Solution

Changed to use **different contexts for different operations**:

### When Checking Spelling

```python
params={'context': 'view'}  # Published content only
```

This returns:
- ✅ **Published content** - What visitors actually see
- ✅ **Rendered HTML** - The final output
- ✅ **Current version only** - No drafts or revisions

### When Applying Corrections

```python
params={'context': 'edit'}  # Editable content
```

This returns:
- ✅ **Raw content** - Needed to make edits
- ✅ **Full permissions** - Can modify the post

## Benefits

✅ **No false positives** from draft content  
✅ **No false positives** from old revisions  
✅ **Checks exactly what's live** on your site  
✅ **Still edits correctly** when applying fixes

## Example

**Before (context=edit):**
```
Checking post: "My VMware Setup"
   ⚠️  Found error: "teh" → "the" (in paragraph_3)
   # But you look at the live site and "teh" isn't there!
   # It was in a draft or old revision
```

**After (context=view):**
```
Checking post: "My VMware Setup"
   ✅ No potential errors found
   # Only checks what's actually published
```

## WordPress REST API Context Explained

WordPress REST API supports three context modes:

| Context | Description | Use Case |
|---------|-------------|----------|
| `view` | Public content only | Reading published posts |
| `embed` | Minimal data for embeds | Embedding in other sites |
| `edit` | Full editable data | Making changes |

**Key Differences:**

```json
// context=view
{
  "title": {
    "rendered": "My Post Title"
  },
  "content": {
    "rendered": "<p>Published content</p>"
  }
}

// context=edit (includes raw + drafts)
{
  "title": {
    "raw": "My Post Title",
    "rendered": "My Post Title"
  },
  "content": {
    "raw": "Published content\n\n<!-- Draft paragraph -->",
    "rendered": "<p>Published content</p>"
  }
}
```

The `raw` field in `context=edit` includes everything - published, draft, and revisions.

## Code Changes

**In `wp_spell_check_and_fix.py`:**

1. Line 307: Changed `context=edit` → `context=view` for spell checking
2. Line 471: Added fresh fetch with `context=edit` when applying corrections
3. Line 377: Removed storing `post_data` during check (fetch fresh when needed)

## Testing

To verify this fix works:

1. Make a draft change in WordPress (don't publish)
2. Run spell check workflow
3. Should NOT flag the draft content
4. Only checks published content

---

**Related:** See `SPELL_CHECKER_UPDATE.md` for the full two-stage optimization details.
