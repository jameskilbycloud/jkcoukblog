# Live Site Formatting Test - Quick Start

## Run the Test

```bash
# Test production site
./test_live_site_formatting.py

# Test staging site  
./test_live_site_formatting.py --url https://jkcoukblog.pages.dev
```

## What It Tests

✅ **HTML & Structure**
- Valid DOCTYPE and HTML structure
- All required meta tags (charset, viewport, description)
- Page title and canonical URLs
- Structured data (JSON-LD)

✅ **Analytics & Tracking**
- Plausible Analytics properly configured
- Correct data-domain attribute
- No duplicate tracking scripts

✅ **Comments System**
- Utterances comments widget properly configured
- Correct GitHub repository linked
- Theme and issue-term settings present

✅ **Assets & Resources**
- CSS stylesheets load correctly
- JavaScript files load correctly
- Images have alt attributes
- Responsive images have srcset

✅ **SEO & Social**
- Open Graph tags (Facebook/LinkedIn)
- Twitter Card tags
- Canonical URLs point to correct domain

✅ **Content Quality**
- Internal links are not broken
- WordPress-specific elements removed
- Cache control headers present

## Sample Output

```
======================================================================
🚀 Starting Live Site Formatting Tests
🌐 Testing: https://jameskilby.co.uk
======================================================================

✅ Homepage loads successfully
✅ HTML structure is valid
✅ Plausible Analytics configured correctly
✅ All tested images have proper attributes
✅ CSS assets load successfully

======================================================================
📈 Results: 14/14 tests passed
❌ Errors: 0
⚠️  Warnings: 0
======================================================================
```

## Exit Codes

- **0** = All tests passed ✅
- **1** = Tests failed ❌

## Full Documentation

See `docs/LIVE_SITE_FORMATTING_TESTS.md` for complete documentation.

## Requirements

Already installed via `requirements.txt`:
- requests
- beautifulsoup4
