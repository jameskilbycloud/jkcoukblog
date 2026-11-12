# Stream Deck Deploy Button - Quick Reference

## 🚀 Quick Setup (Recommended Method)

1. **Open Stream Deck Software**
2. **Drag "Open" action** onto a button
3. **Configure**:
   - **App/File**: `/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh`
   - **Title**: `Deploy`
   - **Icon**: 🚀 (or custom icon)
4. **Press the button** to deploy!

---

## 📋 One-Liner Test

Test the deployment script before adding to Stream Deck:
```bash
/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
```

---

## 🔗 Alternative: Direct URL Button

If you prefer to open the GitHub Actions page and click "Run workflow" manually:

1. **Drag "Website" action** onto a button
2. **URL**: `https://github.com/jameskilbycloud/jkcoukblog/actions/workflows/deploy-static-site.yml`
3. **Title**: `Deploy`

---

## 📊 Monitor Deployment

**GitHub Actions Page**:
- https://github.com/jameskilbycloud/jkcoukblog/actions

**View Latest Run**:
```bash
gh run list --workflow=deploy-static-site.yml --limit 1
```

**Watch Live**:
```bash
gh run watch
```

---

## ⏱️ Deployment Timeline

1. Press button → Workflow triggered (instant)
2. Build & optimize (5-15 min)
3. Cloudflare deploy (1-2 min)
4. **Site live!** → https://jameskilby.co.uk

**Total: 6-20 minutes**

---

## 🎨 Recommended Button Appearance

- **Title**: "Deploy Site" or "🚀 Deploy"
- **Icon**: Rocket emoji or GitHub Actions icon
- **Background**: Blue/Green gradient
- **Font**: Bold, white text

---

## ⚡ Keyboard Shortcut (Bonus)

Create a macOS keyboard shortcut using Automator or BetterTouchTool:
```bash
/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
```

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| Button does nothing | Test script manually: `/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh` |
| "gh not found" | Run: `brew install gh` |
| "Not authenticated" | Run: `gh auth login` |
| No notification | Check System Preferences > Notifications > Terminal |

---

## 📚 Full Documentation

See `docs/STREAMDECK_DEPLOY_SETUP.md` for complete setup instructions.
