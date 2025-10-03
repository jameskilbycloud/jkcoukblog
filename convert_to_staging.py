#!/usr/bin/env python3
"""
Convert static site to use relative URLs for staging deployment
"""
import os
import re
from pathlib import Path

def convert_html_to_relative_urls(html_content):
    """Convert absolute URLs to relative URLs for staging"""
    # Replace absolute URLs with relative URLs
    html_content = re.sub(
        r'https://jameskilby\.co\.uk/wp-content/',
        '/wp-content/',
        html_content
    )
    
    # Also replace any other absolute references to the domain
    html_content = re.sub(
        r'https://jameskilby\.co\.uk/',
        '/',
        html_content
    )
    
    return html_content

def process_directory(directory):
    """Process all HTML files in directory"""
    html_files = list(Path(directory).rglob('*.html'))
    
    print(f"🔄 Converting {len(html_files)} HTML files to use relative URLs...")
    
    for html_file in html_files:
        # Read original content
        original_content = html_file.read_text(encoding='utf-8')
        
        # Convert URLs
        converted_content = convert_html_to_relative_urls(original_content)
        
        # Write back if changed
        if original_content != converted_content:
            html_file.write_text(converted_content, encoding='utf-8')
            print(f"✅ Converted: {html_file.relative_to(directory)}")
    
    print("✅ Conversion complete!")

if __name__ == "__main__":
    public_dir = Path("public")
    if not public_dir.exists():
        print("❌ public/ directory not found!")
        exit(1)
    
    process_directory(public_dir)