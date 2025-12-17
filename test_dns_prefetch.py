#!/usr/bin/env python3
"""Test DNS prefetch and preconnect additions for analytics"""

from bs4 import BeautifulSoup

# Sample HTML
html = """
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

soup = BeautifulSoup(html, 'html.parser')

# Simulate the add_plausible_analytics method logic
plausible_domain = 'plausible.jameskilby.cloud'
plausible_script_url = f'https://{plausible_domain}/js/script.js'
target_analytics_domain = 'jameskilby.co.uk'

print('Before modifications:')
print('=' * 60)
print(soup.head.prettify())

# Add DNS prefetch
existing_dns_prefetch = soup.find('link', rel='dns-prefetch', href=f'//{plausible_domain}')
if not existing_dns_prefetch:
    dns_prefetch = soup.new_tag('link')
    dns_prefetch['rel'] = 'dns-prefetch'
    dns_prefetch['href'] = f'//{plausible_domain}'
    soup.head.insert(0, dns_prefetch)
    print(f"✅ Added DNS prefetch for {plausible_domain}")

# Add preconnect
existing_preconnect = soup.find('link', rel='preconnect', href=f'https://{plausible_domain}')
if not existing_preconnect:
    preconnect = soup.new_tag('link')
    preconnect['rel'] = 'preconnect'
    preconnect['href'] = f'https://{plausible_domain}'
    preconnect['crossorigin'] = ''
    soup.head.insert(1, preconnect)
    print(f"✅ Added preconnect for {plausible_domain}")

# Add Plausible script
existing_plausible = soup.find('script', src=lambda x: x and 'plausible' in x and 'script.js' in x)
if not existing_plausible:
    plausible_script = soup.new_tag('script')
    plausible_script['data-domain'] = target_analytics_domain
    plausible_script['defer'] = ''
    plausible_script['src'] = plausible_script_url
    soup.head.append(plausible_script)
    print(f"✅ Added Plausible analytics script")

print('\n' + '=' * 60)
print('After modifications:')
print('=' * 60)
print(soup.head.prettify())

# Verify order
print('\n' + '=' * 60)
print('Verification:')
print('=' * 60)

head_children = list(soup.head.children)
link_elements = [child for child in head_children if child.name == 'link']

print(f"Total link elements: {len(link_elements)}")
for idx, link in enumerate(link_elements):
    rel = link.get('rel', [''])[0] if isinstance(link.get('rel'), list) else link.get('rel', '')
    href = link.get('href', '')
    print(f"  Link {idx + 1}: rel='{rel}' href='{href}'")

# Check dns-prefetch
dns_prefetch_check = soup.find('link', rel='dns-prefetch')
if dns_prefetch_check:
    print(f"\n✅ DNS prefetch found: {dns_prefetch_check.get('href')}")
else:
    print("\n❌ DNS prefetch NOT found")

# Check preconnect
preconnect_check = soup.find('link', rel='preconnect')
if preconnect_check:
    print(f"✅ Preconnect found: {preconnect_check.get('href')}")
    if preconnect_check.get('crossorigin') is not None:
        print("✅ Crossorigin attribute present")
else:
    print("❌ Preconnect NOT found")

# Check Plausible script
script_check = soup.find('script', {'data-domain': target_analytics_domain})
if script_check:
    print(f"✅ Plausible script found: {script_check.get('src')}")
    print(f"   data-domain: {script_check.get('data-domain')}")
    if script_check.get('defer') is not None:
        print("✅ Defer attribute present")
else:
    print("❌ Plausible script NOT found")
