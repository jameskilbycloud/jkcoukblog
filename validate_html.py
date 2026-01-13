#!/usr/bin/env python3
"""
HTML validation script for static site build validation.

This script validates the generated static site before deployment:
- Checks for broken internal links
- Validates all assets exist (images, CSS, JS)
- Verifies HTML structure
- Checks for missing alt attributes
- Validates relative paths are correct
"""

import os
import sys
import re
from pathlib import Path
from typing import Set, List, Dict, Tuple
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
import argparse


class HTMLValidator:
    """Validate HTML files in a static site directory."""
    
    def __init__(self, site_dir: str, verbose: bool = False):
        self.site_dir = Path(site_dir).resolve()
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.html_files: Set[Path] = set()
        self.asset_files: Set[Path] = set()
        
    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        print(f"❌ ERROR: {message}")
        
    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")
        
    def log_info(self, message: str):
        """Log info message."""
        if self.verbose:
            print(f"ℹ️  {message}")
            
    def log_success(self, message: str):
        """Log success message."""
        print(f"✅ {message}")
        
    def discover_files(self):
        """Discover all HTML and asset files in the site directory."""
        print("\n🔍 Discovering files...")
        
        # Find all HTML files
        for html_file in self.site_dir.rglob("*.html"):
            self.html_files.add(html_file)
            
        # Find all asset files (images, CSS, JS, fonts)
        asset_patterns = ["*.css", "*.js", "*.png", "*.jpg", "*.jpeg", "*.gif", 
                         "*.svg", "*.webp", "*.avif", "*.woff", "*.woff2", 
                         "*.ttf", "*.eot", "*.ico", "*.xml", "*.json"]
        
        for pattern in asset_patterns:
            for asset_file in self.site_dir.rglob(pattern):
                self.asset_files.add(asset_file)
                
        self.log_info(f"Found {len(self.html_files)} HTML files")
        self.log_info(f"Found {len(self.asset_files)} asset files")
        
    def normalize_path(self, url: str, current_file: Path) -> Path:
        """
        Normalize a URL/path relative to the current file.
        Returns the expected absolute path in the filesystem.
        """
        # Parse URL
        parsed = urlparse(url)
        
        # Skip external URLs
        if parsed.scheme in ['http', 'https', 'mailto', 'tel', 'data']:
            return None
            
        # Skip fragments and empty
        if not parsed.path or parsed.path == '#':
            return None
            
        # Get the path component
        path = unquote(parsed.path)
        
        # Remove leading slash for relative resolution
        if path.startswith('/'):
            # Absolute path from site root
            target_path = self.site_dir / path.lstrip('/')
        else:
            # Relative path from current file's directory
            target_path = (current_file.parent / path).resolve()
            
        return target_path
        
    def file_exists(self, path: Path) -> bool:
        """Check if a file exists, trying various extensions for HTML files."""
        if path.exists():
            return True
            
        # Try adding .html
        if path.with_suffix('.html').exists():
            return True
            
        # Try as directory with index.html
        if path.is_dir() and (path / 'index.html').exists():
            return True
        if (path / 'index.html').exists():
            return True
            
        return False
        
    def validate_html_structure(self, html_file: Path) -> bool:
        """Validate basic HTML structure."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for basic structure
            if not soup.find('html'):
                self.log_error(f"{html_file.relative_to(self.site_dir)}: Missing <html> tag")
                return False
                
            if not soup.find('head'):
                self.log_error(f"{html_file.relative_to(self.site_dir)}: Missing <head> tag")
                return False
                
            if not soup.find('body'):
                self.log_error(f"{html_file.relative_to(self.site_dir)}: Missing <body> tag")
                return False
                
            # Check for title
            if not soup.find('title'):
                self.log_warning(f"{html_file.relative_to(self.site_dir)}: Missing <title> tag")
                
            return True
            
        except Exception as e:
            self.log_error(f"{html_file.relative_to(self.site_dir)}: Failed to parse HTML - {e}")
            return False
            
    def validate_links(self, html_file: Path) -> bool:
        """Validate all internal links in an HTML file."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            soup = BeautifulSoup(content, 'html.parser')
            all_good = True
            
            # Check all <a> tags
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Skip external links, mailto, tel, and fragments
                if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
                    continue
                    
                target_path = self.normalize_path(href, html_file)
                if target_path is None:
                    continue
                    
                if not self.file_exists(target_path):
                    rel_source = html_file.relative_to(self.site_dir)
                    self.log_error(f"{rel_source}: Broken link to '{href}'")
                    all_good = False
                    
            return all_good
            
        except Exception as e:
            self.log_error(f"{html_file.relative_to(self.site_dir)}: Failed to validate links - {e}")
            return False
            
    def validate_assets(self, html_file: Path) -> bool:
        """Validate all assets referenced in an HTML file."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            soup = BeautifulSoup(content, 'html.parser')
            all_good = True
            
            # Check images
            for img in soup.find_all('img', src=True):
                src = img['src']
                
                # Skip external images and data URIs
                if src.startswith(('http://', 'https://', 'data:')):
                    continue
                    
                target_path = self.normalize_path(src, html_file)
                if target_path is None:
                    continue
                    
                if not target_path.exists():
                    rel_source = html_file.relative_to(self.site_dir)
                    self.log_error(f"{rel_source}: Missing image '{src}'")
                    all_good = False
                    
                # Check for alt attribute
                if not img.get('alt'):
                    rel_source = html_file.relative_to(self.site_dir)
                    self.log_warning(f"{rel_source}: Image missing alt attribute: '{src}'")
                    
            # Check picture source elements
            for source in soup.find_all('source', srcset=True):
                srcset = source['srcset']
                # Parse srcset (can have multiple sources with sizes)
                for src_item in srcset.split(','):
                    src = src_item.strip().split()[0]  # Get just the URL part
                    
                    if src.startswith(('http://', 'https://', 'data:')):
                        continue
                        
                    target_path = self.normalize_path(src, html_file)
                    if target_path is None:
                        continue
                        
                    if not target_path.exists():
                        rel_source = html_file.relative_to(self.site_dir)
                        self.log_error(f"{rel_source}: Missing source image '{src}'")
                        all_good = False
                        
            # Check CSS files
            for link in soup.find_all('link', rel='stylesheet', href=True):
                href = link['href']
                
                # Skip external URLs (including protocol-relative URLs)
                if href.startswith(('http://', 'https://', '//')):
                    continue
                    
                target_path = self.normalize_path(href, html_file)
                if target_path is None:
                    continue
                    
                if not target_path.exists():
                    rel_source = html_file.relative_to(self.site_dir)
                    self.log_error(f"{rel_source}: Missing CSS file '{href}'")
                    all_good = False
                    
            # Check JavaScript files
            for script in soup.find_all('script', src=True):
                src = script['src']
                
                # Skip external URLs (including protocol-relative URLs)
                if src.startswith(('http://', 'https://', '//')):
                    continue
                    
                target_path = self.normalize_path(src, html_file)
                if target_path is None:
                    continue
                    
                if not target_path.exists():
                    rel_source = html_file.relative_to(self.site_dir)
                    self.log_error(f"{rel_source}: Missing JavaScript file '{src}'")
                    all_good = False
                    
            return all_good
            
        except Exception as e:
            self.log_error(f"{html_file.relative_to(self.site_dir)}: Failed to validate assets - {e}")
            return False
            
    def validate_css_assets(self, css_file: Path) -> bool:
        """Validate assets referenced in CSS files (fonts, images)."""
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            all_good = True
            
            # Find all url() references
            url_pattern = re.compile(r'url\(["\']?([^"\'()]+)["\']?\)', re.IGNORECASE)
            
            for match in url_pattern.finditer(content):
                url = match.group(1)
                
                # Skip external URLs and data URIs
                if url.startswith(('http://', 'https://', 'data:', '//')):
                    continue
                    
                target_path = self.normalize_path(url, css_file)
                if target_path is None:
                    continue
                    
                if not target_path.exists():
                    rel_source = css_file.relative_to(self.site_dir)
                    self.log_error(f"{rel_source}: Missing asset '{url}'")
                    all_good = False
                    
            return all_good
            
        except Exception as e:
            self.log_error(f"{css_file.relative_to(self.site_dir)}: Failed to validate CSS assets - {e}")
            return False
            
    def run_validation(self) -> bool:
        """Run all validation checks."""
        print("=" * 70)
        print("🚀 Starting HTML Validation")
        print(f"📁 Directory: {self.site_dir}")
        print("=" * 70)
        
        # Discover all files
        self.discover_files()
        
        if not self.html_files:
            self.log_error("No HTML files found!")
            return False
            
        # Validate each HTML file
        print("\n🔍 Validating HTML files...")
        for html_file in sorted(self.html_files):
            self.log_info(f"Checking {html_file.relative_to(self.site_dir)}")
            self.validate_html_structure(html_file)
            self.validate_links(html_file)
            self.validate_assets(html_file)
            
        # Validate CSS files for missing assets
        print("\n🔍 Validating CSS files...")
        css_files = [f for f in self.asset_files if f.suffix == '.css']
        for css_file in sorted(css_files):
            self.log_info(f"Checking {css_file.relative_to(self.site_dir)}")
            self.validate_css_assets(css_file)
            
        # Print summary
        print("\n" + "=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)
        print(f"📄 HTML files checked: {len(self.html_files)}")
        print(f"📦 Asset files found: {len(self.asset_files)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print("=" * 70)
        
        if self.errors:
            print("\n🚨 ERRORS FOUND:")
            for error in self.errors[:20]:  # Limit to first 20
                print(f"  • {error}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more errors")
                
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)} warning(s) found")
            if self.verbose:
                for warning in self.warnings[:10]:
                    print(f"  • {warning}")
                if len(self.warnings) > 10:
                    print(f"  ... and {len(self.warnings) - 10} more warnings")
                    
        if not self.errors:
            self.log_success("All validation checks passed!")
            return True
        else:
            print("\n❌ Validation failed with errors")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate HTML and assets in static site',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'site_dir',
        help='Path to the static site directory to validate'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.isdir(args.site_dir):
        print(f"❌ Error: Directory '{args.site_dir}' does not exist")
        sys.exit(1)
        
    validator = HTMLValidator(args.site_dir, verbose=args.verbose)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
