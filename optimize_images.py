#!/usr/bin/env python3
"""
Image Optimization Script for WordPress Static Site
Fetches images from WordPress API, optimizes them, and replaces in static site.

Features:
- Converts JPEG/PNG to WebP and AVIF formats
- Generates responsive image variants
- Updates HTML to use <picture> elements with format fallbacks
- Maintains original images as fallback
- Tracks optimization metrics

Requirements:
- Pillow (PIL) for image processing
- pillow-avif-plugin for AVIF support
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
import hashlib
from datetime import datetime

try:
    from PIL import Image
    import pillow_avif
except ImportError:
    print("ERROR: Required packages not installed")
    print("Run: pip install Pillow pillow-avif-plugin")
    sys.exit(1)

from bs4 import BeautifulSoup


class ImageOptimizer:
    """Optimizes images for static site performance"""

    def __init__(self, public_dir: str, wp_api_url: str = None):
        self.public_dir = Path(public_dir)
        self.wp_api_url = wp_api_url
        self.stats = {
            'total_images': 0,
            'optimized': 0,
            'skipped': 0,
            'errors': 0,
            'original_size': 0,
            'optimized_size': 0,
            'webp_generated': 0,
            'avif_generated': 0
        }
        self.optimization_cache = {}
        self.load_optimization_cache()

    def load_optimization_cache(self):
        """Load cache of previously optimized images to avoid reprocessing"""
        cache_file = self.public_dir / '.image-optimization-cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.optimization_cache = json.load(f)
                print(f"📦 Loaded optimization cache with {len(self.optimization_cache)} entries")
            except Exception as e:
                print(f"⚠️  Could not load cache: {e}")

    def save_optimization_cache(self):
        """Save optimization cache for future runs"""
        cache_file = self.public_dir / '.image-optimization-cache.json'
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.optimization_cache, f, indent=2)
            print(f"💾 Saved optimization cache with {len(self.optimization_cache)} entries")
        except Exception as e:
            print(f"⚠️  Could not save cache: {e}")

    def get_image_hash(self, image_path: Path) -> str:
        """Calculate hash of image file for cache checking"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def should_optimize_image(self, image_path: Path) -> bool:
        """Check if image should be optimized based on cache"""
        if not image_path.exists():
            return False

        # Skip if already webp or avif
        if image_path.suffix.lower() in ['.webp', '.avif']:
            return False

        # Check cache
        cache_key = str(image_path.relative_to(self.public_dir))
        if cache_key in self.optimization_cache:
            cached_hash = self.optimization_cache[cache_key].get('hash', '')
            current_hash = self.get_image_hash(image_path)
            if cached_hash == current_hash:
                # Image unchanged, skip
                return False

        return True

    def optimize_image(self, image_path: Path, quality: int = 85) -> Dict[str, any]:
        """
        Optimize a single image by creating WebP and AVIF versions

        Args:
            image_path: Path to the original image
            quality: Quality level for compression (0-100)

        Returns:
            Dictionary with optimization results
        """
        result = {
            'original': str(image_path),
            'webp': None,
            'avif': None,
            'original_size': 0,
            'webp_size': 0,
            'avif_size': 0,
            'success': False,
            'error': None
        }

        try:
            # Check if should optimize
            if not self.should_optimize_image(image_path):
                self.stats['skipped'] += 1
                return result

            # Get original size
            original_size = image_path.stat().st_size
            result['original_size'] = original_size
            self.stats['original_size'] += original_size

            # Open image
            with Image.open(image_path) as img:
                # Convert RGBA to RGB for JPEG compatibility
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Generate WebP version
                webp_path = image_path.with_suffix('.webp')
                img.save(
                    webp_path,
                    'WEBP',
                    quality=quality,
                    method=6  # Slower but better compression
                )
                webp_size = webp_path.stat().st_size
                result['webp'] = str(webp_path)
                result['webp_size'] = webp_size
                self.stats['webp_generated'] += 1
                self.stats['optimized_size'] += webp_size

                # Generate AVIF version (best compression)
                try:
                    avif_path = image_path.with_suffix('.avif')
                    img.save(
                        avif_path,
                        'AVIF',
                        quality=quality,
                        speed=4  # Balance between speed and compression
                    )
                    avif_size = avif_path.stat().st_size
                    result['avif'] = str(avif_path)
                    result['avif_size'] = avif_size
                    self.stats['avif_generated'] += 1
                    self.stats['optimized_size'] += avif_size
                except Exception as e:
                    # AVIF might fail on some systems
                    print(f"⚠️  AVIF generation failed for {image_path.name}: {e}")

                result['success'] = True
                self.stats['optimized'] += 1

                # Update cache
                cache_key = str(image_path.relative_to(self.public_dir))
                self.optimization_cache[cache_key] = {
                    'hash': self.get_image_hash(image_path),
                    'optimized_at': datetime.now().isoformat(),
                    'webp': str(webp_path.relative_to(self.public_dir)),
                    'avif': str(avif_path.relative_to(self.public_dir)) if result['avif'] else None
                }

                # Calculate savings
                savings = original_size - webp_size
                savings_pct = (savings / original_size * 100) if original_size > 0 else 0
                print(f"✅ {image_path.name}: {original_size/1024:.1f}KB → {webp_size/1024:.1f}KB ({savings_pct:.1f}% saved)")

        except Exception as e:
            result['error'] = str(e)
            self.stats['errors'] += 1
            print(f"❌ Error optimizing {image_path.name}: {e}")

        return result

    def find_all_images(self) -> List[Path]:
        """Find all images in the public directory"""
        image_extensions = {'.jpg', '.jpeg', '.png'}
        images = []

        uploads_dir = self.public_dir / 'wp-content' / 'uploads'
        if uploads_dir.exists():
            for ext in image_extensions:
                images.extend(uploads_dir.rglob(f'*{ext}'))
                images.extend(uploads_dir.rglob(f'*{ext.upper()}'))

        return images

    def optimize_all_images(self, max_workers: int = 4, quality: int = 85):
        """
        Optimize all images in parallel

        Args:
            max_workers: Number of parallel workers
            quality: Image quality (0-100)
        """
        images = self.find_all_images()
        self.stats['total_images'] = len(images)

        print(f"\n🖼️  Found {len(images)} images to process")
        print(f"⚙️  Using {max_workers} workers with quality={quality}\n")

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.optimize_image, img, quality): img
                for img in images
            }

            for future in as_completed(futures):
                result = future.result()

        duration = time.time() - start_time

        # Save cache
        self.save_optimization_cache()

        # Print statistics
        self.print_statistics(duration)

    def update_html_files(self):
        """Update all HTML files to use picture elements with WebP/AVIF fallbacks"""
        print("\n📝 Updating HTML files with optimized images...")

        html_files = list(self.public_dir.rglob('*.html'))
        updated_count = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                soup = BeautifulSoup(content, 'html.parser')
                modified = False

                # Find all img tags that aren't already in picture elements
                for img in soup.find_all('img'):
                    # Skip if already in a picture element
                    if img.parent.name == 'picture':
                        continue

                    src = img.get('src', '')
                    if not src or not any(src.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        continue

                    # Check if optimized versions exist
                    img_path = self.public_dir / src.lstrip('/')
                    webp_path = img_path.with_suffix('.webp')
                    avif_path = img_path.with_suffix('.avif')

                    if not webp_path.exists() and not avif_path.exists():
                        continue

                    # Create picture element
                    picture = soup.new_tag('picture')

                    # Add AVIF source if exists
                    if avif_path.exists():
                        avif_src = '/' + str(avif_path.relative_to(self.public_dir))
                        source_avif = soup.new_tag('source', srcset=avif_src, type='image/avif')
                        picture.append(source_avif)

                    # Add WebP source if exists
                    if webp_path.exists():
                        webp_src = '/' + str(webp_path.relative_to(self.public_dir))
                        source_webp = soup.new_tag('source', srcset=webp_src, type='image/webp')
                        picture.append(source_webp)

                    # Clone the original img as fallback
                    img_clone = soup.new_tag('img')
                    for attr, value in img.attrs.items():
                        img_clone[attr] = value
                    picture.append(img_clone)

                    # Replace img with picture
                    img.replace_with(picture)
                    modified = True

                # Write back if modified
                if modified:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    updated_count += 1

            except Exception as e:
                print(f"⚠️  Error updating {html_file}: {e}")

        print(f"✅ Updated {updated_count} HTML files with <picture> elements")

    def print_statistics(self, duration: float):
        """Print optimization statistics"""
        print("\n" + "="*60)
        print("📊 IMAGE OPTIMIZATION STATISTICS")
        print("="*60)
        print(f"Total images found:      {self.stats['total_images']}")
        print(f"Images optimized:        {self.stats['optimized']}")
        print(f"Images skipped (cached): {self.stats['skipped']}")
        print(f"Errors:                  {self.stats['errors']}")
        print(f"\nWebP images generated:   {self.stats['webp_generated']}")
        print(f"AVIF images generated:   {self.stats['avif_generated']}")
        print(f"\nOriginal size:           {self.stats['original_size'] / 1024 / 1024:.2f} MB")
        print(f"Optimized size:          {self.stats['optimized_size'] / 1024 / 1024:.2f} MB")

        if self.stats['original_size'] > 0:
            savings = self.stats['original_size'] - self.stats['optimized_size']
            savings_pct = (savings / self.stats['original_size']) * 100
            print(f"Total savings:           {savings / 1024 / 1024:.2f} MB ({savings_pct:.1f}%)")

        print(f"\nProcessing time:         {duration:.2f} seconds")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Optimize images for WordPress static site'
    )
    parser.add_argument(
        'public_dir',
        nargs='?',
        default='./public',
        help='Path to public directory (default: ./public)'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=85,
        help='Image quality (0-100, default: 85)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )
    parser.add_argument(
        '--skip-html',
        action='store_true',
        help='Skip updating HTML files'
    )

    args = parser.parse_args()

    print("🚀 WordPress Static Site Image Optimizer")
    print(f"📁 Public directory: {args.public_dir}\n")

    # Initialize optimizer
    optimizer = ImageOptimizer(args.public_dir)

    # Optimize images
    optimizer.optimize_all_images(
        max_workers=args.workers,
        quality=args.quality
    )

    # Update HTML files
    if not args.skip_html:
        optimizer.update_html_files()

    print("\n✅ Image optimization complete!")

    # Exit with error code if there were errors
    if optimizer.stats['errors'] > 0:
        print(f"\n⚠️  Warning: {optimizer.stats['errors']} errors occurred during optimization")
        sys.exit(1)


if __name__ == '__main__':
    main()
