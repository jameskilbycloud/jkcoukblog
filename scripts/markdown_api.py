#!/usr/bin/env python3
"""
Markdown API Generator
Creates JSON API endpoints for markdown content
"""

import json
from pathlib import Path
from datetime import datetime
import yaml
import re

class MarkdownAPIGenerator:
    def __init__(self, markdown_dir, api_dir):
        self.markdown_dir = Path(markdown_dir)
        self.api_dir = Path(api_dir)
        self.api_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_api(self):
        """Generate complete API structure"""
        print("🔌 Generating Markdown API...")
        
        # Generate list endpoints
        self._generate_posts_list()
        self._generate_posts_by_category()
        self._generate_posts_by_tag()
        self._generate_posts_by_date()
        
        # Generate individual post endpoints
        self._generate_individual_posts()
        
        # Generate API index
        self._generate_api_index()
        
        print("✅ Markdown API generated successfully!")
    
    def _generate_posts_list(self):
        """Generate /api/posts.json endpoint"""
        posts = []
        posts_dir = self.markdown_dir / 'posts'
        
        if posts_dir.exists():
            for md_file in sorted(posts_dir.glob('*.md'), reverse=True):
                post_data = self._parse_markdown_file(md_file)
                if post_data:
                    posts.append(post_data)
        
        # Save complete list
        output_file = self.api_dir / 'posts.json'
        output_file.write_text(json.dumps(posts, indent=2, ensure_ascii=False))
        
        # Also save paginated versions
        page_size = 10
        for i in range(0, len(posts), page_size):
            page_num = (i // page_size) + 1
            page_posts = posts[i:i+page_size]
            
            page_data = {
                'posts': page_posts,
                'page': page_num,
                'per_page': page_size,
                'total': len(posts),
                'total_pages': (len(posts) + page_size - 1) // page_size
            }
            
            page_file = self.api_dir / f'posts-page-{page_num}.json'
            page_file.write_text(json.dumps(page_data, indent=2, ensure_ascii=False))
        
        print(f"   📄 Generated posts list ({len(posts)} posts)")
    
    def _generate_posts_by_category(self):
        """Generate /api/categories/*.json endpoints"""
        categories_dir = self.api_dir / 'categories'
        categories_dir.mkdir(exist_ok=True)
        
        categories = {}
        posts_dir = self.markdown_dir / 'posts'
        
        if posts_dir.exists():
            for md_file in posts_dir.glob('*.md'):
                post_data = self._parse_markdown_file(md_file)
                if post_data and 'categories' in post_data:
                    for category in post_data['categories']:
                        # Skip None or empty categories
                        if not category:
                            continue
                        slug = self._slugify(category)
                        if slug not in categories:
                            categories[slug] = {
                                'name': category,
                                'slug': slug,
                                'posts': []
                            }
                        categories[slug]['posts'].append(post_data)
        
        # Save each category
        for slug, data in categories.items():
            output_file = categories_dir / f'{slug}.json'
            output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Save categories index
        categories_index = [
            {'name': data['name'], 'slug': slug, 'count': len(data['posts'])}
            for slug, data in categories.items()
        ]
        
        index_file = categories_dir / 'index.json'
        index_file.write_text(json.dumps(categories_index, indent=2, ensure_ascii=False))
        
        print(f"   📁 Generated {len(categories)} category endpoints")
    
    def _generate_posts_by_tag(self):
        """Generate /api/tags/*.json endpoints"""
        tags_dir = self.api_dir / 'tags'
        tags_dir.mkdir(exist_ok=True)
        
        tags = {}
        posts_dir = self.markdown_dir / 'posts'
        
        if posts_dir.exists():
            for md_file in posts_dir.glob('*.md'):
                post_data = self._parse_markdown_file(md_file)
                if post_data and 'tags' in post_data:
                    for tag in post_data['tags']:
                        # Skip None or empty tags
                        if not tag:
                            continue
                        slug = self._slugify(tag)
                        if slug not in tags:
                            tags[slug] = {
                                'name': tag,
                                'slug': slug,
                                'posts': []
                            }
                        tags[slug]['posts'].append(post_data)
        
        # Save each tag
        for slug, data in tags.items():
            output_file = tags_dir / f'{slug}.json'
            output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Save tags index
        tags_index = [
            {'name': data['name'], 'slug': slug, 'count': len(data['posts'])}
            for slug, data in tags.items()
        ]
        
        index_file = tags_dir / 'index.json'
        index_file.write_text(json.dumps(tags_index, indent=2, ensure_ascii=False))
        
        print(f"   🏷️  Generated {len(tags)} tag endpoints")
    
    def _generate_posts_by_date(self):
        """Generate /api/archive/*.json endpoints"""
        archive_dir = self.api_dir / 'archive'
        archive_dir.mkdir(exist_ok=True)
        
        archives = {}
        posts_dir = self.markdown_dir / 'posts'
        
        if posts_dir.exists():
            for md_file in posts_dir.glob('*.md'):
                post_data = self._parse_markdown_file(md_file)
                if post_data and 'date' in post_data:
                    try:
                        date = datetime.fromisoformat(post_data['date'].replace('Z', '+00:00'))
                        year_month = date.strftime('%Y-%m')
                        
                        if year_month not in archives:
                            archives[year_month] = {
                                'year': date.year,
                                'month': date.month,
                                'month_name': date.strftime('%B'),
                                'posts': []
                            }
                        archives[year_month]['posts'].append(post_data)
                    except:
                        pass
        
        # Save each month
        for year_month, data in archives.items():
            output_file = archive_dir / f'{year_month}.json'
            output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Save archive index
        archive_index = [
            {
                'year_month': ym,
                'year': data['year'],
                'month': data['month'],
                'month_name': data['month_name'],
                'count': len(data['posts'])
            }
            for ym, data in sorted(archives.items(), reverse=True)
        ]
        
        index_file = archive_dir / 'index.json'
        index_file.write_text(json.dumps(archive_index, indent=2, ensure_ascii=False))
        
        print(f"   📅 Generated {len(archives)} archive endpoints")
    
    def _generate_individual_posts(self):
        """Generate individual post JSON files"""
        posts_api_dir = self.api_dir / 'posts'
        posts_api_dir.mkdir(exist_ok=True)
        
        posts_dir = self.markdown_dir / 'posts'
        count = 0
        
        if posts_dir.exists():
            for md_file in posts_dir.glob('*.md'):
                post_data = self._parse_markdown_file(md_file, include_content=True)
                if post_data:
                    slug = md_file.stem
                    output_file = posts_api_dir / f'{slug}.json'
                    output_file.write_text(json.dumps(post_data, indent=2, ensure_ascii=False))
                    count += 1
        
        print(f"   📝 Generated {count} individual post endpoints")
    
    def _generate_api_index(self):
        """Generate API documentation/index"""
        api_docs = {
            'version': '1.0',
            'generated': datetime.now().isoformat(),
            'base_url': '/api',
            'endpoints': {
                'posts': {
                    'all': '/api/posts.json',
                    'paginated': '/api/posts-page-{page}.json',
                    'single': '/api/posts/{slug}.json',
                    'description': 'All blog posts with metadata and content'
                },
                'categories': {
                    'index': '/api/categories/index.json',
                    'single': '/api/categories/{slug}.json',
                    'description': 'Posts grouped by category'
                },
                'tags': {
                    'index': '/api/tags/index.json',
                    'single': '/api/tags/{slug}.json',
                    'description': 'Posts grouped by tag'
                },
                'archive': {
                    'index': '/api/archive/index.json',
                    'single': '/api/archive/{year}-{month}.json',
                    'description': 'Posts grouped by month/year'
                }
            },
            'content_format': {
                'markdown': {
                    'raw': '/markdown/posts/{slug}.md',
                    'description': 'Raw markdown with frontmatter'
                },
                'html': {
                    'url': '/{year}/{month}/{slug}/',
                    'description': 'Rendered HTML page'
                }
            }
        }
        
        index_file = self.api_dir / 'index.json'
        index_file.write_text(json.dumps(api_docs, indent=2, ensure_ascii=False))
        
        # Also create a human-readable markdown version
        readme_lines = ['# Markdown Content API\n']
        readme_lines.append(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        readme_lines.append('## Endpoints\n')
        readme_lines.append('### Posts')
        readme_lines.append('- All posts: `/api/posts.json`')
        readme_lines.append('- Paginated: `/api/posts-page-{page}.json`')
        readme_lines.append('- Single post: `/api/posts/{slug}.json`\n')
        readme_lines.append('### Categories')
        readme_lines.append('- All categories: `/api/categories/index.json`')
        readme_lines.append('- Category posts: `/api/categories/{slug}.json`\n')
        readme_lines.append('### Tags')
        readme_lines.append('- All tags: `/api/tags/index.json`')
        readme_lines.append('- Tag posts: `/api/tags/{slug}.json`\n')
        readme_lines.append('### Archive')
        readme_lines.append('- All months: `/api/archive/index.json`')
        readme_lines.append('- Month posts: `/api/archive/{year}-{month}.json`\n')
        readme_lines.append('## Content Formats')
        readme_lines.append('- Markdown: `/markdown/posts/{slug}.md`')
        readme_lines.append('- HTML: `/{year}/{month}/{slug}/`')
        
        readme_file = self.api_dir / 'README.md'
        readme_file.write_text('\n'.join(readme_lines))
        
        print(f"   📖 Generated API documentation")
    
    def _parse_markdown_file(self, md_file, include_content=False):
        """Parse markdown file and extract metadata"""
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Extract frontmatter
            frontmatter_match = re.search(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
            
            if not frontmatter_match:
                return None
            
            frontmatter_str = frontmatter_match.group(1)
            body = frontmatter_match.group(2).strip()
            
            # Parse YAML frontmatter
            try:
                metadata = yaml.safe_load(frontmatter_str)
            except yaml.YAMLError as ye:
                print(f"   ⚠️  YAML parsing error in {md_file.name}: {str(ye)}")
                return None
            
            # Convert datetime objects to strings for JSON serialization
            date_value = metadata.get('date', '')
            if isinstance(date_value, datetime):
                date_value = date_value.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            modified_value = metadata.get('modified', '')
            if isinstance(modified_value, datetime):
                modified_value = modified_value.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Create post data
            post_data = {
                'slug': md_file.stem,
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'date': date_value,
                'modified': modified_value,
                'author': metadata.get('author', 'James Kilby'),
                'url': metadata.get('url', ''),
                'markdown_url': f"/markdown/posts/{md_file.name}",
                'api_url': f"/api/posts/{md_file.stem}.json"
            }
            
            # Optional fields
            if 'categories' in metadata:
                post_data['categories'] = metadata['categories']
            
            if 'tags' in metadata:
                post_data['tags'] = metadata['tags']
            
            if 'image' in metadata:
                post_data['image'] = metadata['image']
            
            if 'word_count' in metadata:
                post_data['word_count'] = metadata['word_count']
            
            if 'reading_time' in metadata:
                post_data['reading_time'] = metadata['reading_time']
            
            # Include full content if requested
            if include_content:
                post_data['content'] = body
                post_data['excerpt'] = body[:300] + '...' if len(body) > 300 else body
            else:
                # Just include excerpt
                post_data['excerpt'] = body[:300] + '...' if len(body) > 300 else body
            
            return post_data
            
        except Exception as e:
            print(f"   ⚠️  Error parsing {md_file.name}: {str(e)}")
            return None
    
    def _slugify(self, text):
        """Convert text to URL-friendly slug"""
        if not text:
            return 'untitled'
        text = str(text).lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text if text else 'untitled'


def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python generate_markdown_api.py <markdown_directory> <api_output_directory>")
        print("Example: python generate_markdown_api.py ./public/markdown ./public/api")
        sys.exit(1)
    
    markdown_dir = sys.argv[1]
    api_dir = sys.argv[2]
    
    if not Path(markdown_dir).exists():
        print(f"❌ Error: Markdown directory '{markdown_dir}' does not exist")
        sys.exit(1)
    
    generator = MarkdownAPIGenerator(markdown_dir, api_dir)
    generator.generate_api()
    
    print(f"\n💡 API endpoints available:")
    print(f"   - Documentation: {api_dir}/README.md")
    print(f"   - All posts: {api_dir}/posts.json")
    print(f"   - Categories: {api_dir}/categories/")
    print(f"   - Tags: {api_dir}/tags/")
    print(f"   - Archive: {api_dir}/archive/")

if __name__ == '__main__':
    main()
