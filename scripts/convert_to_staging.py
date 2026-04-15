#!/usr/bin/env python3
"""
Convert static site to use relative URLs for staging deployment
"""
import os
import re
from pathlib import Path
from config import Config

def convert_html_to_relative_urls(html_content):
    """Convert absolute URLs to relative URLs for staging.

    Preserves absolute URLs in elements that require them for correctness:
    - <meta property="og:*"> and <meta name="twitter:image"> (social previews)
    - <link rel="canonical"> (SEO deduplication)
    - <script type="application/ld+json"> blocks (structured data)
    """
    # Get domain from config
    target_domain = Config.TARGET_DOMAIN.replace('https://', '').replace('http://', '')

    # Protect elements that must keep absolute URLs by replacing them with
    # placeholders before the global regex runs, then restoring them after.
    preserved = []

    def _preserve(match):
        idx = len(preserved)
        preserved.append(match.group(0))
        return f'__PRESERVE_{idx}__'

    # Preserve canonical links
    html_content = re.sub(
        r'<link\s[^>]*rel=["\']canonical["\'][^>]*/?>',
        _preserve,
        html_content,
        flags=re.IGNORECASE,
    )

    # Preserve OG and Twitter meta tags with URL values
    html_content = re.sub(
        r'<meta\s[^>]*(?:property=["\']og:|name=["\']twitter:image)[^>]*/?>',
        _preserve,
        html_content,
        flags=re.IGNORECASE,
    )

    # Preserve JSON-LD script blocks
    html_content = re.sub(
        r'<script\s[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>',
        _preserve,
        html_content,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Apply the domain-stripping replacements
    html_content = re.sub(
        rf'https://{re.escape(target_domain)}/wp-content/',
        '/wp-content/',
        html_content
    )

    html_content = re.sub(
        rf'https://{re.escape(target_domain)}/',
        '/',
        html_content
    )

    # Restore preserved elements
    for idx, original in enumerate(preserved):
        html_content = html_content.replace(f'__PRESERVE_{idx}__', original)

    return html_content

def convert_css_urls(css_content):
    """Convert WordPress URLs in CSS files to relative URLs"""
    # Get domains from config
    wp_domain = Config.WP_URL.replace('https://', '').replace('http://', '')
    target_domain = Config.TARGET_DOMAIN.replace('https://', '').replace('http://', '')
    
    # Replace WordPress private site font URLs with relative paths
    css_content = re.sub(
        rf'https://{re.escape(wp_domain)}/wp-content/',
        '/wp-content/',
        css_content
    )
    
    # Also replace any absolute references to the public domain in CSS
    css_content = re.sub(
        rf'https://{re.escape(target_domain)}/wp-content/',
        '/wp-content/',
        css_content
    )
    
    return css_content

def process_directory(directory):
    """Process all HTML and CSS files in directory"""
    html_files = list(Path(directory).rglob('*.html'))
    css_files = list(Path(directory).rglob('*.css'))
    
    print(f"🔄 Converting {len(html_files)} HTML files to use relative URLs...")
    
    for html_file in html_files:
        # Read original content
        original_content = html_file.read_text(encoding='utf-8')
        
        # Convert URLs
        converted_content = convert_html_to_relative_urls(original_content)
        
        # Write back if changed
        if original_content != converted_content:
            html_file.write_text(converted_content, encoding='utf-8')
            print(f"✅ Converted HTML: {html_file.relative_to(directory)}")
    
    print(f"🎨 Converting {len(css_files)} CSS files to use relative URLs...")
    
    for css_file in css_files:
        try:
            # Read original content
            original_content = css_file.read_text(encoding='utf-8')
            
            # Convert URLs
            converted_content = convert_css_urls(original_content)
            
            # Write back if changed
            if original_content != converted_content:
                css_file.write_text(converted_content, encoding='utf-8')
                print(f"✅ Converted CSS: {css_file.relative_to(directory)}")
        except Exception as e:
            print(f"⚠️  Error processing CSS {css_file.relative_to(directory)}: {e}")
    
    print("✅ Conversion complete!")

if __name__ == "__main__":
    public_dir = Path("public")
    if not public_dir.exists():
        print("❌ public/ directory not found!")
        exit(1)
    
    process_directory(public_dir)