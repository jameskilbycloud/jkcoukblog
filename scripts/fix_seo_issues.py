#!/usr/bin/env python3
"""
SEO Issues Fixer
Fixes common SEO problems in generated HTML files
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re


class SEOFixer:
    """Fix SEO issues in HTML files"""

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_fixed = 0
        self.issues_fixed = 0

    def process_all_files(self):
        """Process all HTML files"""
        html_files = list(self.public_dir.rglob('*.html'))

        # Exclude feeds and sitemaps
        html_files = [f for f in html_files if not any(
            pattern in str(f) for pattern in ['feed/', 'sitemap']
        )]

        print(f"🔧 Fixing SEO issues in {len(html_files)} HTML files...")

        for html_file in html_files:
            if self.process_file(html_file):
                self.files_fixed += 1

        print(f"\n✅ Fixed {self.files_fixed} files")
        print(f"   Resolved {self.issues_fixed} SEO issues")

    def process_file(self, file_path):
        """Process a single HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            modified = False

            # Apply fixes
            if self.fix_title_length(soup, file_path):
                modified = True

            if self.fix_meta_description(soup, file_path):
                modified = True

            if self.fix_multiple_h1(soup, file_path):
                modified = True

            if self.ensure_image_alt_text(soup, file_path):
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

    def fix_title_length(self, soup, file_path):
        """Fix title tags that are too long or too short"""
        title_tag = soup.find('title')
        if not title_tag:
            return False

        title_text = title_tag.get_text().strip()
        modified = False

        # Too long (>60 chars)
        if len(title_text) > 60:
            # Try to intelligently truncate
            # Remove site suffix if present
            if ' | ' in title_text:
                parts = title_text.split(' | ')
                # Keep first part and last part (site name), truncate middle
                if len(parts) > 2:
                    new_title = f"{parts[0]} | {parts[-1]}"
                    if len(new_title) <= 60:
                        title_tag.string = new_title
                        self.issues_fixed += 1
                        modified = True
                        print(f"   📏 Fixed long title: {file_path.name}")
                        return modified

            # Simple truncation with ellipsis
            truncated = title_text[:57] + '...'
            title_tag.string = truncated
            self.issues_fixed += 1
            modified = True
            print(f"   📏 Truncated long title: {file_path.name}")

        return modified

    def fix_meta_description(self, soup, file_path):
        """Fix meta description length"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            return False

        desc = meta_desc.get('content', '')
        modified = False

        # Too long (>160 chars)
        if len(desc) > 160:
            truncated = desc[:157] + '...'
            meta_desc['content'] = truncated
            self.issues_fixed += 1
            modified = True
            print(f"   📝 Truncated long description: {file_path.name}")

        # Too short (<120 chars) - try to expand from page content
        elif len(desc) < 120:
            # Get first paragraph text
            first_p = soup.find('p')
            if first_p:
                p_text = first_p.get_text().strip()
                if len(p_text) >= 120:
                    # Use first 157 chars of paragraph
                    new_desc = p_text[:157] + '...'
                    meta_desc['content'] = new_desc
                    self.issues_fixed += 1
                    modified = True
                    print(f"   📝 Expanded short description: {file_path.name}")
                elif len(desc + ' ' + p_text) <= 160:
                    # Append paragraph to existing description
                    new_desc = f"{desc} {p_text}"
                    meta_desc['content'] = new_desc
                    self.issues_fixed += 1
                    modified = True
                    print(f"   📝 Expanded short description: {file_path.name}")

        return modified

    def fix_multiple_h1(self, soup, file_path):
        """Ensure only one H1 tag per page"""
        h1_tags = soup.find_all('h1')

        if len(h1_tags) <= 1:
            return False

        # Keep the first H1, convert others to H2
        for h1 in h1_tags[1:]:
            h1.name = 'h2'
            self.issues_fixed += 1

        print(f"   🏷️  Fixed multiple H1 tags: {file_path.name} ({len(h1_tags)} → 1)")
        return True

    def ensure_image_alt_text(self, soup, file_path):
        """Add generic alt text to images missing it"""
        modified = False

        for img in soup.find_all('img'):
            if not img.get('alt'):
                # Try to generate alt text from image filename
                src = img.get('src', '')
                if src:
                    # Extract filename without extension
                    filename = Path(src).stem
                    # Convert dashes/underscores to spaces and capitalize
                    alt_text = filename.replace('-', ' ').replace('_', ' ').title()
                    img['alt'] = alt_text
                    self.issues_fixed += 1
                    modified = True
                else:
                    # Generic fallback
                    img['alt'] = 'Image'
                    self.issues_fixed += 1
                    modified = True

        if modified:
            print(f"   🖼️  Added alt text to images: {file_path.name}")

        return modified


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        public_dir = sys.argv[1]
    else:
        public_dir = 'public'

    fixer = SEOFixer(public_dir)
    fixer.process_all_files()

    sys.exit(0)


if __name__ == '__main__':
    main()
