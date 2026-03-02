#!/usr/bin/env python3
"""
Brotli + Gzip Compression for Static Site
Pre-compresses HTML, CSS, JS, JSON, SVG, and XML files with Brotli (primary)
and Gzip (fallback for clients that don't support Brotli).
"""

import gzip as _gzip
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
        self.gzip_stats = {
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

        # Extensions that benefit from Brotli's text-aware entropy model.
        # Everything else uses MODE_GENERIC (binary/structured data).
        self._text_mode_extensions = {'.html', '.css', '.js', '.md', '.txt'}
    
    def should_compress(self, file_path):
        """Check if file should be compressed"""
        # Check extension
        if file_path.suffix.lower() not in self.compressible_extensions:
            return False
        
        # Skip already compressed files
        if file_path.suffix in ('.br', '.gz'):
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
            
            # K: use MODE_TEXT only for prose/code; MODE_GENERIC for structured
            #    data formats (JSON, SVG, XML) where the text model adds no benefit.
            mode = (brotli.MODE_TEXT
                    if file_path.suffix.lower() in self._text_mode_extensions
                    else brotli.MODE_GENERIC)
            compressed_data = brotli.compress(
                original_data,
                quality=self.quality,
                mode=mode
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
    
    def should_compress_gzip(self, file_path):
        """Check if file should be gzip compressed"""
        if file_path.suffix.lower() not in self.compressible_extensions:
            return False
        if file_path.suffix in ('.br', '.gz'):
            return False
        gz_file = file_path.with_suffix(file_path.suffix + '.gz')
        if gz_file.exists():
            if file_path.stat().st_mtime <= gz_file.stat().st_mtime:
                return False
        if file_path.stat().st_size < 1024:
            return False
        return True

    def compress_file_gzip(self, file_path):
        """Compress a single file with Gzip (level 9) as a Brotli fallback"""
        gz_file = file_path.with_suffix(file_path.suffix + '.gz')
        try:
            original_data = file_path.read_bytes()
            original_size = len(original_data)

            with _gzip.open(gz_file, 'wb', compresslevel=9) as f:
                f.write(original_data)

            compressed_size = gz_file.stat().st_size

            if compressed_size < original_size * 0.95:
                ratio = (1 - compressed_size / original_size) * 100
                self.gzip_stats['files_compressed'] += 1
                self.gzip_stats['original_size'] += original_size
                self.gzip_stats['compressed_size'] += compressed_size
                return True
            else:
                gz_file.unlink()
                self.gzip_stats['files_skipped'] += 1
                return False

        except Exception as e:
            print(f"   ❌ Error gzip compressing {file_path}: {e}")
            if gz_file.exists():
                gz_file.unlink()
            return False

    def compress_directory(self):
        """Compress all eligible files in directory with Brotli and Gzip"""
        print(f"🗜️  Compressing files with Brotli (quality={self.quality}) + Gzip fallback...")
        print(f"   Source: {self.public_dir}")

        # Find all files (once, reuse for both passes)
        all_files = [f for f in self.public_dir.rglob('*') if f.is_file()]
        print(f"   Found {len(all_files)} total files\n")

        # --- Brotli pass ---
        brotli_files = [f for f in all_files if self.should_compress(f)]

        if not brotli_files:
            print("   ℹ️  No files need Brotli compression (all up to date)")
        else:
            print(f"   [Brotli] Processing {len(brotli_files)} files...")
            for file_path in brotli_files:
                self.stats['files_processed'] += 1
                self.compress_file(file_path)

        # --- Gzip pass ---
        # Re-scan so newly created .br files are excluded automatically
        all_files = [f for f in self.public_dir.rglob('*') if f.is_file()]
        gzip_files = [f for f in all_files if self.should_compress_gzip(f)]

        if not gzip_files:
            print("   ℹ️  No files need Gzip compression (all up to date)")
        else:
            print(f"\n   [Gzip]   Processing {len(gzip_files)} files...")
            for file_path in gzip_files:
                self.compress_file_gzip(file_path)

        # Print summary
        print(f"\n📊 Compression Summary:")
        print(f"   Brotli — compressed: {self.stats['files_compressed']}, "
              f"skipped: {self.stats['files_skipped']}")
        print(f"   Gzip   — compressed: {self.gzip_stats['files_compressed']}, "
              f"skipped: {self.gzip_stats['files_skipped']}")

        if self.stats['compressed_size'] > 0:
            total_original = self.stats['original_size']
            total_compressed = self.stats['compressed_size']
            total_saved = total_original - total_compressed
            total_ratio = (1 - total_compressed / total_original) * 100

            print(f"\n💾 Brotli Space Savings:")
            print(f"   Original size: {total_original:,} bytes ({total_original/1024/1024:.2f} MB)")
            print(f"   Compressed size: {total_compressed:,} bytes ({total_compressed/1024/1024:.2f} MB)")
            print(f"   Space saved: {total_saved:,} bytes ({total_saved/1024/1024:.2f} MB)")
            print(f"   Average compression: {total_ratio:.1f}%")

        if self.gzip_stats['compressed_size'] > 0:
            gz_original = self.gzip_stats['original_size']
            gz_compressed = self.gzip_stats['compressed_size']
            gz_saved = gz_original - gz_compressed
            gz_ratio = (1 - gz_compressed / gz_original) * 100

            print(f"\n💾 Gzip Space Savings:")
            print(f"   Original size: {gz_original:,} bytes ({gz_original/1024/1024:.2f} MB)")
            print(f"   Compressed size: {gz_compressed:,} bytes ({gz_compressed/1024/1024:.2f} MB)")
            print(f"   Space saved: {gz_saved:,} bytes ({gz_saved/1024/1024:.2f} MB)")
            print(f"   Average compression: {gz_ratio:.1f}%")

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
    
    print("\n✅ Brotli + Gzip compression complete!")
    print("\n📝 Note: Upload the original, .br, and .gz files to your hosting.")
    print("   Cloudflare Pages serves .br to Brotli-capable browsers and .gz as fallback.")

if __name__ == '__main__':
    main()
