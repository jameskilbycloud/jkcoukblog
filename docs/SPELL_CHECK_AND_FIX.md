# WordPress Spell Check and Fix with Manual Approval

Automated spell checking for WordPress content using Ollama AI, with manual approval before applying corrections.

## Overview

This workflow:
1. **Checks** WordPress posts for spelling errors using Ollama
2. **Creates** a GitHub issue with proposed corrections
3. **Waits** for manual approval via issue comment
4. **Applies** corrections back to WordPress upon approval
5. **Notifies** via Slack at each step

## Workflow Files

- `.github/workflows/spell-check-and-fix.yml` - Main spell check and fix workflow
- `.github/workflows/spell-check-approval-handler.yml` - Handles `/approve` and `/reject` commands
- `wp_spell_check_and_fix.py` - Python script that checks and applies corrections

## How It Works

### Step 1: Run Spell Check

Manually trigger the workflow from GitHub Actions:

```bash
# Via GitHub CLI
gh workflow run spell-check-and-fix.yml

# Or via GitHub UI
# Go to Actions → Spell Check and Fix WordPress Content → Run workflow
```

**Options:**
- **Post count**: Number of recent posts to check (default: 5)
- **Check modified**: Only check posts modified since last run

### Step 2: Review Corrections

If errors are found, the workflow will:
1. Create a GitHub issue with all proposed corrections
2. Upload detailed report as an artifact
3. Send Slack notification with link to issue

The issue will look like:

```markdown
## 📝 Spelling Corrections Proposed

### Post Title Here
**Post ID:** 123
**URL:** https://wordpress.jameskilby.cloud/post-slug/

#### Section: title
- **teh** → **the**

#### Section: paragraph_1
- **recieve** → **receive**
  - Context: _You will recieve a notification..._

---

## ✅ Approve and Apply Corrections

To apply these corrections to WordPress:
1. Review the corrections above
2. If you approve, comment on this issue with: `/approve`
3. The workflow will automatically apply the corrections

## ❌ Reject Corrections

To reject: comment `/reject` and close the issue
```

### Step 3: Approve or Reject

**To Approve:**
```
/approve
```

The workflow will:
- Download the corrections from the artifact
- Apply them to WordPress via the REST API
- Update the timestamp for incremental checks
- Close the issue
- Send success notification to Slack

**To Reject:**
```
/reject
```

The workflow will:
- Close the issue without applying changes
- No changes made to WordPress

## Usage Examples

### Check Last 5 Posts
```bash
gh workflow run spell-check-and-fix.yml
```

### Check Last 10 Posts
```bash
gh workflow run spell-check-and-fix.yml -f post_count=10
```

### Check Only Modified Posts
```bash
gh workflow run spell-check-and-fix.yml -f check_modified=true
```

## Script Usage

The Python script can also be run locally:

### Check Only (Don't Apply)
```bash
export WP_AUTH_TOKEN="your_token"
./wp_spell_check_and_fix.py --check-only --count 5
```

This generates:
- `spelling_corrections_report.md` - Human-readable report
- `spelling_corrections.json` - Machine-readable corrections

### Apply Corrections from File
```bash
./wp_spell_check_and_fix.py --apply-from-file spelling_corrections.json
```

### Check and Apply Immediately
```bash
./wp_spell_check_and_fix.py --count 5
```
⚠️ **Warning:** This applies corrections without approval!

## Configuration

### Environment Variables

The workflow uses these environment variables:

- `WP_AUTH_TOKEN` (required) - WordPress Basic Auth token
- `OLLAMA_API_CREDENTIALS` (optional) - Ollama API credentials (format: `username:password`)
- `WP_URL` - WordPress URL (default: `https://wordpress.jameskilby.cloud`)
- `OLLAMA_URL` - Ollama API URL (default: `https://ollama.jameskilby.cloud`)
- `OLLAMA_MODEL` - Model to use (default: `llama3.1:8b`)

### Whitelisted Terms

Technical terms that won't be flagged as errors:

- VMware ecosystem: `vmware`, `vsphere`, `vsan`, `vmc`
- DevOps: `kubernetes`, `docker`, `ansible`, `terraform`
- Infrastructure: `cloudflare`, `github`, `nginx`, `postgres`
- Common: `api`, `json`, `yaml`, `cli`, `devops`, `cicd`
- Hardware: `nvme`, `pcie`, `cpu`, `gpu`, `ram`, `ssd`
- Networking: `nas`, `iscsi`, `nfs`, `vlan`

Add more in `wp_spell_check_and_fix.py` in the `whitelist` set.

## How Corrections Work

### Text Extraction

