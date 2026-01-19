# HTML Validation

This document describes the HTML validation system that checks the generated static site for broken links and missing assets before deployment.

## Overview

The `validate_html.py` script performs comprehensive validation of the generated static site to ensure:
- No broken internal links
- All assets are present (images, CSS, JS, fonts)
- HTML structure is valid
- Images have alt attributes
- CSS references to assets are valid

This validation runs automatically in the GitHub Actions deployment workflow after site generation and before deployment.

## Usage

### Manual Validation

```bash
# Validate the generated static site
python3 validate_html.py ./static-output

# Verbose mode (shows all files being checked)
python3 validate_html.py ./static-output -v
```

### In GitHub Actions

The validation step runs automatically in the deployment workflow:

```yaml
- name: Validate HTML build
  timeout-minutes: 5
  run: |
    python3 validate_html.py ./static-output
```

If validation fails, the workflow will stop and not deploy the broken site.

## What It Checks

### 1. HTML Structure
- Validates presence of `<!DOCTYPE>`, `<html>`, `<head>`, and `<body>` tags
- Checks for `<title>` tag (warning if missing)
- Ensures files can be parsed as valid HTML

### 2. Internal Links
- Validates all `<a href>` links pointing to internal pages
- Checks that target pages exist
- Handles various URL formats (absolute from root, relative paths)
- Skips external links, mailto, tel, and fragment-only links

### 3. Asset References

#### Images
- Validates `<img src>` references
- Checks `<picture><source srcset>` references
- Verifies AVIF, WebP, PNG, JPG, and other image formats
- Warns about missing alt attributes

#### CSS Files
- Validates `<link rel="stylesheet">` references
- Checks CSS files exist
- Validates assets referenced within CSS files (via `url()`)

#### JavaScript Files
- Validates `<script src>` references
- Checks JS files exist

#### Fonts and Other Assets
- Validates font references in CSS files
- Checks background images in CSS
- Verifies all `url()` references in CSS

### 4. Path Resolution

The validator handles various path formats:

```html
<!-- Absolute from site root -->
<img src="/wp-content/uploads/image.jpg">

<!-- Relative to current file -->
<img src="../images/logo.png">
<img src="./assets/style.css">

<!-- Directory index files -->
<a href="/about/">  <!-- Resolves to /about/index.html -->
```

## Exit Codes

- `0` - All validation checks passed
- `1` - Validation failed (errors found)

## Output

The script provides detailed output:

```
======================================================================
🚀 Starting HTML Validation
📁 Directory: /path/to/static-output
======================================================================

🔍 Discovering files...

🔍 Validating HTML files...
✅ All validation checks passed!

🔍 Validating CSS files...

======================================================================
📊 VALIDATION SUMMARY
======================================================================
📄 HTML files checked: 156
📦 Asset files found: 342
❌ Errors: 0
⚠️  Warnings: 3
======================================================================

✅ All validation checks passed!
```

## Error Examples

### Broken Link
```
❌ ERROR: index.html: Broken link to '/nonexistent-page'
```

### Missing Asset
```
❌ ERROR: blog/post.html: Missing image 'images/hero.jpg'
```

### Missing Alt Attribute
```
⚠️  WARNING: blog/post.html: Image missing alt attribute: 'photo.jpg'
```

## Integration with CI/CD

The validation step is positioned strategically in the workflow:

1. ✅ Generate static site
2. ✅ **Validate HTML** ← Catches issues early
3. ✅ Optimize images
4. ✅ Convert to picture elements
5. ✅ Deploy to production

By validating immediately after generation, we catch issues before spending time on image optimization and other post-processing steps.

## Performance

- Validates ~150 HTML files in under 5 seconds
- Checks ~350 asset references
- Uses local filesystem checks (no network requests)
- Minimal memory footprint

## Skipped Validations

The validator intentionally skips:

- External URLs (http://, https://)
- Protocol-relative URLs (//cdn.example.com)
- Data URIs (data:image/png;base64,...)
- Email links (mailto:)
- Phone links (tel:)
- Fragment-only links (#section)
- External CDN resources

## Future Enhancements

Potential improvements:

- [ ] Validate Open Graph image URLs
- [ ] Check for redirect chains
- [ ] Validate JSON-LD structured data
- [ ] Check for duplicate IDs
- [ ] Validate ARIA attributes
- [ ] Performance budget checks (file sizes)

## Related Documentation

- `WARP.md` - Project overview and commands
- `test_live_site_formatting.py` - Live site testing (post-deployment)
- `.github/workflows/deploy-static-site.yml` - Deployment workflow

## Troubleshooting

### False Positives

If the validator reports errors for valid files:

1. Check if the file path is correct
2. Verify the file exists in the output directory
3. Check for URL encoding issues
4. Ensure the path is relative or absolute from root correctly

### Performance Issues

If validation is slow:

1. Check the number of HTML files
2. Look for very large CSS files
3. Consider adding parallelization for large sites

### Running Locally

To test validation locally before pushing:

```bash
# Generate site
python3 wp_to_static_generator.py ./test-output

# Validate before deploying
python3 validate_html.py ./test-output

# If validation passes, you're good to deploy
```
