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
import subprocess
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import time


@dataclass
class OptimizationResult:
    """Result of image optimization"""
    path: str
    original_size: int
    optimized_size: int
    saved_bytes: int
    format_type: str
    was_cached: bool
    duration_ms: float
    avif_created: bool = False
    avif_size: int = 0
    webp_created: bool = False
    webp_size: int = 0


class ImageOptimizer:
    """Advanced image optimizer with parallel processing and caching"""
    
    def __init__(self, cache_dir: str = ".image_optimization_cache", max_workers: int = 4):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_workers = max_workers
        self.cache_file = self.cache_dir / "optimization_cache.json"
        self.cache = self._load_cache()
        
        # Check available tools
        self.tools = {
            'optipng': self._check_tool('optipng'),
            'jpegoptim': self._check_tool('jpegoptim'),
            'avifenc': self._check_tool('avifenc'),  # AVIF encoder
            'cwebp': self._check_tool('cwebp'),  # WebP encoder
        }
        
        print(f"🔧 Available optimization tools:")
        for tool, available in self.tools.items():
            status = "✅" if available else "❌"
            print(f"   {status} {tool}")
    
    def _check_tool(self, tool: str) -> bool:
        """Check if an optimization tool is available"""
        try:
            result = subprocess.run(
                ['which', tool],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _load_cache(self) -> Dict:
        """Load optimization cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    print(f"📂 Loaded cache with {len(cache)} entries")
                    if cache:
                        # Show sample cache key
                        sample_key = list(cache.keys())[0]
                        print(f"   Sample cache key: {sample_key}")
                    return cache
            except Exception as e:
                print(f"⚠️  Could not load cache: {e}")
        else:
            print(f"ℹ️  No existing cache file found at {self.cache_file}")
        return {}
    
    def _save_cache(self):
        """Save optimization cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save cache: {e}")
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Get MD5 hash of file content"""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            # Read in chunks for memory efficiency
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _is_cached(self, filepath: Path) -> bool:
        """Check if file has already been optimized"""
        path_str = str(filepath)
        if path_str not in self.cache:
            return False
        
        cached_hash = self.cache[path_str].get('hash')
        current_hash = self._get_file_hash(filepath)
        
        is_match = cached_hash == current_hash
        # Debug: Show first cache hit
        if is_match and not hasattr(self, '_first_cache_hit_logged'):
            self._first_cache_hit_logged = True
            print(f"✓ First cache hit: {path_str}")
            print(f"  Cached hash: {cached_hash[:8]}...")
            print(f"  Current hash: {current_hash[:8]}...")
        
        return is_match
    
    def _update_cache(self, filepath: Path, result: OptimizationResult):
        """Update cache with optimization result"""
        path_str = str(filepath)
        self.cache[path_str] = {
            'hash': self._get_file_hash(filepath),
            'optimized_size': result.optimized_size,
            'timestamp': time.time()
        }
    
    def _optimize_png(self, filepath: Path) -> Optional[OptimizationResult]:
        """Optimize PNG file using optipng"""
        if not self.tools['optipng']:
            return None
        
        start_time = time.time()
        original_size = filepath.stat().st_size
        
        # Check cache
        if self._is_cached(filepath):
            return OptimizationResult(
                path=str(filepath),
                original_size=original_size,
                optimized_size=original_size,
                saved_bytes=0,
                format_type='PNG',
                was_cached=True,
                duration_ms=0
            )
        
        try:
            # Use -o2 for balance between speed and compression
            subprocess.run(
                ['optipng', '-o2', '-quiet', str(filepath)],
                capture_output=True,
                check=True,
                timeout=60
            )
            
            optimized_size = filepath.stat().st_size
            duration_ms = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                path=str(filepath),
                original_size=original_size,
                optimized_size=optimized_size,
                saved_bytes=original_size - optimized_size,
                format_type='PNG',
                was_cached=False,
                duration_ms=duration_ms
            )
            
            self._update_cache(filepath, result)
            return result
            
        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout optimizing {filepath}")
            return None
        except Exception as e:
            print(f"⚠️  Error optimizing {filepath}: {e}")
            return None
    
    def _optimize_jpeg(self, filepath: Path) -> Optional[OptimizationResult]:
        """Optimize JPEG file using jpegoptim"""
        if not self.tools['jpegoptim']:
            return None
        
        start_time = time.time()
        original_size = filepath.stat().st_size
        
        # Check cache
        if self._is_cached(filepath):
            return OptimizationResult(
                path=str(filepath),
                original_size=original_size,
                optimized_size=original_size,
                saved_bytes=0,
                format_type='JPEG',
                was_cached=True,
                duration_ms=0
            )
        
        try:
            # Quality 85 maintains good visual quality with compression
            subprocess.run(
                ['jpegoptim', '--max=85', '--strip-all', '--quiet', str(filepath)],
                capture_output=True,
                check=True,
                timeout=60
            )
            
            optimized_size = filepath.stat().st_size
            duration_ms = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                path=str(filepath),
                original_size=original_size,
                optimized_size=optimized_size,
                saved_bytes=original_size - optimized_size,
                format_type='JPEG',
                was_cached=False,
                duration_ms=duration_ms
            )
            
            self._update_cache(filepath, result)
            return result
            
        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout optimizing {filepath}")
            return None
        except Exception as e:
            print(f"⚠️  Error optimizing {filepath}: {e}")
            return None
    
    def _create_avif(self, filepath: Path, was_cached: bool = False) -> Tuple[bool, int, bool]:
        """Create AVIF version of image
        
        Returns:
            Tuple of (created, size, was_newly_created)
        """
        if not self.tools['avifenc']:
            return False, 0, False
        
        avif_path = filepath.with_suffix('.avif')
        
        # Skip if AVIF already exists and is newer than source
        if avif_path.exists():
            if avif_path.stat().st_mtime >= filepath.stat().st_mtime:
                return True, avif_path.stat().st_size, False
        
        try:
            # Speed 6 (balanced), quality 80 for good balance
            # Using -s for speed, -q for quality (more compatible syntax)
            result = subprocess.run(
                ['avifenc', '-s', '6', '-q', '80', str(filepath), str(avif_path)],
                capture_output=True,
                check=True,
                timeout=60,
                text=True
            )
            
            return True, avif_path.stat().st_size, True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            print(f"⚠️  Error creating AVIF for {filepath}: {error_msg}")
            return False, 0, False
        except Exception as e:
            print(f"⚠️  Error creating AVIF for {filepath}: {e}")
            return False, 0, False
    
    def _create_webp(self, filepath: Path, was_cached: bool = False) -> Tuple[bool, int, bool]:
        """Create WebP version of image
        
        Returns:
            Tuple of (created, size, was_newly_created)
        """
        if not self.tools['cwebp']:
            return False, 0, False
        
        webp_path = filepath.with_suffix('.webp')
        
        # Skip if WebP already exists and is newer than source
        if webp_path.exists():
            if webp_path.stat().st_mtime >= filepath.stat().st_mtime:
                return True, webp_path.stat().st_size, False
        
        try:
            # Quality 80 for good balance
            subprocess.run(
                ['cwebp', '-q', '80', '-quiet', str(filepath), '-o', str(webp_path)],
                capture_output=True,
                check=True,
                timeout=60
            )
            
            return True, webp_path.stat().st_size, True
            
        except Exception as e:
            print(f"⚠️  Error creating WebP for {filepath}: {e}")
            return False, 0, False
    
    def _optimize_image(self, filepath: Path, create_avif: bool = False, create_webp: bool = False) -> Optional[OptimizationResult]:
        """Optimize a single image file"""
        suffix = filepath.suffix.lower()
        
        result = None
        if suffix == '.png':
            result = self._optimize_png(filepath)
        elif suffix in ['.jpg', '.jpeg']:
            result = self._optimize_jpeg(filepath)
        else:
            return None
        
        # Create modern format versions if requested and result was successful
        # IMPORTANT: Create AVIF/WebP even for cached images to ensure all images have modern formats
        if result:
            if create_avif:
                avif_created, avif_size, avif_newly_created = self._create_avif(filepath, result.was_cached)
                result.avif_created = avif_created
                result.avif_size = avif_size
                # If image was cached and AVIF wasn't newly created, ensure was_cached stays true
                if result.was_cached and not avif_newly_created:
                    result.was_cached = True
            
            if create_webp:
                webp_created, webp_size, webp_newly_created = self._create_webp(filepath, result.was_cached)
                result.webp_created = webp_created
                result.webp_size = webp_size
                # If image was cached and WebP wasn't newly created, ensure was_cached stays true
                if result.was_cached and not webp_newly_created:
                    result.was_cached = True
        
        return result
    
    def optimize_directory(
        self,
        directory: str,
        create_avif: bool = False,
        create_webp: bool = False,
        recursive: bool = True
    ) -> List[OptimizationResult]:
        """
        Optimize all images in a directory
        
        Args:
            directory: Path to directory containing images
            create_avif: Whether to create AVIF versions
            create_webp: Whether to create WebP versions
            recursive: Whether to search recursively
            
        Returns:
            List of optimization results
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            print(f"❌ Directory does not exist: {directory}")
            return []
        
        # Find all image files
        patterns = ['*.png', '*.jpg', '*.jpeg']
        image_files = []
        
        for pattern in patterns:
            if recursive:
                image_files.extend(dir_path.rglob(pattern))
            else:
                image_files.extend(dir_path.glob(pattern))
        
        print(f"📊 Found {len(image_files)} images to process")
        
        if not image_files:
            return []
        
        # Process images in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._optimize_image, img, create_avif, create_webp): img
                for img in image_files
            }
            
            # Process results as they complete
            completed = 0
            for future in concurrent.futures.as_completed(future_to_file):
                completed += 1
                filepath = future_to_file[future]
                
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        
                        # Show progress every 10 images or for last image
                        if completed % 10 == 0 or completed == len(image_files):
                            print(f"   ⏳ Progress: {completed}/{len(image_files)} images processed")
                        
                except Exception as e:
                    print(f"⚠️  Error processing {filepath}: {e}")
        
        # Save cache after all optimizations
        self._save_cache()
        
        return results
    
    def print_summary(self, results: List[OptimizationResult]):
        """Print optimization summary"""
        if not results:
            print("\nℹ️  No images were optimized")
            return
        
        total_original = sum(r.original_size for r in results)
        total_optimized = sum(r.optimized_size for r in results)
        total_saved = total_original - total_optimized
        
        cached_count = sum(1 for r in results if r.was_cached)
        optimized_count = len(results) - cached_count
        
        png_count = sum(1 for r in results if r.format_type == 'PNG')
        jpeg_count = sum(1 for r in results if r.format_type == 'JPEG')
        
        avif_count = sum(1 for r in results if r.avif_created)
        avif_saved = sum(
            r.optimized_size - r.avif_size
            for r in results if r.avif_created and r.avif_size < r.optimized_size
        )
        
        webp_count = sum(1 for r in results if r.webp_created)
        webp_saved = sum(
            r.optimized_size - r.webp_size
            for r in results if r.webp_created and r.webp_size < r.optimized_size
        )
        
        avg_duration = sum(r.duration_ms for r in results if not r.was_cached) / max(optimized_count, 1)
        
        print("\n" + "="*60)
        print("🖼️  IMAGE OPTIMIZATION SUMMARY")
        print("="*60)
        print(f"📊 Total Images:        {len(results)}")
        print(f"   • PNG:               {png_count}")
        print(f"   • JPEG:              {jpeg_count}")
        print(f"\n✅ Newly Optimized:     {optimized_count}")
        print(f"⏭️  Cached (Skipped):    {cached_count}")
        
        if avif_count > 0:
            print(f"🎨 AVIF Created:        {avif_count}")
        
        if webp_count > 0:
            print(f"🌐 WebP Created:        {webp_count}")
        
        print(f"\n💾 Space Savings:")
        print(f"   • Original:          {total_original / 1024 / 1024:.2f} MB")
        print(f"   • Optimized:         {total_optimized / 1024 / 1024:.2f} MB")
        print(f"   • Saved:             {total_saved / 1024 / 1024:.2f} MB ({(total_saved / total_original * 100) if total_original > 0 else 0:.1f}%)")
        
        if avif_count > 0 and avif_saved > 0:
            print(f"   • AVIF Extra:        {avif_saved / 1024 / 1024:.2f} MB")
        
        if webp_count > 0 and webp_saved > 0:
            print(f"   • WebP Extra:        {webp_saved / 1024 / 1024:.2f} MB")
        
        if optimized_count > 0:
            print(f"\n⏱️  Performance:")
            print(f"   • Avg Time/Image:    {avg_duration:.0f} ms")
            print(f"   • Workers Used:      {self.max_workers}")
        
        print("="*60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Optimize images with parallel processing and intelligent caching'
    )
    parser.add_argument(
        'directory',
        help='Directory containing images to optimize'
    )
    parser.add_argument(
        '--avif',
        action='store_true',
        default=True,
        help='Create AVIF versions of images (requires avifenc) - enabled by default'
    )
    parser.add_argument(
        '--no-avif',
        action='store_true',
        help='Disable AVIF creation'
    )
    parser.add_argument(
        '--webp',
        action='store_true',
        help='Also create WebP versions of images (requires cwebp)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )
    parser.add_argument(
        '--cache-dir',
        default='.image_optimization_cache',
        help='Cache directory (default: .image_optimization_cache)'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories'
    )
    parser.add_argument(
        '--json-output',
        help='Output results as JSON to specified file'
    )
    
    args = parser.parse_args()
    
    # Create optimizer
    optimizer = ImageOptimizer(
        cache_dir=args.cache_dir,
        max_workers=args.workers
    )
    
    # Determine format flags
    create_avif = args.avif and not args.no_avif
    create_webp = args.webp
    
    # Run optimization
    print(f"\n🚀 Starting image optimization...")
    print(f"📁 Directory: {args.directory}")
    print(f"👷 Workers: {args.workers}")
    print(f"🎨 AVIF: {'Yes' if create_avif else 'No'}")
    print(f"🌐 WebP: {'Yes' if create_webp else 'No'}")
    print()
    
    start_time = time.time()
    
    results = optimizer.optimize_directory(
        args.directory,
        create_avif=create_avif,
        create_webp=create_webp,
        recursive=not args.no_recursive
    )
    
    duration = time.time() - start_time
    
    # Print summary
    optimizer.print_summary(results)
    print(f"\n⏱️  Total time: {duration:.2f} seconds")
    
    # Output JSON if requested
    if args.json_output and results:
        try:
            with open(args.json_output, 'w') as f:
                json.dump([asdict(r) for r in results], f, indent=2)
            print(f"📄 JSON output saved to: {args.json_output}")
        except Exception as e:
            print(f"⚠️  Could not save JSON output: {e}")
    
    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main())
