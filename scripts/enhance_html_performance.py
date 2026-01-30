#!/usr/bin/env python3
"""
HTML Performance Enhancement Script
Post-processes generated HTML files to add performance optimizations
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re


class HTMLPerformanceEnhancer:
    """Enhance HTML files with performance optimizations"""

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_processed = 0
        self.optimizations_applied = 0

    def process_all_files(self):
        """Process all HTML files in the public directory"""
        html_files = list(self.public_dir.rglob('*.html'))

        print(f"🚀 Processing {len(html_files)} HTML files for performance enhancements...")

        for html_file in html_files:
            if self.process_file(html_file):
                self.files_processed += 1

        print(f"\n✅ Enhanced {self.files_processed} files")
        print(f"   Applied {self.optimizations_applied} optimizations")

    def process_file(self, file_path):
        """Process a single HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            modified = False

            # Apply optimizations
            if self.add_async_defer_to_scripts(soup):
                modified = True

            if self.add_media_attributes_to_css(soup):
                modified = True

            if self.optimize_external_scripts(soup):
                modified = True

            # Save if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                return True

            return False

        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
            return False

    def add_async_defer_to_scripts(self, soup):
        """Add async or defer attributes to external scripts"""
        modified = False

        for script in soup.find_all('script', src=True):
            # Skip scripts that already have async or defer
            if script.get('async') is not None or script.get('defer') is not None:
                continue

            src = script.get('src', '')

            # Analytics scripts should be async
            if any(keyword in src for keyword in ['plausible', 'analytics', 'gtag', 'ga.js']):
                script['async'] = ''
                modified = True
                self.optimizations_applied += 1

            # Other external scripts should use defer (maintains execution order)
            elif src.startswith('http') or src.startswith('//'):
                script['defer'] = ''
                modified = True
                self.optimizations_applied += 1

            # Internal scripts can use defer too (unless they're critical)
            elif not any(keyword in src for keyword in ['critical', 'inline']):
                script['defer'] = ''
                modified = True
                self.optimizations_applied += 1

        return modified

    def add_media_attributes_to_css(self, soup):
        """Add media attributes to non-critical CSS"""
        modified = False

        for link in soup.find_all('link', rel='stylesheet'):
            # Skip if already has media attribute
            if link.get('media'):
                continue

            href = link.get('href', '')

            # Skip critical CSS
            if 'critical' in href or 'inline' in href:
                continue

            # Print/PDF specific styles
            if 'print' in href:
                link['media'] = 'print'
                modified = True
                self.optimizations_applied += 1

            # Mobile-specific styles
            elif 'mobile' in href:
                link['media'] = 'screen and (max-width: 768px)'
                modified = True
                self.optimizations_applied += 1

            # Default to 'all' to make it explicit (helps with preload)
            else:
                link['media'] = 'all'
                modified = True
                self.optimizations_applied += 1

        return modified

    def optimize_external_scripts(self, soup):
        """Optimize external script loading"""
        modified = False

        # Find head tag
        if not soup.head:
            return False

        # Add DNS prefetch for external domains
        external_domains = set()

        for tag in soup.find_all(['script', 'link', 'img'], src=True):
            src = tag.get('src') or tag.get('href', '')
            if src.startswith('http'):
                domain = src.split('/')[2]
                external_domains.add(domain)

        # Add dns-prefetch for each external domain
        for domain in external_domains:
            # Check if dns-prefetch already exists
            existing = soup.find('link', rel='dns-prefetch', href=f'//{domain}')
            if not existing:
                dns_prefetch = soup.new_tag('link')
                dns_prefetch['rel'] = 'dns-prefetch'
                dns_prefetch['href'] = f'//{domain}'
                soup.head.insert(0, dns_prefetch)
                modified = True
                self.optimizations_applied += 1

        return modified


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        public_dir = sys.argv[1]
    else:
        public_dir = 'public'

    enhancer = HTMLPerformanceEnhancer(public_dir)
    enhancer.process_all_files()

    sys.exit(0)


if __name__ == '__main__':
    main()
