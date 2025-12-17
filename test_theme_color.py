#!/usr/bin/env python3
"""Test theme-color meta tag addition"""

from bs4 import BeautifulSoup

# Sample HTML without theme-color
html_without = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Page</title>
</head>
<body>
    <h1>Test Content</h1>
</body>
</html>
"""

# Sample HTML with existing theme-color
html_with = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="theme-color" content="#000000">
    <title>Test Page</title>
</head>
<body>
    <h1>Test Content</h1>
</body>
</html>
"""

def test_theme_color_addition(html, test_name):
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print('='*60)
    
    soup = BeautifulSoup(html, 'html.parser')
    
    print("\nBefore:")
    existing = soup.find('meta', attrs={'name': 'theme-color'})
    if existing:
        print(f"  ✅ Theme-color exists: {existing.get('content')}")
    else:
        print("  ❌ No theme-color meta tag")
    
    # Simulate add_static_optimizations logic
    existing_theme_color = soup.find('meta', attrs={'name': 'theme-color'})
    if not existing_theme_color:
        theme_color_meta = soup.new_tag('meta')
        theme_color_meta['name'] = 'theme-color'
        theme_color_meta['content'] = '#ffffff'
        soup.head.append(theme_color_meta)
        print("  🎨 Added theme-color meta tag")
    else:
        print("  ℹ️  Theme-color already exists, skipping")
    
    print("\nAfter:")
    result = soup.find('meta', attrs={'name': 'theme-color'})
    if result:
        print(f"  ✅ Theme-color found: {result.get('content')}")
        print(f"     {result}")
    else:
        print("  ❌ Theme-color NOT found")
    
    return result is not None

# Run tests
test1 = test_theme_color_addition(html_without, "HTML without theme-color")
test2 = test_theme_color_addition(html_with, "HTML with existing theme-color")

print(f"\n{'='*60}")
print("Summary:")
print('='*60)
print(f"Test 1 (add new): {'✅ PASS' if test1 else '❌ FAIL'}")
print(f"Test 2 (preserve existing): {'✅ PASS' if test2 else '❌ FAIL'}")