The script extracts text from:
1. **Title** - Post title (cleaned of HTML)
2. **Excerpt** - Post excerpt
3. **Paragraphs** - Individual paragraphs from post content

Code blocks, scripts, and styles are excluded.

### Spelling Check

For each text section:
1. Send to Ollama with specific prompt
2. Receive JSON with corrections
3. Filter out whitelisted terms
4. Store corrections with context

### Applying Corrections

When approved:
1. Load corrections from JSON file
2. For each post:
   - Group corrections by section (title, excerpt, content)
   - Apply text replacements
   - Handle capitalization variants
   - Update via WordPress REST API

### WordPress API

Updates use the REST API:
```
POST /wp-json/wp/v2/posts/{id}
{
  "title": "Corrected Title",
  "content": "Corrected content...",
  "excerpt": "Corrected excerpt..."
}
```

## Incremental Checking

The workflow tracks the last check time in `.last_spell_check_timestamp`.

When running with `check_modified=true`:
- Only checks posts modified after the timestamp
- Updates timestamp after successful correction application
- Saves GitHub Actions runtime

## Security

- WordPress site is behind Cloudflare Access
- Runs on self-hosted runner with access
- Corrections stored as artifacts (30-day retention)
- Manual approval required before any changes
- All changes logged in git commits

## Troubleshooting

### No Issues Created

Check that:
- Spelling errors were actually found
- Script generated `spelling_corrections.json`
- Workflow has permission to create issues

### Approval Not Working

Verify:
- Comment is exactly `/approve` (case-insensitive)
- Issue has `spell-check` and `awaiting-approval` labels
- The approval handler workflow is enabled

### Corrections Not Applied

Check:
- Artifact still exists (30-day retention)
- `WP_AUTH_TOKEN` secret is valid
- Self-hosted runner can access WordPress
- WordPress REST API is responding

### Ollama 404 Error

If you see a 404 error when calling Ollama:

**Likely causes:**
1. **Model name format** - Ollama expects exact model names
2. **Model not pulled** - The model doesn't exist on the server
3. **Wrong API endpoint** - Check Ollama URL is correct

**Diagnose the issue:**
```bash
# Run the test script on the runner
./test_ollama_connection.py
```

This will:
- Test connectivity to Ollama
- List all available models
- Try different model name formats
- Suggest the correct model name to use

**Common fixes:**

1. **Pull the model on the Ollama server:**
```bash
ollama pull llama3.1:8b
```

2. **Try different model name format:**
- If using `llama3.1:8b`, try `llama3.1`
- If using `llama3.1`, try `llama3.1:latest` or `llama3.1:8b`

3. **Update workflow environment variable:**
```yaml
OLLAMA_MODEL: llama3.1  # Remove the :8b tag
```

The script now automatically tries alternative formats if the first attempt fails.

### Ollama Timeout

If Ollama times out:
- Check Ollama service is running
- Verify `OLLAMA_API_CREDENTIALS` if required
- Consider increasing timeout in script (line 94)
- Try smaller post count

## Example Workflow Run

```
1. Trigger: gh workflow run spell-check-and-fix.yml -f post_count=5
   ↓
2. Workflow checks 5 posts
   - Post 1: ✅ No errors
   - Post 2: ⚠️ 3 errors found
   - Post 3: ✅ No errors
   - Post 4: ⚠️ 1 error found
   - Post 5: ✅ No errors
   ↓
3. Issue created: "Spell Check: Corrections Needed (Run #12345)"
   - Lists all corrections with context
   - Slack notification sent
   ↓
4. You review and comment: /approve
   ↓
5. Approval handler triggers apply-corrections job
   - Downloads corrections artifact
   - Applies to Post 2 (3 corrections)
   - Applies to Post 4 (1 correction)
   - Updates timestamp
   - Closes issue
   - Slack success notification
   ↓
6. Done! WordPress content corrected
```

## Benefits

✅ **Automated** - Finds errors automatically with AI
✅ **Safe** - Manual approval prevents unwanted changes
✅ **Auditable** - All changes tracked in GitHub issues
✅ **Efficient** - Incremental checking saves time
✅ **Integrated** - Works with existing WordPress workflow
✅ **Notifications** - Slack alerts keep you informed

## Future Enhancements

- [ ] Grammar checking (not just spelling)
- [ ] Custom dictionary support
- [ ] Batch approval for trusted corrections
- [ ] Auto-approve for high-confidence corrections
- [ ] Style guide enforcement
- [ ] Link checking
- [ ] Image alt text validation

---

**Related Documentation:**
- `ollama_spell_checker.py` - Original spell checker (report only)
- `.github/workflows/spell-check.yml` - Original spell check workflow
- `README.md` - Main project documentation
