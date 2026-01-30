#!/usr/bin/env python3
"""
Enable search engine indexing for Cloudflare Pages project.

This script uses the Cloudflare API to disable the "Disable Indexing" setting
which adds X-Robots-Tag: noindex headers that block search engines.

Requirements:
- CLOUDFLARE_API_TOKEN environment variable
- CLOUDFLARE_ACCOUNT_ID environment variable (or passed as argument)
"""

import os
import sys
import requests
import json


def get_account_id(api_token):
    """Retrieve the Cloudflare account ID"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://api.cloudflare.com/client/v4/accounts",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch accounts: {response.text}")
        return None
    
    data = response.json()
    if data.get("success") and data.get("result"):
        # Return the first account ID
        account_id = data["result"][0]["id"]
        account_name = data["result"][0]["name"]
        print(f"✅ Found account: {account_name} ({account_id})")
        return account_id
    
    return None


def get_pages_project(api_token, account_id, project_name="jkcoukblog"):
    """Get the Pages project details"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch project: {response.text}")
        return None
    
    data = response.json()
    if data.get("success"):
        print(f"✅ Found project: {project_name}")
        return data["result"]
    
    return None


def enable_indexing(api_token, account_id, project_name="jkcoukblog"):
    """Enable search engine indexing for the Pages project"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # The API endpoint to update project settings
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}"
    
    # Payload to disable the "Disable Indexing" setting
    # Setting disable_search_engine_indexing to false enables indexing
    payload = {
        "deployment_configs": {
            "production": {
                "disable_search_engine_indexing": False
            },
            "preview": {
                "disable_search_engine_indexing": False
            }
        }
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ Successfully enabled search engine indexing!")
            print("   Production environment: Indexing ENABLED")
            print("   Preview environment: Indexing ENABLED")
            return True
        else:
            print(f"❌ API returned success=false: {data}")
            return False
    else:
        print(f"❌ Failed to update project settings (HTTP {response.status_code})")
        print(f"   Response: {response.text}")
        return False


def main():
    print("🔧 Cloudflare Pages Indexing Enabler")
    print("=" * 50)
    
    # Get API token from environment
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not api_token:
        print("❌ Error: CLOUDFLARE_API_TOKEN environment variable not set")
        print("   Export it with: export CLOUDFLARE_API_TOKEN='your-token-here'")
        sys.exit(1)
    
    print("✓ API token found")
    
    # Get account ID
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not account_id:
        print("🔍 Fetching account ID...")
        account_id = get_account_id(api_token)
        if not account_id:
            print("❌ Could not determine account ID")
            print("   Please set CLOUDFLARE_ACCOUNT_ID environment variable")
            sys.exit(1)
    else:
        print(f"✓ Account ID: {account_id}")
    
    # Get project name from arguments or use default
    project_name = sys.argv[1] if len(sys.argv) > 1 else "jkcoukblog"
    print(f"📦 Target project: {project_name}")
    print()
    
    # Get current project settings
    print("📋 Checking current project settings...")
    project = get_pages_project(api_token, account_id, project_name)
    
    if project:
        # Check current indexing status
        prod_config = project.get("deployment_configs", {}).get("production", {})
        is_disabled = prod_config.get("disable_search_engine_indexing", False)
        
        print(f"   Current status: {'❌ Indexing DISABLED' if is_disabled else '✅ Indexing ENABLED'}")
        print()
        
        if not is_disabled:
            print("ℹ️  Indexing is already enabled. No changes needed.")
            sys.exit(0)
    
    # Enable indexing
    print("🚀 Enabling search engine indexing...")
    success = enable_indexing(api_token, account_id, project_name)
    
    if success:
        print()
        print("=" * 50)
        print("✅ SUCCESS!")
        print()
        print("Next steps:")
        print("1. Deploy your site to apply the changes")
        print("2. Verify X-Robots-Tag header is removed:")
        print("   curl -I https://jameskilby.co.uk")
        print("3. Submit your sitemap to search engines:")
        print("   https://jameskilby.co.uk/sitemap.xml")
        sys.exit(0)
    else:
        print()
        print("❌ Failed to enable indexing")
        sys.exit(1)


if __name__ == "__main__":
    main()
