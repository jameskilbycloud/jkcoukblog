# Ollama Spell Checker Integration

## Overview

Uses your local Ollama instance at `ollama.jameskilby.cloud` to check WordPress posts for spelling and grammar errors before publishing.

## Features

- ✅ **AI-Powered**: Uses Ollama LLM for intelligent spell checking
- ✅ **Technical Aware**: Whitelists common technical terms (VMware, Kubernetes, etc.)
- ✅ **Context-Sensitive**: Understands technical blog content
- ✅ **Detailed Reports**: Generates markdown reports with all findings
- ✅ **WordPress Integration**: Checks posts directly from WordPress API
- ✅ **Customizable**: Can check specific numbers of posts or single posts

## Prerequisites

```bash
# Ensure you have the required Python packages
pip install requests beautifulsoup4

# Set your WordPress authentication token
export WP_AUTH_TOKEN="your_token_here"
```

## Usage

### Check Recent Posts

```bash
# Check 5 most recent posts (default)
./ollama_spell_checker.py

# Check 10 most recent posts
./ollama_spell_checker.py 10

# Check 1 post
./ollama_spell_checker.py 1
```

### Environment Variables

```bash
# Required
export WP_AUTH_TOKEN="your_wordpress_auth_token"

# Optional (with defaults)
export OLLAMA_URL="https://ollama.jameskilby.cloud"  # Your Ollama endpoint
export WP_URL="https://wordpress.jameskilby.cloud"    # Your WordPress URL
export OLLAMA_MODEL="llama3.2:latest"                 # Model to use
```

## How It Works

### 1. **Fetch Posts from WordPress**
   - Connects to WordPress REST API
   - Retrieves most recent posts (or specific post ID)
   - Extracts rendered HTML content

### 2. **Extract Text Sections**
   - Title
   - Meta description
   - Paragraph content
   - Skips code blocks, scripts, and styles

### 3. **AI Analysis with Ollama**
   - Sends text to Ollama API
   - Uses structured prompt for consistent JSON responses
   - Low temperature (0.1) for deterministic results
   - Identifies:
     - Spelling errors
     - Grammar issues
     - Typos

### 4. **Generate Report**
   - Creates markdown report
   - Lists all errors with context
   - Provides suggestions
   - Saves to `spelling_check_report.md`

## Output

### Console Output
```
🚀 Ollama Spell Checker
Ollama: https://ollama.jameskilby.cloud
WordPress: https://wordpress.jameskilby.cloud
Model: llama3.2:latest
============================================================

🔍 Checking 5 most recent posts...
📄 Checking post ID: 7127
   Title: How I upgraded my blog as a Static Website...
   URL: https://wordpress.jameskilby.cloud/2025/10/...
   Found 15 text sections to check
   🔍 Checking title...
   🔍 Checking description...
   🔍 Checking paragraph_1...
      ⚠️  spelling: inteligent → intelligent

============================================================
📊 Report saved to: spelling_check_report.md
```

### Report File (`spelling_check_report.md`)
```markdown
# Spelling and Grammar Check Report

Generated: 2025-12-05 10:00:00

## Summary
- Total posts checked: 5
- Posts with errors: 1
- Posts clean: 4

## Posts with Errors

### How I upgraded my blog as a Static Website...
**URL**: https://wordpress.jameskilby.cloud/2025/10/...

- **SPELLING** in `title`:
  - Word: `inteligent`
  - Suggestion: `intelligent`
  - Context: the inteligent terminal

## Posts with No Errors ✅
- Managing my Homelab with SemaphoreUI
- VMware Cloud on AWS Host Deep Dive
- ...
```

## Integration with GitHub Actions

Add to `.github/workflows/spell-check.yml`:

```yaml
name: Spell Check WordPress Content

on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM
  workflow_dispatch:  # Manual trigger

jobs:
  spell-check:
    runs-on: self-hosted
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4
      
      - name: Run spell checker
        env:
          WP_AUTH_TOKEN: ${{ secrets.WP_AUTH_TOKEN }}
          OLLAMA_URL: https://ollama.jameskilby.cloud
        run: |
          ./ollama_spell_checker.py 10
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: spelling-report
          path: spelling_check_report.md
      
      - name: Create issue if errors found
        if: failure()
        run: |
          gh issue create \
            --title "Spelling errors found in WordPress posts" \
            --body-file spelling_check_report.md \
            --label "spell-check"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Whitelisted Technical Terms

The checker ignores common technical terms:
- VMware ecosystem: vmware, vsphere, vsan, vmc
- Cloud/DevOps: kubernetes, docker, ansible, terraform
- Infrastructure: homelab, nas, nvme, iscsi, nfs, vlan
- General tech: api, json, yaml, cli, devops, ci/cd

To add more terms, edit the `whitelist` set in `ollama_spell_checker.py`.

## Customizing the Prompt

Edit the `check_spelling_with_ollama()` method to customize how Ollama analyzes text:

```python
prompt = f"""You are a spell checker and grammar assistant for technical blog content.

Review the following text and identify:
1. Spelling errors (ignore technical terms like VMware, vSphere, Kubernetes, etc.)
2. Grammar issues
3. Obvious typos
...
"""
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Test Ollama endpoint
curl https://ollama.jameskilby.cloud/api/tags

# If 401 Unauthorized, check your authentication setup
# The script currently doesn't pass auth to Ollama - add if needed
```

### WordPress API Issues

```bash
# Test WordPress API
curl -H "Authorization: Basic YOUR_TOKEN" \
  https://wordpress.jameskilby.cloud/wp-json/wp/v2/posts?per_page=1
```

### Model Not Available

```bash
# Check available models
curl https://ollama.jameskilby.cloud/api/tags

# Pull a model if needed (on the Ollama host)
docker exec ollama_container ollama pull llama3.2:latest
```

## Pre-Publish Workflow

1. **Write post in WordPress** (wordpress.jameskilby.cloud)
2. **Save as draft** or publish privately
3. **Run spell checker**:
   ```bash
   ./ollama_spell_checker.py 1
   ```
4. **Review report** and fix errors in WordPress
5. **Re-run checker** to verify
6. **Publish post** when clean
7. **Run static generator** to deploy

## Exit Codes

- `0`: No errors found ✅
- `1`: Spelling errors found or script error ❌

Use in scripts:
```bash
if ./ollama_spell_checker.py 5; then
    echo "All posts clean, proceeding with deploy"
    ./wp_to_static_generator.py ./public
else
    echo "Spelling errors found, aborting deploy"
    exit 1
fi
```

## Future Enhancements

- [ ] Add authentication support for Ollama if needed
- [ ] Cache results to avoid re-checking unchanged posts
- [ ] Interactive mode to fix errors directly
- [ ] Support for checking pages, not just posts
- [ ] Parallel processing for multiple posts
- [ ] Custom dictionaries per-post or per-category
- [ ] Integration with WordPress plugin for in-editor checking

## Notes

- **Performance**: Each post takes ~30-60 seconds depending on length and Ollama response time
- **Accuracy**: AI-based, so may occasionally flag correct terms or miss errors
- **Privacy**: All processing happens on your infrastructure, no data sent externally
- **Cost**: Free! Uses your own Ollama instance

## Files

- `ollama_spell_checker.py` - Main spell checker script
- `spelling_check_report.md` - Generated report (gitignored)
- `.gitignore` - Add: `spelling_check_report.md`
