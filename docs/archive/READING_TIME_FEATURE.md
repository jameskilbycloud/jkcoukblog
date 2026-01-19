# Reading Time & Word Count Feature

## Overview

This feature adds visible reading time and word count indicators to all blog posts, providing readers with transparency about article length before they commit to reading.

## Implementation

### Location

Reading time is displayed in the **entry-meta** section of each post, directly after the author and date information.

### Visual Display

```
By James • December 15, 2025 • 📖 5 min read (1,234 words)
```

### How It Works

1. **Content Extraction**: The `_extract_article_text()` method extracts the main article content from the post
2. **Word Count Calculation**: Counts all words in the article content
3. **Reading Time Calculation**: Uses the industry standard of 200 words per minute
4. **HTML Injection**: Adds a styled `<span>` element to the entry-meta div with:
   - Book icon (📖)
   - Reading time in minutes
   - Word count with thousands separator

### Code Location

**File**: `wp_to_static_generator.py`

**Function**: `add_reading_time_indicator(soup)`

**Called from**: `process_html()` method during static site generation

### Styling

The reading time indicator uses inline CSS to match the existing theme:
- Color: `#718096` (gray-600)
- Word count: `#a0aec0` (lighter gray)
- Separator: `•` bullet character
- Icon: 📖 book emoji

## Schema Integration

Reading time and word count are also added to JSON-LD structured data for SEO:

```json
{
  "@type": "BlogPosting",
  "wordCount": 1234,
  "timeRequired": "PT5M"
}
```

This enables rich results in search engines and helps with content discovery.

## Benefits

### User Experience
- **Transparency**: Readers know article length before committing
- **Time Management**: Helps users decide if they have time to read now
- **Engagement**: Short articles may attract quick readers, long articles signal depth

### SEO Benefits
- **Rich Results**: JSON-LD data can appear in search results
- **User Signals**: Better engagement metrics from informed readers
- **Content Depth**: Word count signals comprehensive coverage

### Best Practices Alignment
- Follows patterns from Medium, Dev.to, and other modern blogs
- Industry-standard 200 words/minute reading speed
- Non-intrusive visual design
- Mobile-friendly display

## Testing

To test the feature after regenerating the site:

1. Generate static site:
   ```bash
   python3 wp_to_static_generator.py ./public
   ```

2. Check console output for:
   ```
   📖 Added reading time: X min (Y words)
   ```

3. Inspect generated HTML:
   ```bash
   grep -A 5 "reading-time" public/2025/12/*/index.html
   ```

4. View live in browser:
   - Look for reading time in entry-meta section
   - Verify formatting matches site theme

## Preview

A preview HTML file is available at `test-reading-time-preview.html` showing:
- Before/after comparison
- Examples with different article lengths
- Visual styling

Open in browser:
```bash
open test-reading-time-preview.html
```

## Configuration

### Adjusting Reading Speed

Default: 200 words per minute

To adjust, modify line in `add_reading_time_indicator()`:
```python
reading_minutes = max(1, round(word_count / 200))  # Change 200 to desired WPM
```

### Hiding Word Count

To show only reading time (not word count), comment out lines:
```python
# word_count_text = soup.new_tag('span')
# word_count_text['style'] = 'margin-left: 4px; color: #a0aec0;'
# word_count_text.string = f'({word_count:,} words)'
# reading_time_span.append(word_count_text)
```

### Changing Icons

Replace the book emoji with any Unicode character or HTML entity:
```python
time_icon.string = '⏱️'  # Clock icon
time_icon.string = '📝'  # Memo icon
time_icon.string = '👓'  # Glasses icon
```

## Deployment

The feature is automatically applied during the next site generation:

1. **Manual**: Run `python3 wp_to_static_generator.py ./public`
2. **Automated**: GitHub Actions workflow triggers on repository_dispatch
3. **Trigger**: WordPress webhook sends update notification

No changes needed to WordPress or theme configuration.

## Related Documentation

- [SEO.md](SEO.md) - SEO optimizations including reading time
- [WARP.md](archive/WARP.md) - Project overview and architecture
- [RICH_RESULTS_ENHANCEMENTS.md](archive/RICH_RESULTS_ENHANCEMENTS.md) - Schema markup details

## Future Enhancements

Possible improvements:
- [ ] Add reading progress bar
- [ ] Show estimated time to read remaining content
- [ ] Adjust reading speed based on content type (code-heavy vs prose)
- [ ] Add reading statistics to analytics
- [ ] Show "X% read" indicator
