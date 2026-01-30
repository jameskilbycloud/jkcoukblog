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

            if self.add_resource_hints(soup):
                modified = True

            if self.optimize_fonts(soup):
                modified = True

            if self.add_preload_hints(soup):
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

    def add_resource_hints(self, soup):
        """Add preconnect hints for critical external domains"""
        if not soup.head:
            return False

        modified = False

        # Critical domains that should use preconnect (stronger than dns-prefetch)
        critical_domains = {
            'https://plausible.jameskilby.cloud',  # Analytics
        }

        for domain in critical_domains:
            # Check if this domain is actually used in the page
            domain_used = False
            for tag in soup.find_all(['script', 'link', 'img']):
                src = tag.get('src') or tag.get('href', '')
                if domain in src:
                    domain_used = True
                    break

            if not domain_used:
                continue

            # Check if preconnect already exists
            existing = soup.find('link', rel='preconnect', href=domain)
            if not existing:
                preconnect = soup.new_tag('link')
                preconnect['rel'] = 'preconnect'
                preconnect['href'] = domain

                soup.head.insert(0, preconnect)
                modified = True
                self.optimizations_applied += 1

        return modified

    def optimize_fonts(self, soup):
        """Optimize web font loading"""
        if not soup.head:
            return False

        modified = False

        # Find and preload WOFF2 fonts from @font-face declarations
        for style in soup.find_all('style'):
            if style.string and '@font-face' in style.string:
                # Extract WOFF2 font URLs
                font_urls = re.findall(r'url\(["\']?(.*?\.woff2)["\']?\)', style.string)
                for font_url in font_urls:
                    font_url = font_url.strip('\'"')

                    # Check if preload already exists
                    existing = soup.find('link', rel='preload', href=font_url)
                    if not existing:
                        preload = soup.new_tag('link')
                        preload['rel'] = 'preload'
                        preload['href'] = font_url
                        preload['as'] = 'font'
                        preload['type'] = 'font/woff2'
                        preload['crossorigin'] = ''
                        soup.head.insert(0, preload)
                        modified = True
                        self.optimizations_applied += 1

        return modified

    def add_preload_hints(self, soup):
        """Add preload hints for critical resources"""
        if not soup.head:
            return False

        modified = False

        # Find hero/first image in main content for preloading
        main_content = soup.find(['main', 'article', 'div'])
        if main_content:
            first_img = main_content.find('img')
            if first_img and first_img.get('src'):
                img_src = first_img['src']

                # Only preload if it's not a small icon/avatar
                # Check if image has width/height attributes indicating it's large
                width = first_img.get('width', '')
                try:
                    if width and int(width) > 200:
                        # Check if preload already exists
                        existing = soup.find('link', rel='preload', href=img_src)
                        if not existing:
                            preload = soup.new_tag('link')
                            preload['rel'] = 'preload'
                            preload['href'] = img_src
                            preload['as'] = 'image'

                            # Add type attribute for modern formats
                            img_type = self._get_image_type(img_src)
                            if img_type:
                                preload['type'] = img_type

                            soup.head.insert(0, preload)
                            modified = True
                            self.optimizations_applied += 1
                except (ValueError, AttributeError):
                    pass

        # Preload critical CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            # Only preload critical CSS (indicated by filename)
            if any(keyword in href for keyword in ['critical', 'main', 'style']) and 'print' not in href:
                # Check if it's not already preloaded
                existing = soup.find('link', rel='preload', href=href)
                if not existing and len(href) > 0:
                    preload = soup.new_tag('link')
                    preload['rel'] = 'preload'
                    preload['href'] = href
                    preload['as'] = 'style'
                    soup.head.insert(0, preload)
                    modified = True
                    self.optimizations_applied += 1
                    break  # Only preload one critical CSS file

        return modified

    def _get_image_type(self, src):
        """Get MIME type from image extension"""
        if src.endswith('.avif'):
            return 'image/avif'
        elif src.endswith('.webp'):
            return 'image/webp'
        elif src.endswith(('.jpg', '.jpeg')):
            return 'image/jpeg'
        elif src.endswith('.png'):
            return 'image/png'
        elif src.endswith('.svg'):
            return 'image/svg+xml'
        return None


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
