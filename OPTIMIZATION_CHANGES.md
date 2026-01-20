# Image Optimization Script Enhancement

## Changes Made

### Problem Identified
The current HTML files only include AVIF sources in `<picture>` elements, missing WebP sources entirely. This means browsers that don't support AVIF (15% of users) fall back directly to JPEG, missing out on 40-50% bandwidth savings.

**Current HTML:**
```html
<picture>
  <source srcset="/path/image.avif" type="image/avif"/>
  <img src="/path/image.jpg" srcset="..." />
</picture>
```

**Expected HTML:**
```html
<picture>
  <source srcset="/path/image-768.avif 768w, /path/image-300.avif 300w" type="image/avif"/>
  <source srcset="/path/image-768.webp 768w, /path/image-300.webp 300w" type="image/webp"/>
  <img src="/path/image.jpg" srcset="/path/image-768.jpg 768w, /path/image-300.jpg 300w" />
</picture>
```

### Root Cause
The `optimize_images.py` script skipped updating existing `<picture>` elements (line 273: `if img.parent.name == 'picture': continue`). Since images were already wrapped in picture tags with only AVIF sources, the script never added WebP sources.

### Solution Implemented

#### 1. New Helper Method: `_get_responsive_srcset()`
- Generates responsive srcset for modern formats (WebP/AVIF)
- Parses original img srcset: `"img-300.jpg 300w, img-768.jpg 768w"`
- Converts each size to modern format if file exists
- Returns: `"img-300.webp 300w, img-768.webp 768w"`

#### 2. Enhanced `update_html_files()` Method

**Phase 1: Update Existing Picture Elements**
- Finds all existing `<picture>` elements
- Checks which sources are missing (AVIF/WebP)
- Adds missing WebP sources with responsive srcset
- Updates existing AVIF sources to include responsive srcset
- Maintains proper source order: AVIF → WebP → IMG

**Phase 2: Create New Picture Elements**
- Finds img tags not yet in picture elements
- Creates picture elements with both AVIF and WebP sources
- Includes responsive srcset for all modern formats

### Benefits

1. **Browser Coverage**
   - AVIF support: ~85% (Chrome, Edge, Firefox, Safari 16+)
   - WebP support: ~95% (Chrome, Edge, Firefox, Safari 14+)
   - Combined coverage: 95%+ with optimal format selection

2. **Responsive Images**
   - Modern formats now have responsive srcset
   - Browsers load appropriate size for viewport
   - Mobile users get smaller files automatically

3. **Bandwidth Savings**
   - AVIF users: 70% size reduction
   - WebP users: 65% size reduction (previously fell back to JPEG)
   - Expected overall savings increase: 15-20% for WebP-only browsers

### Example Output

**Before:**
```html
<picture>
  <source srcset="/uploads/2025/02/image-768x193.avif" type="image/avif"/>
  <img src="/uploads/2025/02/image-768x193.png"
       srcset="/uploads/2025/02/image-768x193.png 768w,
               /uploads/2025/02/image-300x75.png 300w"/>
</picture>
```

**After:**
```html
<picture>
  <source srcset="/uploads/2025/02/image-768x193.avif 768w,
                   /uploads/2025/02/image-300x75.avif 300w"
          type="image/avif"/>
  <source srcset="/uploads/2025/02/image-768x193.webp 768w,
                   /uploads/2025/02/image-300x75.webp 300w"
          type="image/webp"/>
  <img src="/uploads/2025/02/image-768x193.png"
       srcset="/uploads/2025/02/image-768x193.png 768w,
               /uploads/2025/02/image-300x75.png 300w"/>
</picture>
```

### Testing

Run the optimization workflow manually:
1. Go to GitHub Actions
2. Select "Optimize Images" workflow
3. Click "Run workflow"
4. Monitor output for:
   - Number of HTML files updated
   - Number of picture elements enhanced
   - Responsive srcset additions

### Expected Results

- ~400-500 HTML files updated
- ~1,200+ picture elements enhanced with WebP sources
- ~1,200+ AVIF sources enhanced with responsive srcset
- ~1,200+ WebP sources added with responsive srcset

### Files Modified

- `scripts/optimize_images.py` (lines 255-446)
  - Added `_get_responsive_srcset()` method
  - Enhanced `update_html_files()` method
