#!/bin/bash

# Stream Deck Deploy Script
# Triggers the GitHub Actions workflow to deploy the static site
# 
# This script should be configured in Stream Deck with:
# - Action: System > Open
# - Path: /Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
# - Or use System > Website to open: https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/deploy-static-site.yml

set -e

# Configuration
REPO="jameskilbycloud/jkcoukblog"
WORKFLOW="deploy-static-site.yml"

# Change to repo directory
cd "$(dirname "$0")/.."

echo "🚀 Stream Deck: Triggering deployment..."
echo "📦 Repository: $REPO"
echo "⚙️  Workflow: $WORKFLOW"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed!"
    echo "📥 Install with: brew install gh"
    echo "🔑 Then authenticate with: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI!"
    echo "🔑 Run: gh auth login"
    exit 1
fi

# Trigger the workflow
echo "⏳ Triggering workflow..."
gh workflow run "$WORKFLOW"

if [ $? -eq 0 ]; then
    echo "✅ Workflow triggered successfully!"
    echo ""
    echo "📊 View status:"
    echo "   gh run list --workflow=$WORKFLOW --limit 1"
    echo ""
    echo "🌐 View in browser:"
    echo "   https://github.com/$REPO/actions/workflows/deploy-static-site.yml"
    
    # Show notification (macOS)
    if command -v osascript &> /dev/null; then
        osascript -e "display notification \"Deployment workflow triggered\" with title \"jkcoukblog Deploy\" sound name \"Glass\""
    fi
    
    # Optional: Open GitHub Actions in browser
    # Uncomment the next line to automatically open the actions page
    # open "https://github.com/$REPO/actions/workflows/deploy-static-site.yml"
else
    echo "❌ Failed to trigger workflow!"
    exit 1
fi
