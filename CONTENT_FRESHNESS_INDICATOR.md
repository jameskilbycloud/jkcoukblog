# Content Freshness Indicator

## Overview

The Content Freshness Indicator is a visible UI element that displays both the original publication date and the last updated date for blog posts and pages. This transparency helps readers understand when content was written and whether it has been recently updated.

## Implementation

### Location in Codebase

**File:** `wp_to_static_generator.py`  
**Method:** `add_content_freshness_indicator(soup)`  
**Called from:** `process_html()` method in the HTML processing pipeline

### How It Works

1. **Date Extraction**
   - Extracts `datePublished` and `dateModified` from JSON-LD structured data
   - Supports both direct schema and `@graph` structure (used by Rank Math SEO)
   - Looks for `BlogPosting` and `WebPage` schema types

2. **Date Comparison**
   - Parses ISO 8601 datetime strings
   - Compares publication and modification dates
   - **Only displays indicator if dates are on different days** (same-day edits don't trigger display)

3. **Visual Insertion**
   - Finds appropriate insertion point (entry header, meta section, or article element)
   - Creates styled div with calendar icon and formatted dates
   - Uses semantic `<time>` HTML5 elements with `datetime` attributes

### Visual Design

```html
<div class="content-freshness-indicator" style="...">
    <span>📅</span>
    <span>
        <strong>Published: </strong>
        <time datetime="2024-01-15T10:00:00+00:00">January 15, 2024</time>
        <span>•</span>
        <strong>Updated: </strong>
        <time datetime="2024-03-20T14:30:00+00:00">March 20, 2024</time>
    </span>
</div>
```

**Styling:**
- Light blue background (#f7fafc)
- Blue left border (4px solid #4299e1)
- Calendar icon (📅)
- Clean, readable typography
- Responsive design with proper spacing

## User Experience

### When It Appears

✅ **Shows when:**
- Post has been updated on a different day than publication
- Both `datePublished` and `dateModified` exist in JSON-LD
- Dates are successfully parsed

❌ **Hidden when:**
- Post was never updated (published = modified dates)
- Same-day edits (allows for typo fixes without showing indicator)
- Missing date metadata
- Page types without structured data (category archives, etc.)

### Example Output

For a post published on January 15, 2024 and updated on March 20, 2024:

```
📅 Published: January 15, 2024 • Updated: March 20, 2024
```

## Benefits

### For Readers

1. **Content Trust**
   - See when information was last verified/updated
   - Helps assess relevance of time-sensitive content
   - Transparency builds credibility

2. **SEO Context**
   - Understand content age
   - Signals that content is maintained
   - Shows commitment to accuracy

### For Content Creators

1. **Encourages Updates**
   - Visual feedback for maintaining content
   - Reward for keeping articles current
   - Differentiates evergreen vs. stale content

2. **SEO Benefits**
   - Google values fresh, updated content
   - Structured datetime attributes improve crawling
   - Signals content maintenance to search engines

## Technical Details

### Date Format

**Input:** ISO 8601 datetime strings from WordPress  
- Example: `2024-01-15T10:00:00+00:00`

**Output:** Human-readable format  
- Example: `January 15, 2024`
- Format string: `%B %d, %Y`

### Semantic HTML

Uses HTML5 `<time>` elements with proper `datetime` attributes:

```html
<time datetime="2024-01-15T10:00:00+00:00">January 15, 2024</time>
```

This provides:
- Machine-readable dates for search engines
- Accessibility for screen readers
- Structured data compliance
- Future-proof date representation

### Theme Compatibility

The indicator works with any WordPress theme by:
- Trying multiple insertion points (header, meta, title, article)
- Using inline styles (no theme CSS dependencies)
- Semantic HTML structure
- Non-intrusive visual design

**Tested insertion points (in priority order):**
1. `<header class="entry-header">`
2. `<div class="entry-meta">`
3. `<h1 class="entry-title">`
4. `<article>` (fallback)

## Configuration

### Modifying Appearance

Edit the `style` attribute in `wp_to_static_generator.py`:

```python
freshness_div['style'] = '''
    background: #f7fafc;        # Background color
    border-left: 4px solid #4299e1;  # Left border
    padding: 12px 16px;         # Spacing
    margin: 20px 0;             # Vertical spacing
    border-radius: 4px;         # Rounded corners
    font-size: 14px;            # Text size
    line-height: 1.6;           # Line spacing
    color: #2d3748;             # Text color
'''
```

### Changing Date Format

Modify the `strftime()` format string:

```python
# Current format: "January 15, 2024"
pub_formatted = pub_dt.strftime('%B %d, %Y')

# Alternative formats:
# "Jan 15, 2024"     → '%b %d, %Y'
# "2024-01-15"       → '%Y-%m-%d'
# "15 Jan 2024"      → '%d %b %Y'
# "January 15th"     → Custom logic needed
```

### Disabling Same-Day Filter

To show indicator even for same-day edits:

```python
# Current (skips same-day)
if pub_dt.date() == mod_dt.date():
    return

# Modified (shows all updates)
# Remove or comment out the above check
```

## Testing

### Test Script

Run the included test suite:

```bash
python3 test_content_freshness.py
```

**Tests:**
1. Date parsing and formatting
2. Same-day edit detection
3. HTML structure validation

### Manual Testing

1. **Generate site:**
   ```bash
   python3 wp_to_static_generator.py ./public
   ```

2. **Check output:**
   - Look for console log: `📅 Added content freshness indicator`
   - Open generated HTML file
   - Search for `class="content-freshness-indicator"`

3. **Verify display:**
   - Start local server: `python3 deploy_static_site.py server ./public 8080`
   - Visit post in browser
   - Check indicator appears below title/header

## Integration with GitHub Actions

The feature is automatically enabled in the CI/CD pipeline:

```yaml
# .github/workflows/deploy-static-site.yml
- name: Generate static site
  run: |
    python3 wp_to_static_generator.py ./public
```

No additional configuration needed - works automatically when:
- WordPress posts have different published/modified dates
- JSON-LD structured data is present
- Static site generation runs

## Performance Impact

**Minimal:**
- Only processes JSON-LD already in page
- No additional API calls
- Pure Python string/datetime operations
- Adds ~200 bytes per page with indicator

**Processing time:** < 1ms per page

## Accessibility

**Features:**
- Semantic `<time>` elements
- Clear visual hierarchy
- Readable color contrast (WCAG AA compliant)
- Screen reader friendly
- No JavaScript dependencies

**Screen reader announcement:**
> "Published: January 15, 2024, Updated: March 20, 2024"

## SEO Impact

**Positive effects:**
1. Structured datetime attributes
2. Signals content freshness to crawlers
3. User engagement (transparency)
4. Encourages content updates

**No negative effects:**
- Doesn't duplicate existing dates
- Doesn't interfere with schema
- Doesn't impact page speed

## Future Enhancements

**Potential improvements:**

1. **Update Age Badge**
   - "Updated 2 months ago"
   - Color-coding (green = recent, yellow = older)

2. **Changelog Link**
   - Link to "What's new" section
   - Show update summary

3. **Version History**
   - Track multiple update dates
   - Show revision count

4. **RSS Feed Integration**
   - Include update dates in feed
   - Notify subscribers of updates

5. **Analytics Integration**
   - Track which posts are kept current
   - Identify stale content automatically

## Related Documentation

- `WARP.md` - Project overview
- `SEO_QUICK_WINS.md` - SEO improvements
- `RICH_RESULTS_ENHANCEMENTS.md` - Schema markup
- `README.md` - General documentation

## Troubleshooting

### Indicator Not Appearing

**Check:**
1. Are published and modified dates different?
2. Is JSON-LD present in the page?
3. Does JSON-LD contain `BlogPosting` or `WebPage` type?
4. Are dates in valid ISO 8601 format?

**Debug:**
```bash
# Check generated HTML
grep -A 5 'content-freshness-indicator' public/path/to/post/index.html

# Check JSON-LD dates
grep -o '"datePublished":"[^"]*"' public/path/to/post/index.html
grep -o '"dateModified":"[^"]*"' public/path/to/post/index.html
```

### Styling Issues

**Fix inline styles:**
- Ensure no CSS interference from theme
- Check browser dev tools for overrides
- Adjust z-index if covered by other elements

### Date Format Issues

**Python datetime errors:**
- Ensure Python 3.7+ (for `fromisoformat()`)
- Check date string format matches ISO 8601
- Handle timezone conversions properly

## Author Notes

**Design decisions:**

1. **Why inline styles?**
   - No theme dependencies
   - Guaranteed consistency
   - Works with any theme

2. **Why hide same-day edits?**
   - Avoid clutter for minor fixes
   - Focus on significant updates
   - User expectations (updates = different days)

3. **Why insert after header?**
   - Prominent but not intrusive
   - Logical placement
   - Standard blog pattern

4. **Why calendar icon?**
   - Universal symbol
   - Visual anchor
   - Breaks up text

## Version History

- **v1.0** (2025-12-17) - Initial implementation
  - Date extraction from JSON-LD
  - Same-day edit filtering
  - Semantic HTML structure
  - Inline styling
  - Test suite
