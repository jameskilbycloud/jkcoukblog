# Environment Variable Validation

## Overview

The GitHub Actions workflow now validates required environment variables at the start of each job, failing fast with clear error messages if configuration is missing.

## Implementation

### Location
`.github/workflows/deploy-static-site.yml`

### Jobs with Validation

#### 1. Spell Check Job
**Required variables:**
- `WP_AUTH_TOKEN` - WordPress API authentication
- `OLLAMA_API_CREDENTIALS` - Ollama API access

**Validation step:**
```yaml
- name: Validate required environment variables
  run: |
    echo "🔍 Validating required environment variables..."
    MISSING_VARS=()
    
    if [ -z "${{ secrets.WP_AUTH_TOKEN }}" ]; then
      MISSING_VARS+=("WP_AUTH_TOKEN")
    fi
    
    if [ -z "${{ secrets.OLLAMA_API_CREDENTIALS }}" ]; then
      MISSING_VARS+=("OLLAMA_API_CREDENTIALS")
    fi
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
      echo "❌ Missing required environment variables:"
      for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
      done
      exit 1
    else
      echo "✅ All required environment variables are set"
    fi
```

#### 2. Build and Deploy Job
**Required variables:**
- `WP_AUTH_TOKEN` - WordPress API authentication

**Optional variables (warning only):**
- `SLACK_WEBHOOK_URL` - Slack notifications

**Validation step:**
```yaml
- name: Validate required environment variables
  run: |
    echo "🔍 Validating required environment variables..."
    MISSING_VARS=()
    MISSING_OPTIONAL=()
    
    # Required
    if [ -z "${{ secrets.WP_AUTH_TOKEN }}" ]; then
      MISSING_VARS+=("WP_AUTH_TOKEN")
    fi
    
    # Optional
    if [ -z "${{ secrets.SLACK_WEBHOOK_URL }}" ]; then
      MISSING_OPTIONAL+=("SLACK_WEBHOOK_URL")
    fi
    
    # Fail if required missing
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
      echo "❌ Missing required environment variables:"
      exit 1
    fi
    
    # Warn if optional missing
    if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
      echo "⚠️  Optional environment variables not set (non-blocking):"
    fi
```

## Benefits

### 1. Fail Fast ⚡
- Validation runs as the **first step** in each job
- Catches configuration issues before any resources are consumed
- No need to wait for checkout, dependencies, or other setup

### 2. Clear Error Messages 📝
```
❌ Missing required environment variables:
  - WP_AUTH_TOKEN
  - OLLAMA_API_CREDENTIALS

📝 Please configure these secrets in repository settings:
   Settings > Secrets and variables > Actions
```

### 3. Helpful Guidance 🧭
- Tells you exactly which variables are missing
- Provides instructions on where to configure secrets
- Distinguishes between required (fail) and optional (warn) variables

### 4. Cost Savings 💰
- Self-hosted runners: Avoids wasting compute time
- GitHub-hosted runners: Saves minutes on failed runs
- Developer time: Faster feedback loop

### 5. Better Debugging 🔍
- Workflow logs clearly show configuration state
- No need to dig through later steps to find auth failures
- Explicit validation vs implicit failures

## Example Output

### Success ✅
```
🔍 Validating required environment variables...
✅ All required environment variables are set
  ✓ WP_AUTH_TOKEN
  ✓ OLLAMA_API_CREDENTIALS
```

### Failure ❌
```
🔍 Validating required environment variables...
❌ Missing required environment variables:
  - WP_AUTH_TOKEN

📝 Please configure these secrets in repository settings:
   Settings > Secrets and variables > Actions
```

### Optional Warning ⚠️
```
✅ All required environment variables are set
  ✓ WP_AUTH_TOKEN

⚠️  Optional environment variables not set (non-blocking):
  - SLACK_WEBHOOK_URL
```

## Required Secrets

### WP_AUTH_TOKEN
**Purpose:** Authenticates with WordPress REST API  
**Format:** Base64-encoded `username:password`  
**Used in:**
- Static site generation
- Spell checking
- Content fetching

**How to generate:**
```bash
echo -n "username:password" | base64
```

**Where to set:**
1. Go to repository Settings
2. Navigate to Secrets and variables > Actions
3. Click "New repository secret"
4. Name: `WP_AUTH_TOKEN`
5. Value: Base64-encoded credentials

