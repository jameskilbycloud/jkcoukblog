#!/usr/bin/env python3
"""
Test script to verify the self-hosted runner environment
"""

import sys
import os
from pathlib import Path

def test_environment():
    """Test the runner environment setup"""
    print("🔍 SELF-HOSTED RUNNER ENVIRONMENT TEST")
    print("=" * 50)
    
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📄 Python executable: {sys.executable}")
    
    print("\n📋 Files in current directory:")
    current_dir = Path(".")
    for file in sorted(current_dir.iterdir()):
        if file.is_file():
            print(f"   📄 {file.name}")
        elif file.is_dir() and not file.name.startswith('.'):
            print(f"   📁 {file.name}/")
    
    print("\n🔍 Looking for required files:")
    required_files = [
        "wp_to_static_generator.py",
        ".github/workflows/deploy-static-site.yml"
    ]
    
    all_present = True
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NOT FOUND")
            all_present = False
    
    print("\n🔧 Testing Python imports:")
    try:
        import requests
        print(f"   ✅ requests: {requests.__version__}")
    except ImportError:
        print("   ❌ requests - NOT INSTALLED")
        all_present = False
    
    try:
        import bs4
        print(f"   ✅ beautifulsoup4: {bs4.__version__}")
    except ImportError:
        print("   ❌ beautifulsoup4 - NOT INSTALLED") 
        all_present = False
    
    print("\n🔐 Environment variables:")
    wp_token = os.getenv('WP_AUTH_TOKEN')
    if wp_token:
        print(f"   ✅ WP_AUTH_TOKEN: {'*' * len(wp_token[:10])}... (present)")
    else:
        print("   ⚠️  WP_AUTH_TOKEN: NOT SET (will need to be set by GitHub Actions)")
    
    print("\n" + "=" * 50)
    if all_present:
        print("🎉 ENVIRONMENT TEST: PASSED")
        print("   The runner environment looks good!")
    else:
        print("❌ ENVIRONMENT TEST: FAILED") 
        print("   Some required components are missing")
    
    return all_present

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)