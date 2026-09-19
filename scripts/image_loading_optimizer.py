#!/usr/bin/env python3
"""
Image loading strategy — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the fifth cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

Two related per-page jobs on the same already-parsed soup: assigning
loading="eager"/"lazy" + fetchpriority based on an image's position and
likely importance (hero/featured/above-fold vs. everything else), and
tuning the `sizes` attribute on responsive featured images for mobile
breakpoints. Both are fully stateless — they only ever touch the soup
they're handed.

WordPressStaticGenerator.process_html() drives these via an
ImageLoadingOptimizer instance (self.images); see that method for where
they run. Behaviour is unchanged from the pre-extraction version — this is
a pure move, not a rewrite.
"""


class ImageLoadingOptimizer:
    """Image loading/priority strategy and responsive `sizes` tuning for a
    single page's already-parsed soup. Fully stateless: takes no
    constructor arguments."""

    def add_lazy_loading(self, soup):
        """Add intelligent lazy loading based on image position and priority"""

        # Find all images
        images = soup.find_all('img')

        if not images:
            return

        eager_count = 0
        lazy_count = 0
        high_priority_count = 0

        for idx, img in enumerate(images):
            # Skip if image already has loading attribute
            if img.get('loading'):
                continue

            # Determine if this is a high-priority image
            is_hero_image = self._is_hero_image(img)
            is_featured_post = self._is_featured_post_image(img, idx)
            is_above_fold = idx < 3  # First 3 images likely above fold

            # High priority images: load eagerly with high fetchpriority
            if is_hero_image or (is_featured_post and idx == 0):
                img['loading'] = 'eager'
                img['fetchpriority'] = 'high'
                high_priority_count += 1
                eager_count += 1
                print(f"   🚀 Image {idx + 1}: HIGH PRIORITY (hero/featured)")

            # Above-fold images: eager loading but normal priority
            elif is_above_fold and (is_featured_post or idx < 2):
                img['loading'] = 'eager'
                img['decoding'] = 'async'
                eager_count += 1
                print(f"   ⚡ Image {idx + 1}: eager loading (above fold)")

            # Below-fold images: lazy loading
            else:
                img['loading'] = 'lazy'
                img['decoding'] = 'async'
                lazy_count += 1
                # Reduce priority for way-below-fold images
                if idx > 10:
                    # These are far down the page, lowest priority
                    pass

        print("   ✅ Image loading strategy:")
        print(f"      🚀 High priority: {high_priority_count}")
        print(f"      ⚡ Eager: {eager_count - high_priority_count}")
        print(f"      📦 Lazy: {lazy_count}")

    def _is_hero_image(self, img):
        """Determine if an image is a hero/banner image"""
        # Check for hero image classes or attributes
        img_class = ' '.join(img.get('class', []))

        # Common hero image patterns
        hero_patterns = ['hero', 'banner', 'featured-image', 'masthead']

        for pattern in hero_patterns:
            if pattern in img_class.lower():
                return True

        # Check parent elements for hero sections
        parent = img.parent
        for _ in range(3):  # Check up to 3 levels up
            if parent and parent.name:
                parent_class = ' '.join(parent.get('class', []))
                for pattern in hero_patterns:
                    if pattern in parent_class.lower():
                        return True
                parent = parent.parent
            else:
                break

        return False

    def _is_featured_post_image(self, img, idx):
        """Determine if an image is a featured post thumbnail"""
        img_class = ' '.join(img.get('class', []))

        # WordPress post thumbnail classes
        if 'wp-post-image' in img_class or 'post-thumbnail' in img_class:
            return True

        # Check if inside a post entry/article
        parent = img.parent
        for _ in range(5):  # Check up to 5 levels up
            if parent and parent.name:
                parent_class = ' '.join(parent.get('class', []))
                # Archive/list page entry classes
                if any(cls in parent_class for cls in ['entry', 'post', 'article']):
                    return True
                parent = parent.parent
            else:
                break

        return False

    def optimize_responsive_images(self, soup):
        """Optimize responsive image sizes attribute for better mobile performance"""
        # Find featured images (post thumbnails) that have srcset
        featured_images = soup.find_all('img', class_=lambda x: x and 'wp-post-image' in x and 'attachment-medium_large' in x)

        if not featured_images:
            return

        optimized_count = 0

        for img in featured_images:
            srcset = img.get('srcset', '')
            sizes = img.get('sizes', '')

            if not srcset or not sizes:
                continue

            # Mobile-optimized sizes attribute with granular breakpoints
            # Tells browser to load appropriately sized images for each device
            # Original: sizes="(max-width: 768px) 100vw, 768px" or similar
            # Optimized with mobile breakpoints:
            #   - 320px screens (iPhone SE): ~95vw = 304px -> use 300w image
            #   - 375px screens (iPhone): ~95vw = 356px -> use 300w image
            #   - 480px screens: ~90vw = 432px -> use 768w image
            #   - 768px tablets: ~90vw = 691px -> use 768w image
            #   - Desktop: fixed 400px

            # Check if this needs optimization (has old pattern)
            if sizes and ('768px' in sizes or '100vw' in sizes):
                # New mobile-optimized sizes with multiple breakpoints
                new_sizes = '(max-width: 480px) 95vw, (max-width: 768px) 90vw, 400px'
                img['sizes'] = new_sizes
                optimized_count += 1
                print("   📱 Optimized image sizes for mobile: added 480px breakpoint")

        if optimized_count > 0:
            print(f"   ✅ Optimized {optimized_count} featured image(s) with mobile-specific breakpoints")
