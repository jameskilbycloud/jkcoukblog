#!/bin/bash
#
# Deploy to Staging Helper Script
# 
# Opens the GitHub Actions page for the staging workflow
# GitHub CLI has a caching issue, so use the web UI until it clears
#

echo "🎭 Opening staging deployment workflow..."
echo ""
echo "Instructions:"
echo "1. Click the 'Run workflow' button (green button on the right)"
echo "2. Confirm by clicking 'Run workflow' again"
echo "3. Wait 2-3 minutes for deployment"
echo "4. Visit https://jkcoukblog.pages.dev to see your changes"
echo ""

# Open the workflow page
open "https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-staging-site.yml"

echo ""
echo "📊 To monitor the deployment:"
echo "   gh run list --workflow=deploy-staging-site.yml --limit 1"
echo ""
echo "   Or watch in real-time:"
echo "   gh run watch"
