# Plausible Analytics Automation

## Overview

The static site generator automatically injects [Plausible Analytics](https://plausible.io/) tracking code into every generated page. This ensures consistent, privacy-focused analytics tracking across your entire site without requiring manual configuration in WordPress.

## Features

### Automatic Injection
- **Always Present**: The generator automatically adds the Plausible script to every HTML page during static site generation
- **Idempotent**: If the script already exists in WordPress, it updates the configuration rather than creating duplicates
- **Fail-safe**: Works even if analytics are missing from WordPress templates

### Configuration Validation
- **Domain Verification**: Ensures `data-domain` is always set to `jameskilby.co.uk`
- **Correct URL**: Uses the self-hosted Plausible instance at `https://plausible.jameskilby.cloud`
- **Proper Attributes**: Adds the `defer` attribute for optimal page load performance

### Duplicate Prevention
- Detects existing Plausible scripts in the HTML
- Updates configuration of existing scripts rather than adding duplicates
- Prevents multiple tracking calls from the same page

## Implementation

The analytics injection is implemented in `wp_to_static_generator.py` in the `add_plausible_analytics()` method:

```python
def add_plausible_analytics(self, soup):
    """Add Plausible Analytics script to the page if not already present"""
    if not soup.head:
        return
    
    # Configuration
    plausible_domain = 'plausible.jameskilby.cloud'
    plausible_script_url = f'https://{plausible_domain}/js/script.js'
    target_analytics_domain = 'jameskilby.co.uk'
    
    # Check for existing Plausible script
    existing_plausible = soup.find('script', src=lambda x: x and 'plausible' in x and 'script.js' in x)
    
    if existing_plausible:
        # Update the data-domain attribute to ensure it's correct
        existing_plausible['data-domain'] = target_analytics_domain
        existing_plausible['defer'] = ''
        print(f"   📊 Updated existing Plausible analytics configuration")
    else:
        # Add new Plausible script
        plausible_script = soup.new_tag('script')
        plausible_script['data-domain'] = target_analytics_domain
        plausible_script['defer'] = ''
        plausible_script['src'] = plausible_script_url
        soup.head.append(plausible_script)
        print(f"   📊 Added Plausible analytics script to page")
```

## Generated HTML

The generator adds the following script tag to the `<head>` section of every page:

```html
<script defer="" src="https://plausible.jameskilby.cloud/js/script.js" data-domain="jameskilby.co.uk"></script>
```

## Configuration

### Customization

To customize the Plausible configuration for your own site, edit the following variables in `wp_to_static_generator.py` (line ~492-494):

```python
plausible_domain = 'plausible.jameskilby.cloud'  # Your Plausible instance URL
target_analytics_domain = 'jameskilby.co.uk'     # Your public site domain
```

### WordPress Integration

You can optionally add Plausible to your WordPress theme as well. The generator will:
1. Detect the existing script
2. Verify the configuration is correct
3. Update it if necessary
4. Avoid creating duplicates

This provides defense-in-depth: analytics work even if WordPress configuration changes.

## Privacy Considerations

- **Self-hosted**: Uses a self-hosted Plausible instance for full data control
- **No cookies**: Plausible is cookie-free and doesn't require cookie banners
- **GDPR compliant**: Plausible is designed for privacy compliance
- **Lightweight**: The script is only ~1KB and loads asynchronously with `defer`

## Testing

The repository includes `test_plausible_integration.py` which validates:
1. ✅ Analytics injection on pages without existing scripts
2. ✅ Configuration update on pages with existing scripts
3. ✅ No duplicate scripts created
4. ✅ Correct domain configuration
5. ✅ Graceful handling of edge cases (missing `<head>` tags)

Run tests with:
```bash
python3 test_plausible_integration.py
```

## Deployment

The analytics automation is triggered automatically when:
- GitHub Actions workflow runs (twice daily at 6 AM and 6 PM UTC)
- Manual workflow dispatch
- Webhook trigger from WordPress

Every generated page will include the Plausible tracking code in the published static site.

## Troubleshooting

### Analytics Not Showing Up

1. **Check the generated HTML**: Inspect a page in the `public/` directory and verify the script tag is present
2. **Verify Plausible instance**: Ensure `https://plausible.jameskilby.cloud/js/script.js` is accessible
3. **Check browser console**: Look for any JavaScript errors related to Plausible

### Duplicate Scripts

The generator prevents duplicates, but if you see them:
1. Check your WordPress theme for hardcoded Plausible scripts
2. Review any plugins that might inject analytics
3. Run the test script to verify the deduplication logic

### Wrong Domain

If analytics are tracking the wrong domain:
1. Check the `data-domain` attribute in the generated HTML
2. Verify the `target_analytics_domain` variable in `wp_to_static_generator.py`
3. Re-run the static site generation

## Related Documentation

- [Plausible Documentation](https://plausible.io/docs)
- [Main README](README.md)
- [Deployment Guide](automated_static_deployment_guide.md)
