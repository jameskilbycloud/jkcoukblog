# GitHub Actions Spell Check Integration

## ✅ Integration Complete!

Your spell checker is now integrated with GitHub Actions in two ways:

### 1. **Dedicated Spell Check Workflow** (New)
**File**: `.github/workflows/spell-check.yml`

#### Triggers
- **Weekly**: Every Monday at 8 AM UTC
- **Manual**: Via GitHub Actions UI
- **Manual with options**: Can specify number of posts to check

#### What It Does
- Checks specified number of WordPress posts for spelling errors
- Generates detailed markdown report
- Uploads report as artifact (kept for 30 days)
- Sends Slack notification with results
- **Non-blocking**: Doesn't prevent deployments

#### Manual Trigger
1. Go to GitHub Actions tab
2. Select "Spell Check WordPress Content"
3. Click "Run workflow"
4. Enter number of posts (default: 5)
5. Click "Run workflow"

### 2. **Integrated with Deployment** (Updated)
**File**: `.github/workflows/deploy-static-site.yml`

#### What Changed
- Added optional spell check step before deployment
- Checks 3 most recent posts
- **Non-blocking**: Deployment continues even if errors found
- Warnings appear in logs but don't fail the build

## Usage

### Weekly Automated Check
Runs automatically every Monday:
- Checks 5 most recent posts
- Report uploaded to GitHub Actions artifacts
- Slack notification sent to #web channel

### Manual Spell Check
```bash
# Via GitHub UI
Actions → Spell Check WordPress Content → Run workflow

# Or trigger via gh CLI
gh workflow run spell-check.yml -f post_count=10
```

### View Reports
1. Go to GitHub Actions
2. Click on the workflow run
3. Scroll to "Artifacts" section
4. Download `spelling-report-[run-id]`

## Configuration

### Environment Variables
Set in workflow files:
```yaml
env:
  WP_AUTH_TOKEN: ${{ secrets.WP_AUTH_TOKEN }}
  OLLAMA_URL: https://ollama.jameskilby.cloud
  WP_URL: https://wordpress.jameskilby.cloud
  OLLAMA_MODEL: llama3.2:latest
```

### Required Secrets
Add in GitHub repository settings (Settings → Secrets and variables → Actions):

| Secret | Description | Required |
|--------|-------------|----------|
| `WP_AUTH_TOKEN` | WordPress API authentication | ✅ Yes |
| `SLACK_WEBHOOK_URL` | Slack notifications | Optional |

### Change Check Frequency

Edit `.github/workflows/spell-check.yml`:
```yaml
schedule:
  - cron: '0 8 * * 1'  # Weekly on Monday at 8 AM

# Change to:
  - cron: '0 8 * * *'  # Daily at 8 AM
  - cron: '0 8 * * 0'  # Weekly on Sunday
  - cron: '0 */6 * * *'  # Every 6 hours
```

### Change Number of Posts Checked

#### Deployment Workflow
Edit `.github/workflows/deploy-static-site.yml` line 57:
```yaml
./ollama_spell_checker.py 3  # Change 3 to desired number
```

#### Spell Check Workflow
Change default in `.github/workflows/spell-check.yml` line 11:
```yaml
default: '5'  # Change to desired default
```

## Workflow Outputs

### Successful Check
```
🚀 Starting spell check...
📝 Checking 5 most recent posts

📄 Checking post ID: 7127
   Title: How I upgraded my blog...
   Found 15 text sections to check
   🔍 Checking title...
   🔍 Checking description...
   ✅ No errors

============================================================
📊 Report saved to: spelling_check_report.md

✅ No spelling errors found!
```

### Errors Found
```
🚀 Starting spell check...
📝 Checking 5 most recent posts

📄 Checking post ID: 7127
   Title: How I upgraded my blog...
   Found 15 text sections to check
   🔍 Checking title...
      ⚠️  spelling: inteligent → intelligent

============================================================
📊 Report saved to: spelling_check_report.md

⚠️  Spelling errors found! Please review the report.
```

## Slack Notifications

### Success Message
```
✅ WordPress Spell Check ✅ Passed

✅ All posts are clean!

📝 Posts checked: 5
📅 Time: 2025-12-05T08:00:00Z
🔗 Report: [View Run]

No action needed.
```

