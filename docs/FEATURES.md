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
- **Automatic injection**: the build adds the Plausible script to every HTML page
- **Idempotent**: if WordPress already emits a Plausible script, its attributes are corrected instead of adding a second one
- **Domain**: `data-domain` is always set to `jameskilby.co.uk`
- **Same-origin script**: the page loads `/js/script.js` from the site itself; the Worker proxies it to the self-hosted Plausible instance (`Config.PLAUSIBLE_URL`), so no preconnect to a third-party host is needed. Old `dns-prefetch`/`preconnect` hints to the Plausible host are removed
- **Attributes**: `defer`, and `data-cfasync="false"` so Cloudflare Rocket Loader leaves it alone

### Implementation
Location: `scripts/head_chrome_optimizations.py`, `add_plausible_analytics()`

The tag added to `<head>`:
```html
<script data-domain="jameskilby.co.uk" defer="" data-cfasync="false" src="/js/script.js"></script>
```

### Privacy
- **Self-hosted**: Plausible Community Edition, so the data stays under our control
- **No cookies**: no cookie banner needed
- **Lightweight**: the script is about 1 KB and loads with `defer`

### Testing
`make test-csp` checks the CSP still allows Plausible, and `scripts/test_live_site_formatting.py` checks the script and its `data-domain` on the live site.

---

## Search Functionality

### Overview
A powerful, fast, client-side search feature using Fuse.js for fuzzy searching.

### Features
- ⚡ **Fast Client-Side Search**: No server required, instant results
- 🔍 **Fuzzy Search**: Finds results even with typos
- 🏷️ **Multi-field Search**: Searches titles, descriptions and post content
- 🎨 **Beautiful UI**: Modal overlay with highlighted search terms
- ⌨️ **Keyboard Shortcuts**: Ctrl+K (Cmd+K on Mac) to quickly open search
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🔒 **Privacy Friendly**: No external services, all data stays local

### Quick Start

#### Step 1: Generate Search Index
The search index is automatically created during static site generation:
```bash
export WP_AUTH_TOKEN="your_token"
python3 scripts/wp_to_static_generator.py ./static-output
```

This creates:
- `search-index.json` - Full search index with formatting
- `search-index.min.json` - Minified version for production

CI also uploads `search-index.json` to the `SEARCH_INDEX` Workers KV namespace after each deploy.

#### Step 2: Add Search JavaScript
The search script is automatically included. Its source is `scripts/assets/js/search.js` (Fuse.js is vendored alongside it); the generator copies it to `/js/search.js`.

#### Step 3: Test
```bash
make generate
make deploy-local   # then open http://localhost:8080 and use the search box
```

### Search Capabilities
- **Fuzzy Matching**: Finds "homelab" when you type "homelb"
- **Multi-word Search**: "docker networking" finds posts about both topics
- **Partial Matching**: "AI" finds "Artificial Intelligence"

### Configuration
Edit `scripts/assets/js/search.js` (never the built copy in `public/`). The Fuse options:
```javascript
new Fuse(index, {
    keys: ['title', 'description', 'content'],
    threshold: 0.4,          // Lower = stricter, higher = fuzzier
    includeMatches: true,
    ignoreLocation: true,
    minMatchCharLength: 2
});
```
Each index entry holds `title`, `url`, `description` and `content`. Categories, tags and dates are not in the index.

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
    <title>James Kilby</title>
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
  </channel>
</rss>
```

### Implementation
Location: `scripts/site_artifacts_builder.py`, `generate_rss_feed()`

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
To customize the feed, edit `generate_rss_feed()` in `scripts/site_artifacts_builder.py`:
- **Post count**: `posts = posts[:20]`
- **Title and description**: the `<title>` and `<description>` lines in `rss_lines`

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
- **`scripts/brutalist-theme.css`** — the theme, including the `@font-face` rules; the build copies it to `/assets/css/brutalist-theme.css`
- **`scripts/head_chrome_optimizations.py`** — links the theme into every page's `<head>`

### How It Works
During generation the build:
1. Processes the HTML from WordPress
2. Adds a `preload` and a normal `<link rel="stylesheet">` for the theme. It loads synchronously on purpose: the browser must parse it to find the font URLs
3. Updates the theme-color meta tag for mobile browsers
4. Sets the Utterances comments to the dark theme

### Usage
```bash
make generate        # needs WP_AUTH_TOKEN and access to WordPress
make deploy-local    # preview on http://localhost:8080
```
To publish, merge to `main` and run `deploy-static-site.yml` (see [DEPLOYMENT.md](DEPLOYMENT.md)). A theme change only reaches the pages a build re-renders, so run **Force Full Deploy (no cache)** after merging one.

### Customization

#### Colors
Edit `scripts/brutalist-theme.css`:
```css
:root {
  --bg-dark: #0a0a0a;        /* Background color */
  --text-light: #fafafa;     /* Text color */
  --accent-orange: #f6821f;  /* Links, buttons, highlights */
  --gray-mid: #404040;       /* Borders */
  --gray-light: #949494;     /* Meta text */
}
```

#### Typography
Fonts are self-hosted WOFF2 files under `/assets/fonts/`, declared with `@font-face` at the top of `scripts/brutalist-theme.css` (`font-display: optional`). To change a font, add its WOFF2 file and update the matching `@font-face` rule. The build subsets all six font files to the characters the site uses (`scripts/subset_fonts.py`).

#### Noise Intensity
Adjust the noise overlay opacity in `scripts/brutalist-theme.css`:
```css
body::before {
  opacity: 0.03;  /* Lower = less noise, Higher = more noise */
}
```

### Performance Impact
- **CSS file size**: about 68 KB uncompressed (before the build's unused-rule removal, minify and Brotli)
- **Font loading**: 3 self-hosted families, 6 files, no third-party font requests
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
- **GitHub Repository**: `Config.UTTERANCES_REPO` is still `jameskilbynet/jkcoukblog`, the repo's old name; GitHub redirects it to `jameskilbycloud/jkcoukblog`
- **Theme**: GitHub Dark (matches brutalist theme)
- **Issue Mapping**: By page pathname

### Implementation
`add_utterances_comments()` in `scripts/head_chrome_optimizations.py` adds the widget to posts during generation.

---

## Related Documentation
- [Main README](../README.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [TESTING.md](TESTING.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
