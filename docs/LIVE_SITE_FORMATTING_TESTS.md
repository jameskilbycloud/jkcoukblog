# Live Site Formatting Tests

## Overview

The `test_live_site_formatting.py` script performs comprehensive validation of the live site at jameskilby.co.uk to ensure proper formatting, structure, and functionality.

## Purpose

This test suite validates that:
- The site has valid HTML structure
- All critical meta tags are present and correct
- CSS and JavaScript assets load properly
- Plausible Analytics is correctly configured
- Utterances comments widget is properly configured
- WordPress-specific elements have been removed
- Images have proper alt attributes and responsive srcset
- Internal links are not broken
- SEO elements (canonical URLs, structured data) are present

## Usage

### Basic Usage

Test the production site:
```bash
./test_live_site_formatting.py
```

### Test Staging Site

Test the staging site instead:
```bash
./test_live_site_formatting.py --url https://jkcoukblog.pages.dev
```

### Run from Python

```bash
python3 test_live_site_formatting.py
```

## Test Categories

### 1. Homepage Load Test
- **Purpose:** Verify the homepage loads successfully
- **Checks:** HTTP 200 status, content length
- **Failure Impact:** Critical - indicates site is down

### 2. HTML Structure Test
- **Purpose:** Validate basic HTML structure
- **Checks:** DOCTYPE, `<html>`, `<head>`, `<body>` tags
- **Failure Impact:** Critical - indicates malformed HTML

### 3. Meta Tags Test
- **Purpose:** Ensure SEO and viewport meta tags are present
- **Checks:**
  - Charset meta tag
  - Viewport meta tag
  - Description meta tag
  - Open Graph tags (og:title, og:description, og:image)
  - Twitter Card tags
- **Failure Impact:** High - affects SEO and social sharing

### 4. Title Tag Test
- **Purpose:** Validate page title
- **Checks:** Title presence, length (recommended < 60 chars)
- **Failure Impact:** High - affects SEO

### 5. Canonical URL Test
- **Purpose:** Ensure canonical URL is present and correct
- **Checks:** Canonical link points to jameskilby.co.uk
- **Failure Impact:** Medium - affects SEO

### 6. Plausible Analytics Test
- **Purpose:** Verify analytics tracking is configured correctly
- **Checks:**
  - Plausible script is present (and not duplicated)
  - Script source: `plausible.jameskilby.cloud/js/script.js`
  - `data-domain` attribute: `jameskilby.co.uk`
  - Script has `defer` attribute
- **Failure Impact:** Medium - affects analytics collection

### 7. WordPress Cleanup Test
- **Purpose:** Ensure WordPress-specific elements are removed
- **Checks:**
  - No WordPress generator meta tag
  - No REST API discovery links
  - No wp-embed scripts
  - No admin bar (`#wpadminbar`)
- **Failure Impact:** Low to Medium - affects security and performance

### 8. Utterances Comments Test
- **Purpose:** Verify utterances commenting system is configured correctly
- **Checks:**
  - Utterances script is present (on post pages)
  - Script source: `utteranc.es/client.js`
  - `data-repo` attribute: `jameskilbynet/jkcoukblog`
  - `data-theme` attribute is set
  - `data-issue-term` attribute is set
  - Script has `crossorigin` attribute
- **Failure Impact:** Medium - affects commenting functionality
- **Note:** This check only applies to individual post pages, not the homepage

### 9. Images Test
- **Purpose:** Validate image attributes (samples first 10 images)
- **Checks:**
  - All images have `src` attribute
  - All images have `alt` attribute
  - Responsive images have `srcset`
  - Images have `loading` attribute (lazy/eager)
- **Failure Impact:** Medium - affects accessibility and SEO

### 9. CSS Assets Test
- **Purpose:** Verify CSS stylesheets load (samples first 5)
- **Checks:** Each CSS file returns HTTP 200
- **Failure Impact:** High - affects site appearance

### 10. JavaScript Assets Test
- **Purpose:** Verify JavaScript files load (samples first 5)
- **Checks:** Each JS file returns HTTP 200
- **Failure Impact:** Medium to High - affects site functionality

### 11. Internal Links Test
- **Purpose:** Check for broken internal links (samples first 10)
- **Checks:** Internal links don't return 404
- **Failure Impact:** Medium - affects user experience

### 12. Structured Data Test
- **Purpose:** Validate JSON-LD structured data
- **Checks:**
  - JSON-LD script tags are present
  - JSON is valid
  - Schema types are identified
- **Failure Impact:** Medium - affects rich snippets in search

