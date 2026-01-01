#!/bin/bash

###############################################################################
# HTML Cache Worker Deployment Script
#
# This script deploys the HTML caching worker to improve site performance
# by caching HTML at Cloudflare's edge.
#
# Usage:
#   ./deploy-cache-worker.sh [pages|worker]
#
# Options:
#   pages  - Deploy as Cloudflare Pages Function (recommended)
#   worker - Deploy as standalone Cloudflare Worker
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Deployment method (default to pages)
METHOD="${1:-pages}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}HTML Cache Worker Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

###############################################################################
# Deploy as Cloudflare Pages Function
###############################################################################
if [ "$METHOD" = "pages" ]; then
  echo -e "${GREEN}Deploying as Cloudflare Pages Function...${NC}"
  echo ""
  
  # Create functions directory if it doesn't exist
  if [ ! -d "functions" ]; then
    echo "📁 Creating functions directory..."
    mkdir -p functions
  fi
  
  # Copy worker to functions/_middleware.js
  echo "📄 Copying worker to functions/_middleware.js..."
  cp workers/html-cache.js functions/_middleware.js
  
  # Add to git
  echo "📝 Adding to git..."
  git add functions/_middleware.js
  
  # Show git status
  echo ""
  echo -e "${YELLOW}Git status:${NC}"
  git status --short functions/_middleware.js
  echo ""
  
  # Commit
  echo -e "${GREEN}✅ Ready to commit!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Review the changes: git diff functions/_middleware.js"
  echo "  2. Commit: git commit -m 'feat: Add HTML caching via Pages Function'"
  echo "  3. Push: git push"
  echo "  4. Cloudflare Pages will automatically deploy the function"
  echo ""
  echo "After deployment, test with:"
  echo "  curl -I https://jameskilby.co.uk/ | grep X-Worker-Cache"
  echo ""

###############################################################################
# Deploy as Standalone Worker
###############################################################################
elif [ "$METHOD" = "worker" ]; then
  echo -e "${GREEN}Deploying as standalone Cloudflare Worker...${NC}"
  echo ""
  
  # Check if wrangler is installed
  if ! command -v wrangler &> /dev/null; then
    echo -e "${RED}❌ Error: wrangler is not installed${NC}"
    echo ""
    echo "Install with: npm install -g wrangler"
    echo "Or use: npx wrangler"
    exit 1
  fi
  
  # Check if logged in
  echo "🔐 Checking Cloudflare authentication..."
  if ! wrangler whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Cloudflare${NC}"
    echo ""
    echo "Login with: wrangler login"
    exit 1
  fi
  
  echo -e "${GREEN}✅ Authenticated${NC}"
  echo ""
  
  # Deploy the worker
  echo "🚀 Deploying worker..."
  wrangler deploy workers/html-cache.js --name jkcoukblog-html-cache
  
  echo ""
  echo -e "${GREEN}✅ Worker deployed successfully!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Go to Cloudflare Dashboard"
  echo "  2. Navigate to: Workers & Pages → jkcoukblog-html-cache → Settings → Triggers"
  echo "  3. Add Route: jameskilby.co.uk/*"
  echo "  4. Zone: jameskilby.co.uk"
  echo "  5. Save"
  echo ""
  echo "After adding the route, test with:"
  echo "  curl -I https://jameskilby.co.uk/ | grep X-Worker-Cache"
  echo ""

###############################################################################
# Invalid option
###############################################################################
else
  echo -e "${RED}❌ Invalid deployment method: $METHOD${NC}"
  echo ""
  echo "Usage: $0 [pages|worker]"
  echo ""
  echo "Options:"
  echo "  pages  - Deploy as Cloudflare Pages Function (recommended)"
  echo "  worker - Deploy as standalone Cloudflare Worker"
  exit 1
fi

###############################################################################
# Show documentation
###############################################################################
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Documentation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📚 Full documentation: docs/HTML_CACHE_WORKER.md"
echo ""
echo "📊 Performance expectations:"
echo "  • TTFB: 320ms → ~50ms (85% improvement)"
echo "  • Total load: 665ms → ~200ms (70% improvement)"
echo "  • Cache hit ratio: 80-95% for typical traffic"
echo ""
echo "🔍 Monitoring:"
echo "  • Debug headers: X-Worker-Cache, X-Cache-Age"
echo "  • Cloudflare Analytics: Dashboard → Analytics → Traffic"
echo "  • Worker logs: wrangler tail jkcoukblog-html-cache"
echo ""
echo "🧹 Cache management:"
echo "  • Auto-expires: 5 minutes"
echo "  • Manual purge: curl -H 'X-Purge-Cache: true' https://jameskilby.co.uk/"
echo "  • Full purge: Cloudflare Dashboard → Caching → Purge Everything"
echo ""
echo -e "${GREEN}Deployment script complete!${NC}"
