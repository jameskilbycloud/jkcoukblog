#!/usr/bin/env python3
"""
Content Validator for jameskilby.co.uk
Validates content quality before deployment to Cloudflare Pages
"""

import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

# JSON-LD types that require specific fields to be eligible for Google rich results
_ARTICLE_TYPES = frozenset({
    'Article', 'BlogPosting', 'NewsArticle', 'TechArticle', 'ScholarlyArticle'
})
_ARTICLE_REQUIRED_FIELDS = ('headline', 'datePublished', 'author')


class ContentValidator:
    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.errors = []
        self.warnings = []
        self.checks_run = 0

    def validate_html_file(self, file_path, target_domain='jameskilby.co.uk'):
        """Run all validation checks on HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except Exception as e:
            self.errors.append({
                'type': 'file_read_error',
                'file': str(file_path),
                'message': f'Failed to read file: {str(e)}'
            })
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Critical checks
        self._check_broken_links(soup, file_path)
        self._check_missing_alt_text(soup, file_path)
        self._check_seo_basics(soup, file_path)
        self._check_structured_data(soup, file_path)
        self._check_performance_issues(soup, file_path)
        self._check_security_headers(html, file_path)
        self._check_accessibility(soup, file_path)
        
        self.checks_run += 1
    
    def _check_broken_links(self, soup, file_path):
        """Check for broken internal links"""
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip external links, anchors, and special protocols
            if href.startswith(('http://', 'https://', '#', 'mailto:', 'tel:')):
                continue
            
            # Check if internal link exists
            if href.startswith('/'):
                # Try both with and without index.html
                target_file = self.public_dir / href.lstrip('/')
                target_index = target_file / 'index.html' if target_file.is_dir() else target_file.parent / target_file.name
                
                if not target_file.exists() and not target_index.exists() and not (target_file.parent / (target_file.name + '.html')).exists():
                    self.errors.append({
                        'type': 'broken_link',
                        'file': str(file_path),
                        'link': href,
                        'message': f'Broken internal link: {href}'
                    })
    
    def _check_missing_alt_text(self, soup, file_path):
        """Check for images without alt text"""
        for img in soup.find_all('img'):
            if not img.get('alt'):
                self.warnings.append({
                    'type': 'missing_alt',
                    'file': str(file_path),
                    'src': img.get('src', 'unknown'),
                    'message': f'Image missing alt text: {img.get("src", "unknown")}'
                })
    
    def _check_seo_basics(self, soup, file_path):
        """Check basic SEO requirements"""
        # Title length (skip for RSS/Atom feed files — they have no <title> by design)
        rel = str(file_path)
        is_feed = 'feed' in rel.lower()
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            if len(title_text) > 60:
                self.warnings.append({
                    'type': 'seo_title_long',
                    'file': str(file_path),
                    'length': len(title_text),
                    'message': f'Title too long ({len(title_text)} chars, recommended max 60)'
                })
            elif len(title_text) < 30:
                self.warnings.append({
                    'type': 'seo_title_short',
                    'file': str(file_path),
                    'length': len(title_text),
                    'message': f'Title too short ({len(title_text)} chars, recommended min 30)'
                })
        elif not is_feed:
            self.errors.append({
                'type': 'seo_no_title',
                'file': str(file_path),
                'message': 'Missing title tag'
            })
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
            if len(desc) > 160:
                self.warnings.append({
                    'type': 'seo_description_long',
                    'file': str(file_path),
                    'length': len(desc),
                    'message': f'Meta description too long ({len(desc)} chars, recommended max 160)'
                })
            elif len(desc) < 120:
                self.warnings.append({
                    'type': 'seo_description_short',
                    'file': str(file_path),
                    'length': len(desc),
                    'message': f'Meta description too short ({len(desc)} chars, recommended min 120)'
                })
        else:
            self.warnings.append({
                'type': 'seo_no_description',
                'file': str(file_path),
                'message': 'Missing meta description'
            })
        
        # H1 tags (skip for RSS/Atom feed files — they have no H1 by design)
        rel = str(file_path)
        is_feed = 'feed' in rel.lower()
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0 and not is_feed:
            self.errors.append({
                'type': 'seo_no_h1',
                'file': str(file_path),
                'message': 'Missing H1 tag'
            })
        elif len(h1_tags) > 1:
            self.warnings.append({
                'type': 'seo_multiple_h1',
                'file': str(file_path),
                'count': len(h1_tags),
                'message': f'Multiple H1 tags ({len(h1_tags)}, recommended 1)'
            })
        
        # Check for canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            self.warnings.append({
                'type': 'seo_no_canonical',
                'file': str(file_path),
                'message': 'Missing canonical URL'
            })
        
        # Check for Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if not og_title:
            self.warnings.append({
                'type': 'seo_no_og_title',
                'file': str(file_path),
                'message': 'Missing Open Graph title'
            })
        if not og_desc:
            self.warnings.append({
                'type': 'seo_no_og_description',
                'file': str(file_path),
                'message': 'Missing Open Graph description'
            })
        if not og_image:
            self.warnings.append({
                'type': 'seo_no_og_image',
                'file': str(file_path),
                'message': 'Missing og:image - shared links on X/LinkedIn/Slack will show no preview image'
            })
        elif not og_image.get('content', '').startswith('https://'):
            self.warnings.append({
                'type': 'seo_og_image_not_absolute',
                'file': str(file_path),
                'content': og_image.get('content', ''),
                'message': f'og:image must be an absolute HTTPS URL, got: {og_image.get("content", "")}'
            })
    
    def _check_structured_data(self, soup, file_path):
        """Validate JSON-LD structured data blocks"""
        ld_scripts = soup.find_all('script', type='application/ld+json')

        if not ld_scripts:
            # Only warn for pages that have meaningful article content — skip
            # utility pages (search, 404, archives) that rarely need rich results.
            if soup.find('article') or soup.find('main'):
                self.warnings.append({
                    'type': 'seo_no_structured_data',
                    'file': str(file_path),
                    'message': (
                        'No JSON-LD structured data found — '
                        'page is ineligible for Google rich results'
                    )
                })
            return

        for idx, script in enumerate(ld_scripts, 1):
            raw = (script.string or '').strip()
            if not raw:
                self.warnings.append({
                    'type': 'structured_data_empty',
                    'file': str(file_path),
                    'message': f'Empty JSON-LD block (script #{idx})'
                })
                continue

            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                self.errors.append({
                    'type': 'structured_data_invalid_json',
                    'file': str(file_path),
                    'message': f'JSON-LD parse error in block #{idx}: {exc}'
                })
                continue

            # Support both single objects and @graph arrays
            if isinstance(data, dict):
                items = data.get('@graph', [data])
            elif isinstance(data, list):
                items = data
            else:
                items = []

            for item in items:
                if not isinstance(item, dict):
                    continue

                # @context must reference schema.org
                context = str(item.get('@context', ''))
                if context and 'schema.org' not in context:
                    self.warnings.append({
                        'type': 'structured_data_bad_context',
                        'file': str(file_path),
                        'message': (
                            f'JSON-LD @context should reference schema.org, '
                            f'got: {context}'
                        )
                    })

                # Article types must have headline, datePublished, and author
                raw_type = item.get('@type', '')
                schema_type = raw_type if isinstance(raw_type, str) else (raw_type[0] if raw_type else '')
                if schema_type in _ARTICLE_TYPES:
                    for field in _ARTICLE_REQUIRED_FIELDS:
                        if not item.get(field):
                            self.warnings.append({
                                'type': 'structured_data_missing_field',
                                'file': str(file_path),
                                'schema_type': schema_type,
                                'field': field,
                                'message': (
                                    f'JSON-LD {schema_type} missing '
                                    f'required field: {field}'
                                )
                            })

    def _check_performance_issues(self, soup, file_path):
        """Check for performance issues"""
        # Large images without lazy loading
        for img in soup.find_all('img'):
            if not img.get('loading'):
                self.warnings.append({
                    'type': 'performance_no_lazy_loading',
                    'file': str(file_path),
                    'src': img.get('src', 'unknown'),
                    'message': f'Image without lazy loading: {img.get("src", "unknown")}'
                })
        
        # Too many inline styles
        inline_styles = len(soup.find_all(style=True))
        if inline_styles > 10:
            self.warnings.append({
                'type': 'performance_inline_styles',
                'file': str(file_path),
                'count': inline_styles,
                'message': f'Too many inline styles ({inline_styles}, recommended <10)'
            })
        
        # Render-blocking resources
        # Note: <link> elements have no 'async' attribute (only <script> does),
        # so we check only for 'media' to detect non-deferred stylesheets.
        for link in soup.find_all('link', rel='stylesheet'):
            if not link.get('media'):
                href = link.get('href', 'unknown')
                # Skip if it's a critical CSS file
                if 'critical' not in href.lower():
                    self.warnings.append({
                        'type': 'performance_render_blocking',
                        'file': str(file_path),
                        'href': href,
                        'message': f'Render-blocking CSS without media attribute: {href}'
                    })
        
        # Check for unoptimized scripts
        for script in soup.find_all('script', src=True):
            if not script.get('async') and not script.get('defer'):
                src = script.get('src', 'unknown')
                self.warnings.append({
                    'type': 'performance_blocking_script',
                    'file': str(file_path),
                    'src': src,
                    'message': f'Blocking script without async/defer: {src}'
                })
    
    def _check_security_headers(self, html, file_path):
        """Check for security issues"""
        soup = BeautifulSoup(html, 'html.parser')

        # Inline scripts without nonce/hash (CSP violation).
        # Only flag <script> tags without a src attribute — genuine inline
        # scripts. External <script src="..."> tags don't require a nonce and
        # were causing false positives with the previous string-search approach.
        inline_scripts = [
            s for s in soup.find_all('script')
            if not s.get('src') and s.string and s.string.strip()
        ]
        if inline_scripts and 'nonce=' not in html:
            self.warnings.append({
                'type': 'security_inline_script',
                'file': str(file_path),
                'message': (
                    f'Inline script without CSP nonce '
                    f'({len(inline_scripts)} script block(s) found)'
                )
            })

        # Mixed content warnings
        if 'http://' in html and 'https://' in html:
            for tag in soup.find_all(['img', 'script', 'link'], src=True):
                if tag.get('src', '').startswith('http://'):
                    self.errors.append({
                        'type': 'security_mixed_content',
                        'file': str(file_path),
                        'src': tag['src'],
                        'message': f'Mixed content: insecure resource {tag["src"]}'
                    })
    
    def _check_accessibility(self, soup, file_path):
        """Check basic accessibility"""
        # Links without text
        for link in soup.find_all('a'):
            link_text = link.get_text(strip=True)
            has_img = link.find('img')
            aria_label = link.get('aria-label')
            
            if not link_text and not has_img and not aria_label:
                self.errors.append({
                    'type': 'accessibility_empty_link',
                    'file': str(file_path),
                    'href': link.get('href', 'unknown'),
                    'message': f'Link without text content: {link.get("href", "unknown")}'
                })
        
        # Form inputs without labels
        for input_tag in soup.find_all('input'):
            input_id = input_tag.get('id')
            input_type = input_tag.get('type', 'text')
            
            if input_type not in ['hidden', 'submit', 'button']:
                if input_id:
                    label = soup.find('label', attrs={'for': input_id})
                    if not label and not input_tag.get('aria-label'):
                        self.warnings.append({
                            'type': 'accessibility_no_label',
                            'file': str(file_path),
                            'input_id': input_id,
                            'message': f'Input #{input_id} without label'
                        })
        
        # Check for heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        prev_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if prev_level > 0 and level > prev_level + 1:
                self.warnings.append({
                    'type': 'accessibility_heading_skip',
                    'file': str(file_path),
                    'message': f'Heading hierarchy skip: {heading.name} after h{prev_level}'
                })
            prev_level = level
    
    def generate_report(self, output_format='console'):
        """Generate validation report"""
        report = {
            'summary': {
                'checks_run': self.checks_run,
                'errors': len(self.errors),
                'warnings': len(self.warnings),
                'status': 'FAIL' if self.errors else 'PASS'
            },
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        # Save to file
        report_file = Path('validation-report.json')
        report_file.write_text(json.dumps(report, indent=2))
        
        # Print summary
        print(f"\n📋 Content Validation Report")
        print(f"{'=' * 50}")
        print(f"Files checked: {self.checks_run}")
        print(f"Status: {'✅ PASS' if report['summary']['status'] == 'PASS' else '❌ FAIL'}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"{'=' * 50}\n")
        
        if self.errors:
            print(f"❌ Critical Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:10], 1):
                print(f"   {i}. {error['message']}")
                print(f"      File: {error['file']}")
            
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors\n")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings[:10], 1):
                print(f"   {i}. {warning['message']}")
                print(f"      File: {warning['file']}")
            
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings\n")
        
        print(f"\n📄 Full report saved to: validation-report.json\n")
        
        return report


def main():
    """Main entry point"""
    # Accept directory as optional CLI arg so CI can pass 'static-output'
    # instead of the committed 'public/' to validate the freshly-built site.
    public_dir_arg = sys.argv[1] if len(sys.argv) > 1 else 'public'
    validator = ContentValidator(public_dir=public_dir_arg)

    # Find all HTML files in the specified directory
    public_dir = Path(public_dir_arg)

    if not public_dir.exists():
        print(f"❌ Error: directory '{public_dir}' not found")
        print("   Make sure you're running this from the project root")
        sys.exit(1)
    
    html_files = list(public_dir.rglob('*.html'))

    if not html_files:
        print("⚠️  Warning: No HTML files found in public directory")
        sys.exit(0)

    print(f"🔍 Validating {len(html_files)} HTML files...\n")

    # Files to exclude from validation (RSS feeds, sitemaps, etc.)
    exclude_patterns = ['feed/index.html', 'sitemap', 'robots.txt']

    for html_file in html_files:
        # Check if file should be excluded
        relative_path = str(html_file.relative_to(public_dir))
        if any(pattern in relative_path for pattern in exclude_patterns):
            print(f"⏭️  Skipping: {relative_path} (excluded pattern)")
            continue

        validator.validate_html_file(html_file)
    
    report = validator.generate_report()
    
    # Exit with error code if there are critical errors
    if report['summary']['status'] == 'FAIL':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
