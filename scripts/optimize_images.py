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

    def __init__(self, public_dir: str, wp_api_url: str = None, cache_dir: str = None):
        self.public_dir = Path(public_dir)
        self.wp_api_url = wp_api_url
        # Use project root cache directory for consistency with GitHub Actions
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default to .image_optimization_cache in project root (parent of public_dir)
            self.cache_dir = Path('.image_optimization_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
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
        self.optimization_results = []  # For JSON output
        self.optimization_cache = {}
        self.load_optimization_cache()

    def load_optimization_cache(self):
        """Load cache of previously optimized images to avoid reprocessing"""
        cache_file = self.cache_dir / 'optimization_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.optimization_cache = json.load(f)
                print(f"📦 Loaded optimization cache with {len(self.optimization_cache)} entries")
            except Exception as e:
                print(f"⚠️  Could not load cache: {e}")

    def save_optimization_cache(self):
        """Save optimization cache for future runs"""
        cache_file = self.cache_dir / 'optimization_cache.json'
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
        """Check if image should be optimized based on cache and existing files"""
        if not image_path.exists():
            return False

        # Skip if already webp or avif
        if image_path.suffix.lower() in ['.webp', '.avif']:
            return False

        # Check if AVIF and WebP already exist (even if not in cache)
        avif_path = image_path.with_suffix('.avif')
        webp_path = image_path.with_suffix('.webp')
        
        # If both modern formats exist, check cache to see if image changed
        if avif_path.exists() and webp_path.exists():
            cache_key = str(image_path.relative_to(self.public_dir))
            if cache_key in self.optimization_cache:
                cached_hash = self.optimization_cache[cache_key].get('hash', '')
                current_hash = self.get_image_hash(image_path)
                if cached_hash == current_hash:
                    # Image unchanged and both formats exist, skip
                    return False

        # Check cache for unchanged images that need AVIF/WebP created
        cache_key = str(image_path.relative_to(self.public_dir))
        if cache_key in self.optimization_cache:
            cached_data = self.optimization_cache[cache_key]
            cached_hash = cached_data.get('hash', '')
            current_hash = self.get_image_hash(image_path)
            
            # If hash matches and cache says AVIF was created, verify file exists
            if cached_hash == current_hash:
                avif_created = cached_data.get('avif_created', False)
                webp_created = cached_data.get('webp_created', False)
                
                # Only skip if both formats were created AND files still exist
                if avif_created and webp_created and avif_path.exists() and webp_path.exists():
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
        start_time = time.time()
        result = {
            'original': str(image_path),
            'webp': None,
            'avif': None,
            'original_size': 0,
            'webp_size': 0,
            'avif_size': 0,
            'success': False,
            'error': None,
            'was_cached': False,
            'avif_created': False,
            'webp_created': False,
            'saved_bytes': 0,
            'duration_ms': 0,
            'format_type': 'UNKNOWN'
        }

        try:
            # Determine format type
            suffix = image_path.suffix.lower()
            if suffix in ['.jpg', '.jpeg']:
                result['format_type'] = 'JPEG'
            elif suffix == '.png':
                result['format_type'] = 'PNG'

            # Check if should optimize
            if not self.should_optimize_image(image_path):
                self.stats['skipped'] += 1
                result['was_cached'] = True
                result['duration_ms'] = int((time.time() - start_time) * 1000)
                self.optimization_results.append(result)
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
                result['webp_created'] = True
                self.stats['webp_generated'] += 1
                self.stats['optimized_size'] += webp_size

                # Generate AVIF version (best compression)
                avif_created = False
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
                    result['avif_created'] = True
                    avif_created = True
                    self.stats['avif_generated'] += 1
                    self.stats['optimized_size'] += avif_size
                except Exception as e:
                    # AVIF might fail on some systems
                    print(f"⚠️  AVIF generation failed for {image_path.name}: {e}")

                result['success'] = True
                self.stats['optimized'] += 1

                # Calculate savings (use smallest modern format vs original)
                smallest_size = min(webp_size, avif_size if avif_created else webp_size)
                result['saved_bytes'] = original_size - smallest_size

                # Update cache with new format tracking
                cache_key = str(image_path.relative_to(self.public_dir))
                self.optimization_cache[cache_key] = {
                    'hash': self.get_image_hash(image_path),
                    'optimized_at': datetime.now().isoformat(),
                    'optimized_size': webp_size,
                    'timestamp': time.time(),
                    'webp_created': True,
                    'avif_created': avif_created,
                    'webp': str(webp_path.relative_to(self.public_dir)),
                    'avif': str(avif_path.relative_to(self.public_dir)) if avif_created else None
                }

                # Calculate savings for display
                savings = original_size - webp_size
                savings_pct = (savings / original_size * 100) if original_size > 0 else 0
                print(f"✅ {image_path.name}: {original_size/1024:.1f}KB → {webp_size/1024:.1f}KB ({savings_pct:.1f}% saved)")

        except Exception as e:
            result['error'] = str(e)
            self.stats['errors'] += 1
            print(f"❌ Error optimizing {image_path.name}: {e}")

        result['duration_ms'] = int((time.time() - start_time) * 1000)
        self.optimization_results.append(result)
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

    def _get_responsive_srcset(self, base_path: Path, img_srcset: str, format_ext: str) -> str:
        """
        Generate responsive srcset for modern formats based on original img srcset

        Args:
            base_path: Base path for the image (without extension)
            img_srcset: Original srcset from img tag (e.g., "img-300.jpg 300w, img-768.jpg 768w")
            format_ext: File extension for modern format (.webp or .avif)

        Returns:
            Responsive srcset string for the modern format
        """
        if not img_srcset:
            return None

        srcset_parts = []
        for part in img_srcset.split(','):
            part = part.strip()
            if not part:
                continue

            # Parse "path/to/image.jpg 300w" format
            components = part.split()
            if len(components) >= 2:
                img_url = components[0]
                width_descriptor = components[1]  # e.g., "300w"

                # Convert the image URL to modern format
                # Handle both relative and absolute paths
                img_path_str = img_url.lstrip('/')
                img_path = self.public_dir / img_path_str

                # Check if modern format exists
                modern_path = img_path.with_suffix(format_ext)
                if modern_path.exists():
                    modern_url = '/' + str(modern_path.relative_to(self.public_dir))
                    srcset_parts.append(f"{modern_url} {width_descriptor}")

        return ', '.join(srcset_parts) if srcset_parts else None

    def update_html_files(self):
        """Update all HTML files to use picture elements with WebP/AVIF fallbacks and responsive srcset"""
        print("\n📝 Updating HTML files with optimized images...")

        html_files = list(self.public_dir.rglob('*.html'))
        updated_count = 0
        pictures_updated = 0
        pictures_created = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                soup = BeautifulSoup(content, 'html.parser')
                modified = False

                # First, update existing picture elements that are missing WebP sources
                for picture in soup.find_all('picture'):
                    img = picture.find('img')
                    if not img:
                        continue

                    src = img.get('src', '')
                    if not src or not any(src.endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        continue

                    # Get the base image path
                    img_path = self.public_dir / src.lstrip('/')
                    webp_path = img_path.with_suffix('.webp')
                    avif_path = img_path.with_suffix('.avif')

                    # Check what sources already exist in the picture element
                    existing_sources = {s.get('type'): s for s in picture.find_all('source')}
                    img_srcset = img.get('srcset', '')

                    # Add missing AVIF source with responsive srcset
                    if avif_path.exists() and 'image/avif' not in existing_sources:
                        avif_src = '/' + str(avif_path.relative_to(self.public_dir))
                        avif_srcset = self._get_responsive_srcset(img_path, img_srcset, '.avif')

                        source_avif = soup.new_tag('source', type='image/avif')
                        source_avif['srcset'] = avif_srcset if avif_srcset else avif_src

                        # Insert AVIF source as first child (highest priority)
                        picture.insert(0, source_avif)
                        modified = True
                        pictures_updated += 1

                    # Update existing AVIF source to add responsive srcset if missing
                    elif 'image/avif' in existing_sources:
                        avif_source = existing_sources['image/avif']
                        current_srcset = avif_source.get('srcset', '')
                        # Only update if current srcset doesn't have multiple sizes (no commas)
                        if ',' not in current_srcset and img_srcset:
                            avif_srcset = self._get_responsive_srcset(img_path, img_srcset, '.avif')
                            if avif_srcset:
                                avif_source['srcset'] = avif_srcset
                                modified = True

                    # Add missing WebP source with responsive srcset
                    if webp_path.exists() and 'image/webp' not in existing_sources:
                        webp_src = '/' + str(webp_path.relative_to(self.public_dir))
                        webp_srcset = self._get_responsive_srcset(img_path, img_srcset, '.webp')

                        source_webp = soup.new_tag('source', type='image/webp')
                        source_webp['srcset'] = webp_srcset if webp_srcset else webp_src

                        # Insert WebP source after AVIF (if exists) or as first child
                        if 'image/avif' in existing_sources:
                            avif_source = existing_sources['image/avif']
                            avif_source.insert_after(source_webp)
                        else:
                            picture.insert(0, source_webp)

                        modified = True
                        pictures_updated += 1

                    # Update existing WebP source to add responsive srcset if missing
                    elif 'image/webp' in existing_sources:
                        webp_source = existing_sources['image/webp']
                        current_srcset = webp_source.get('srcset', '')
                        # Only update if current srcset doesn't have multiple sizes (no commas)
                        if ',' not in current_srcset and img_srcset:
                            webp_srcset = self._get_responsive_srcset(img_path, img_srcset, '.webp')
                            if webp_srcset:
                                webp_source['srcset'] = webp_srcset
                                modified = True

                # Second, find all img tags that aren't already in picture elements
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
                    img_srcset = img.get('srcset', '')

                    # Add AVIF source with responsive srcset if exists
                    if avif_path.exists():
                        avif_src = '/' + str(avif_path.relative_to(self.public_dir))
                        avif_srcset = self._get_responsive_srcset(img_path, img_srcset, '.avif')

                        source_avif = soup.new_tag('source', type='image/avif')
                        source_avif['srcset'] = avif_srcset if avif_srcset else avif_src
                        picture.append(source_avif)

                    # Add WebP source with responsive srcset if exists
                    if webp_path.exists():
                        webp_src = '/' + str(webp_path.relative_to(self.public_dir))
                        webp_srcset = self._get_responsive_srcset(img_path, img_srcset, '.webp')

                        source_webp = soup.new_tag('source', type='image/webp')
                        source_webp['srcset'] = webp_srcset if webp_srcset else webp_src
                        picture.append(source_webp)

                    # Clone the original img as fallback
                    img_clone = soup.new_tag('img')
                    for attr, value in img.attrs.items():
                        img_clone[attr] = value
                    picture.append(img_clone)

                    # Replace img with picture
                    img.replace_with(picture)
                    modified = True
                    pictures_created += 1

                # Write back if modified
                if modified:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    updated_count += 1

            except Exception as e:
                print(f"⚠️  Error updating {html_file}: {e}")

        print(f"✅ Updated {updated_count} HTML files")
        print(f"   - {pictures_created} new <picture> elements created")
        print(f"   - {pictures_updated} existing <picture> elements enhanced with WebP/responsive srcset")

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
    parser.add_argument(
        '--json-output',
        type=str,
        default=None,
        help='Path to write JSON optimization results'
    )
    parser.add_argument(
        '--cache-dir',
        type=str,
        default='.image_optimization_cache',
        help='Directory for optimization cache (default: .image_optimization_cache)'
    )

    args = parser.parse_args()

    print("🚀 WordPress Static Site Image Optimizer")
    print(f"📁 Public directory: {args.public_dir}")
    print(f"📦 Cache directory: {args.cache_dir}\n")

    # Initialize optimizer with cache directory
    optimizer = ImageOptimizer(args.public_dir, cache_dir=args.cache_dir)

    # Optimize images
    optimizer.optimize_all_images(
        max_workers=args.workers,
        quality=args.quality
    )

    # Update HTML files
    if not args.skip_html:
        optimizer.update_html_files()

    # Write JSON output if requested
    if args.json_output:
        try:
            with open(args.json_output, 'w') as f:
                json.dump(optimizer.optimization_results, f, indent=2)
            print(f"\n📄 Optimization results written to {args.json_output}")
        except Exception as e:
            print(f"⚠️  Could not write JSON output: {e}")

    print("\n✅ Image optimization complete!")

    # Exit with error code if there were errors
    if optimizer.stats['errors'] > 0:
        print(f"\n⚠️  Warning: {optimizer.stats['errors']} errors occurred during optimization")
        sys.exit(1)


if __name__ == '__main__':
    main()
