#!/usr/bin/env python3
"""
Test script to verify Plausible analytics integration in the static site generator
"""

from bs4 import BeautifulSoup
import sys
import os

# Add the current directory to path to import the generator
sys.path.insert(0, os.path.dirname(__file__))
from wp_to_static_generator import WordPressStaticGenerator

def test_plausible_injection():
    """Test that Plausible analytics is properly injected"""
    
    # Create a test generator instance
    generator = WordPressStaticGenerator(
        wp_url='https://wordpress.jameskilby.cloud',
        auth_token='test_token',
        output_dir='./test_output',
        target_domain='https://jameskilby.co.uk'
    )
    
    print("🧪 Testing Plausible Analytics Integration\n")
    
    # Test Case 1: HTML without Plausible
    print("Test 1: Adding Plausible to HTML without existing analytics...")
    html_without_plausible = """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Test</h1>
        </body>
    </html>
    """
    soup1 = BeautifulSoup(html_without_plausible, 'html.parser')
    generator.add_plausible_analytics(soup1)
    
    plausible_script = soup1.find('script', src=lambda x: x and 'plausible' in x)
    if plausible_script:
        print("✅ Plausible script added successfully")
        print(f"   - src: {plausible_script.get('src')}")
        print(f"   - data-domain: {plausible_script.get('data-domain')}")
        print(f"   - defer: {plausible_script.get('defer')}")
    else:
        print("❌ Failed to add Plausible script")
        return False
    
    print()
    
    # Test Case 2: HTML with existing Plausible (should update)
    print("Test 2: Updating existing Plausible configuration...")
    html_with_plausible = """
    <html>
        <head>
            <title>Test Page</title>
            <script defer="" src="https://plausible.jameskilby.cloud/js/script.js" data-domain="wrong-domain.com"></script>
        </head>
        <body>
            <h1>Test</h1>
        </body>
    </html>
    """
    soup2 = BeautifulSoup(html_with_plausible, 'html.parser')
    generator.add_plausible_analytics(soup2)
    
    plausible_scripts = soup2.find_all('script', src=lambda x: x and 'plausible' in x)
    if len(plausible_scripts) == 1:
        print("✅ Existing Plausible script updated (no duplicates)")
        print(f"   - data-domain corrected to: {plausible_scripts[0].get('data-domain')}")
        if plausible_scripts[0].get('data-domain') == 'jameskilby.co.uk':
            print("✅ Domain correctly set to jameskilby.co.uk")
        else:
            print(f"❌ Domain incorrect: {plausible_scripts[0].get('data-domain')}")
            return False
    else:
        print(f"❌ Duplicate scripts found: {len(plausible_scripts)}")
        return False
    
    print()
    
    # Test Case 3: HTML without head (edge case)
    print("Test 3: Handling HTML without <head> tag...")
    html_no_head = """
    <html>
        <body>
            <h1>Test</h1>
        </body>
    </html>
    """
    soup3 = BeautifulSoup(html_no_head, 'html.parser')
    generator.add_plausible_analytics(soup3)
    print("✅ No error when <head> is missing")
    
    print()
    print("=" * 60)
    print("✅ All tests passed! Plausible analytics integration is working correctly.")
    return True

if __name__ == '__main__':
    success = test_plausible_injection()
    sys.exit(0 if success else 1)
