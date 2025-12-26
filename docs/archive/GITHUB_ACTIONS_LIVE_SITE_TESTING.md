# GitHub Actions: Live Site Testing

## Overview

The **Test Live Site Formatting** workflow provides automated testing of the live site (production or staging) with results reported to Slack. This workflow runs manually on-demand to verify that the site meets formatting, SEO, and technical standards.

## Workflow File

`.github/workflows/test-live-site.yml`

## Trigger

**Manual Only** - This workflow must be triggered manually through the GitHub Actions UI.

## How to Run

### Via GitHub Web Interface

1. Go to **Actions** tab in the GitHub repository
2. Select **Test Live Site Formatting** from the workflows list
3. Click **Run workflow** button
4. Configure options:
   - **URL to test**: Choose between production (`jameskilby.co.uk`) or staging (`jkcoukblog.pages.dev`)
   - **Test post page** (optional): Enter a specific post URL to test (e.g., `https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/`)
5. Click **Run workflow**

### Via GitHub CLI

```bash
# Test production site only
gh workflow run test-live-site.yml

# Test production with a specific post
gh workflow run test-live-site.yml \
  -f test_url='https://jameskilby.co.uk' \
  -f test_post='https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/'

# Test staging site
gh workflow run test-live-site.yml \
  -f test_url='https://jkcoukblog.pages.dev'
```

## Input Parameters

### `test_url` (required)
- **Description**: The base URL to test
- **Type**: Choice dropdown
- **Options**:
  - `https://jameskilby.co.uk` (production - default)
  - `https://jkcoukblog.pages.dev` (staging)
- **Default**: `https://jameskilby.co.uk`

### `test_post` (optional)
- **Description**: A specific post page URL to test
- **Type**: String
- **Default**: Empty (no post page test)
- **Example**: `https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/`

## What Gets Tested

The workflow runs `test_live_site_formatting.py` which performs 14 comprehensive tests:

1. **Homepage Loads** - Verifies the URL is accessible
2. **HTML Structure** - Validates DOCTYPE and basic HTML tags
3. **Meta Tags** - Checks charset, viewport, description, Open Graph, Twitter Card
4. **Title Tag** - Ensures page title is present and reasonable length
5. **Canonical URL** - Verifies canonical link points to correct domain
6. **Plausible Analytics** - Validates analytics script and configuration
7. **WordPress Cleanup** - Checks that WordPress-specific elements are removed
8. **Utterances Comments** - Verifies comments widget configuration (on post pages)
9. **Images** - Validates image alt attributes and responsive srcset
10. **CSS Assets** - Tests that stylesheets load correctly
11. **JavaScript Assets** - Verifies JavaScript files load
12. **Internal Links** - Checks for broken links (404s)
13. **Structured Data** - Validates JSON-LD schema markup
14. **Cache Control** - Checks for cache headers

## Output and Results

### GitHub Actions UI

The workflow provides a detailed summary in the **Summary** tab:

```
🧪 Live Site Formatting Test Results

🌐 Main URL Test
URL: https://jameskilby.co.uk

- Tests Passed: 13/14
- Errors: 0
- Warnings: 1
- Status: ✅ All tests passed

📄 Post Page Test (if tested)
URL: https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/

- Tests Passed: 13/14
- Errors: 0
- Warnings: 2
- Status: ✅ All tests passed

---
Triggered by: @username
```

### Slack Notifications

If `SLACK_WEBHOOK_URL` is configured, results are automatically sent to Slack:

**Successful Test:**
```
✅ Live Site Formatting Test: Passed

🌐 Main URL Test:
https://jameskilby.co.uk
• Tests passed: 13/14
• Errors: 0
• Warnings: 1

Triggered by username | View Workflow Run
```

**Failed Test:**
```
❌ Live Site Formatting Test: Failed

🌐 Main URL Test:
https://jameskilby.co.uk
• Tests passed: 11/14
• Errors: 2
• Warnings: 1

Triggered by username | View Workflow Run
```

## Configuration

### Required Secrets

None - this workflow tests the public site and doesn't require authentication.

### Optional Secrets