### OLLAMA_API_CREDENTIALS
**Purpose:** Authenticates with Ollama API for spell checking  
**Format:** API key or token  
**Used in:** Spell check job only

**Where to set:**
1. Go to repository Settings
2. Navigate to Secrets and variables > Actions
3. Click "New repository secret"
4. Name: `OLLAMA_API_CREDENTIALS`
5. Value: Your Ollama API credentials

## Optional Secrets

### SLACK_WEBHOOK_URL
**Purpose:** Sends Slack notifications on build success/failure  
**Format:** Slack webhook URL  
**Used in:** Notification steps (non-blocking)

**Where to set:**
1. Create a Slack webhook in your workspace
2. Add as repository secret: `SLACK_WEBHOOK_URL`

## Workflow Behavior

### If Required Variable Missing
1. ❌ Validation step fails immediately
2. ⏹️ Workflow stops (doesn't proceed to next steps)
3. 📧 GitHub sends failure notification
4. 🔍 Logs show which variable is missing

### If Optional Variable Missing
1. ⚠️ Warning message displayed
2. ✅ Validation step succeeds
3. ▶️ Workflow continues normally
4. 🔕 Related features (e.g., Slack notifications) won't work

## Testing

### Local Testing
Cannot test locally as secrets are GitHub-specific.

### Testing in GitHub Actions
1. **Test with all secrets:**
   - Trigger workflow manually or via push
   - Validation should pass with ✅

2. **Test with missing required secret:**
   - Temporarily rename `WP_AUTH_TOKEN` in repository secrets
   - Trigger workflow
   - Should fail immediately with clear error
   - Restore secret name when done

3. **Test with missing optional secret:**
   - Remove `SLACK_WEBHOOK_URL` from repository secrets
   - Trigger workflow
   - Should show warning but continue
   - Slack notifications won't work

## Maintenance

### Adding New Required Variables
1. Add check in validation step:
```yaml
if [ -z "${{ secrets.NEW_SECRET }}" ]; then
  MISSING_VARS+=("NEW_SECRET")
fi
```

2. Add to success output:
```yaml
echo "  ✓ NEW_SECRET"
```

3. Update this documentation

### Adding New Optional Variables
1. Add check to `MISSING_OPTIONAL` array:
```yaml
if [ -z "${{ secrets.NEW_OPTIONAL }}" ]; then
  MISSING_OPTIONAL+=("NEW_OPTIONAL")
fi
```

2. Update this documentation

## Troubleshooting

### "Missing required environment variables: WP_AUTH_TOKEN"
**Solution:** Configure the secret in repository settings

### "Variable shows as set but still failing"
**Possible causes:**
- Secret value is empty string
- Secret has extra spaces or newlines
- Using wrong secret name

**Debug:**
Check secret name matches exactly (case-sensitive)

### "Optional warning shown but I don't need that feature"
**Solution:** This is expected behavior - you can ignore the warning

## Related Files

- `.github/workflows/deploy-static-site.yml` - Workflow with validation
- `docs/ENVIRONMENT_VALIDATION.md` - This documentation
- `wp_to_static_generator.py` - Uses WP_AUTH_TOKEN
- `ollama_spell_checker.py` - Uses OLLAMA_API_CREDENTIALS

## Best Practices

1. **Always validate at job start** - First step catches issues early
2. **Distinguish required vs optional** - Different handling for each
3. **Provide clear error messages** - Include variable names and instructions
4. **Don't expose secret values** - Only check if set, never echo values
5. **Keep documentation updated** - Document what each secret is for

## Security Notes

- ✅ Validation only checks if secrets exist, never exposes values
- ✅ Secrets are masked in GitHub Actions logs
- ✅ Validation script doesn't log secret contents
- ⚠️ Be careful not to echo secret values in other steps
- 🔒 Secrets are only available to workflows in the repository

## Future Enhancements

### Possible Improvements
1. **Validate secret format** - Check if WP_AUTH_TOKEN is valid Base64
2. **Test API connectivity** - Verify secrets work before proceeding
3. **Cache validation results** - Skip validation on retry runs
4. **Add more optional checks** - Validate URLs, versions, etc.
5. **Create validation action** - Reusable action for other repos

## Version History

- **v1.0** (2025-12-18) - Initial implementation
  - Validate WP_AUTH_TOKEN in both jobs
  - Validate OLLAMA_API_CREDENTIALS in spell-check
  - Warn about optional SLACK_WEBHOOK_URL
  - Clear error messages and instructions
