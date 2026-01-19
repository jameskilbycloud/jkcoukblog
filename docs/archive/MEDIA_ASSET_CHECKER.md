# WordPress Media Asset Checker

## Overview
The `check_missing_media.py` script reviews all posts and pages in your WordPress site to identify any missing or broken media assets (images, videos, audio files, etc.).

## What It Does
1. **Fetches all media** from the WordPress Media Library via the REST API
2. **Scans all posts** for media references in content and excerpts
3. **Scans all pages** for media references
4. **Extracts media from:**
   - `<img>` tags
   - `<picture>` and `<source>` tags with srcset
   - Background images in inline styles
   - `<video>` and `<source>` tags
   - `<audio>` tags
5. **Verifies accessibility** by making HEAD requests to potentially missing URLs
6. **Generates a detailed report** of missing media

## Usage

### Basic Usage
```bash
export WP_AUTH_TOKEN='your_base64_encoded_token'
python3 check_missing_media.py
```

### Skip Accessibility Verification
If you want to skip the HTTP verification step (faster but may include false positives):
```bash
python3 check_missing_media.py --no-verify
```

## Requirements
- Python 3.6+
- Dependencies: `requests`, `beautifulsoup4`
- WordPress REST API access with authentication

## Authentication
The script uses Basic Authentication with the WordPress REST API. You need to set the `WP_AUTH_TOKEN` environment variable with a base64-encoded `username:password` string.

To create the token:
```bash
echo -n "username:password" | base64
```

## Output
The script provides:
- Real-time progress as it scans posts and pages
- A summary of total media items found
- A detailed report showing:
  - Which posts/pages have missing media
  - The type of media (image, video, etc.)
  - The URL of the missing asset
  - Context (surrounding HTML)
  - Alt text (for images)

## Example Output
```
================================================================================
WordPress Media Asset Checker
================================================================================
🖼️  Fetching all media from WordPress Media API...
   📄 Page 1: 100 items
   📄 Page 2: 50 items
✅ Found 150 media items with 450 total URLs (including sizes)

📝 Checking posts for media references...
   📄 Page 1: 100 posts checked
✅ Checked 100 posts

📑 Checking pages for media references...
   📄 Page 1: 5 pages checked
✅ Checked 5 pages

🔍 Verifying accessibility of potentially missing media...
   ❌ 404: https://wordpress.jameskilby.cloud/wp-content/uploads/old-image.jpg

================================================================================
📊 MISSING MEDIA REPORT
================================================================================

⚠️  Found missing media in 2 content items
📊 Total referenced media URLs: 523
🖼️  Total available media URLs: 450

────────────────────────────────────────────────────────────────────────────────
📄 POST: My Blog Post Title
   ID: 123
   Missing items: 1

   ❌ IMAGE
      URL: https://wordpress.jameskilby.cloud/wp-content/uploads/old-image.jpg
      Alt: Old screenshot
      Context: <img src="https://wordpress.jameskilby.cloud/wp-content/uploads/old-image.jpg" alt="Old screenshot" class="wp-image-456"/>...

================================================================================
📊 SUMMARY: 1 total missing media items
================================================================================
```

## Integration with Static Site Generation
This tool is designed to work alongside the existing `wp_to_static_generator.py` script. Use it to:
- Identify and fix broken media before static site generation
- Audit your WordPress media library
- Find unused or orphaned media assets
- Ensure all content has proper media resources

## Configuration
The script uses the centralized `config.py` file for WordPress URL configuration:
- `Config.WP_URL`: Your WordPress site URL (default: https://wordpress.jameskilby.cloud)

## Notes
- The script only checks published posts and pages
- External media URLs (not hosted on your WordPress site) are considered "available"
- The verification step makes HEAD requests to avoid downloading full media files
- Large sites may take several minutes to scan completely
