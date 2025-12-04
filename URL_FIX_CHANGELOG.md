# URL Fix Changelog - December 4, 2025

## Problem
All generated static pages contained references to `wordpress.jameskilby.cloud` instead of the public domain `jameskilby.co.uk`, causing:
- SEO confusion and duplicate content signals
- Broken social media sharing (Open Graph URLs incorrect)
- Poor search engine indexing
- Inconsistent canonical URLs

## Changes Made

### 1. Enhanced `wp_to_static_generator.py`

#### New Function: `fix_meta_tag_urls()`
**Purpose**: Replace WordPress URLs in meta tags
- Fixed Open Graph tags (`og:url`, `og:image`, etc.)
- Fixed Twitter Card tags (`twitter:image`, `twitter:url`, etc.)
- Fixed canonical link tags
- Fixed RSS feed URLs

#### New Function: `fix_jsonld_urls()`
**Purpose**: Replace WordPress URLs in JSON-LD structured data
- Handles both escaped (`https:\/\/`) and unescaped URLs
- Fixes Schema.org structured data for all pages
- Updates all `@id`, `url`, and other URL fields

#### Modified Function: `replace_urls_in_soup()`
- Now calls `fix_meta_tag_urls()` and `fix_jsonld_urls()`
- Changed relative URL handling to keep URLs relative (not make absolute)
- Maintains existing functionality for HTML elements

### 2. Added `robots.txt`
**Location**: `public/robots.txt`
**Purpose**: Guide search engines
```
User-agent: *
Allow: /
Disallow: /wp-admin/
Disallow: /wp-includes/
Disallow: /wp-json/
Sitemap: https://jameskilby.co.uk/sitemap.xml
```

### 3. Added `_headers`
**Location**: `public/_headers`
**Purpose**: Security and performance headers
- Security: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- Privacy: Referrer-Policy, Permissions-Policy
- Performance: Cache-Control directives for static assets and HTML

## What Gets Fixed

### Meta Tags
Before:
```html
<meta property="og:url" content="https://wordpress.jameskilby.cloud/..." />
<link rel="canonical" href="https://wordpress.jameskilby.cloud/..." />
```

After:
```html
<meta property="og:url" content="https://jameskilby.co.uk/..." />
<link rel="canonical" href="https://jameskilby.co.uk/..." />
```

### JSON-LD Structured Data
Before:
```json
{
  "@id": "https://wordpress.jameskilby.cloud/#website",
  "url": "https://wordpress.jameskilby.cloud/"
}
```

After:
```json
{
  "@id": "https://jameskilby.co.uk/#website",
  "url": "https://jameskilby.co.uk/"
}
```

## Testing the Fix

### Quick Verification
After generating the site, check any HTML file:
```bash
# Should return 0 matches
grep -r "wordpress.jameskilby.cloud" public/*.html | wc -l

# Should have many matches for the correct domain
grep -r "jameskilby.co.uk" public/*.html | wc -l
```

### Detailed Check
```bash
# Check meta tags
grep -A 2 'property="og:url"' public/index.html

# Check JSON-LD
grep -A 5 'application/ld+json' public/index.html
```

## Next Deployment

When you next run the static site generator:
1. The script will automatically apply all URL fixes
2. All meta tags will reference `jameskilby.co.uk`
3. All JSON-LD will reference `jameskilby.co.uk`
4. robots.txt and _headers will be deployed with the site

## SEO Impact

### Immediate Benefits
- ✅ Correct canonical URLs for search engines
- ✅ Proper Open Graph for social media sharing
- ✅ Valid structured data for rich snippets
- ✅ Consolidated domain authority

### Within 1-2 Weeks
- Search engines will re-index with correct URLs
- Social media previews will show correct domain
- Duplicate content warnings should resolve

## Additional Recommendations

### Still To Implement
1. **Disable duplicate SEO plugin** - Remove either All in One SEO or Rank Math (keep Rank Math)
2. **Update meta descriptions** - Create unique descriptions per page
3. **Fix future dates** - Posts show dates in 2025 (should be 2024)
4. **Optimize images** - Add proper alt text to all images
5. **Add visible breadcrumbs** - Schema is there, but no UI breadcrumbs

### Optional Enhancements
- Create a proper 404 page
- Add security.txt file
- Implement structured data testing
- Add Web App Manifest for PWA support

## Monitoring

After deployment, use these tools to verify:
- **Google Search Console**: Check for duplicate content warnings
- **Facebook Debugger**: Test Open Graph tags (https://developers.facebook.com/tools/debug/)
- **Twitter Card Validator**: Test Twitter Cards (https://cards-dev.twitter.com/validator)
- **Rich Results Test**: Validate structured data (https://search.google.com/test/rich-results)

## Files Modified
- `wp_to_static_generator.py` - Enhanced URL replacement logic
- `public/robots.txt` - Created new
- `public/_headers` - Created new
