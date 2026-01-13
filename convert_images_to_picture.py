#!/usr/bin/env python3
"""
Convert <img> tags to <picture> elements with AVIF and WebP sources
Processes HTML files to add modern image format support
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple
from bs4 import BeautifulSoup


class ImageToPictureConverter:
    """Converts img tags to picture elements with AVIF/WebP sources"""
    
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.stats = {
            'files_processed': 0,
            'images_converted': 0,
            'images_skipped': 0,
        }
        self.debug_count = 0  # For debugging first few images
    
    def _has_modern_format(self, img_src: str, base_path: Path) -> Tuple[bool, bool]:
        """Check if AVIF and WebP versions exist for an image"""
        if not img_src or img_src.startswith(('http://', 'https://', 'data:', '//')):
            return False, False
        
        # Remove leading slash for local path resolution
        img_path = img_src.lstrip('/')
        full_path = base_path / img_path
        
        # Debug first few images
        if self.debug_count < 3:
            self.debug_count += 1
            print(f"\n🔍 DEBUG Image #{self.debug_count}:")
            print(f"   img_src: {img_src}")
            print(f"   img_path: {img_path}")
            print(f"   full_path: {full_path}")
            print(f"   full_path exists: {full_path.exists()}")
        
        if not full_path.exists():
            if self.debug_count <= 3:
                print(f"   ⚠️  Original image not found!")
            return False, False
        
        # Check for AVIF and WebP versions
        avif_path = full_path.with_suffix('.avif')
        webp_path = full_path.with_suffix('.webp')
        
        if self.debug_count <= 3:
            print(f"   avif_path: {avif_path}")
            print(f"   avif exists: {avif_path.exists()}")
            print(f"   webp_path: {webp_path}")
            print(f"   webp exists: {webp_path.exists()}")
        
        return avif_path.exists(), webp_path.exists()
    
    def _should_convert_img(self, img) -> bool:
        """Determine if an img tag should be converted"""
        # Skip if already inside a picture element
        if img.parent and img.parent.name == 'picture':
            return False
        
        # Skip if it's a data URI or external image
        src = img.get('src', '')
        if not src or src.startswith(('data:', 'http://', 'https://', '//')):
            return False
        
        # Skip SVG images (already vector format)
        if src.endswith('.svg'):
            return False
        
        # Only convert image formats we optimize
        if not re.search(r'\.(png|jpg|jpeg)($|\?)', src, re.IGNORECASE):
            return False
        
        return True
    
    def _create_picture_element(self, img, has_avif: bool, has_webp: bool) -> BeautifulSoup:
        """Create a picture element with AVIF/WebP sources"""
        soup = BeautifulSoup('', 'html.parser')
        picture = soup.new_tag('picture')
        
        src = img.get('src', '')
        base_src = re.sub(r'\.(png|jpg|jpeg)($|\?)', '', src, flags=re.IGNORECASE)
        
        # Add AVIF source if available
        if has_avif:
            source_avif = soup.new_tag('source')
            source_avif['srcset'] = f"{base_src}.avif"
            source_avif['type'] = 'image/avif'
            picture.append(source_avif)
        
        # Add WebP source if available
        if has_webp:
            source_webp = soup.new_tag('source')
            source_webp['srcset'] = f"{base_src}.webp"
            source_webp['type'] = 'image/webp'
            picture.append(source_webp)
        
        # Add original img as fallback (clone all attributes)
        img_clone = soup.new_tag('img')
        for attr, value in img.attrs.items():
            img_clone[attr] = value
        
        picture.append(img_clone)
        
        return picture
    
    def _process_html_file(self, html_file: Path) -> int:
        """Process a single HTML file and convert img tags"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            images_converted = 0
            
            # Find all img tags
            img_tags = soup.find_all('img')
            
            # Debug first file
            if self.debug_count == 0 and img_tags:
                print(f"\n🔍 DEBUG: First HTML file: {html_file}")
                print(f"   Total img tags found: {len(img_tags)}")
                if img_tags:
                    first_img = img_tags[0]
                    print(f"   First img src: {first_img.get('src', 'NO SRC')}")
            
            for img in img_tags:
                if not self._should_convert_img(img):
                    self.stats['images_skipped'] += 1
                    continue
                
                # Check if modern formats exist
                has_avif, has_webp = self._has_modern_format(
                    img.get('src', ''),
                    self.directory
                )
                
                # Only convert if at least one modern format exists
                if not (has_avif or has_webp):
                    self.stats['images_skipped'] += 1
                    if self.debug_count <= 3:
                        print(f"   ⚠️  No AVIF or WebP found for this image")
                    continue
                
                # Create picture element and replace img
                picture = self._create_picture_element(img, has_avif, has_webp)
                img.replace_with(picture)
                images_converted += 1
                self.stats['images_converted'] += 1
            
            # Save modified HTML if any images were converted
            if images_converted > 0:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
            
            return images_converted
            
        except Exception as e:
            print(f"⚠️  Error processing {html_file}: {e}")
            return 0
    
    def process_directory(self) -> dict:
        """Process all HTML files in the directory"""
        if not self.directory.exists():
            print(f"❌ Directory does not exist: {self.directory}")
            return self.stats
        
        print(f"🔍 Scanning for HTML files in {self.directory}")
        
        # Find all HTML files
        html_files = list(self.directory.rglob('*.html'))
        
        if not html_files:
            print("ℹ️  No HTML files found")
            return self.stats
        
        print(f"📄 Found {len(html_files)} HTML files")
        print("🖼️  Converting img tags to picture elements...")
        
        for html_file in html_files:
            converted = self._process_html_file(html_file)
            if converted > 0:
                self.stats['files_processed'] += 1
                
                # Show progress every 50 files
                if self.stats['files_processed'] % 50 == 0:
                    print(f"   ⏳ Processed {self.stats['files_processed']} files...")
        
        return self.stats
    
    def print_summary(self):
        """Print conversion summary"""
        print("\n" + "="*60)
        print("🖼️  IMAGE TO PICTURE CONVERSION SUMMARY")
        print("="*60)
        print(f"📄 Files Modified:      {self.stats['files_processed']}")
        print(f"✅ Images Converted:    {self.stats['images_converted']}")
        print(f"⏭️  Images Skipped:      {self.stats['images_skipped']}")
        print("="*60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert img tags to picture elements with AVIF/WebP sources'
    )
    parser.add_argument(
        'directory',
        help='Directory containing HTML files to process'
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Starting image to picture conversion...")
    print(f"📁 Directory: {args.directory}\n")
    
    converter = ImageToPictureConverter(args.directory)
    converter.process_directory()
    converter.print_summary()
    
    return 0 if converter.stats['files_processed'] > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
