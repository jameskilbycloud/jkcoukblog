#!/usr/bin/env python3
"""
Markdown Content Exporter
Converts HTML content to clean, readable markdown with frontmatter
"""

import os
import sys
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import html2text
import yaml

class MarkdownExporter:
    def __init__(self, html_dir, markdown_dir, base_url):
        self.html_dir = Path(html_dir)
        self.markdown_dir = Path(markdown_dir)
        self.base_url = base_url.rstrip('/')
        
        # Configure html2text converter
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_emphasis = False
        self.converter.body_width = 0  # Don't wrap text
        self.converter.unicode_snob = True
        self.converter.skip_internal_links = False
        
        self.stats = {
            'posts_exported': 0,
            'pages_exported': 0,
            'errors': 0
        }
    
    def export_all_content(self):
        """Export all HTML content to markdown"""
        print("📝 Exporting content to markdown...")
        
        # Create output directory structure
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
        # Export posts (content in year/month structure)
        posts_exported = self._export_posts()
        
        # Export pages (top-level content)
        pages_exported = self._export_pages()
        
        # Create index of all markdown files
        self._create_markdown_index()
        
        # Create markdown sitemap
        self._create_markdown_sitemap()
        
        print(f"\n✅ Markdown export complete!")
        print(f"   Posts: {self.stats['posts_exported']}")
        print(f"   Pages: {self.stats['pages_exported']}")
        print(f"   Errors: {self.stats['errors']}")
        print(f"   Output: {self.markdown_dir}")
    
    def _export_posts(self):
        """Export blog posts to markdown"""
        print("\n📰 Exporting blog posts...")
        
        # Find post directories (year/month/slug pattern)
        for year_dir in sorted(self.html_dir.glob('[0-9][0-9][0-9][0-9]'), reverse=True):
            for month_dir in sorted(year_dir.glob('[0-9][0-9]'), reverse=True):
                for post_dir in month_dir.iterdir():
                    if post_dir.is_dir():
                        index_file = post_dir / 'index.html'
                        if index_file.exists():
                            try:
                                self._export_single_post(index_file, post_dir)
                                self.stats['posts_exported'] += 1
                            except Exception as e:
                                print(f"   ❌ Error exporting {post_dir.name}: {str(e)}")
                                self.stats['errors'] += 1
        
        return self.stats['posts_exported']
    
    def _export_single_post(self, html_file, post_dir):
        """Export a single post to markdown"""
        # Read and parse HTML
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        metadata = self._extract_metadata(soup, html_file)
        
        # Extract main content
        content_html = self._extract_content_html(soup)
        
        # Convert to markdown
        markdown_content = self.converter.handle(content_html)
        
        # Clean up markdown
        markdown_content = self._clean_markdown(markdown_content)
        
        # Create frontmatter
        frontmatter = self._create_frontmatter(metadata)
        
        # Combine frontmatter and content
        full_markdown = f"{frontmatter}\n\n{markdown_content}"
        
        # Determine output path (mirror directory structure)
        relative_path = post_dir.relative_to(self.html_dir)
        output_dir = self.markdown_dir / relative_path
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'index.md'
        output_file.write_text(full_markdown, encoding='utf-8')
        
        # Also create a flat file with slug
        slug = post_dir.name
        flat_file = self.markdown_dir / 'posts' / f"{slug}.md"
        flat_file.parent.mkdir(parents=True, exist_ok=True)
        flat_file.write_text(full_markdown, encoding='utf-8')
        
        print(f"   ✅ {relative_path}")
    
    def _export_pages(self):
        """Export standalone pages to markdown"""
        print("\n📄 Exporting pages...")
        
        # Find top-level pages (not in year directories)
        for item in self.html_dir.iterdir():
            if item.is_dir() and not item.name.isdigit():
                index_file = item / 'index.html'
                if index_file.exists():
                    try:
                        self._export_single_page(index_file, item)
                        self.stats['pages_exported'] += 1
                    except Exception as e:
                        print(f"   ❌ Error exporting {item.name}: {str(e)}")
                        self.stats['errors'] += 1
        
        # Also export root index.html
        root_index = self.html_dir / 'index.html'
        if root_index.exists():
            try:
                self._export_single_page(root_index, self.html_dir, is_root=True)
                self.stats['pages_exported'] += 1
            except Exception as e:
                print(f"   ❌ Error exporting root index: {str(e)}")
                self.stats['errors'] += 1
        
        return self.stats['pages_exported']
    
    def _export_single_page(self, html_file, page_dir, is_root=False):
        """Export a single page to markdown"""
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        metadata = self._extract_metadata(soup, html_file)
        
        # Extract main content
        content_html = self._extract_content_html(soup)
        
        # Convert to markdown
        markdown_content = self.converter.handle(content_html)
        markdown_content = self._clean_markdown(markdown_content)
        
        # Create frontmatter
        frontmatter = self._create_frontmatter(metadata)
        
        # Combine
        full_markdown = f"{frontmatter}\n\n{markdown_content}"
        
        # Determine output path
        if is_root:
            output_file = self.markdown_dir / 'index.md'
        else:
            relative_path = page_dir.relative_to(self.html_dir)
            output_dir = self.markdown_dir / relative_path
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / 'index.md'
        
        output_file.write_text(full_markdown, encoding='utf-8')
        print(f"   ✅ {output_file.relative_to(self.markdown_dir)}")
    
    def _extract_metadata(self, soup, html_file):
        """Extract metadata from HTML"""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            # Remove site name from title
            title = re.sub(r'\s*[-–|]\s*jameskilby.*$', '', title, flags=re.IGNORECASE)
            metadata['title'] = title
        
        # Also check for H1 (more accurate for posts)
        h1 = soup.find('h1', class_=re.compile(r'entry-title', re.I))
        if h1:
            metadata['title'] = h1.get_text().strip()
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
        
        # Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image:
            metadata['image'] = og_image.get('content', '')
        
        # Extract dates from JSON-LD
        dates = self._extract_dates_from_jsonld(soup)
        if dates:
            metadata.update(dates)
        
        # Categories
        categories = []
        cat_links = soup.find_all('a', href=re.compile(r'/category/'))
        for link in cat_links:
            cat_text = link.get_text().strip()
            if cat_text and cat_text not in categories:
                categories.append(cat_text)
        if categories:
            metadata['categories'] = categories
        
        # Tags
        tags = []
        tag_links = soup.find_all('a', href=re.compile(r'/tag/'))
        for link in tag_links:
            tag_text = link.get_text().strip()
            if tag_text and tag_text not in tags:
                tags.append(tag_text)
        if tags:
            metadata['tags'] = tags
        
        # Author
        author_elem = soup.find('a', class_=re.compile(r'author', re.I))
        if author_elem:
            metadata['author'] = author_elem.get_text().strip()
        else:
            metadata['author'] = 'James Kilby'
        
        # URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            metadata['url'] = canonical.get('href', '')
        else:
            # Construct from file path
            relative_path = html_file.parent.relative_to(self.html_dir)
            if relative_path == Path('.'):
                metadata['url'] = self.base_url + '/'
            else:
                metadata['url'] = f"{self.base_url}/{relative_path}/"
        
        return metadata
    
    def _extract_dates_from_jsonld(self, soup):
        """Extract dates from JSON-LD structured data"""
        dates = {}
        
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                try:
                    data = json.loads(script.string)
                    
                    # Handle @graph structure
                    items = data.get('@graph', [data]) if '@graph' in data else [data]
                    
                    for item in items:
                        if isinstance(item, dict):
                            item_type = item.get('@type')
                            if item_type in ['BlogPosting', 'Article', 'WebPage']:
                                if 'datePublished' in item:
                                    dates['date_published'] = item['datePublished']
                                if 'dateModified' in item:
                                    dates['date_modified'] = item['dateModified']
                                if 'wordCount' in item:
                                    dates['word_count'] = item['wordCount']
                                if 'timeRequired' in item:
                                    dates['reading_time'] = item['timeRequired']
                                
                                # Break after finding first article
                                if dates:
                                    break
                    
                    if dates:
                        break
                        
                except (json.JSONDecodeError, Exception):
                    continue
        
        return dates
    
    def _extract_content_html(self, soup):
        """Extract main content HTML"""
        # Try multiple selectors for content
        content_selectors = [
            ('article', {'class': re.compile(r'entry-content|post-content', re.I)}),
            ('div', {'class': re.compile(r'entry-content|post-content|content', re.I)}),
            ('main', {}),
            ('article', {})
        ]
        
        content_div = None
        for tag, attrs in content_selectors:
            content_div = soup.find(tag, attrs)
            if content_div:
                break
        
        if not content_div:
            # Fallback to body
            content_div = soup.find('body')
        
        if not content_div:
            return ""
        
        # Clone to avoid modifying original
        content_copy = BeautifulSoup(str(content_div), 'html.parser')
        
        # Remove unwanted elements
        unwanted_selectors = [
            'script', 'style', 'nav', 'footer', 'aside',
            {'class': re.compile(r'comment|share|social|sidebar|navigation', re.I)},
            {'id': re.compile(r'comment|share|social|sidebar|navigation', re.I)}
        ]
        
        for selector in unwanted_selectors:
            if isinstance(selector, str):
                for element in content_copy.find_all(selector):
                    element.decompose()
            else:
                for element in content_copy.find_all(attrs=selector):
                    element.decompose()
        
        return str(content_copy)
    
    def _clean_markdown(self, markdown):
        """Clean up converted markdown"""
        # Remove excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Fix image paths (make them absolute)
        markdown = re.sub(
            r'!\[([^\]]*)\]\((/[^)]+)\)',
            rf'![\1]({self.base_url}\2)',
            markdown
        )
        
        # Fix relative links (make them absolute)
        markdown = re.sub(
            r'\[([^\]]+)\]\((/[^)]+)\)',
            rf'[\1]({self.base_url}\2)',
            markdown
        )
        
        # Remove HTML comments
        markdown = re.sub(r'<!--.*?-->', '', markdown, flags=re.DOTALL)
        
        # Clean up code blocks
        markdown = re.sub(r'```\s*\n\s*```', '', markdown)
        
        # Strip leading/trailing whitespace
        markdown = markdown.strip()
        
        return markdown
    
    def _create_frontmatter(self, metadata):
        """Create YAML frontmatter"""
        frontmatter = ['---']
        
        # Add metadata in consistent order
        if 'title' in metadata:
            frontmatter.append(f"title: \"{metadata['title']}\"")
        
        if 'description' in metadata:
            frontmatter.append(f"description: \"{metadata['description']}\"")
        
        if 'date_published' in metadata:
            frontmatter.append(f"date: {metadata['date_published']}")
        
        if 'date_modified' in metadata:
            frontmatter.append(f"modified: {metadata['date_modified']}")
        
        if 'author' in metadata:
            frontmatter.append(f"author: {metadata['author']}")
        
        if 'categories' in metadata:
            frontmatter.append(f"categories:")
            for cat in metadata['categories']:
                frontmatter.append(f"  - {cat}")
        
        if 'tags' in metadata:
            frontmatter.append(f"tags:")
            for tag in metadata['tags']:
                frontmatter.append(f"  - {tag}")
        
        if 'url' in metadata:
            frontmatter.append(f"url: {metadata['url']}")
        
        if 'image' in metadata:
            frontmatter.append(f"image: {metadata['image']}")
        
        if 'word_count' in metadata:
            frontmatter.append(f"word_count: {metadata['word_count']}")
        
        if 'reading_time' in metadata:
            frontmatter.append(f"reading_time: {metadata['reading_time']}")
        
        frontmatter.append('---')
        
        return '\n'.join(frontmatter)
    
    def _create_markdown_index(self):
        """Create index of all markdown files"""
        print("\n📋 Creating markdown index...")
        
        index_data = {
            'generated': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'total_files': self.stats['posts_exported'] + self.stats['pages_exported'],
            'posts': [],
            'pages': []
        }
        
        # Index posts
        posts_dir = self.markdown_dir / 'posts'
        if posts_dir.exists():
            for md_file in sorted(posts_dir.glob('*.md')):
                # Extract frontmatter
                content = md_file.read_text(encoding='utf-8')
                frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                
                if frontmatter_match:
                    try:
                        fm = yaml.safe_load(frontmatter_match.group(1))
                        # Convert date to string if it's a datetime object
                        date_value = fm.get('date', '')
                        if isinstance(date_value, datetime):
                            date_value = date_value.strftime('%Y-%m-%dT%H:%M:%SZ')
                        
                        index_data['posts'].append({
                            'file': f"posts/{md_file.name}",
                            'title': fm.get('title', ''),
                            'date': date_value,
                            'url': fm.get('url', '')
                        })
                    except:
                        pass
        
        # Save index
        index_file = self.markdown_dir / 'index.json'
        index_file.write_text(json.dumps(index_data, indent=2, ensure_ascii=False))
        
        print(f"   ✅ Created index: {index_file}")
    
    def _create_markdown_sitemap(self):
        """Create sitemap of markdown files"""
        print("🗺️  Creating markdown sitemap...")
        
        sitemap_lines = ['# Markdown Content Sitemap\n']
        sitemap_lines.append(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        sitemap_lines.append(f'Total Files: {self.stats["posts_exported"] + self.stats["pages_exported"]}\n')
        
        # List posts
        sitemap_lines.append('## Blog Posts\n')
        posts_dir = self.markdown_dir / 'posts'
        if posts_dir.exists():
            for md_file in sorted(posts_dir.glob('*.md'), reverse=True):
                content = md_file.read_text(encoding='utf-8')
                frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                
                if frontmatter_match:
                    try:
                        fm = yaml.safe_load(frontmatter_match.group(1))
                        title = fm.get('title', md_file.stem)
                        url = fm.get('url', '')
                        date = fm.get('date', '')
                        
                        sitemap_lines.append(f"- [{title}]({url}) - {date}")
                        sitemap_lines.append(f"  - Markdown: `/markdown/posts/{md_file.name}`\n")
                    except:
                        sitemap_lines.append(f"- {md_file.name}\n")
        
        # Save sitemap
        sitemap_file = self.markdown_dir / 'SITEMAP.md'
        sitemap_file.write_text('\n'.join(sitemap_lines))
        
        print(f"   ✅ Created sitemap: {sitemap_file}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python markdown_exporter.py <html_directory> <markdown_output_directory> [base_url]")
        print("Example: python markdown_exporter.py ./public ./public/markdown https://jameskilby.co.uk")
        sys.exit(1)
    
    html_dir = sys.argv[1]
    markdown_dir = sys.argv[2]
    base_url = sys.argv[3] if len(sys.argv) > 3 else 'https://jameskilby.co.uk'
    
    if not Path(html_dir).exists():
        print(f"❌ Error: HTML directory '{html_dir}' does not exist")
        sys.exit(1)
    
    # Create exporter
    exporter = MarkdownExporter(html_dir, markdown_dir, base_url)
    
    # Export all content
    exporter.export_all_content()
    
    print(f"\n💡 Access markdown files:")
    print(f"   - All posts: {markdown_dir}/posts/")
    print(f"   - Index: {markdown_dir}/index.json")
    print(f"   - Sitemap: {markdown_dir}/SITEMAP.md")

if __name__ == '__main__':
    main()
