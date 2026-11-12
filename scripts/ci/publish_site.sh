#!/usr/bin/env bash
# Commit build caches to main and publish ./public to the site branch as one parentless commit.
#
# Run by the "Commit and push static site" step of .github/workflows/deploy-static-site.yml,
# which supplies the environment. Moved out of the workflow verbatim so it
# can be linted and tested.
set -e   # same as a default Actions run: step (bash -e)

# 1) Build state that stays on main: the image-optimisation cache is
#    an input to the next build, not site output. Small, and only
#    committed when it actually changed.
git add .image_optimization_cache/ .indexnow_key 2>/dev/null || true
if [ -n "$(git diff --cached)" ]; then
  git commit -m "chore(build): update build caches - $(date '+%Y-%m-%d %H:%M:%S')"
  if ! git push origin HEAD:main; then
    echo "⚠️  Push to main failed, rebasing and retrying..."
    git fetch origin main
    if ! { git rebase origin/main && git push origin HEAD:main; }; then
      git rebase --abort 2>/dev/null || true
      echo "⚠️  Build-cache commit not pushed (non-fatal — next build re-optimises the missing entries)"
    fi
  fi
fi

# 2) The site itself: public/ as a single parentless commit on the
#    site branch. A throwaway index keeps it out of main's index;
#    -f because public/ is gitignored on main.
export GIT_INDEX_FILE="$RUNNER_TEMP/site-index"
rm -f "$GIT_INDEX_FILE"
git add -f public/
NEW_TREE=$(git write-tree)
unset GIT_INDEX_FILE

if [ -n "$PREV_SITE_SHA" ] && [ "$NEW_TREE" = "$(git rev-parse "$PREV_SITE_SHA^{tree}")" ]; then
  echo "ℹ️  No changes to commit"
  echo "" >> $GITHUB_STEP_SUMMARY
  echo "## ℹ️ Deployment Summary" >> $GITHUB_STEP_SUMMARY
  echo "" >> $GITHUB_STEP_SUMMARY
  echo "- **Status:** No changes detected" >> $GITHUB_STEP_SUMMARY
  echo "- **Note:** Site is already up to date" >> $GITHUB_STEP_SUMMARY
  # Signal to the KV-purge step that nothing new is on its way — no
  # need to poll Cloudflare for a new deployment.
  echo "pushed_sha=" >> $GITHUB_OUTPUT
  exit 0
fi

# Diff size, captured before the commit. A build that rewrites ~1500
# files instead of ~20 is the shape the WP-Optimize timestamp churn
# took (every page rewritten for zero content change), and it was only
# ever visible by reading `git log --stat` after the fact.
PREV_TREE=$(git hash-object -t tree /dev/null)
if [ -n "$PREV_SITE_SHA" ]; then PREV_TREE=$(git rev-parse "$PREV_SITE_SHA^{tree}"); fi
DIFF_STAT=$(git diff --shortstat "$PREV_TREE" "$NEW_TREE" | sed 's/^ *//')
DIFF_FILES=$(git diff --name-only "$PREV_TREE" "$NEW_TREE" | wc -l | tr -d ' ')
echo "diff_stat=${DIFF_STAT:-none}" >> $GITHUB_OUTPUT
echo "diff_files=${DIFF_FILES}" >> $GITHUB_OUTPUT
echo "📊 Diff: ${DIFF_STAT}"

echo "📝 Changes detected, committing..."
PUSHED_SHA=$(git commit-tree "$NEW_TREE" -m "🚀 Static site - $(date '+%Y-%m-%d %H:%M:%S') (main@${GITHUB_SHA:0:7})")

# Parentless commit, so this is always a force-push. The lease pins
# it to the site commit this build seeded from: if anything else
# published in between, fail rather than silently overwrite it.
echo "📤 Pushing to site branch..."
if ! git push --force-with-lease="refs/heads/site:${PREV_SITE_SHA}" origin "$PUSHED_SHA:refs/heads/site"; then
  echo "❌ site branch moved since this build started — failing for manual review"
  exit 1
fi

# The SHA we pushed is what Cloudflare Pages creates a deployment for
# — the KV-purge step polls for it. Not $GITHUB_SHA, which is a main
# commit Pages never deploys.
echo "pushed_sha=$PUSHED_SHA" >> $GITHUB_OUTPUT
echo "📌 Pushed commit: $PUSHED_SHA"

echo "✅ Static site updated successfully"
echo "" >> $GITHUB_STEP_SUMMARY
echo "## 🚀 Deployment Summary" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "- **Status:** ✅ Successfully deployed" >> $GITHUB_STEP_SUMMARY
echo "- **Commit:** site@${PUSHED_SHA:0:7} (built from main@${GITHUB_SHA:0:7})" >> $GITHUB_STEP_SUMMARY
echo "- **Cloudflare Pages:** Will auto-deploy from the site branch" >> $GITHUB_STEP_SUMMARY