#### `SLACK_WEBHOOK_URL`
- **Purpose**: Send test results to Slack
- **Required**: No (workflow will skip Slack notification if not set)
- **Format**: Slack incoming webhook URL
- **How to get**: 
  1. Go to your Slack workspace
  2. Create an Incoming Webhook in App settings
  3. Copy the webhook URL
  4. Add as repository secret: `Settings > Secrets and variables > Actions > New repository secret`

## Workflow Behavior

### Success Criteria

- **Exit Code 0**: All critical tests pass (warnings are acceptable)
- The workflow completes successfully
- Green checkmark in GitHub Actions UI
- Slack shows ✅ Passed status

### Failure Criteria

- **Exit Code 1**: One or more tests have errors
- The workflow fails
- Red X in GitHub Actions UI
- Slack shows ❌ Failed status

### Always Runs

The following steps run regardless of test results:
- GitHub Step Summary creation
- Slack notification (if webhook configured)

## Use Cases

### 1. Post-Deployment Verification

After deploying new content or changes, run this workflow to verify:
- All assets still load correctly
- Meta tags and SEO elements are intact
- Analytics tracking is working
- No broken links were introduced

### 2. Staging Validation

Before deploying from staging to production:
```bash
gh workflow run test-live-site.yml \
  -f test_url='https://jkcoukblog.pages.dev'
```

### 3. Regular Site Health Checks

Run periodically (e.g., weekly) to catch any issues:
- CDN/caching problems
- Broken external assets
- Degraded performance

### 4. Specific Page Testing

Test individual posts after publishing:
```bash
gh workflow run test-live-site.yml \
  -f test_post='https://jameskilby.co.uk/2025/12/new-post/'
```

## Timeout and Resource Limits

- **Timeout**: 15 minutes
- **Runner**: `ubuntu-latest` (GitHub-hosted)
- **Python Version**: 3.11
- **Dependencies**: Cached for faster runs

## Troubleshooting

### Workflow Times Out

If the workflow times out after 15 minutes:
1. Check if the site is down or very slow
2. Reduce the number of tests (sample sizes in the script)
3. Test specific pages instead of the entire site

### Tests Fail Unexpectedly

1. Check the detailed output in the workflow logs
2. Run the script locally to reproduce: `./test_live_site_formatting.py --url https://jameskilby.co.uk`
3. Look for specific error messages in the test output

### Slack Notifications Not Sent

1. Verify `SLACK_WEBHOOK_URL` secret is set
2. Check the webhook is still valid in Slack settings
3. Look for curl errors in the workflow logs
4. Test the webhook manually: `curl -X POST $SLACK_WEBHOOK_URL -H 'Content-Type: application/json' -d '{"text":"test"}'`

### False Positives

Some tests may show warnings that are acceptable:
- WordPress generator meta tag (if it says "WordPress Static Generator" - this is fine)
- Missing alt attributes on decorative images
- Long title tags (acceptable if they're descriptive)

These warnings don't cause the workflow to fail.

## Integration with Other Workflows

This workflow is standalone and doesn't depend on other workflows. However, it's recommended to run it:

**After** the `deploy-static-site.yml` workflow completes:
1. Deploy workflow generates and pushes new static site
2. Cloudflare Pages auto-deploys
3. Manually trigger `test-live-site.yml` to verify deployment

## Performance

Typical run time: **2-5 minutes**
- Setup and dependencies: ~1 minute
- Main URL test: ~30 seconds
- Post page test: ~30 seconds
- Slack notification: ~1 second

## Best Practices

1. **Test after major changes**: Run after updating themes, plugins, or site structure
2. **Test both URLs**: When making changes, test both production and staging
3. **Test specific posts**: When publishing new content, test the specific post page
4. **Review warnings**: Even if tests pass, review warnings for potential issues
5. **Keep Slack informed**: Ensure the team gets notifications of test results

## Related Documentation

- `test_live_site_formatting.py` - The test script itself
- `docs/LIVE_SITE_FORMATTING_TESTS.md` - Detailed test documentation
- `TEST_SCRIPT_QUICKSTART.md` - Quick reference for running tests locally
- `.github/workflows/deploy-static-site.yml` - Main deployment workflow

## Future Enhancements

Potential improvements:
- Schedule automatic weekly tests
- Add performance metrics (page load time)
- Test multiple post pages automatically
- Add accessibility (WCAG) testing
- Integrate with monitoring/alerting systems
- Generate historical test reports
