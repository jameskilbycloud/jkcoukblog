# Features Documentation

This document covers all the major features implemented in the static site generator.

## Table of Contents
- [Plausible Analytics](#plausible-analytics)
- [Search Functionality](#search-functionality)
- [RSS Feed](#rss-feed)
- [Brutalist Theme](#brutalist-theme)
- [Comments System](#comments-system)

---

## Plausible Analytics

### Overview
The static site generator automatically injects [Plausible Analytics](https://plausible.io/) tracking code into every generated page. This ensures consistent, privacy-focused analytics tracking across your entire site without requiring manual configuration in WordPress.

### Features
- **Automatic Injection**: The generator automatically adds the Plausible script to every HTML page during static site generation
- **Idempotent**: If the script already exists in WordPress, it updates the configuration rather than creating duplicates
- **Fail-safe**: Works even if analytics are missing from WordPress templates
- **Domain Verification**: Ensures `data-domain` is always set to `jameskilby.co.uk`
- **Correct URL**: Uses the self-hosted Plausible instance at `https://plausible.jameskilby.cloud`
- **Proper Attributes**: Adds the `defer` attribute for optimal page load performance

### Implementation
Location: `wp_to_static_generator.py` in the `add_plausible_analytics()` method

The generator adds this script tag to the `<head>` section of every page:
```html
<script defer="" src="https://plausible.jameskilby.cloud/js/script.js" data-domain="jameskilby.co.uk"></script>
```

### Privacy
- **Self-hosted**: Uses a self-hosted Plausible instance for full data control
- **No cookies**: Plausible is cookie-free and doesn't require cookie banners
- **GDPR compliant**: Plausible is designed for privacy compliance
- **Lightweight**: The script is only ~1KB and loads asynchronously with `defer`

### Testing
Run validation tests with:
```bash
python3 test_plausible_integration.py
```

---

## Search Functionality

### Overview
A powerful, fast, client-side search feature using Fuse.js for fuzzy searching.

### Features
- ⚡ **Fast Client-Side Search**: No server required, instant results
- 🔍 **Fuzzy Search**: Finds results even with typos
- 🏷️ **Multi-field Search**: Searches titles, content, categories, and tags
- 🎨 **Beautiful UI**: Modal overlay with highlighted search terms
- ⌨️ **Keyboard Shortcuts**: Ctrl+K (Cmd+K on Mac) to quickly open search
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🔒 **Privacy Friendly**: No external services, all data stays local

### Quick Start

#### Step 1: Generate Search Index
The search index is automatically created during static site generation:
```bash
export WP_AUTH_TOKEN="your_token"
python3 wp_to_static_generator.py ./public
```

This creates:
- `public/search-index.json` - Full search index with formatting
- `public/search-index.min.json` - Minified version for production

#### Step 2: Add Search JavaScript
The search script is automatically included. To customize, edit `public/js/search.js`.

#### Step 3: Test
```bash
# Test the search generation and functionality
python3 test_search.py

# Start local server for testing
python3 test_search.py --server
```

### Search Capabilities
- **Fuzzy Matching**: Finds "homelab" when you type "homelb"
- **Multi-word Search**: "docker networking" finds posts about both topics
- **Category/Tag Search**: Find all posts in specific categories
- **Partial Matching**: "AI" finds "Artificial Intelligence"

### Configuration
Edit `public/js/search.js` to customize search behavior:
```javascript
const fuseOptions = {
    keys: [
        { name: 'title', weight: 0.4 },
        { name: 'description', weight: 0.3 },
        { name: 'content', weight: 0.2 },
        { name: 'categories', weight: 0.05 },
        { name: 'tags', weight: 0.05 }
    ],
    threshold: 0.4,  // Lower = more strict, Higher = more fuzzy
    minMatchCharLength: 2
};
```

### Performance
- **Index Size**: Typically 50-200KB for a blog with 100+ posts
- **Load Time**: Index loads only when search is first used
- **Search Speed**: Near-instant results with Fuse.js
- **Browser Support**: Works in all modern browsers

---

## RSS Feed

### Overview
Automatically generates an RSS 2.0 feed from your static site content.

### Features
- **Automatic RSS Generation**: Scans all blog posts and creates valid RSS 2.0 XML feed
- **Feed Content**: Includes most recent 20 posts with title, description, author, and date
- **Proper Formatting**: RFC-compliant date formatting and XML escaping
- **Standards Compliant**: Works with all RSS readers

### Feed Details
- **Feed URL**: `https://jameskilby.co.uk/feed/index.xml`
- **Alternative**: `https://jameskilby.co.uk/feed/` (redirects to XML)
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
    <description>VMware and cloud infrastructure tutorials</description>
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
  </channel>
</rss>
```

### Implementation
Location: `wp_to_static_generator.py` in the `generate_rss_feed()` method (line 1022)

The RSS feed is automatically generated during the static site build process.

### Testing
```bash
# Check if feed exists
curl https://jameskilby.co.uk/feed/index.xml

# Validate RSS feed
curl -s https://jameskilby.co.uk/feed/index.xml | head -30

# Count posts in feed
curl -s https://jameskilby.co.uk/feed/index.xml | grep -c "<item>"
```

### Validation Tools
- **W3C Feed Validator**: https://validator.w3.org/feed/
- **RSS Feed Reader**: Test in Feedly, NewsBlur, or any RSS reader
- **Browser**: Most browsers will display RSS nicely

### Customization
To customize the feed, edit `wp_to_static_generator.py`:
- **Change post count**: Line 1097 - `posts = posts[:20]` (change 20 to desired number)
- **Modify description**: Line 1112 - Update channel description
- **Change title**: Line 1110 - Update feed title

---

## Brutalist Theme

### Overview
A brutalist dark theme inspired by [justfuckingusecloudflare.com](https://justfuckingusecloudflare.com), featuring high contrast, bold typography, and minimal design.

### Design Elements
- **Dark color scheme**: Background `#0a0a0a`, text `#fafafa`
- **Orange accent**: `#f6821f` for links, buttons, and highlights
- **Noise texture overlay**: Subtle grain effect for visual interest
- **Bold typography**:
  - Headings: Anton (uppercase, bold)
  - Body: Space Grotesk (clean, modern)
  - Code: JetBrains Mono (monospace)
- **Minimalist UI**: Sharp borders, no rounded corners, high contrast
- **Custom selection color**: Orange background when selecting text

### Files
1. **`brutalist-theme.css`** - Complete CSS theme with all styling rules
2. **`wp_to_static_generator.py`** - Modified to inject CSS into generated pages
3. **`brutalist-theme-demo.html`** - Demo page to preview the theme

### How It Works
When you run the static site generator, it will:
1. Process HTML from WordPress
2. Inject the brutalist theme CSS into the `<head>` section
3. Update the theme-color meta tag for mobile browsers
4. Apply dark theme to Utterances comments

### Usage

#### Preview the Theme
```bash
open brutalist-theme-demo.html
```

#### Generate Site with Theme
```bash
export WP_AUTH_TOKEN="your_token_here"
python3 wp_to_static_generator.py ./static-output
```

#### Deploy to Staging
```bash
python3 deploy_static_site.py full ./static-output --git
```

### Customization

#### Colors
Edit `brutalist-theme.css`:
```css
:root {
  --bg-dark: #0a0a0a;        /* Background color */
  --text-light: #fafafa;     /* Text color */
  --accent-orange: #f6821f;  /* Links, buttons, highlights */
  --gray-mid: #404040;       /* Borders */
  --gray-light: #666666;     /* Meta text */
}
```

#### Typography
To use different fonts, modify the Google Fonts import in `brutalist-theme.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=YourFont&display=swap');
```

#### Noise Intensity
Adjust the noise overlay opacity in `brutalist-theme.css`:
```css
body::before {
  opacity: 0.03;  /* Lower = less noise, Higher = more noise */
}
```

### Performance Impact
- **CSS file size**: ~11 KB uncompressed
- **Font loading**: 3 Google Fonts families
- **Rendering**: No JavaScript required, pure CSS
- **Mobile**: Optimized with responsive breakpoints

### Browser Support
- CSS Custom Properties (variables) - all modern browsers
- `::selection` pseudo-element - all browsers
- SVG data URLs - all browsers
- CSS Grid & Flexbox - all modern browsers

Tested on: Chrome/Edge, Firefox, Safari

---

## Comments System

### Overview
Uses [Utterances](https://utteranc.es/) for GitHub-based comments integrated with the brutalist theme.

### Configuration
- **GitHub Repository**: jameskilbynet/jkcoukblog
- **Theme**: GitHub Dark (matches brutalist theme)
- **Issue Mapping**: By page pathname

### Implementation
Comments are automatically configured during static site generation to match the site theme.

---

## Related Documentation
- [Main README](../README.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [TESTING.md](TESTING.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
