#!/usr/bin/env python3
"""
Verify Spelling Corrections
Checks if spelling corrections from a corrections file were actually applied to WordPress
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List
from bs4 import BeautifulSoup

def load_corrections(filename: str) -> List[Dict]:
    """Load corrections from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in: {filename}")
        sys.exit(1)

def fetch_post_content(wp_url: str, auth_token: str, post_id: int) -> Dict:
    """Fetch current post content from WordPress"""
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Basic {auth_token}',
        'User-Agent': 'SpellChecker/1.0'
    })
    
    try:
        response = session.get(f'{wp_url}/wp-json/wp/v2/posts/{post_id}')
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch post {post_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching post {post_id}: {str(e)}")
        return None

def extract_text_from_post(post: Dict) -> Dict[str, str]:
    """Extract text from different post sections"""
    from html import unescape
    
    texts = {}
    
    # Title
    title = post.get('title', {}).get('rendered', '')
    if title:
        texts['title'] = BeautifulSoup(unescape(title), 'html.parser').get_text()
    
    # Excerpt
    excerpt = post.get('excerpt', {}).get('rendered', '')
    if excerpt:
        excerpt_soup = BeautifulSoup(unescape(excerpt), 'html.parser')
        texts['excerpt'] = excerpt_soup.get_text().strip()
    
    # Content
    content = post.get('content', {}).get('rendered', '')
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        texts['content'] = soup.get_text()
    
    return texts

def verify_correction(correction: Dict, post_texts: Dict[str, str]) -> Dict:
    """Verify if a single correction was applied"""
    section = correction['section']
    original = correction['original']
    corrected = correction['corrected']
    
    # Map section names to text keys
    section_key = None
    if section == 'title':
        section_key = 'title'
    elif section == 'excerpt':
        section_key = 'excerpt'
    elif section.startswith('paragraph_'):
        section_key = 'content'
    else:
        section_key = 'content'
    
    if section_key not in post_texts:
        return {
            'status': 'unknown',
            'reason': f'Section {section_key} not found in post'
        }
    
    text = post_texts[section_key]
    
    # Check if the corrected word is present
    has_corrected = corrected.lower() in text.lower()
    has_original = original.lower() in text.lower()
    
    if has_corrected and not has_original:
        return {
            'status': 'applied',
            'reason': f'Found "{corrected}", original "{original}" not present'
        }
    elif has_original and not has_corrected:
        return {
            'status': 'not_applied',
            'reason': f'Still has "{original}", corrected "{corrected}" not found'
        }
    elif has_corrected and has_original:
        return {
            'status': 'partial',
            'reason': f'Both "{original}" and "{corrected}" present (partial fix or multiple instances)'
        }
    else:
        return {
            'status': 'neither',
            'reason': f'Neither "{original}" nor "{corrected}" found (section may have changed)'
        }

def verify_corrections(corrections_file: str, wp_url: str, auth_token: str):
    """Main verification function"""
    print(f"🔍 Verifying Spelling Corrections")
    print(f"File: {corrections_file}")
    print(f"WordPress: {wp_url}")
    print("=" * 80)
    print()
    
    # Load corrections
    corrections_data = load_corrections(corrections_file)
    
    if not corrections_data:
        print("❌ No corrections data found")
        return
    
    print(f"📊 Found {len(corrections_data)} post(s) with corrections\n")
    
    total_corrections = 0
    applied_count = 0
    not_applied_count = 0
    partial_count = 0
    unknown_count = 0
    
    for post_corrections in corrections_data:
        post_id = post_corrections['post_id']
        post_title = post_corrections['title']
        corrections = post_corrections['corrections']
        
        print(f"📄 Post {post_id}: {post_title}")
        print(f"   URL: {post_corrections['link']}")
        print(f"   Corrections to verify: {len(corrections)}")
        
        # Fetch current post
        post = fetch_post_content(wp_url, auth_token, post_id)
        
        if not post:
            print(f"   ❌ Could not fetch post - skipping")
            unknown_count += len(corrections)
            print()
            continue
        
        # Extract text
        post_texts = extract_text_from_post(post)
        
        # Verify each correction
        post_applied = 0
        post_not_applied = 0
        
        for correction in corrections:
            total_corrections += 1
            result = verify_correction(correction, post_texts)
            
            status_icon = {
                'applied': '✅',
                'not_applied': '❌',
                'partial': '⚠️',
                'neither': '❓',
                'unknown': '❓'
            }.get(result['status'], '❓')
            
            print(f"   {status_icon} {correction['original']} → {correction['corrected']}")
            print(f"      Section: {correction['section']}")
            print(f"      Result: {result['reason']}")
            
            if result['status'] == 'applied':
                applied_count += 1
                post_applied += 1
            elif result['status'] == 'not_applied':
                not_applied_count += 1
                post_not_applied += 1
            elif result['status'] == 'partial':
                partial_count += 1
            else:
                unknown_count += 1
        
        # Post summary
        if post_not_applied == 0 and post_applied > 0:
            print(f"   ✅ All corrections applied for this post")
        elif post_not_applied > 0:
            print(f"   ⚠️  {post_not_applied} correction(s) NOT applied")
        
        print()
    
    # Overall summary
    print("=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Total corrections checked: {total_corrections}")
    print(f"✅ Applied:     {applied_count} ({applied_count/total_corrections*100:.1f}%)")
    print(f"❌ Not Applied: {not_applied_count} ({not_applied_count/total_corrections*100:.1f}%)")
    print(f"⚠️  Partial:    {partial_count} ({partial_count/total_corrections*100:.1f}%)")
    print(f"❓ Unknown:     {unknown_count} ({unknown_count/total_corrections*100:.1f}%)")
    print()
    
    if not_applied_count == 0 and unknown_count == 0:
        print("🎉 SUCCESS: All corrections have been applied!")
        return 0
    elif not_applied_count > 0:
        print("⚠️  WARNING: Some corrections were NOT applied to WordPress")
        print("   This could mean:")
        print("   - The apply workflow didn't run successfully")
        print("   - The post was edited after corrections were applied")
        print("   - The WordPress API update failed")
        return 1
    else:
        print("❓ UNCERTAIN: Could not verify some corrections")
        return 2

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify spelling corrections were applied to WordPress')
    parser.add_argument('corrections_file', nargs='?', default='spelling_corrections.json',
                        help='Path to corrections JSON file (default: spelling_corrections.json)')
    
    args = parser.parse_args()
    
    # Configuration
    WP_URL = os.getenv('WP_URL', 'https://wordpress.jameskilby.cloud')
    AUTH_TOKEN = os.getenv('WP_AUTH_TOKEN')
    
    if not AUTH_TOKEN:
        print('❌ Error: WP_AUTH_TOKEN environment variable is required')
        print('   Set it with: export WP_AUTH_TOKEN="your_token_here"')
        sys.exit(1)
    
    # Verify
    exit_code = verify_corrections(args.corrections_file, WP_URL, AUTH_TOKEN)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
