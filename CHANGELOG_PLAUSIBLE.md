# Changelog: Plausible Analytics Automation

## Summary

Automated the inclusion of Plausible Analytics tracking code on every page during static site publishing. This ensures consistent analytics tracking without manual configuration in WordPress.

## Changes Made

### 1. Core Implementation (`wp_to_static_generator.py`)

#### Added `add_plausible_analytics()` method (Line 486-512)
- **Purpose**: Inject or update Plausible Analytics script in HTML pages
- **Location**: Called from `add_static_optimizations()` during HTML processing
- **Features**:
  - Automatically detects existing Plausible scripts
  - Updates configuration if script exists
  - Adds new script if missing
  - Prevents duplicate scripts
  - Validates `data-domain` attribute is set to `jameskilby.co.uk`

#### Updated `add_static_optimizations()` method (Line 457-484)
- **Change**: Added call to `self.add_plausible_analytics(soup)` at line 475
- **Purpose**: Integrate analytics injection into the standard HTML processing flow
- **Position**: Executes after meta tags and before preload hints

### 2. Documentation

#### Created `PLAUSIBLE_ANALYTICS.md`
- Complete documentation of the analytics automation feature
- Implementation details and code examples
- Configuration instructions
- Troubleshooting guide
- Privacy considerations

#### Updated `README.md`
- Added "Analytics Automation" section to features list
- Documented automatic Plausible injection in "Static Site Optimizations"
- Added reference to PLAUSIBLE_ANALYTICS.md in repository structure

### 3. Testing

#### Created `test_plausible_integration.py`
- Unit tests for analytics injection functionality
- Tests three scenarios:
  1. Adding analytics to pages without existing scripts
  2. Updating configuration on pages with existing scripts
  3. Handling edge cases (missing `<head>` tags)
- Validates no duplicate scripts are created
- Confirms correct domain configuration

## Configuration

The analytics configuration is centralized in `add_plausible_analytics()`:

```python
plausible_domain = 'plausible.jameskilby.cloud'  # Self-hosted Plausible instance
plausible_script_url = f'https://{plausible_domain}/js/script.js'
target_analytics_domain = 'jameskilby.co.uk'      # Public site domain for tracking
```

## Generated Output

Every HTML page now includes this script in the `<head>` section:

```html
<script defer="" src="https://plausible.jameskilby.cloud/js/script.js" data-domain="jameskilby.co.uk"></script>
```

## Behavior

### When Plausible is already in WordPress:
- ✅ Detects existing script
- ✅ Verifies and updates `data-domain` attribute
- ✅ Ensures `defer` attribute is present
- ✅ Logs: "📊 Updated existing Plausible analytics configuration"

### When Plausible is missing from WordPress:
- ✅ Creates new script tag
- ✅ Sets correct `src`, `data-domain`, and `defer` attributes
- ✅ Appends to `<head>` section
- ✅ Logs: "📊 Added Plausible analytics script to page"

## Deployment

The changes are automatically deployed via GitHub Actions:
- Workflow: `.github/workflows/deploy-static-site.yml`
- Schedule: Twice daily (6 AM and 6 PM UTC)
- Manual trigger: Available via workflow dispatch
- Webhook: Can be triggered from WordPress

## Benefits

1. **Reliability**: Analytics always present, regardless of WordPress theme changes
2. **Consistency**: Same configuration across all pages
3. **Maintenance**: Single point of configuration in the generator
4. **Privacy**: Self-hosted Plausible instance maintains data control
5. **Performance**: Script loads with `defer` for optimal page performance

## Testing the Changes

### Syntax Validation
```bash
python3 -m py_compile wp_to_static_generator.py
```

### Functional Testing
```bash
python3 test_plausible_integration.py
```

### Integration Testing
```bash
# Trigger manual workflow run
gh workflow run deploy-static-site.yml

# Or run locally
export WP_AUTH_TOKEN="your_token"
python3 wp_to_static_generator.py ./test-output
```

### Verification
```bash
# Check generated HTML for Plausible script
grep -r "plausible.jameskilby.cloud" ./public/ | head -5

# Verify data-domain attribute
grep -r 'data-domain="jameskilby.co.uk"' ./public/ | head -5
```

## Files Modified

- `wp_to_static_generator.py` - Core implementation
- `README.md` - Updated documentation
- `test_plausible_integration.py` - New test file
- `PLAUSIBLE_ANALYTICS.md` - New documentation
- `CHANGELOG_PLAUSIBLE.md` - This file

## Backward Compatibility

✅ **Fully backward compatible**
- No breaking changes to existing functionality
- Works with or without Plausible in WordPress
- All existing features remain unchanged

## Future Enhancements

Possible future improvements:
- [ ] Make Plausible domain configurable via environment variable
- [ ] Support multiple analytics providers (e.g., Plausible + self-hosted Matomo)
- [ ] Add analytics script integrity verification
- [ ] Support custom Plausible script extensions (e.g., `script.outbound-links.js`)
