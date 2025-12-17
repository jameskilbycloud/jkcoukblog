# RSS Feed Implementation

## ✅ Completed - December 4, 2025

### What Was Added

**New Function: `generate_rss_feed()`**
Location: `wp_to_static_generator.py` (line 1022)

### Features

1. **Automatic RSS Generation**
   - Scans all blog posts in the static output
   - Extracts title, description, author, and publication date
   - Generates valid RSS 2.0 XML feed

2. **Feed Content**
   - Includes most recent 20 posts
   - Proper XML escaping for special characters
   - RFC-compliant date formatting
   - Includes author information

3. **Feed Files Created**
   - `/feed/index.xml` - The actual RSS feed
   - `/feed/index.html` - HTML redirect page for browsers

4. **Feed Details**
   - **Feed URL**: `https://jameskilby.co.uk/feed/index.xml`
   - **Format**: RSS 2.0 with Atom namespace
   - **Language**: en-gb
   - **Posts**: Latest 20 articles

### RSS Feed Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Jameskilbycouk</title>
    <link>https://jameskilby.co.uk/</link>
    <description>VMware and cloud infrastructure tutorials, homelab guides, and DevOps insights</description>
    <language>en-gb</language>
    <lastBuildDate>Wed, 04 Dec 2025 12:00:00 +0000</lastBuildDate>
    <atom:link href="https://jameskilby.co.uk/feed/index.xml" rel="self" type="application/rss+xml" />
    
    <item>
      <title>Post Title</title>
      <link>https://jameskilby.co.uk/2025/10/post-slug/</link>
      <description>Post excerpt or meta description...</description>
      <author>James Kilby</author>
      <guid isPermaLink="true">https://jameskilby.co.uk/2025/10/post-slug/</guid>
      <pubDate>Mon, 06 Oct 2025 15:57:06 +0000</pubDate>
    </item>
    <!-- More items... -->
  </channel>
</rss>
```

### How It Works

1. **Post Discovery**
   - Scans output directory for posts in `YYYY/MM/post-slug/` pattern
   - Processes posts in reverse chronological order (newest first)

2. **Content Extraction**
   - Parses each post's HTML
   - Extracts title from `<h1 class="entry-title">` or `<title>`
   - Gets description from meta description tag or content excerpt
   - Finds publication date from `<time>` element
   - Extracts author from author link

3. **Feed Generation**
   - Creates RSS 2.0 compliant XML
   - Properly escapes all content for XML safety
   - Adds Atom self-reference link
   - Includes lastBuildDate timestamp

4. **File Output**
   - Saves feed to `/feed/index.xml`
   - Creates HTML redirect at `/feed/index.html` for browsers

### Integration

The RSS feed is automatically generated during the static site build process:

```python
# In generate_static_site() method:
self.create_redirects_file()
self.create_sitemap()
self.generate_rss_feed()  # ← New!
self.generate_search_index()
```

### Testing After Next Deployment

```bash
# Check if feed exists
curl https://jameskilby.co.uk/feed/index.xml

# Validate RSS feed
curl -s https://jameskilby.co.uk/feed/index.xml | head -30

# Test in browser
open https://jameskilby.co.uk/feed/

# Count posts in feed
curl -s https://jameskilby.co.uk/feed/index.xml | grep -c "<item>"
```

### Feed Validation Tools

After deployment, validate your RSS feed:
- **W3C Feed Validator**: https://validator.w3.org/feed/
- **RSS Feed Reader**: Test in Feedly, NewsBlur, or any RSS reader
- **Browser**: Most browsers will display RSS nicely

### Benefits

✅ **Subscribers can follow your blog** via RSS readers
✅ **Automatic updates** - feed regenerates on each build
✅ **SEO boost** - RSS feeds are crawled by search engines
✅ **No broken links** - fixes the 404 on `/feed/` that existed before
✅ **Standards compliant** - works with all RSS readers

### Feed URL to Share

**Subscribe to the blog:**
```
https://jameskilby.co.uk/feed/index.xml
```

Or simply:
```
https://jameskilby.co.uk/feed/
```
(This redirects to the XML file)

### Customization

To customize the feed, edit the RSS generation section in `wp_to_static_generator.py`:

- **Change post count**: Line 1097 - `posts = posts[:20]` (change 20 to desired number)
- **Modify description**: Line 1112 - Update channel description
- **Change title**: Line 1110 - Update feed title
- **Adjust excerpt length**: Line 1060 - `words[:50]` for description length

## Next Steps

1. ✅ RSS generation is ready
2. Run the generator on next deployment
3. Verify feed at `/feed/index.xml`
4. Submit feed to RSS directories if desired
5. Add RSS icon/link to website footer (optional)

## Files Modified
- `wp_to_static_generator.py` - Added `generate_rss_feed()` method (136 lines)
