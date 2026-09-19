#!/usr/bin/env python3
"""
Inline CSS extraction + asset-URL cleanup — extracted from
WordPressStaticGenerator (wp_to_static_generator.py), the fifteenth cut out
of that god object (see scripts/site_artifacts_builder.py's docstring for
the first).

Four per-page passes, in the order process_html() ran them:
- fix_inline_css_urls(): rewrites absolute WordPress font URLs inside
  <style> blocks to relative ones.
- extract_inline_css(): lifts inline <style> blocks out to deduplicated
  external files under css_output_dir (assets/css/), replacing each with a
  <link rel="stylesheet">. Dedup is by an MD5 hash of the CSS content,
  cached on the instance in extracted_css_files so identical inline blocks
  across pages share one file.
- strip_asset_version_queries(): strips WordPress's ?ver=x.y.z cache-busting
  query strings from <link>/<script> URLs and renames the matching files on
  disk — Cloudflare Pages strips query strings from requests, so a
  downloaded file at the versioned path would otherwise 404.
- fix_splide_carousel(): adds the Splide.js carousel library + init script
  for the Kadence theme's related/similar-posts carousel, which WordPress
  renders server-side but never ships the JS for in a static export.

Needs wp_url (URL rewriting) and output_dir (css_output_dir derives from
it, and strip_asset_version_queries renames files under it).
WordPressStaticGenerator.process_html() drives this via an
InlineCSSFixups instance (self.inline_css); see that method for where each
pass runs. Behaviour is unchanged from the pre-extraction version — this is
a pure move, not a rewrite.
"""


