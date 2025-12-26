# Testing Documentation

This document covers all testing procedures and tools.

## Table of Contents
- [Live Site Testing](#live-site-testing)
- [Spell Checking](#spell-checking)
- [Search Testing](#search-testing)
- [Environment Testing](#environment-testing)

---

## Live Site Testing

### Overview
Automated tests for site formatting, SEO, and technical standards.

### Test Script
`test_live_site_formatting.py`

### Usage

**Test production:**
```bash
./test_live_site_formatting.py
```

**Test staging:**
```bash
./test_live_site_formatting.py --url https://jkcoukblog.pages.dev
```

**Test specific post:**
```bash
./test_live_site_formatting.py --post https://jameskilby.co.uk/2025/12/post-slug/
```

### What Gets Tested (14 Tests)

#### HTML & Structure
- ✅ Valid DOCTYPE and HTML structure
- ✅ All required meta tags (charset, viewport, description)
- ✅ Page title and canonical URLs
- ✅ Structured data (JSON-LD)

#### Analytics & Tracking
- ✅ Plausible Analytics properly configured
- ✅ Correct data-domain attribute
- ✅ No duplicate tracking scripts

#### Comments System
- ✅ Utterances comments widget properly configured
- ✅ Correct GitHub repository linked
- ✅ Theme and issue-term settings present

#### Assets & Resources
- ✅ CSS stylesheets load correctly
- ✅ JavaScript files load correctly
- ✅ Images have alt attributes
- ✅ Responsive images have srcset

#### SEO & Social
- ✅ Open Graph tags (Facebook/LinkedIn)
- ✅ Twitter Card tags
- ✅ Canonical URLs point to correct domain

#### Content Quality
- ✅ Internal links are not broken
- ✅ WordPress-specific elements removed
- ✅ Cache control headers present

### Exit Codes
- **0** = All tests passed ✅
- **1** = Tests failed ❌

### GitHub Actions Integration

**Via CLI:**
```bash
# Test production
gh workflow run test-live-site.yml

# Test staging
gh workflow run test-live-site.yml -f test_url='https://jkcoukblog.pages.dev'
```

---

## Spell Checking

### Overview
AI-powered spell and grammar checking using local Ollama instance before publishing.

### Implementation
Script: `ollama_spell_checker.py`

### Features
- Uses local Ollama instance (llama3.1:8b model)
- Checks WordPress posts via REST API before publishing
- Whitelists technical terms (vmware, kubernetes, etc.)
- Non-blocking in CI/CD pipeline (continues on error)

### Usage

**Check last 3 posts:**
```bash
./ollama_spell_checker.py 3
```

**Check posts modified since timestamp:**
```bash
export SINCE_TIMESTAMP="2025-01-01T00:00:00Z"
./ollama_spell_checker.py
```

**Check all recent posts:**
```bash
./ollama_spell_checker.py
```

### Configuration

**Environment Variables:**
- `WP_AUTH_TOKEN` - WordPress API authentication (required)
- `OLLAMA_API_CREDENTIALS` - Format: `username:password`
- `OLLAMA_URL` - Default: `https://ollama.jameskilby.cloud`
- `OLLAMA_MODEL` - Default: `llama3.1:8b`
- `SINCE_TIMESTAMP` - ISO timestamp for incremental checking

**Technical Term Whitelist:**
The spell checker knows common technical terms:
- vmware, vcenter, esxi
- kubernetes, k8s, docker
- terraform, ansible, packer
- And many more...

### GitHub Actions Integration

Spell checking runs automatically in the deployment workflow:
```yaml
- name: Spell check recent posts
  continue-on-error: true  # Non-blocking
  run: |
    export SINCE_TIMESTAMP=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)
    ./ollama_spell_checker.py
```

### Spell Check Tracking

Results are logged to `spell-check-history.json`:
```json
{
  "checks": [
    {
      "timestamp": "2025-12-26T10:00:00Z",
      "post_title": "Example Post",
      "issues_found": 3,
      "fixed": true
    }
  ]
}
```

---

## Search Testing

### Overview
Tests the search index generation and validates search functionality.

### Test Script
`test_search.py`

### Usage

**Run search tests:**
```bash
python3 test_search.py
```

**Start local server for testing:**
```bash
python3 test_search.py --server
# Then open http://localhost:8000
```

### What Gets Tested

**Search Index Tests:**
- Validates search index file exists
- Checks JSON structure is valid
- Verifies required fields are present
- Tests search index size and performance
- Validates URLs in search results

**Search Query Tests:**
- Tests various search queries
- Validates search results relevance
- Checks fuzzy search functionality
- Tests category and tag filtering

### Requirements
Already installed via `requirements.txt`:
- requests
- beautifulsoup4

---

## Environment Testing

### Overview
Validates that the GitHub runner environment is properly configured.

### Test Script
`test_runner_env.py`

### Usage

**Run environment validation:**
```bash
python3 test_runner_env.py
```

### What Gets Checked

**Python Environment:**
- Python version
- Python executable path
- Current working directory

**File System:**
- Lists files in current directory
- Checks for required Python scripts
- Verifies GitHub Actions workflow files exist

**Python Dependencies:**
- Tests `requests` library import and version
- Tests `beautifulsoup4` library import and version
- Reports missing dependencies

**Environment Variables:**
- Checks for `WP_AUTH_TOKEN` presence
- Masks token value for security
- Warns if not set

### Exit Codes
- **0** = All checks passed ✅
- **1** = Some checks failed ❌

### Sample Output

```
======================================================================
🚀 Starting Environment Validation
======================================================================

✅ Python 3.11.5 found
✅ Required scripts exist
✅ Dependencies installed (requests, beautifulsoup4)
✅ WP_AUTH_TOKEN environment variable set

======================================================================
📈 Results: All checks passed
======================================================================
```

---

## Related Documentation
- [Main README](../README.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [FEATURES.md](FEATURES.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
