#!/usr/bin/env python3
"""
Verify AVIF files exist for all images and check if they're properly referenced in HTML
"""

from pathlib import Path
from bs4 import BeautifulSoup
import sys

def check_avif_files():
    """Check if all PNG/JPG/JPEG files have corresponding AVIF files"""
    missing_avif = []
    wp_uploads = Path('public/wp-content/uploads')
    
    if not wp_uploads.exists():
        print(f"❌ Directory not found: {wp_uploads}")
        return missing_avif
    
    print("🔍 Checking for missing AVIF files...\n")
    
    image_extensions = ['*.png', '*.jpg', '*.jpeg']
    total_images = 0
    total_avif = 0
    
    for ext in image_extensions:
        for img_file in wp_uploads.rglob(ext):
            total_images += 1
            avif_file = img_file.with_suffix('.avif')
            if not avif_file.exists():
                missing_avif.append(str(img_file.relative_to('public')))
            else:
                total_avif += 1
    
    print(f"📊 Statistics:")
    print(f"   Total images: {total_images}")
    print(f"   AVIF files: {total_avif}")
    print(f"   Missing AVIF: {len(missing_avif)}")
    
    if missing_avif:
        print(f"\n❌ Found {len(missing_avif)} images without AVIF versions:")
        for img in sorted(missing_avif)[:20]:  # Show first 20
            print(f"   {img}")
        if len(missing_avif) > 20:
            print(f"   ... and {len(missing_avif) - 20} more")
    else:
        print("\n✅ All images have AVIF versions!")
    
    return missing_avif

def check_picture_elements():
    """Check if HTML files use picture elements with AVIF sources"""
    print("\n🔍 Checking HTML files for picture elements...\n")
    
    html_files = list(Path('public').rglob('*.html'))
    
    files_with_picture = 0
    files_with_img = 0
    total_picture_tags = 0
    total_avif_sources = 0
    
    for html_file in html_files[:10]:  # Sample first 10 files
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        pictures = soup.find_all('picture')
        imgs = soup.find_all('img')
        
        if pictures:
            files_with_picture += 1
            total_picture_tags += len(pictures)
            
            # Count AVIF sources
            for picture in pictures:
                avif_sources = picture.find_all('source', type='image/avif')
                total_avif_sources += len(avif_sources)
        
        if imgs:
            files_with_img += 1
    
    print(f"📊 HTML Analysis (sample of 10 files):")
    print(f"   Files with <picture> tags: {files_with_picture}")
    print(f"   Total <picture> elements: {total_picture_tags}")
    print(f"   Total AVIF <source> tags: {total_avif_sources}")
    print(f"   Files with <img> tags: {files_with_img}")
    
    if total_avif_sources > 0:
        print(f"\n✅ AVIF sources are being used in HTML!")
    else:
        print(f"\n⚠️  No AVIF sources found in sampled HTML files")

def main():
    print("=" * 70)
    print("AVIF VERIFICATION REPORT")
    print("=" * 70)
    print()
    
    # Check AVIF files
    missing = check_avif_files()
    
    # Check HTML
    check_picture_elements()
    
    print()
    print("=" * 70)
    
    return 0 if len(missing) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