class InlineCSSFixups:
    """Inline-CSS URL rewriting/extraction and asset-version-query cleanup
    for a single page's already-parsed soup. Needs wp_url/output_dir."""

    def __init__(self, wp_url, output_dir):
        self.wp_url = wp_url
        self.output_dir = output_dir
        self.css_output_dir = self.output_dir / 'assets' / 'css'
        self.extracted_css_files = {}  # Map CSS hash to filename

    def fix_inline_css_urls(self, soup):
        """Fix inline CSS to convert font URLs from absolute to relative"""
        import re

        # Find all style tags with inline CSS
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_content = style_tag.string

                # Pattern to match font URLs
                font_url_pattern = r"url\(([^)]+)\)"

                def replace_font_url(match):
                    url = match.group(1).strip('"\'')
                    if url.startswith(self.wp_url):
                        # Convert absolute WordPress URL to relative
                        relative_url = url.replace(self.wp_url, '')
                        return f"url({relative_url})"
                    else:
                        # Leave other URLs as-is
                        return match.group(0)

                # Replace font URLs in the inline CSS
                updated_css = re.sub(font_url_pattern, replace_font_url, css_content)

                if updated_css != css_content:
                    style_tag.string = updated_css
                    print("   🎨 Fixed inline CSS font URLs")

    def extract_inline_css(self, soup, current_url):
        """Extract inline CSS to external files to reduce HTML payload"""
        import hashlib

        # Find all inline style tags
        style_tags = soup.find_all('style')

        if not style_tags:
            return

        # Ensure CSS output directory exists
        self.css_output_dir.mkdir(parents=True, exist_ok=True)

        for style_tag in style_tags:
            # Skip empty style tags
            if not style_tag.string or not style_tag.string.strip():
                continue

            # Get style ID if present
            style_id = style_tag.get('id', 'inline-styles')
            css_content = style_tag.string

            # Skip very small CSS blocks (< 100 bytes) - not worth extracting
            if len(css_content) < 100:
                continue

            # Create a hash of the CSS content for deduplication
            css_hash = hashlib.md5(css_content.encode()).hexdigest()[:8]

            # Check if we've already created a file for this CSS content
            if css_hash in self.extracted_css_files:
                css_filename = self.extracted_css_files[css_hash]
            else:
                # Create external CSS file
                css_filename = f"{style_id}-{css_hash}.min.css"
                css_file_path = self.css_output_dir / css_filename

                # Write CSS to external file
                css_file_path.write_text(css_content, encoding='utf-8')
                self.extracted_css_files[css_hash] = css_filename
                print(f"   📄 Created CSS: /assets/css/{css_filename}")

            # Use absolute path from root for CSS files
            # This works correctly at any depth in the site hierarchy
            css_path = f"/assets/css/{css_filename}"

            # Create link tag to replace inline style
            link_tag = soup.new_tag('link')
            link_tag['rel'] = 'stylesheet'
            link_tag['href'] = css_path
            link_tag['media'] = 'all'

            # Replace inline style with link tag
            style_tag.replace_with(link_tag)

    def strip_asset_version_queries(self, soup):
        """Strip ?ver= query strings from CSS/JS asset URLs.

        WordPress appends ?ver=x.y.z to asset URLs for cache busting. When these
        assets are downloaded to disk, the query string becomes part of the filename
        which breaks static file serving (e.g. Cloudflare Pages strips query strings
        from requests, so the file is never found).

        This method:
        1. Strips ?ver=... from all <link> href and <script> src attributes
        2. Renames any files on disk that have ?ver= in their filename
        """
        import re

        # Fix <link> stylesheet hrefs
        for link in soup.find_all('link', href=True):
            href = link['href']
            if '?ver=' in href:
                clean_href = re.sub(r'\?ver=[^&"\']+', '', href)
                link['href'] = clean_href
                # Rename the file on disk if it exists with the versioned name
                versioned_path = self.output_dir / href.lstrip('/')
                clean_path = self.output_dir / clean_href.lstrip('/')
                if versioned_path.exists() and not clean_path.exists():
                    clean_path.parent.mkdir(parents=True, exist_ok=True)
                    versioned_path.rename(clean_path)
                    print(f"   📦 Renamed asset: {href} → {clean_href}")

        # Fix <script> srcs
        for script in soup.find_all('script', src=True):
            src = script['src']
            if '?ver=' in src:
                clean_src = re.sub(r'\?ver=[^&"\']+', '', src)
                script['src'] = clean_src
                versioned_path = self.output_dir / src.lstrip('/')
                clean_path = self.output_dir / clean_src.lstrip('/')
                if versioned_path.exists() and not clean_path.exists():
                    clean_path.parent.mkdir(parents=True, exist_ok=True)
                    versioned_path.rename(clean_path)
                    print(f"   📦 Renamed asset: {src} → {clean_src}")

    def fix_splide_carousel(self, soup):
        """Fix the Kadence theme's Splide carousel for the Similar Posts section.

        The WordPress Kadence theme uses Splide.js for the related/similar posts
        carousel, but the JS was never included in the static export. This method
        adds Splide JS from CDN and initialization code.
        """
        # Only add if there's a Splide carousel on the page
        carousels = soup.find_all(class_=lambda x: x and 'kadence-slide-init' in x)
        if not carousels:
            return

        # Strip pre-baked Splide state classes from static HTML.
        # WordPress server-side rendering adds is-initialized/is-active/splide-initial
        # but without the JS these cause broken display (e.g. display:block on the list).
        # Splide will re-add them correctly when it mounts.
        for carousel in carousels:
            classes = carousel.get('class', [])
            for cls in ['is-initialized', 'is-active', 'splide-initial', 'is-rendered']:
                if cls in classes:
                    classes.remove(cls)
            carousel['class'] = classes

        # Add Splide arrow/pagination styles inline (CSS optimizer strips
        # them from the external stylesheet because JS-injected elements
        # don't exist in the static HTML at build time)
        if soup.head:
            splide_style = soup.new_tag('style')
            splide_style.string = """
.splide button.splide__arrow{background:transparent!important;opacity:1!important;width:36px!important;height:36px!important;border-radius:50%!important;border:2px solid #f6821f!important;transition:all .2s!important}
.splide button.splide__arrow:hover{background:#f6821f!important}
.splide button.splide__arrow svg{fill:#f6821f!important;width:16px!important;height:16px!important;transition:fill .2s!important}
.splide button.splide__arrow:hover svg{fill:#0a0a0a!important}
.splide button.splide__arrow--prev{left:0.5em!important}
.splide button.splide__arrow--next{right:0.5em!important}
.splide .splide__pagination{padding:0.75rem 0!important}
.splide .splide__pagination li{display:inline-block!important;line-height:0!important}
.splide .splide__pagination button.splide__pagination__page{background:#555!important;opacity:1!important;width:8px!important;height:8px!important;min-width:8px!important;min-height:8px!important;max-width:8px!important;max-height:8px!important;border-radius:50%!important;margin:0 3px!important;padding:0!important;transition:all .2s!important;border:none!important}
.splide .splide__pagination button.splide__pagination__page.is-active{background:#f6821f!important;transform:scale(1.4)}
"""
            soup.head.append(splide_style)

        # Add Splide JS from CDN (before </body>)
        body = soup.find('body')
        if not body:
            return

        # Add Splide JS
        splide_script = soup.new_tag('script')
        splide_script['src'] = '/js/splide.min.js'
        splide_script['defer'] = ''
        body.append(splide_script)

        # Add initialization script that reads the data attributes
        init_script = soup.new_tag('script')
        init_script.string = """
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.kadence-slide-init.splide').forEach(function(el) {
    var cols = parseInt(el.dataset.columnsXxl || el.dataset.columnsMd || 3);
    var colsMd = parseInt(el.dataset.columnsMd || 3);
    var colsSm = parseInt(el.dataset.columnsSm || 2);
    var colsSs = parseInt(el.dataset.columnsSs || 1);
    var gutter = parseInt(el.dataset.sliderGutter || 40);
    var loop = el.dataset.sliderLoop === 'true';
    var arrows = el.dataset.sliderArrows === 'true';
    var dots = el.dataset.sliderDots === 'true';
    var autoplay = el.dataset.sliderAuto === 'true';
    var speed = parseInt(el.dataset.sliderAnimSpeed || 400);
    var perMove = parseInt(el.dataset.sliderScroll || 1);

    new Splide(el, {
      type: loop ? 'loop' : 'slide',
      perPage: cols,
      perMove: perMove,
      gap: gutter + 'px',
      arrows: arrows,
      pagination: dots,
      autoplay: autoplay,
      speed: speed,
      breakpoints: {
        1199: { perPage: colsMd },
        767: { perPage: colsSm },
        543: { perPage: colsSs }
      }
    }).mount();
  });
});
"""
        body.append(init_script)
        print("   🎠 Added Splide carousel JS and initialization")
