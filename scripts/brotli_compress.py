#!/usr/bin/env python3
"""
Brotli Compression for Static Site
Pre-compresses HTML, CSS, JS, JSON, SVG, and XML files with Brotli
"""

import os
import sys
from pathlib import Path

# Check if brotli is installed
try:
    import brotli
except ImportError:
    print("❌ Brotli module not installed")
    print("\nTo install, run:")
    print("  pip install brotli")
    print("\nOr add to requirements.txt:")
    print("  echo 'brotli' >> requirements.txt")
    print("  pip install -r requirements.txt")
    sys.exit(1)

class BrotliCompressor:
    def __init__(self, public_dir, quality=11):
        """
        Initialize Brotli compressor
        
        Args:
            public_dir: Path to public directory
            quality: Compression quality (0-11, default 11 for max compression)
        """
        self.public_dir = Path(public_dir)
        self.quality = quality
        self.stats = {
            'files_processed': 0,
            'files_compressed': 0,
            'original_size': 0,
            'compressed_size': 0,
            'files_skipped': 0
        }
        
        # File extensions to compress
        self.compressible_extensions = {
            '.html', '.css', '.js', '.json', '.xml', '.svg',
            '.txt', '.md', '.csv', '.tsv', '.rss', '.atom'
        }
    
    def should_compress(self, file_path):
        """Check if file should be compressed"""
        # Check extension
        if file_path.suffix.lower() not in self.compressible_extensions:
            return False
        
        # Skip already compressed files
        if file_path.suffix == '.br':
            return False
        
        # Check if .br file already exists and is newer
        br_file = file_path.with_suffix(file_path.suffix + '.br')
        if br_file.exists():
            # Check if original is newer than compressed version
            if file_path.stat().st_mtime <= br_file.stat().st_mtime:
                return False
        
        # Only compress files larger than 1KB (smaller files not worth it)
        if file_path.stat().st_size < 1024:
            return False
        
        return True
    
    def compress_file(self, file_path):
        """Compress a single file with Brotli"""
        try:
            # Read original file
            original_data = file_path.read_bytes()
            original_size = len(original_data)
            
            # Compress with Brotli
            # Quality 11 = maximum compression (slower but best ratio)
            # Quality 4 = default (good balance)
            compressed_data = brotli.compress(
                original_data,
                quality=self.quality,
                mode=brotli.MODE_TEXT  # Optimized for text
            )
            compressed_size = len(compressed_data)
            
            # Only save if compression is beneficial (at least 5% reduction)
            if compressed_size < original_size * 0.95:
                # Write compressed file
                br_file = file_path.with_suffix(file_path.suffix + '.br')
                br_file.write_bytes(compressed_data)
                
                # Calculate compression ratio
                ratio = (1 - compressed_size / original_size) * 100
                
                self.stats['files_compressed'] += 1
                self.stats['original_size'] += original_size
                self.stats['compressed_size'] += compressed_size
                
                # Show compression info
                relative_path = file_path.relative_to(self.public_dir)
                print(f"   ✅ {relative_path}")
                print(f"      {original_size:,} bytes → {compressed_size:,} bytes ({ratio:.1f}% reduction)")
                
                return True
            else:
                self.stats['files_skipped'] += 1
                return False
                
        except Exception as e:
            print(f"   ❌ Error compressing {file_path}: {e}")
            return False
    
    def compress_directory(self):
        """Compress all eligible files in directory"""
        print(f"🗜️  Compressing files with Brotli (quality={self.quality})...")
        print(f"   Source: {self.public_dir}")
        
        # Find all files
        all_files = [f for f in self.public_dir.rglob('*') if f.is_file()]
        print(f"   Found {len(all_files)} total files\n")
        
        # Filter compressible files
        compressible_files = [f for f in all_files if self.should_compress(f)]
        
        if not compressible_files:
            print("   ℹ️  No files need compression (all up to date)")
            return
        
        print(f"   Processing {len(compressible_files)} files...\n")
        
        # Compress each file
        for file_path in compressible_files:
            self.stats['files_processed'] += 1
            self.compress_file(file_path)
        
        # Print summary
        print(f"\n📊 Compression Summary:")
        print(f"   Files processed: {self.stats['files_processed']}")
        print(f"   Files compressed: {self.stats['files_compressed']}")
        print(f"   Files skipped (no benefit): {self.stats['files_skipped']}")
        
        if self.stats['compressed_size'] > 0:
            total_original = self.stats['original_size']
            total_compressed = self.stats['compressed_size']
            total_saved = total_original - total_compressed
            total_ratio = (1 - total_compressed / total_original) * 100
            
            print(f"\n💾 Space Savings:")
            print(f"   Original size: {total_original:,} bytes ({total_original/1024/1024:.2f} MB)")
            print(f"   Compressed size: {total_compressed:,} bytes ({total_compressed/1024/1024:.2f} MB)")
            print(f"   Space saved: {total_saved:,} bytes ({total_saved/1024/1024:.2f} MB)")
            print(f"   Average compression: {total_ratio:.1f}%")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 brotli_compress.py <public_directory> [quality]")
        print("\nArguments:")
        print("  public_directory  Path to the static site directory (e.g., ./public)")
        print("  quality          Compression quality 0-11 (default: 11, max compression)")
        print("\nExample:")
        print("  python3 brotli_compress.py ./public")
        print("  python3 brotli_compress.py ./public 9  # Faster compression")
        sys.exit(1)
    
    public_dir = sys.argv[1]
    quality = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    
    if not Path(public_dir).exists():
        print(f"❌ Error: Directory '{public_dir}' does not exist")
        sys.exit(1)
    
    if quality < 0 or quality > 11:
        print(f"❌ Error: Quality must be between 0 and 11 (got {quality})")
        sys.exit(1)
    
    compressor = BrotliCompressor(public_dir, quality)
    compressor.compress_directory()
    
    print("\n✅ Brotli compression complete!")
    print("\n📝 Note: Upload both original and .br files to your hosting.")
    print("   Cloudflare Pages will automatically serve .br files when supported.")

if __name__ == '__main__':
    main()
