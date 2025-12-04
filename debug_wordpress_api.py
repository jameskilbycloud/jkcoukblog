#!/usr/bin/env python3
"""
Debug script to test WordPress REST API responses
"""
import os
import requests
import json

WP_URL = 'https://wordpress.jameskilby.cloud'
AUTH_TOKEN = os.getenv('WP_AUTH_TOKEN')

if not AUTH_TOKEN:
    print('❌ WP_AUTH_TOKEN environment variable not set')
    print('   Set it with: export WP_AUTH_TOKEN="your_token"')
    exit(1)

session = requests.Session()
session.headers.update({
    'Authorization': f'Basic {AUTH_TOKEN}',
    'User-Agent': 'StaticSiteGenerator/1.0'
})

print(f"🔍 Testing WordPress REST API: {WP_URL}")
print("=" * 60)

# Test posts endpoint
print("\n📄 Testing Posts Endpoint...")
page = 1
total_posts = 0
zfs_found = False

while True:
    print(f"\n  Page {page}:")
    response = session.get(
        f'{WP_URL}/wp-json/wp/v2/posts',
        params={'per_page': 100, 'page': page, 'status': 'publish', '_fields': 'id,link,title,slug,date'}
    )
    
    print(f"    Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"    Error response: {response.text[:200]}")
        break
    
    posts = response.json()
    if not posts:
        break
    
    print(f"    Found {len(posts)} posts")
    total_posts += len(posts)
    
    # Check for ZFS post
    for post in posts:
        if 'zfs' in post['slug'].lower():
            print(f"    ✅ FOUND ZFS POST: {post['slug']}")
            print(f"       Title: {post['title']['rendered']}")
            print(f"       Link: {post['link']}")
            print(f"       Date: {post['date']}")
            zfs_found = True
    
    page += 1
    
    # Safety limit
    if page > 10:
        print("    ⚠️  Reached page limit (10), stopping")
        break

print(f"\n📊 Summary:")
print(f"   Total posts discovered: {total_posts}")
print(f"   ZFS post found: {'✅ YES' if zfs_found else '❌ NO'}")

# Also test direct access to the ZFS post
print(f"\n🔍 Testing direct access to ZFS post...")
zfs_response = session.get(f'{WP_URL}/2024/12/zfs-on-vmware/')
print(f"   Status: {zfs_response.status_code}")
print(f"   Content-Type: {zfs_response.headers.get('content-type', 'N/A')}")

if zfs_response.status_code == 200:
    # Check if it's the right page
    if 'post-6247' in zfs_response.text or 'ZFS on VMware' in zfs_response.text:
        print(f"   ✅ Direct access works - page content found")
    else:
        print(f"   ⚠️  Got 200 but content seems wrong")
