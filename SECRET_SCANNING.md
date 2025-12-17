# Secret Scanning Implementation

This repository is protected by automated secret scanning to prevent accidental exposure of sensitive credentials.

## 🛡️ What's Implemented

### 1. GitHub Actions Workflow (`.github/workflows/secret-scan.yml`)
- **Triggers:**
  - Every push to main/master branch
  - Every pull request
  - Weekly scheduled scan (Sundays at 2 AM UTC)
  - Manual workflow dispatch
  
- **Features:**
  - Scans entire repository history for secrets
  - Uploads scan results as artifacts on failure
  - Sends Slack alerts when secrets are detected
  - Uses Gitleaks for comprehensive secret detection

### 2. Pre-Commit Hook (`.git-hooks/pre-commit`)
- **Purpose:** Prevent secrets from being committed locally
- **Features:**
  - Scans only staged files (fast)
  - Auto-installs gitleaks if missing (macOS)
  - Blocks commits containing secrets
  - Provides helpful error messages

### 3. Configuration File (`.gitleaks.toml`)
- **Purpose:** Customize secret detection behavior
- **Features:**
  - Allowlist for known false positives
  - Path exclusions (e.g., `public/`, documentation)
  - Custom regex patterns
  - Entropy thresholds

---

## 🚀 Setup Instructions

### Quick Setup (Automated)
```bash
# Run the setup script
./setup-secret-scanning.sh
```

This will:
1. Install gitleaks (if not already installed)
2. Configure git hooks
3. Run an initial repository scan
4. Provide next steps

### Manual Setup

#### 1. Install Gitleaks

**macOS:**
```bash
brew install gitleaks
```

**Linux:**
```bash
# Download and install latest release
curl -sSfL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz | \
  sudo tar -xz -C /usr/local/bin gitleaks
sudo chmod +x /usr/local/bin/gitleaks
```

**Windows:**
```powershell
# Using Chocolatey
choco install gitleaks

# Or download from: https://github.com/gitleaks/gitleaks/releases
```

#### 2. Enable Pre-Commit Hook
```bash
# Configure git to use custom hooks directory
git config core.hooksPath .git-hooks

# Make the hook executable
chmod +x .git-hooks/pre-commit
```

#### 3. Verify Setup
```bash
# Check gitleaks is working
gitleaks version

# Test pre-commit hook (should scan and allow if no secrets)
git add .
git commit -m "test commit"
```

---

## 📋 Usage

### Local Development

The pre-commit hook runs automatically before each commit:

```bash
git add myfile.py
git commit -m "My changes"

# Output:
# 🔍 Running secret scan before commit...
# 🔎 Scanning staged files for secrets...
# ✅ No secrets detected - commit allowed
```

If secrets are detected:
```bash
# Output:
# ❌ SECRETS DETECTED IN STAGED FILES!
# 
# 🚨 Your commit has been blocked because Gitleaks detected potential secrets.
#
# Next steps:
#   1. Review the output above
#   2. Remove the secrets from your code
#   3. If false positive, add to .gitleaks.toml
```

### Bypass Pre-Commit Hook (NOT RECOMMENDED)

Only if you're absolutely sure it's a false positive:
```bash
git commit --no-verify -m "message"
```

### Manual Scan

Scan entire repository:
```bash
gitleaks detect --verbose --redact
```

Scan staged files only:
```bash
gitleaks protect --staged --verbose
```

Scan specific files:
```bash
gitleaks protect --source=myfile.py
```

---

## ⚙️ Configuration

### Adding False Positives to Allowlist

Edit `.gitleaks.toml`:

```toml
[allowlist]
# Add regex patterns
regexes = [
    '''example\.com''',  # Allow example.com URLs
    '''test-api-key-123''',  # Allow test keys
]

# Add file paths to exclude
paths = [
    '''docs/examples/.*''',  # Exclude example files
    '''test/fixtures/.*''',  # Exclude test fixtures
]
```

### Custom Secret Detection Rules

Add custom rules to `.gitleaks.toml`:

```toml
[[rules]]
id = "custom-api-key"
description = "Custom API Key Pattern"
regex = '''custom-api-[0-9a-z]{32}'''
tags = ["api", "custom"]
```

---

## 🚨 What to Do If Secrets Are Found

### If Detected Before Push (Pre-Commit Hook)

