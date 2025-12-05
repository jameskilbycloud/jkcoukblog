# Ollama Spell Checker - Quick Start

## ✅ Setup Complete!

Your Ollama-powered spell checker is ready to use!

## Quick Test

```bash
# Make sure your auth token is set
export WP_AUTH_TOKEN="your_token_here"

# Run a quick test on your most recent post
./ollama_spell_checker.py 1
```

## Daily Workflow

### Before Publishing

1. **Write your post** in WordPress
2. **Run spell checker**:
   ```bash
   ./ollama_spell_checker.py 1
   ```
3. **Review the report**: `spelling_check_report.md`
4. **Fix any errors** in WordPress
5. **Re-check** if needed
6. **Publish** the post

### Weekly Content Audit

```bash
# Check last 10 posts
./ollama_spell_checker.py 10
```

## What It Checks

✅ Spelling errors  
✅ Grammar issues  
✅ Obvious typos  
❌ Ignores technical terms (VMware, Kubernetes, etc.)

## Example Output

```
🚀 Ollama Spell Checker
Ollama: https://ollama.jameskilby.cloud
WordPress: https://wordpress.jameskilby.cloud
Model: llama3.2:latest
============================================================

🔍 Checking 1 most recent posts...
📄 Checking post ID: 7127
   Title: How I upgraded my blog...
   URL: https://wordpress.jameskilby.cloud/...
   Found 15 text sections to check
   🔍 Checking title...
   🔍 Checking description...
   🔍 Checking paragraph_1...
   🔍 Checking paragraph_2...
      ⚠️  spelling: recieve → receive

============================================================
📊 Report saved to: spelling_check_report.md

⚠️  Spelling errors found! Please review the report.
```

## Configuration

### Change Ollama Model

```bash
export OLLAMA_MODEL="llama3.2:3b"  # Use smaller model
export OLLAMA_MODEL="qwen2.5:latest"  # Use different model
```

### Check Different WordPress

```bash
export WP_URL="https://your-other-wordpress.com"
```

## Troubleshooting

### Can't Connect to Ollama

```bash
# Test connection
curl https://ollama.jameskilby.cloud/api/tags

# If you get 401, you may need to add authentication
# (Currently the script assumes no auth for Ollama)
```

### Can't Connect to WordPress

```bash
# Verify your token
curl -H "Authorization: Basic $WP_AUTH_TOKEN" \
  https://wordpress.jameskilby.cloud/wp-json/wp/v2/posts?per_page=1
```

### Script is Slow

- Each post takes ~30-60 seconds
- Ollama processing time depends on model size and server load
- Check fewer posts: `./ollama_spell_checker.py 1`

## Integration with Deployment

### Manual Check Before Deploy

```bash
# Check recent posts
./ollama_spell_checker.py 5

# If clean, deploy
if [ $? -eq 0 ]; then
    ./wp_to_static_generator.py ./public
fi
```

### Automated GitHub Actions

See `OLLAMA_SPELL_CHECKER.md` for full GitHub Actions workflow example.

## Key Features

| Feature | Description |
|---------|-------------|
| **AI-Powered** | Uses your Ollama LLM |
| **Technical Aware** | Knows VMware, Kubernetes, etc. |
| **Context-Sensitive** | Understands blog content |
| **Detailed Reports** | Markdown format with all errors |
| **WordPress Direct** | Checks via API, no manual export |
| **Exit Codes** | Use in scripts and CI/CD |

## Files Created

- ✅ `ollama_spell_checker.py` - Main script
- ✅ `OLLAMA_SPELL_CHECKER.md` - Full documentation  
- ✅ `SPELL_CHECKER_QUICKSTART.md` - This file
- 📄 `spelling_check_report.md` - Generated report (gitignored)

## Next Steps

1. **Test it now**: `./ollama_spell_checker.py 1`
2. **Review the report**
3. **Integrate into your workflow**
4. **Consider adding to GitHub Actions**

## Support

For detailed documentation, see: `OLLAMA_SPELL_CHECKER.md`

For questions about:
- WordPress API: Check your auth token
- Ollama connection: Verify `ollama.jameskilby.cloud` is accessible
- Script behavior: See full documentation
