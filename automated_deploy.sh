#!/bin/bash
# Automated WordPress to Static Site Deployment
# Add to cron with: 0 6,18 * * * /path/to/this/script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/static-output"
LOG_FILE="$SCRIPT_DIR/deploy.log"

echo "🚀 Starting automated deployment at $(date)" >> "$LOG_FILE"

cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "wordpress_spellcheck_env" ]; then
    source wordpress_spellcheck_env/bin/activate
fi

# Generate static site
python wp_to_static_generator.py "$OUTPUT_DIR" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Static site generation successful at $(date)" >> "$LOG_FILE"
    
    # Deploy (customize this section for your deployment target)
    python deploy_static_site.py "$OUTPUT_DIR" --cloudflare jameskilby-co-uk >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Deployment successful at $(date)" >> "$LOG_FILE"
    else
        echo "❌ Deployment failed at $(date)" >> "$LOG_FILE"
    fi
else
    echo "❌ Static site generation failed at $(date)" >> "$LOG_FILE"
fi

echo "📝 Log file: $LOG_FILE"
