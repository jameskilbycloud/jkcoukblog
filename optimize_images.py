#!/usr/bin/env python3
"""
Advanced Image Optimization Script
Handles parallel processing, AVIF/WebP conversion, and intelligent caching
"""

import os
import sys
import hashlib
import json
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
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load cache: {e}")
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
        # TEMPORARILY DISABLED FOR TROUBLESHOOTING - Always return False to force re-optimization
        return False
        
        # Original code commented out:
        # path_str = str(filepath)
        # if path_str not in self.cache:
        #     return False
        # 
        # cached_hash = self.cache[path_str].get('hash')
        # current_hash = self._get_file_hash(filepath)
        # 
        # return cached_hash == current_hash
    
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
    
    def _create_avif(self, filepath: Path) -> Tuple[bool, int]:
        """Create AVIF version of image"""
        if not self.tools['avifenc']:
            return False, 0
        
        avif_path = filepath.with_suffix('.avif')
        
        # TEMPORARILY DISABLED - Always recreate AVIF for troubleshooting
        # Skip if AVIF already exists and is newer than source
        # if avif_path.exists():
        #     if avif_path.stat().st_mtime > filepath.stat().st_mtime:
        #         return True, avif_path.stat().st_size
        
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
            
            return True, avif_path.stat().st_size
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            print(f"⚠️  Error creating AVIF for {filepath}: {error_msg}")
            return False, 0
        except Exception as e:
            print(f"⚠️  Error creating AVIF for {filepath}: {e}")
            return False, 0
    
    def _create_webp(self, filepath: Path) -> Tuple[bool, int]:
        """Create WebP version of image"""
        if not self.tools['cwebp']:
            return False, 0
        
        webp_path = filepath.with_suffix('.webp')
        
        # Skip if WebP already exists and is newer than source
        if webp_path.exists():
            if webp_path.stat().st_mtime > filepath.stat().st_mtime:
                return True, webp_path.stat().st_size
        
        try:
            # Quality 80 for good balance
            subprocess.run(
                ['cwebp', '-q', '80', '-quiet', str(filepath), '-o', str(webp_path)],
                capture_output=True,
                check=True,
                timeout=60
            )
            
            return True, webp_path.stat().st_size
            
        except Exception as e:
            print(f"⚠️  Error creating WebP for {filepath}: {e}")
            return False, 0
    
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
                avif_created, avif_size = self._create_avif(filepath)
                result.avif_created = avif_created
                result.avif_size = avif_size
            
            if create_webp:
                webp_created, webp_size = self._create_webp(filepath)
                result.webp_created = webp_created
                result.webp_size = webp_size
        
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
