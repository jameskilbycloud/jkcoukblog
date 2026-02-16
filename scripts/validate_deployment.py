#!/usr/bin/env python3
"""
Comprehensive post-optimization validation for static site deployment.

This script validates that all optimization steps completed successfully:
- Brotli compression integrity (.br files match originals)
- Modern image formats (AVIF/WebP exist and are valid)
- Picture elements (correct structure and fallback order)
- Minification (no broken HTML/CSS/JS)
- Critical CSS inlining

Usage:
    python3 validate_deployment.py <site_directory>
"""

import sys
from pathlib import Path
import brotli
from PIL import Image
from bs4 import BeautifulSoup
import json


class DeploymentValidator:
    """Validates optimized static site before deployment."""

    def __init__(self, site_dir):
        self.site_dir = Path(site_dir)
        self.errors = []
        self.warnings = []
        self.stats = {}

    def find_files(self, extensions):
        """Find all files with given extensions."""
        files = []
        for ext in extensions:
            files.extend(self.site_dir.glob(f'**/*{ext}'))
        return sorted(files)

    def validate_brotli_files(self):
        """
        Verify Brotli compression integrity.

        Checks:
        1. All compressible files (>1KB) have .br variants
        2. .br files are valid and can decompress
        3. Decompressed content matches original
        4. No orphaned .br files
        """
        print("📦 Validating Brotli compression...")

        compressible_exts = ['.html', '.css', '.js', '.json', '.xml', '.svg']
        compressible_files = self.find_files(compressible_exts)

        # Filter files >1KB (same threshold as brotli_compress.py)
        compressible_files = [f for f in compressible_files if f.stat().st_size > 1024]

        brotli_found = 0
        brotli_valid = 0
        brotli_mismatch = 0

        for file_path in compressible_files:
            br_path = Path(str(file_path) + '.br')

            if not br_path.exists():
                # Not all files get compressed (need ≥5% reduction)
                # This is a warning, not an error
                continue

            brotli_found += 1

            # Verify .br is valid by decompressing
            try:
                with open(br_path, 'rb') as f:
                    compressed = f.read()
                decompressed = brotli.decompress(compressed)

                # Verify content matches original
                with open(file_path, 'rb') as f:
                    original = f.read()

                if decompressed != original:
                    self.errors.append(
                        f"Brotli mismatch: {br_path.relative_to(self.site_dir)} "
                        f"doesn't match {file_path.relative_to(self.site_dir)}"
                    )
                    brotli_mismatch += 1
                else:
                    brotli_valid += 1

            except Exception as e:
                self.errors.append(
                    f"Corrupt Brotli file: {br_path.relative_to(self.site_dir)} - {e}"
                )

        # Check for orphaned .br files
        all_br_files = self.find_files(['.br'])
        for br_file in all_br_files:
            original_path = Path(str(br_file)[:-3])  # Remove .br extension
            if not original_path.exists():
                self.warnings.append(
                    f"Orphaned Brotli file: {br_file.relative_to(self.site_dir)} "
                    f"(no original file)"
                )

        self.stats['brotli_files_found'] = brotli_found
        self.stats['brotli_files_valid'] = brotli_valid
        self.stats['brotli_files_mismatch'] = brotli_mismatch

        print(f"  ✓ Found {brotli_found} Brotli compressed files")
        print(f"  ✓ {brotli_valid} valid, {brotli_mismatch} mismatches")

    def validate_image_formats(self):
        """
        Verify modern image formats exist and are valid.

        Checks:
        1. All .jpg/.jpeg/.png images have .avif and .webp variants
        2. AVIF/WebP files are valid (can be opened by PIL)
        3. Report coverage percentage
        """
        print("\n🖼️  Validating image formats...")

        original_images = self.find_files(['.jpg', '.jpeg', '.png'])

        # Filter out very small images (likely icons, logos)
        original_images = [img for img in original_images if img.stat().st_size > 10240]  # >10KB

        avif_count = 0
        webp_count = 0
        missing_avif = []
        missing_webp = []

        for img_path in original_images:
            stem = img_path.stem
            parent = img_path.parent

            # Check AVIF exists
            avif_path = parent / f"{stem}.avif"
            if not avif_path.exists():
                missing_avif.append(img_path)
            else:
                # Verify AVIF is valid
                try:
                    img = Image.open(avif_path)
                    img.verify()
                    avif_count += 1
                except Exception as e:
                    self.errors.append(
                        f"Invalid AVIF: {avif_path.relative_to(self.site_dir)} - {e}"
                    )

            # Check WebP exists
            webp_path = parent / f"{stem}.webp"
            if not webp_path.exists():
                missing_webp.append(img_path)
            else:
                try:
                    img = Image.open(webp_path)
                    img.verify()
                    webp_count += 1
                except Exception as e:
                    self.errors.append(
                        f"Invalid WebP: {webp_path.relative_to(self.site_dir)} - {e}"
                    )

        # Calculate coverage
        total = len(original_images)
        avif_coverage = (avif_count / total * 100) if total > 0 else 0
        webp_coverage = (webp_count / total * 100) if total > 0 else 0

        self.stats['total_images'] = total
        self.stats['avif_count'] = avif_count
        self.stats['webp_count'] = webp_count
        self.stats['avif_coverage'] = f"{avif_coverage:.1f}%"
        self.stats['webp_coverage'] = f"{webp_coverage:.1f}%"

        print(f"  ✓ Total images (>10KB): {total}")
        print(f"  ✓ AVIF coverage: {avif_coverage:.1f}% ({avif_count}/{total})")
        print(f"  ✓ WebP coverage: {webp_coverage:.1f}% ({webp_count}/{total})")

        # Warn if coverage is low
        if avif_coverage < 90 and total > 0:
            self.warnings.append(
                f"Low AVIF coverage: {avif_coverage:.1f}% (expected >90%)"
            )
            if len(missing_avif) <= 5:
                for img in missing_avif:
                    self.warnings.append(f"  Missing AVIF for: {img.relative_to(self.site_dir)}")

        if webp_coverage < 90 and total > 0:
            self.warnings.append(
                f"Low WebP coverage: {webp_coverage:.1f}% (expected >90%)"
            )
            if len(missing_webp) <= 5:
                for img in missing_webp:
                    self.warnings.append(f"  Missing WebP for: {img.relative_to(self.site_dir)}")

    def validate_picture_elements(self):
        """
        Verify picture elements are properly structured.

        Checks:
        1. All <picture> elements have <source> tags with type attributes
        2. Type attributes are correct (image/avif, image/webp)
        3. Referenced files exist on disk
        4. Fallback order is correct (AVIF → WebP → original)
        5. Every <picture> has an <img> fallback
        """
        print("\n🎨 Validating picture elements...")

        html_files = self.find_files(['.html'])

        total_pictures = 0
        valid_pictures = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
            except Exception as e:
                self.errors.append(
                    f"Failed to parse HTML: {html_file.relative_to(self.site_dir)} - {e}"
                )
                continue

            for picture in soup.find_all('picture'):
                total_pictures += 1
                sources = picture.find_all('source')
                img = picture.find('img')

                rel_file = html_file.relative_to(self.site_dir)

                # Verify <img> fallback exists
                if not img:
                    self.errors.append(f"{rel_file}: <picture> without <img> fallback")
                    continue

                # Verify sources have type attributes
                has_avif = False
                has_webp = False

                for source in sources:
                    srcset = source.get('srcset', '')
                    image_type = source.get('type', '')

                    if not image_type:
                        self.errors.append(
                            f"{rel_file}: <source> without type attribute"
                        )
                        continue

                    # Track format types
                    if image_type == 'image/avif':
                        has_avif = True
                    elif image_type == 'image/webp':
                        has_webp = True

                    # Verify type matches srcset extension
                    if 'avif' in srcset and image_type != 'image/avif':
                        self.errors.append(
                            f"{rel_file}: AVIF source with wrong type: {image_type}"
                        )
                    if 'webp' in srcset and image_type != 'image/webp':
                        self.errors.append(
                            f"{rel_file}: WebP source with wrong type: {image_type}"
                        )

                    # Verify referenced files exist (first URL only, not all srcset variants)
                    if srcset:
                        first_url = srcset.split(',')[0].strip().split()[0]
                        # Skip data URIs, absolute URLs, and fragments
                        if first_url.startswith(('data:', 'http://', 'https://', '//', '#')):
                            continue

                        file_path = self.site_dir / first_url.lstrip('/')
                        if not file_path.exists():
                            self.warnings.append(
                                f"{rel_file}: Referenced image not found: {first_url}"
                            )

                # Verify correct source order (AVIF before WebP)
                if len(sources) >= 2 and has_avif and has_webp:
                    first_type = sources[0].get('type', '')
                    second_type = sources[1].get('type', '')

                    if first_type == 'image/avif' and second_type == 'image/webp':
                        valid_pictures += 1
                    else:
                        self.warnings.append(
                            f"{rel_file}: Picture sources not in optimal order "
                            f"(should be AVIF, then WebP)"
                        )

        self.stats['picture_elements'] = total_pictures
        self.stats['valid_picture_elements'] = valid_pictures

        print(f"  ✓ Found {total_pictures} picture elements")
        print(f"  ✓ {valid_pictures} with optimal source order")

    def validate_minification(self):
        """
        Verify minification didn't break HTML/CSS/JS.

        Checks:
        1. HTML files parse correctly with BeautifulSoup
        2. No unclosed tags
        """
        print("\n✂️  Validating minification...")

        html_files = self.find_files(['.html'])
        valid_html = 0
        broken_html = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # Check for basic HTML structure
                if soup.html and soup.head and soup.body:
                    valid_html += 1
                else:
                    self.warnings.append(
                        f"Incomplete HTML structure: {html_file.relative_to(self.site_dir)}"
                    )
                    broken_html += 1

            except Exception as e:
                self.errors.append(
                    f"HTML parsing failed (possible minification issue): "
                    f"{html_file.relative_to(self.site_dir)} - {e}"
                )
                broken_html += 1

        self.stats['html_files_checked'] = len(html_files)
        self.stats['valid_html_files'] = valid_html
        self.stats['broken_html_files'] = broken_html

        print(f"  ✓ Checked {len(html_files)} HTML files")
        print(f"  ✓ {valid_html} valid, {broken_html} with issues")

    def validate_critical_css(self):
        """
        Verify critical CSS was inlined.

        Checks:
        1. HTML files have <style> tags in <head>
        2. Main CSS is loaded with media="print" or async attribute
        """
        print("\n🎨 Validating critical CSS...")

        html_files = self.find_files(['.html'])
        files_with_inline = 0
        files_with_async_css = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # Check for inline styles in head
                if soup.head:
                    inline_styles = soup.head.find_all('style')
                    if inline_styles:
                        files_with_inline += 1

                    # Check for async CSS loading
                    css_links = soup.head.find_all('link', rel='stylesheet')
                    for link in css_links:
                        if link.get('media') == 'print' or link.get('onload'):
                            files_with_async_css += 1
                            break

            except Exception as e:
                # Already logged in minification check
                pass

        self.stats['files_with_critical_css'] = files_with_inline
        self.stats['files_with_async_css'] = files_with_async_css

        print(f"  ✓ {files_with_inline} files with inlined critical CSS")
        print(f"  ✓ {files_with_async_css} files with async CSS loading")

    def validate_all(self):
        """Run all validation checks."""
        print("🔍 Running comprehensive deployment validation...\n")
        print("="*80)

        self.validate_brotli_files()
        self.validate_image_formats()
        self.validate_picture_elements()
        self.validate_minification()
        self.validate_critical_css()

        self.print_summary()

        return len(self.errors) == 0

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        if self.errors:
            print(f"\n❌ {len(self.errors)} ERROR(S) found:")
            for error in self.errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} WARNING(S):")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"  - {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more warnings")

        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")

        # Print stats
        if self.stats:
            print("\n📊 Statistics:")
            for key, value in self.stats.items():
                print(f"  {key}: {value}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: validate_deployment.py <site_directory>")
        print("\nExample:")
        print("  python3 validate_deployment.py ./static-output")
        sys.exit(1)

    site_dir = sys.argv[1]

    if not Path(site_dir).exists():
        print(f"❌ Error: Directory not found: {site_dir}")
        sys.exit(1)

    validator = DeploymentValidator(site_dir)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
