#!/usr/bin/env python3
"""
Search Index Generator for Static Site
Creates a JSON search index from static HTML files
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class SearchIndexGenerator:
    def __init__(self, site_dir, base_url="https://jameskilby.co.uk"):
        self.site_dir = Path(site_dir)
        self.base_url = base_url.rstrip('/')
        self.index = []
        
    def extract_text_content(self, html_content):
        """Extract clean text content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_metadata(self, soup, url_path):
        """Extract metadata from HTML"""
        # Title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "Untitled"
        
        # Clean up title (remove site name)
        title = re.sub(r'\s*[-–|]\s*jameskilby.*$', '', title, flags=re.IGNORECASE)
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ''
        
        # Extract excerpt from content
        if not description:
            # Try to find article content or entry content
            content_areas = soup.find_all(['div'], class_=re.compile(r'(content|entry|post|article)', re.I))
            if content_areas:
                content_text = self.extract_text_content(str(content_areas[0]))
                # Take first 150 words as excerpt
                words = content_text.split()
                description = ' '.join(words[:150]) + ('...' if len(words) > 150 else '')
        
        # Categories and tags
        categories = []
        tags = []
        
        # Look for category and tag links
        cat_links = soup.find_all('a', href=re.compile(r'/category/'))
        for link in cat_links:
            cat_text = link.get_text().strip()
            if cat_text and cat_text not in categories:
                categories.append(cat_text)
        
        tag_links = soup.find_all('a', href=re.compile(r'/tag/'))
        for link in tag_links:
            tag_text = link.get_text().strip()
            if tag_text and tag_text not in tags:
                tags.append(tag_text)
        
        # Date
        date = ""
        date_elem = soup.find('time', class_=re.compile(r'(entry-date|published)', re.I))
        if date_elem:
            date = date_elem.get('datetime', '') or date_elem.get_text().strip()
        
        return {
            'title': title,
            'description': description,
            'categories': categories,
            'tags': tags,
            'date': date
        }
    
    def process_html_file(self, file_path, url_path):
        """Process a single HTML file and add to index"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Skip if it's a redirect or error page
            if soup.find('meta', attrs={'http-equiv': 'refresh'}):
                return
            
            # Extract metadata
            metadata = self.extract_metadata(soup, url_path)
            
            # Skip if no meaningful title
            if not metadata['title'] or metadata['title'].lower() in ['untitled', 'page not found', '404']:
                return
            
            # Extract content
            content = self.extract_text_content(html_content)
            
            # Skip if content is too short (likely navigation pages)
            if len(content.split()) < 50:
                return
            
            # Create search entry
            entry = {
                'title': metadata['title'],
                'url': f"{self.base_url}{url_path}",
                'description': metadata['description'][:200],  # Limit description length
                'content': content[:1000],  # Limit content for searching
                'categories': metadata['categories'],
                'tags': metadata['tags'],
                'date': metadata['date']
            }
            
            self.index.append(entry)
            print(f"✅ Indexed: {metadata['title']}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
    
    def generate_index(self):
        """Generate search index from all HTML files"""
        print("🔍 Generating search index...")
        
        # Find all HTML files
        html_files = list(self.site_dir.rglob('*.html'))
        
        for html_file in html_files:
            # Convert file path to URL path
            rel_path = html_file.relative_to(self.site_dir)
            
            # Convert index.html files to directory URLs
            if rel_path.name == 'index.html':
                if rel_path.parent == Path('.'):
                    url_path = '/'
                else:
                    url_path = f'/{rel_path.parent}/'
            else:
                url_path = f'/{rel_path}'
            
            self.process_html_file(html_file, url_path)
        
        print(f"✅ Generated search index with {len(self.index)} entries")
        return self.index
    
    def save_index(self, output_file):
        """Save search index to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
        
        # Also create a minified version
        minified_file = output_file.replace('.json', '.min.json')
        with open(minified_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, separators=(',', ':'))
        
        print(f"💾 Search index saved to {output_file}")
        print(f"💾 Minified version saved to {minified_file}")

def main():
    """Main function to generate search index"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate search index for static site')
    parser.add_argument('site_dir', help='Directory containing static site files')
    parser.add_argument('--output', '-o', default='search-index.json', help='Output file for search index')
    parser.add_argument('--base-url', default='https://jameskilby.co.uk', help='Base URL for the site')
    
    args = parser.parse_args()
    
    generator = SearchIndexGenerator(args.site_dir, args.base_url)
    generator.generate_index()
    
    output_path = Path(args.site_dir) / args.output
    generator.save_index(output_path)

if __name__ == '__main__':
    main()