### Warning Message
```
⚠️  WordPress Spell Check ⚠️  Issues Found

⚠️  Spelling errors detected

📝 Posts checked: 5
📅 Time: 2025-12-05T08:00:00Z
🔗 Report: [View Run]

Please review the report and fix errors before publishing.
```

## Deployment Integration

The deployment workflow now includes an **optional spell check**:

1. **Before generating static site**
2. **Checks 3 most recent posts**
3. **Non-blocking** - deployment continues regardless
4. **Warnings in logs** if errors found

### View Spell Check in Deployment
1. Go to Actions → WordPress to Static Site Deploy
2. Click on a run
3. Expand "Optional spell check (non-blocking)" step
4. See inline spell check results

## Troubleshooting

### Workflow Fails to Run

**Self-hosted runner not available**
```
Error: No runner matching the specified labels: self-hosted
```
**Solution**: Ensure your self-hosted runner is online and connected

### Ollama Connection Fails

**401 Unauthorized**
```
❌ Ollama API error: 401
```
**Solution**: Add authentication to Ollama or configure it to allow unauthenticated requests from runner

### WordPress API Fails

**401 Unauthorized**
```
❌ Failed to fetch posts: 401
```
**Solution**: Verify `WP_AUTH_TOKEN` secret is set correctly

### Report Not Generated

**File not found**
```
Error: Unable to locate artifact file
```
**Solution**: Check if spell checker actually ran and generated the report file

## Disable/Enable Features

### Disable Spell Check in Deployment
Edit `.github/workflows/deploy-static-site.yml`:
```yaml
- name: Optional spell check (non-blocking)
  if: false  # Add this line
  env:
    ...
```

### Disable Weekly Checks
Edit `.github/workflows/spell-check.yml`:
```yaml
on:
  # schedule:  # Comment out or remove schedule
  #   - cron: '0 8 * * 1'
  workflow_dispatch:  # Keep manual trigger
```

### Make Spell Check Blocking
To fail deployment if errors found, edit `.github/workflows/deploy-static-site.yml`:
```yaml
- name: Optional spell check (non-blocking)
  # Remove continue-on-error: true
  env:
    ...
```

## Best Practices

### 1. **Review Reports Weekly**
- Check artifacts from weekly runs
- Fix errors in WordPress before they accumulate

### 2. **Manual Check Before Publishing**
- Run spell check manually when publishing new content
- Review report before deploying

### 3. **Keep Non-Blocking in Deployment**
- Allows emergency fixes to deploy
- Spell errors don't prevent critical updates

### 4. **Monitor Slack Notifications**
- Set up #web channel in Slack
- Review notifications for trends

### 5. **Tune Ollama Model**
- Balance accuracy vs speed
- Test different models for your content

## Integration Checklist

- ✅ Spell check workflow created
- ✅ Deployment workflow updated
- ✅ Artifacts configured (30 day retention)
- ✅ Slack notifications configured
- ✅ Manual trigger enabled
- ✅ Weekly schedule set (Mondays 8 AM)
- ✅ Non-blocking deployment integration
- ✅ Self-hosted runner configured

## Next Steps

1. **Test the workflows**:
   ```bash
   # Trigger manually from GitHub UI
   Actions → Spell Check WordPress Content → Run workflow
   ```

2. **Review first report**:
   - Download artifact
   - Check for any false positives
   - Update whitelist if needed

3. **Monitor over next week**:
   - Wait for Monday's automatic run
   - Check Slack notifications
   - Review artifact reports

4. **Fine-tune as needed**:
   - Adjust post count
   - Change schedule
   - Update Ollama model

## Files Modified

- ✅ `.github/workflows/spell-check.yml` - New dedicated workflow
- ✅ `.github/workflows/deploy-static-site.yml` - Added optional check
- ✅ `ollama_spell_checker.py` - Spell checker script
- ✅ `.gitignore` - Ignores report files

## Support

For detailed spell checker docs, see: `OLLAMA_SPELL_CHECKER.md`
For quick reference, see: `SPELL_CHECKER_QUICKSTART.md`