### 13. Cache Control Test
- **Purpose:** Check for cache control meta tag
- **Checks:** Cache-Control meta tag (optional)
- **Failure Impact:** Low - affects caching behavior

## Exit Codes

- **0:** All tests passed (no errors)
- **1:** One or more tests failed (errors present)

Note: Warnings do not cause the script to exit with a failure code.

## Output Format

The script uses emojis for easy visual scanning:
- ✅ Success
- ❌ Error (test failure)
- ⚠️  Warning (issue that doesn't fail the test)
- ℹ️  Info (informational message)

## Sample Output

```
======================================================================
🚀 Starting Live Site Formatting Tests
🌐 Testing: https://jameskilby.co.uk
======================================================================

🔍 Testing homepage load...
✅ Homepage loads successfully

🔍 Testing HTML structure...
✅ HTML structure is valid

🔍 Testing meta tags...
✅ Charset meta tag present
✅ Viewport meta tag present
✅ Description meta tag present: James Kilby's technical blog covering VMware, homelab proj...
✅ Open Graph tags present
✅ Twitter Card meta tag present

🔍 Testing Plausible Analytics...
✅ Plausible script source correct: https://plausible.jameskilby.cloud/js/script.js
✅ Plausible data-domain correct: jameskilby.co.uk
✅ Plausible script has 'defer' attribute

======================================================================
📊 TEST SUMMARY
======================================================================
✅ PASS - Homepage Loads
✅ PASS - HTML Structure
✅ PASS - Meta Tags
✅ PASS - Title Tag
✅ PASS - Canonical URL
✅ PASS - Plausible Analytics
✅ PASS - WordPress Cleanup
✅ PASS - Utterances Comments
✅ PASS - Images
✅ PASS - CSS Assets
✅ PASS - JavaScript Assets
✅ PASS - Internal Links
✅ PASS - Structured Data
✅ PASS - Cache Control

======================================================================
📈 Results: 14/14 tests passed
❌ Errors: 0
⚠️  Warnings: 0
ℹ️  Info: 5
======================================================================
```

## Integration with CI/CD

### GitHub Actions

You can integrate this into the deployment workflow:

```yaml
- name: Test Live Site Formatting
  run: |
    python3 test_live_site_formatting.py
  continue-on-error: false  # Fail the workflow if tests fail
```

Or run as a separate check after deployment:

```yaml
- name: Test Live Site Formatting (Post-Deploy)
  run: |
    python3 test_live_site_formatting.py
  continue-on-error: true  # Don't fail deployment, just notify
```

### Local Development

Run before pushing changes to verify everything still works:

```bash
# Test production
./test_live_site_formatting.py

# Test staging
./test_live_site_formatting.py --url https://jkcoukblog.pages.dev
```

## Sampling Strategy

To keep tests fast and server-friendly, the script samples:
- **Images:** First 10 images
- **CSS Assets:** First 5 stylesheets
- **JavaScript Assets:** First 5 scripts
- **Internal Links:** First 10 unique links

This provides good coverage while avoiding excessive requests.

## Rate Limiting

The script includes polite delays:
- 0.1 seconds between asset tests (CSS/JS)
- 0.2 seconds between link tests

## Dependencies

The script requires:
```bash
pip install requests beautifulsoup4
```

These are already in `requirements.txt`.

## Troubleshooting

### Connection Errors

If tests fail with connection errors:
1. Check your internet connection
2. Verify the site is accessible: `curl -I https://jameskilby.co.uk`
3. Check for DNS issues: `nslookup jameskilby.co.uk`

### False Positives

If CSS/JS/links fail but work in browser:
1. Check if files are served with authentication
2. Verify User-Agent isn't being blocked
3. Test with curl: `curl -I https://jameskilby.co.uk/path/to/asset.css`

### Plausible Analytics Failures

If Plausible tests fail:
1. Check the generator script: `wp_to_static_generator.py`
2. Verify analytics injection is working
3. Test manually: View source and search for "plausible"

## Future Enhancements

Potential additions:
- Performance testing (page load time, asset sizes)
- Accessibility testing (WCAG compliance)
- Mobile responsiveness validation
- RSS feed validation
- Sitemap.xml validation
- robots.txt validation
- Security headers check (CSP, X-Frame-Options, etc.)
- Lighthouse score integration

## Related Documentation

- `README.md` - Project overview
- `WARP.md` - Warp-specific guidance
- `automated_static_deployment_guide.md` - Deployment details
- `PLAUSIBLE_ANALYTICS.md` - Analytics implementation
