#!/usr/bin/env python3
"""
Extract Inline CSS to External Files
Extracts inline <style> blocks from HTML files and moves them to external CSS files
"""

import os
import sys
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup

class InlineCSSExtractor:
    def __init__(self, public_dir):
        self.public_dir = Path(public_dir)
        self.css_output_dir = self.public_dir / 'assets' / 'css'
        self.css_output_dir.mkdir(parents=True, exist_ok=True)
        self.css_files_created = {}
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'css_files_created': 0,
            'bytes_saved': 0
        }
    
    def extract_css_from_html_files(self):
        """Extract inline CSS from all HTML files"""
        print("🎨 Extracting inline CSS from HTML files...")
        
        # Find all HTML files
        html_files = list(self.public_dir.rglob('*.html'))
        print(f"   Found {len(html_files)} HTML files")
        
        for html_file in html_files:
            self.process_html_file(html_file)
        
        # Print statistics
        print(f"\n📊 Extraction Complete:")
        print(f"   Files processed: {self.stats['files_processed']}")
        print(f"   Files modified: {self.stats['files_modified']}")
        print(f"   CSS files created: {self.stats['css_files_created']}")
        print(f"   Bytes saved from HTML: {self.stats['bytes_saved']:,}")
        print(f"   Reduction: {self.stats['bytes_saved'] / 1024:.1f} KB")
    
    def process_html_file(self, html_file):
        """Process a single HTML file"""
        self.stats['files_processed'] += 1
        
        try:
            # Read HTML content
            html_content = html_file.read_text(encoding='utf-8')
            original_size = len(html_content)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all inline style tags
            style_tags = soup.find_all('style')
            
            if not style_tags:
                return
            
            modified = False
            head = soup.find('head')
            
            for style_tag in style_tags:
                # Skip empty style tags
                if not style_tag.string or not style_tag.string.strip():
                    continue
                
                # Get style ID if present
                style_id = style_tag.get('id', 'inline-styles')
                css_content = style_tag.string
                
                # Skip very small CSS blocks (< 100 bytes)
                if len(css_content) < 100:
                    continue
                
                # Create a hash of the CSS content for deduplication
                css_hash = hashlib.md5(css_content.encode()).hexdigest()[:8]
                
                # Check if we've already created a file for this CSS content
                if css_hash in self.css_files_created:
                    css_filename = self.css_files_created[css_hash]
                else:
                    # Create external CSS file
                    css_filename = f"{style_id}-{css_hash}.min.css"
                    css_file_path = self.css_output_dir / css_filename
                    
                    # Write CSS to external file
                    css_file_path.write_text(css_content, encoding='utf-8')
                    self.css_files_created[css_hash] = css_filename
                    self.stats['css_files_created'] += 1
                    print(f"   📄 Created: /assets/css/{css_filename}")
                
                # Calculate path from current HTML file to CSS file
                css_path = self.get_relative_path(html_file, self.css_output_dir / css_filename)
                
                # Create link tag to replace inline style
                link_tag = soup.new_tag('link')
                link_tag['rel'] = 'stylesheet'
                link_tag['href'] = css_path
                link_tag['media'] = 'all'
                
                # Replace inline style with link tag
                style_tag.replace_with(link_tag)
                modified = True
            
            if modified:
                # Write modified HTML back to file
                new_html = str(soup)
                html_file.write_text(new_html, encoding='utf-8')
                
                new_size = len(new_html)
                bytes_saved = original_size - new_size
                self.stats['bytes_saved'] += bytes_saved
                self.stats['files_modified'] += 1
                
                print(f"   ✅ {html_file.relative_to(self.public_dir)} (-{bytes_saved:,} bytes)")
        
        except Exception as e:
            print(f"   ❌ Error processing {html_file}: {e}")
    
    def get_relative_path(self, from_file, to_file):
        """Calculate relative path from one file to another"""
        try:
            # Get the directory containing the HTML file
            from_dir = from_file.parent
            
            # Calculate relative path
            rel_path = os.path.relpath(to_file, from_dir)
            
            # Convert backslashes to forward slashes (Windows)
            rel_path = rel_path.replace('\\', '/')
            
            return rel_path
        except Exception:
            # Fall back to absolute path from site root
            abs_path = to_file.relative_to(self.public_dir)
            return f"/{abs_path}".replace('\\', '/')

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_inline_css.py <public_directory>")
        print("Example: python3 extract_inline_css.py ./public")
        sys.exit(1)
    
    public_dir = sys.argv[1]
    
    if not Path(public_dir).exists():
        print(f"❌ Error: Directory '{public_dir}' does not exist")
        sys.exit(1)
    
    extractor = InlineCSSExtractor(public_dir)
    extractor.extract_css_from_html_files()
    
    print("\n✅ Done! Inline CSS has been extracted to external files.")
    print("   Remember to regenerate the site if making this a permanent change.")

if __name__ == '__main__':
    main()
