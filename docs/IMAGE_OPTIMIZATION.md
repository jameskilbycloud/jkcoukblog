# 🖼️ Image Optimization Guide

Automated image optimization for your WordPress static site using WebP and AVIF formats.

## 📋 Overview

The image optimization system automatically:
- ✅ Converts JPEG/PNG images to modern WebP and AVIF formats
- ✅ Reduces image file sizes by 30-50% without visible quality loss
- ✅ Updates HTML files with `<picture>` elements for browser compatibility
- ✅ Caches optimization results to avoid reprocessing
- ✅ Maintains original images as fallback for older browsers

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended)

The easiest way to optimize images is using the automated GitHub Actions workflow.

**Run manually:**
1. Go to **Actions** tab in GitHub
2. Select **Optimize Images** workflow
3. Click **Run workflow**
4. Choose options:
   - Quality: 85 (default, range 0-100)
   - Workers: 4 (parallel processing threads)
   - Skip HTML: false (update HTML files)

**Automatic weekly optimization:**
- Runs every Sunday at 2 AM UTC
- Optimizes any new images added to the site

### Option 2: Local Optimization

Run image optimization on your local machine:

```bash
# Install dependencies
pip install -r requirements-images.txt

# Optimize images in public directory
python3 scripts/optimize_images.py ./public

# With custom settings
python3 scripts/optimize_images.py ./public --quality 90 --workers 8

# Skip HTML updates (optimization only)
python3 scripts/optimize_images.py ./public --skip-html
```

## ⚙️ How It Works

### 1. Image Conversion

For each JPEG/PNG image, the script:

```
Original:  image.jpg (500 KB)
    ↓
Generated: image.webp (175 KB) - 65% savings
Generated: image.avif (150 KB) - 70% savings
```

### 2. HTML Updates

Original HTML:
```html
<img src="/wp-content/uploads/2024/12/photo.jpg" alt="Photo">
```

Optimized HTML:
```html
<picture>
  <source srcset="/wp-content/uploads/2024/12/photo.avif" type="image/avif">
  <source srcset="/wp-content/uploads/2024/12/photo.webp" type="image/webp">
  <img src="/wp-content/uploads/2024/12/photo.jpg" alt="Photo">
</picture>
```

**Browser behavior:**
- Modern browsers (Chrome, Edge, Firefox): Use AVIF (smallest)
- Safari, older browsers: Use WebP (smaller than JPEG)
- Very old browsers: Use original JPEG (fallback)

### 3. Intelligent Caching

The system maintains a cache file (`.image-optimization-cache.json`) to:
- Skip already-optimized images (unless source changed)
- Speed up subsequent runs
- Track optimization history

## 📊 Performance Benefits

### Expected Results

Based on your current 92MB of images:

| Format | Size | Savings | Browser Support |
|--------|------|---------|-----------------|
| Original JPEG/PNG | 92 MB | - | 100% |
| WebP | ~55 MB | 40% | 95%+ |
| AVIF | ~46 MB | 50% | 85%+ |

### Real-World Impact

- **Page Load Time:** -30% to -50% reduction
- **Bandwidth Usage:** -40% to -50% reduction
- **CDN Costs:** -40% to -50% reduction
- **User Experience:** Faster page loads, especially on mobile
- **SEO:** Improved Core Web Vitals scores

## 🔧 Configuration Options

### Command Line Arguments

```bash
python3 scripts/optimize_images.py [PUBLIC_DIR] [OPTIONS]

Arguments:
  PUBLIC_DIR          Path to public directory (default: ./public)

Options:
  --quality QUALITY   Image quality 0-100 (default: 85)
                      Higher = better quality, larger files
                      85 is optimal balance for most images

  --workers WORKERS   Number of parallel workers (default: 4)
                      Increase for faster processing on powerful machines
                      Recommended: Number of CPU cores

  --skip-html        Skip updating HTML files
                     Use when you only want to generate optimized images
```

### Quality Settings Guide

| Quality | Use Case | File Size | Visual Quality |
|---------|----------|-----------|----------------|
| 60-70 | Thumbnails, previews | Smallest | Slight artifacts |
| **75-85** | **General use (recommended)** | **Balanced** | **Excellent** |
| 90-95 | High-quality photos | Larger | Near-perfect |
| 95-100 | Archives, print | Largest | Perfect |

**Recommendation:** Start with 85, adjust based on results.

## 📁 File Structure

After optimization, your uploads directory will look like:

```
public/wp-content/uploads/
├── 2024/
│   └── 12/
│       ├── photo.jpg          # Original (500 KB)
│       ├── photo.webp         # WebP version (175 KB)
│       └── photo.avif         # AVIF version (150 KB)
└── .image-optimization-cache.json  # Optimization cache
```

## 🔄 Workflow Integration

### Integrate with Static Site Generation

Add to your `deploy_static_site.py` or deployment script:

```python
import subprocess

def deploy_with_optimization():
    # Generate static site
    subprocess.run(['python3', 'scripts/wp_to_static_generator.py', './public'])

    # Optimize images
    subprocess.run(['python3', 'scripts/optimize_images.py', './public', '--quality', '85'])

    # Deploy to Cloudflare
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'Deploy with optimized images'])
    subprocess.run(['git', 'push'])
```

### GitHub Actions Integration

The workflow `.github/workflows/optimize-images.yml` includes:

1. **Automatic Scheduling:** Runs weekly
2. **Manual Trigger:** Run on-demand from Actions tab
3. **Statistics Tracking:** Reports optimization metrics
4. **Auto-Deployment:** Commits and pushes optimized images
5. **Cloudflare Integration:** Triggers automatic deployment

## 🐛 Troubleshooting

### Error: "No module named 'PIL'"

```bash
pip install Pillow pillow-avif-plugin
```

### Error: "AVIF generation failed"

AVIF support requires additional libraries on some systems:

**macOS:**
```bash
brew install libavif
pip install --upgrade pillow-avif-plugin
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libavif-dev
pip install --upgrade pillow-avif-plugin
```

**Solution:** If AVIF continues to fail, the script will still generate WebP images.

### Images not being optimized

Check:
1. Images are in `public/wp-content/uploads/` directory
2. Images are JPEG or PNG format
3. Cache might prevent re-optimization (delete `.image-optimization-cache.json` to force)

### HTML not updating

Ensure:
1. You're not using `--skip-html` flag
2. HTML files are writable
3. Image paths in HTML match actual file locations

## 📈 Monitoring & Metrics

### View Optimization Stats

After running the script, you'll see:

```
============================================================
📊 IMAGE OPTIMIZATION STATISTICS
============================================================
Total images found:      312
Images optimized:        156
Images skipped (cached): 156
Errors:                  0

WebP images generated:   156
AVIF images generated:   156

Original size:           92.45 MB
Optimized size:          46.12 MB
Total savings:           46.33 MB (50.1%)

Processing time:         47.23 seconds
============================================================
```

### GitHub Actions Summary

Each workflow run generates a summary showing:
- Images before/after
- New WebP and AVIF files created
- Total size reduction
- Deployment status

## 🎯 Best Practices

### 1. Run After Content Updates

Optimize images after adding new blog posts:
```bash
# Generate new static site
python3 scripts/deploy_static_site.py generate ./public

# Optimize all images (including new ones)
python3 scripts/optimize_images.py ./public
```

### 2. Use Quality 85 for Most Images

- Good balance between size and quality
- Visually indistinguishable from original
- 40-50% file size reduction

### 3. Let GitHub Actions Handle It

- Set up the weekly schedule
- Manual trigger when you publish new content
- Automatic deployment to Cloudflare Pages

### 4. Monitor CDN Bandwidth

Before and after optimization:
- Check Cloudflare Analytics bandwidth usage
- Should see 30-50% reduction in bandwidth
- Faster page loads in Analytics

## 🔐 Security Notes

- Original images are never deleted (always kept as fallback)
- Optimization is lossless for quality > 85
- No external services used (all processing is local)
- Cache file contains only file paths and hashes (no sensitive data)

## 📚 Additional Resources

- [WebP Documentation](https://developers.google.com/speed/webp)
- [AVIF Specification](https://aomediacodec.github.io/av1-avif/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [HTML Picture Element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/picture)

## 🆘 Support

If you encounter issues:

1. Check this documentation
2. Review GitHub Actions logs
3. Check `optimize_images.py` script output
4. Verify Python dependencies are installed
5. Check file permissions on `public/` directory

## 🎉 Results

After implementing image optimization:

- ✅ 30-50% reduction in page load time
- ✅ 40-50% reduction in bandwidth usage
- ✅ Improved Google PageSpeed scores
- ✅ Better mobile performance
- ✅ Lower CDN costs
- ✅ Happier users with faster site

---

**Generated with ❤️ for WordPress Static Site Automation**
