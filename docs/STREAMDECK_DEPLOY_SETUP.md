# Stream Deck Deploy Button Setup

This guide walks you through setting up a Stream Deck button to trigger the GitHub Actions deployment workflow for jkcoukblog.

## Prerequisites

1. **GitHub CLI (gh)** - Required to trigger workflows
   ```bash
   brew install gh
   ```

2. **GitHub Authentication** - Authenticate with GitHub
   ```bash
   gh auth login
   ```
   - Select: GitHub.com
   - Select: HTTPS or SSH (your preference)
   - Authenticate with your browser or paste a token

3. **Verify Authentication**
   ```bash
   gh auth status
   ```

## Stream Deck Configuration

### Option 1: Execute Script (Recommended)

This option runs the script that triggers the deployment and shows a macOS notification.

1. **Add a Button** in Stream Deck
2. **Select Action**: System > Open
3. **Configure**:
   - **App/File**: `/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh`
   - **Title**: Deploy Site
   - **Icon**: Choose a rocket 🚀 or deploy icon
   
4. **Optional: Add Visual Feedback**
   - Go to button appearance settings
   - Add icon or text overlay
   - Consider using different states (normal/pressed)

### Option 2: Open Workflow Page (Simple)

This option just opens the GitHub Actions page in your browser where you can manually click "Run workflow".

1. **Add a Button** in Stream Deck
2. **Select Action**: System > Website
3. **Configure**:
   - **URL**: `https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml`
   - **Title**: Deploy Site
   - **Icon**: Choose a rocket 🚀 or deploy icon

### Option 3: Multi-Action Button (Advanced)

This option combines script execution with opening the browser to monitor progress.

1. **Add a Button** in Stream Deck
2. **Select Action**: Multi Action
3. **Add Actions**:
   - **Action 1**: System > Open
     - App/File: `/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh`
   - **Action 2**: System > Website
     - URL: `https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml`
     - Add 2 second delay before this action
   
4. **Configure**:
   - **Title**: Deploy & Monitor
   - **Icon**: Choose a rocket 🚀 or deploy icon

## Testing the Button

### Test the Script Manually

Before configuring Stream Deck, test that the script works:

```bash
/Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
```

Expected output:
```
🚀 Stream Deck: Triggering deployment...
📦 Repository: jameskilbynet/jkcoukblog
⚙️  Workflow: deploy-static-site.yml

⏳ Triggering workflow...
✅ Workflow triggered successfully!

📊 View status:
   gh run list --workflow=deploy-static-site.yml --limit 1

🌐 View in browser:
   https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml
```

You should also see a macOS notification.

### Test the Stream Deck Button

1. Press the button you configured
2. Check for the notification (if using Option 1 or 3)
3. Verify the workflow started at: https://github.com/jameskilbynet/jkcoukblog/actions

## Monitoring Deployment

### Via CLI

Check the latest workflow run:
```bash
gh run list --workflow=deploy-static-site.yml --limit 1
```

Watch the current run in real-time:
```bash
gh run watch
```

View detailed logs:
```bash
gh run view --log
```

### Via Browser

- **Actions Page**: https://github.com/jameskilbynet/jkcoukblog/actions
- **Workflow Page**: https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml
- **Production Site**: https://jameskilby.co.uk
- **Staging Site**: https://jkcoukblog.pages.dev

## Customization

### Auto-Open Browser

To automatically open the workflow page in your browser after triggering, edit the script:

```bash
nano /Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
```

Uncomment line 61:
```bash
# open "https://github.com/$REPO/actions/workflows/deploy-static-site.yml"
```

### Change Notification Sound

Edit line 56 to use a different macOS sound:
```bash
osascript -e "display notification \"Deployment workflow triggered\" with title \"jkcoukblog Deploy\" sound name \"Submarine\""
```

Available sounds: Glass, Submarine, Ping, Pop, Blow, Bottle, etc.
See all sounds: `ls /System/Library/Sounds/`

### Custom Icon

For a custom icon:
1. Find or create an icon (PNG, 72x72 or 144x144 recommended)
2. In Stream Deck software, click the button
3. Click the icon area in the property inspector
4. Select your custom icon file

## Troubleshooting

### "gh: command not found"

Install GitHub CLI:
```bash
brew install gh
```

### "Not authenticated with GitHub CLI"

Authenticate:
```bash
gh auth login
```

### "Failed to trigger workflow"

Check your permissions:
```bash
gh auth status
```

Ensure you have write access to the repository:
```bash
gh repo view jameskilbynet/jkcoukblog
```

### Button doesn't trigger anything

1. Check script permissions:
   ```bash
   ls -la /Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
   ```
   Should show: `-rwxr-xr-x` (executable)

2. Test script manually:
   ```bash
   /Users/w20kilja/Github/jkcoukblog/scripts/streamdeck-deploy.sh
   ```

3. Check Stream Deck logs:
   - Open Stream Deck software
   - Help > Show Logs

### No notification appears

Check notification permissions:
1. System Preferences > Notifications
2. Find "Script Editor" or "Terminal"
3. Ensure notifications are enabled

## What Happens When You Press the Button

1. **Workflow Triggered** - The GitHub Actions workflow starts
2. **Notification** - macOS shows a notification (Option 1 & 3)
3. **Build Process** (~5-15 minutes):
   - Spell check (optional, non-blocking)
   - Generate static site from WordPress
   - Validate HTML and assets
   - Optimize images (PNG, JPEG → AVIF, WebP)
   - Compress with Brotli
   - Commit to `public/` directory
   - Submit URLs to IndexNow
4. **Cloudflare Deploy** (~1-2 minutes):
   - Cloudflare Pages detects changes to `public/`
   - Automatically deploys to staging and production
5. **Site Live** - https://jameskilby.co.uk updated

Total time: **6-20 minutes** depending on content changes.

## Related Documentation

- **WARP.md** - Complete project documentation
- **deploy-static-site.yml** - GitHub Actions workflow file
- **README.md** - Project overview

## Support

If you encounter issues:
1. Check the script output manually
2. Review GitHub Actions logs
3. Verify GitHub CLI authentication
4. Check Stream Deck logs
