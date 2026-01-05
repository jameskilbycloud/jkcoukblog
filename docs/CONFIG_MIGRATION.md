# Configuration Migration Guide

## Summary

All hardcoded URLs and domains have been centralized into a single `config.py` file. This makes it easier to maintain and update configuration across the entire project.

## What Changed

### New File
- **`config.py`**: Centralized configuration file containing all URLs and domains

### Updated Files
- **`wp_to_static_generator.py`**: Now imports and uses `Config` class
- **`ollama_spell_checker.py`**: Now imports and uses `Config` class  
- **`convert_to_staging.py`**: Now imports and uses `Config` class
- **`docs/archive/WARP.md`**: Updated documentation
- **`README.md`**: Added configuration section

## Configuration File Structure

```python
from config import Config

# Access configuration values
Config.WP_URL                    # https://wordpress.jameskilby.cloud
Config.TARGET_DOMAIN             # https://jameskilby.co.uk
Config.STAGING_DOMAIN            # jkcoukblog.pages.dev
Config.OLLAMA_URL                # https://ollama.jameskilby.cloud
Config.OLLAMA_MODEL              # llama3.1:8b
Config.PLAUSIBLE_URL             # plausible.jameskilby.cloud

# Utility methods
Config.get_plausible_script_url()  # Returns full Plausible script URL
Config.get_plausible_domain()      # Returns domain for analytics tracking
Config.print_config()              # Print all configuration values
```

## What Stayed the Same

**Secrets remain in environment variables and GitHub Secrets:**
- `WP_AUTH_TOKEN` (required)
- `OLLAMA_API_CREDENTIALS` (optional)
- `SLACK_WEBHOOK_URL` (optional)
- `PLAUSIBLE_SHARE_LINK` (optional)

**No changes required to:**
- GitHub Actions workflows
- Environment variable setup
- Deployment processes

## Testing Your Setup

### 1. Test Configuration File
```bash
python3 config.py
```

Expected output:
```
============================================================
Configuration
============================================================
WordPress URL:        https://wordpress.jameskilby.cloud
Target Domain:        https://jameskilby.co.uk
Staging Domain:       jkcoukblog.pages.dev
Ollama URL:           https://ollama.jameskilby.cloud
Ollama Model:         llama3.1:8b
Plausible URL:        plausible.jameskilby.cloud
Max Workers:          3
Request Timeout:      30s
============================================================

✅ Configuration loaded successfully!
```

### 2. Test Static Site Generation
```bash
export WP_AUTH_TOKEN="your_token"
python3 wp_to_static_generator.py ./test-output
```

### 3. Test Spell Checker
```bash
export WP_AUTH_TOKEN="your_token"
export OLLAMA_API_CREDENTIALS="username:password"
python3 ollama_spell_checker.py 1
```

### 4. Test URL Conversion
```bash
python3 convert_to_staging.py
```

## Customizing for Your Environment

To adapt this project for your own setup, simply edit `config.py`:

```python
class Config:
    # WordPress Configuration
    WP_URL = 'https://your-wordpress-site.com'
    
    # Target Domains
    TARGET_DOMAIN = 'https://your-public-site.com'
    STAGING_DOMAIN = 'your-staging-site.pages.dev'
    
    # Service URLs
    OLLAMA_URL = 'https://your-ollama-instance.com'
    PLAUSIBLE_URL = 'your-analytics-instance.com'
```

Then test with:
```bash
python3 config.py
```

## Benefits of Centralized Configuration

1. **Single Source of Truth**: All URLs defined in one place
2. **Easier Maintenance**: Update once, applies everywhere
3. **Better Documentation**: Clear overview of all endpoints
4. **Type Safety**: Configuration values in one class
5. **Easy Testing**: Simple to test configuration validity
6. **Secrets Separation**: Sensitive data stays in environment variables

## Rollback (If Needed)

If you need to roll back to hardcoded configuration:

```bash
git revert HEAD
```

The previous version had URLs hardcoded in individual files:
- `wp_to_static_generator.py` lines 2358, 2365
- `ollama_spell_checker.py` lines 422-423
- `convert_to_staging.py` lines 13, 20, 31, 38

## Questions?

See:
- `config.py` - Configuration file with inline documentation
- `docs/archive/WARP.md` - Full project documentation
- `README.md` - Quick start guide
