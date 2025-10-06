#!/bin/bash
# GitHub URL verification script

if [ $# -eq 0 ]; then
    echo "Usage: $0 <github_repo_url>"
    exit 1
fi

URL="$1"
echo "🔍 Verifying GitHub repository URL..."
echo "URL: $URL"
echo

# Extract repository name from URL
REPO_NAME=$(echo "$URL" | sed 's/.*\/\([^/]*\)\.git.*/\1/')
LOCAL_DIR=$(basename "$PWD")

echo "📋 Verification checks:"
echo

# Check 1: Repository name matches local directory
if [ "$REPO_NAME" = "$LOCAL_DIR" ]; then
    echo "✅ Repository name matches local directory: $REPO_NAME"
else
    echo "⚠️  Repository name mismatch:"
    echo "   Local directory: $LOCAL_DIR"
    echo "   GitHub repository: $REPO_NAME"
    echo "   This might cause confusion later"
fi

# Check 2: Test if repository exists
echo
echo "🌐 Testing repository accessibility..."
if curl -s --head "$URL" | head -n 1 | grep -q "200 OK"; then
    echo "✅ Repository exists and is accessible"
elif curl -s --head "${URL%%.git}" | head -n 1 | grep -q "200 OK"; then
    echo "✅ Repository exists and is accessible"
else
    echo "❌ Repository not found or not accessible"
    echo "   Make sure you've created the repository on GitHub"
    echo "   Check for typos in the URL"
fi

# Check 3: Common typo detection
echo
echo "🔤 Common typo check:"
COMMON_TYPOS="jkcoukbog jkcoukblog"
for typo in $COMMON_TYPOS; do
    if echo "$URL" | grep -q "$typo"; then
        if [ "$typo" = "jkcoukbog" ]; then
            echo "⚠️  Possible typo detected: 'jkcoukbog' (missing 'l' in 'blog')"
            echo "   Should it be: jkcoukblog?"
        else
            echo "✅ Repository name looks correct: $typo"
        fi
    fi
done

echo
echo "🎯 If everything looks good, run:"
echo "./setup_github_remote.sh \"$URL\""