1. **Remove the secret** from your code
2. **Use environment variables** instead:
   ```python
   # Bad
   api_key = "sk-1234567890abcdef"
   
   # Good
   import os
   api_key = os.environ.get('API_KEY')
   ```
3. **Add to .gitleaks.toml** if it's a false positive
4. **Try committing again**

### If Detected in GitHub Actions

1. **Immediately rotate the exposed credential**
   - Change passwords
   - Regenerate API keys
   - Revoke tokens
   
2. **Remove secret from git history**:
   
   **Using BFG Repo Cleaner (recommended):**
   ```bash
   # Install BFG
   brew install bfg
   
   # Clone a fresh copy
   git clone --mirror https://github.com/jameskilbynet/jkcoukblog.git
   
   # Remove secrets
   bfg --replace-text passwords.txt jkcoukblog.git
   
   # Clean up
   cd jkcoukblog.git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Force push
   git push --force
   ```
   
   **Using git-filter-repo:**
   ```bash
   # Install git-filter-repo
   brew install git-filter-repo
   
   # Remove file containing secret
   git filter-repo --path path/to/secret/file.py --invert-paths
   
   # Force push
   git push --force
   ```

3. **Update GitHub secrets** if needed
4. **Notify team** about the incident

### If Detected in Weekly Scan

1. Review the scan results in GitHub Actions artifacts
2. Follow steps above to remediate
3. Consider if the secret has been exposed and for how long
4. Assess potential security impact

---

## 🎯 Best Practices

### ✅ Do's

- **Use environment variables** for all secrets
- **Use GitHub Secrets** for CI/CD credentials
- **Use secret management tools** (HashiCorp Vault, AWS Secrets Manager, etc.)
- **Regularly review** `.gitleaks.toml` allowlist
- **Test locally** before pushing
- **Rotate secrets regularly**

### ❌ Don'ts

- **Never commit** actual secrets (API keys, passwords, tokens)
- **Don't disable** pre-commit hooks without good reason
- **Don't ignore** secret scan failures
- **Don't use** `--no-verify` unless you're certain
- **Don't commit** `.env` files with real secrets

---

## 📊 Monitoring

### GitHub Actions

View secret scan results:
```bash
# List recent workflow runs
gh run list --workflow=secret-scan.yml

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

### Slack Notifications

Secret detections automatically send alerts to `#web` channel with:
- Repository and branch information
- Triggered by user
- Direct link to scan results

---

## 🔧 Troubleshooting

### Pre-Commit Hook Not Running

```bash
# Check hook configuration
git config core.hooksPath

# Should output: .git-hooks

# If not set:
git config core.hooksPath .git-hooks

# Verify hook is executable
ls -l .git-hooks/pre-commit
# Should show: -rwxr-xr-x
```

### Gitleaks Not Found

```bash
# Check if installed
which gitleaks

# If not found, install:
brew install gitleaks  # macOS
```

### False Positives

1. **Verify it's actually a false positive** (not a real secret)
2. **Add to allowlist** in `.gitleaks.toml`
3. **Document why** it's allowlisted (comment in config)
4. **Commit the config change**

### Performance Issues

For large repositories:

```bash
# Scan only recent commits
gitleaks detect --log-opts="--since='1 week ago'"

# Scan specific paths
gitleaks detect --path=src/
```

---

## 📚 Additional Resources

- **Gitleaks Documentation:** https://github.com/gitleaks/gitleaks
- **GitHub Secret Scanning:** https://docs.github.com/en/code-security/secret-scanning
- **BFG Repo Cleaner:** https://rtyley.github.io/bfg-repo-cleaner/
- **Git Filter Repo:** https://github.com/newren/git-filter-repo
- **OWASP Secrets Management:** https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

---

## ❓ Questions?

If you encounter issues:
1. Check this documentation first
2. Review `.gitleaks.toml` configuration
3. Test manually: `gitleaks protect --staged --verbose`
4. Check GitHub Actions logs
5. Review Slack notifications for details

---

## 🔒 Security Contact

If you discover exposed secrets in this repository:
1. **Do NOT** create a public GitHub issue
2. **Immediately** contact the repository owner via private channel
3. Provide details of the exposed secret
4. Include the commit SHA and file path

For security incidents, time is critical - act quickly!
