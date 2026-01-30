# Stream Deck Deploy Button

**One-click deployment for jkcoukblog static site!**

This folder contains everything you need to set up a Stream Deck button that triggers the GitHub Actions workflow to deploy your static site.

## 📁 Files

- **`streamdeck-deploy.sh`** - The deployment script (in `scripts/` folder)
- **`STREAMDECK_DEPLOY_SETUP.md`** - Complete setup guide with all options
- **`STREAMDECK_QUICK_REFERENCE.md`** - Quick setup and troubleshooting
- **`streamdeck-deploy-icon.svg`** - Custom icon for your button (in `docs/assets/`)

## 🚀 Quick Start

### Prerequisites
```bash
# Install GitHub CLI (if not already installed)
brew install gh

# Authenticate with GitHub
gh auth login
```

### Stream Deck Setup
1. Open Stream Deck software
2. Drag **"Open"** action to a button
3. Set **App/File** to:
   ```
   /Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
   ```
4. Add title: **"Deploy Site"**
5. Optionally add the custom icon from `docs/assets/streamdeck-deploy-icon.svg`
6. **Done!** Press the button to deploy.

### Test Before Using
```bash
/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
```

## 📚 Documentation

- **Full Setup Guide**: `STREAMDECK_DEPLOY_SETUP.md` - All setup options, customization, and troubleshooting
- **Quick Reference**: `STREAMDECK_QUICK_REFERENCE.md` - One-page cheat sheet

## 🎯 What It Does

When you press the Stream Deck button:

1. ✅ Triggers GitHub Actions workflow
2. 🔔 Shows macOS notification
3. 🏗️ Builds static site (5-15 min)
4. 🖼️ Optimizes images (AVIF, WebP)
5. 📦 Commits to repository
6. 🌐 Cloudflare auto-deploys (1-2 min)
7. ✨ **Site live** at https://jameskilby.co.uk

**Total time: 6-20 minutes**

## 🔍 Monitor Progress

**Command Line**:
```bash
# View latest workflow run
gh run list --workflow=deploy-static-site.yml --limit 1

# Watch live
gh run watch
```

**Browser**:
- Actions: https://github.com/jameskilbynet/jkcoukblog/actions
- Production: https://jameskilby.co.uk
- Staging: https://jkcoukblog.pages.dev

## 💡 Tips

- **Multi-Action Button**: Combine script execution + opening Actions page
- **Auto-Open Browser**: Uncomment line 61 in the script
- **Custom Notification**: Edit line 56 for different sound
- **Keyboard Shortcut**: Use the script with Automator/BetterTouchTool

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Button doesn't work | Test script manually first |
| No GitHub CLI | `brew install gh` |
| Not authenticated | `gh auth login` |
| No notification | Check System Preferences > Notifications |

See `STREAMDECK_DEPLOY_SETUP.md` for detailed troubleshooting.

## 🔗 Related

- **Main Project Docs**: `docs/archive/WARP.md`
- **GitHub Actions**: `.github/workflows/deploy-static-site.yml`
- **Common Commands**: See WARP.md for all deployment commands

---

**Status**: ✅ Ready to use (GitHub CLI installed & authenticated)

**Created**: 2026-01-30
