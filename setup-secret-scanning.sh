#!/bin/bash
#
# Setup script for local secret scanning
# Installs gitleaks and configures git hooks
#

set -e

echo "🔐 Setting up secret scanning for jkcoukblog"
echo ""

# Check if gitleaks is already installed
if command -v gitleaks &> /dev/null; then
    echo "✅ Gitleaks is already installed"
    gitleaks version
else
    echo "📦 Installing gitleaks..."
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install gitleaks
        else
            echo "❌ Homebrew not found. Please install Homebrew first:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Installing gitleaks for Linux..."
        # Download latest release
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz | \
            sudo tar -xz -C /usr/local/bin gitleaks
        sudo chmod +x /usr/local/bin/gitleaks
    else
        echo "❌ Unsupported OS. Please install gitleaks manually:"
        echo "   https://github.com/gitleaks/gitleaks#installation"
        exit 1
    fi
    
    echo "✅ Gitleaks installed successfully"
fi

echo ""
echo "🔧 Configuring git hooks..."

# Configure git to use our custom hooks directory
git config core.hooksPath .git-hooks

# Ensure the pre-commit hook is executable
chmod +x .git-hooks/pre-commit

echo "✅ Git hooks configured"
echo ""

# Run an initial scan to check current state
echo "🔍 Running initial repository scan..."
echo "   This will scan the entire repository history for secrets"
echo ""

if gitleaks detect --verbose --redact --report-path=gitleaks-report.json; then
    echo ""
    echo "✅ No secrets detected in repository!"
    rm -f gitleaks-report.json
else
    echo ""
    echo "⚠️  Secrets detected! Review the report above."
    echo "   Full report saved to: gitleaks-report.json"
    echo ""
    echo "IMPORTANT: If secrets were found:"
    echo "  1. Rotate ALL detected credentials immediately"
    echo "  2. Remove secrets from git history using BFG or git-filter-repo"
    echo "  3. Force push cleaned history (coordinate with team)"
    echo ""
    echo "To clean git history:"
    echo "  - BFG: https://rtyley.github.io/bfg-repo-cleaner/"
    echo "  - git-filter-repo: https://github.com/newren/git-filter-repo"
    echo ""
fi

echo ""
echo "📋 Setup complete!"
echo ""
echo "What's configured:"
echo "  ✓ Gitleaks installed and working"
echo "  ✓ Pre-commit hook enabled (scans before each commit)"
echo "  ✓ GitHub Actions workflow added (.github/workflows/secret-scan.yml)"
echo "  ✓ Configuration file created (.gitleaks.toml)"
echo ""
echo "Next steps:"
echo "  1. Review .gitleaks.toml and adjust allowlist if needed"
echo "  2. Test the pre-commit hook: git commit -m 'test'"
echo "  3. Commit the new workflow: git add .github/workflows/secret-scan.yml"
echo "  4. Enable GitHub secret scanning in repository settings (recommended)"
echo ""
echo "The pre-commit hook will now scan your commits automatically!"
