#!/usr/bin/env python3
"""
SEO Issues Fixer
Fixes common SEO problems in generated HTML files
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

# Import config for target domain
sys.path.insert(0, str(Path(__file__).parent))
try:
    from config import Config
    TARGET_DOMAIN = Config.TARGET_DOMAIN
except (ImportError, AttributeError):
    TARGET_DOMAIN = 'https://jameskilby.co.uk'


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

            if self.fix_og_absolute_urls(soup, file_path):
                modified = True

            if self.fix_jsonld_absolute_ids(soup, file_path):
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
            # #2: scope to article/main so we don't accidentally grab nav,
            # footer, sidebar, or cookie-banner text as the description.
            content_area = (
                soup.find('article') or
                soup.find('main') or
                soup.find(class_=re.compile(
                    r'entry.?content|post.?content|article.?body', re.I
                )) or
                soup
            )
            first_p = content_area.find('p')
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

    def fix_jsonld_absolute_ids(self, soup, file_path):
        """Ensure JSON-LD @id and url values use absolute URLs.

        convert_to_staging.py strips all domain prefixes including those inside
        <script type="application/ld+json"> blocks, turning @id and url values
        like 'https://jameskilby.co.uk/about/' into '/about/'.  Search engines
        and validators require fully-qualified IRIs for @id.
        """
        import json as _json

        modified = False
        # Keys whose string values should be made absolute.
        # Note: values for these keys can also be nested objects (e.g. "image"
        # can be an ImageObject dict), so we always recurse into dicts/lists
        # regardless of the key name.
        URL_KEYS = {'@id', 'url', 'logo', 'image', 'thumbnailUrl', 'contentUrl',
                    'sameAs'}

        def absolutify(value):
            """Return absolute URL if value is a root-relative path."""
            if isinstance(value, str) and value.startswith('/'):
                return f"{TARGET_DOMAIN}{value}"
            return value

        def fix_node(obj):
            """Recursively walk a JSON-LD node and absolutify URL fields."""
            nonlocal modified
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key == 'sameAs':
                        if isinstance(val, list):
                            new_list = [absolutify(v) for v in val]
                            if new_list != val:
                                obj[key] = new_list
                                modified = True
                        else:
                            new_val = absolutify(val)
                            if new_val != val:
                                obj[key] = new_val
                                modified = True
                    elif key in URL_KEYS and isinstance(val, str):
                        # String value — absolutify directly
                        new_val = absolutify(val)
                        if new_val != val:
                            obj[key] = new_val
                            modified = True
                    # Always recurse into nested dicts/lists so that e.g.
                    # "image": {"@id": "/#logo", "url": "/..."} gets fixed too.
                    if isinstance(val, (dict, list)):
                        fix_node(val)
            elif isinstance(obj, list):
                for item in obj:
                    fix_node(item)

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = _json.loads(script.string or '')
                fix_node(data)
                if modified:
                    script.string = _json.dumps(data, ensure_ascii=False,
                                                separators=(',', ':'))
            except (_json.JSONDecodeError, TypeError):
                continue  # malformed JSON-LD – skip silently

        if modified:
            self.issues_fixed += 1
            print(f"   🔗 Fixed relative JSON-LD @id/url values: {file_path.name}")

        return modified

    def fix_og_absolute_urls(self, soup, file_path):
        """Ensure og:image, og:url, and twitter:image use absolute URLs.

        Social platforms require absolute https:// URLs for link previews.
        Relative paths like /wp-content/uploads/... produce broken previews
        on Facebook, Twitter/X, LinkedIn, and Slack.
        """
        modified = False
        # Open Graph meta tags with property attribute
        OG_URL_PROPS = {'og:image', 'og:image:secure_url', 'og:url'}
        for meta in soup.find_all('meta', property=lambda p: p in OG_URL_PROPS):
            content = meta.get('content', '')
            if content.startswith('/'):
                meta['content'] = f"{TARGET_DOMAIN}{content}"
                modified = True

        # Twitter Card meta tags with name attribute
        for meta in soup.find_all('meta', attrs={'name': 'twitter:image'}):
            content = meta.get('content', '')
            if content.startswith('/'):
                meta['content'] = f"{TARGET_DOMAIN}{content}"
                modified = True

        if modified:
            self.issues_fixed += 1
            print(f"   🔗 Fixed relative og:image/og:url to absolute: {file_path.name}")

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
