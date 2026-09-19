#!/usr/bin/env python3
"""
Head-chrome + static-site optimizations — extracted from
WordPressStaticGenerator (wp_to_static_generator.py), the sixteenth cut out
of that god object (see scripts/site_artifacts_builder.py's docstring for
the first). This is the last slice of that decomposition; everything
remaining on WordPressStaticGenerator is the orchestrator core
(download_and_process_url/process_html/generate_static_site) that calls
into every extracted collaborator, plus WP REST content download.

Seven per-page (mostly) passes:
- add_utterances_comments(): injects the Utterances comments widget on
  single posts/pages.
- add_static_optimizations(): cache-control/generator/theme-color meta
  tags, then calls through to favicon/brutalist-CSS/Plausible below, then
  adds stylesheet preload hints.
- add_favicon_links(): favicon.ico/PNG/apple-touch-icon/webmanifest links.
- consolidate_inline_css_files(): strips WP-leaked inline-CSS <link> tags
  the brutalist theme already overrides, plus any stale
  consolidated-inline-styles.min.css reference from older builds.
- _sync_brutalist_css() / add_brutalist_theme_css(): copies
  brutalist-theme.css into the output tree (content-compared, guarded to
  run once per build via _brutalist_css_synced) and inlines critical
  mobile CSS + links the external stylesheet.
- add_plausible_analytics(): same-origin Plausible script injection,
  dropping any legacy upstream-host preconnect hints.

Needs output_dir (for _sync_brutalist_css's copy target).
WordPressStaticGenerator wires this via a HeadChromeOptimizations instance
(self.head_chrome): process_html() drives the five per-page methods, and
generate_static_site() calls _sync_brutalist_css() once up front (see that
method's docstring for why it's also safe to call per-page). Behaviour is
unchanged from the pre-extraction version — this is a pure move, not a
rewrite.
"""

import shutil
from pathlib import Path


class HeadChromeOptimizations:
    """Head-chrome injection (comments, favicons, brutalist CSS, analytics,
    static-optimization meta tags) for a single page's already-parsed soup.
    Needs output_dir (for the brutalist CSS sync target)."""

    # WP-leaked inline CSS files we drop from the page entirely.
    # The brutalist theme already covers every visible element with !important
    # overrides, so these add parse cost (~150 ms on mobile) without changing
    # the rendered output. Gutenberg block content in posts may use the WP
    # preset variables (--wp--preset--color--*); if a regression appears,
    # re-introduce only `global-styles-inline-css` and `wp-block-library-inline-css`.
    _WP_INLINE_CSS_DROP_PATTERNS = (
        'wp-block-library-inline-css',
        'wp-block-heading-inline-css',
        'wp-block-paragraph-inline-css',
        'wp-block-table-inline-css',
        'wp-img-auto-sizes-contain-inline-css',
        'global-styles-inline-css',
        'classic-theme-styles-inline-css',
        'inline-styles-',
    )

    def __init__(self, output_dir):
        self.output_dir = output_dir

    def add_utterances_comments(self, soup):
        """Add Utterances comments section to the page"""
        # Only add comments to single post/page views, not archive/list pages
        body = soup.find('body')
        if not body:
            return

        # Check body classes to determine if this is a single post
        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()

        # Only add comments if this is explicitly a single post or page
        is_single_post = 'single-post' in body_class_str or 'single' in body_classes
        is_page = 'page-template' in body_class_str or ('page' in body_classes and 'single' not in body_class_str)

        if not (is_single_post or is_page):
            return  # Not a single post/page, skip comments

        # Remove any existing comments area first (so we can re-insert in the correct position)
        comments_area = soup.find('div', id='comments')
        if comments_area:
            comments_area.decompose()

        # Find the entry-content div to insert comments immediately after it
        insertion_point = None
        articles = soup.find_all('article')
        if articles and len(articles) >= 1:
            article = articles[0]

            # Look for entry-content div inside the article - this is the main post content
            entry_content = article.find('div', class_=lambda x: x and 'entry-content' in x)

            if entry_content:
                # Insert immediately after the article content
                insertion_point = entry_content
            else:
                # Fallback: insert after the article itself
                insertion_point = article

        if insertion_point:
            # Create the Utterances comments section
            comments_div = soup.new_tag('div')
            comments_div['id'] = 'comments'
            comments_div['class'] = 'comments-area'

            inner_div = soup.new_tag('div')
            inner_div['class'] = 'pb-30'

            section = soup.new_tag('section')
            section['id'] = 'utterances-comments'

            from config import Config as _utt_config

            script = soup.new_tag('script')
            script['src'] = 'https://utteranc.es/client.js'
            script['data-repo'] = _utt_config.UTTERANCES_REPO
            script['data-issue-term'] = 'pathname'
            script['data-theme'] = 'github-dark'
            script['crossorigin'] = 'anonymous'
            script['async'] = ''
            script['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader

            section.append(script)
            inner_div.append(section)
            comments_div.append(inner_div)

            # Insert immediately after article content
            insertion_point.insert_after(comments_div)
            print("   💬 Added Utterances comments section after article content")

    def add_static_optimizations(self, soup):
        """Add optimizations for static site performance"""
        if not soup.head:
            return

        # Add cache control meta tag
        cache_meta = soup.new_tag('meta')
        cache_meta['http-equiv'] = 'Cache-Control'
        cache_meta['content'] = 'max-age=86400'
        soup.head.append(cache_meta)

        # Add static site generator meta tag
        generator_meta = soup.new_tag('meta')
        generator_meta['name'] = 'generator'
        generator_meta['content'] = 'Static Site Generator 1.0'
        soup.head.append(generator_meta)

        # Add theme-color meta tag for mobile browsers
        # This colors the browser UI to match the site (improves mobile UX)
        existing_theme_color = soup.find('meta', attrs={'name': 'theme-color'})
        if not existing_theme_color:
            theme_color_meta = soup.new_tag('meta')
            theme_color_meta['name'] = 'theme-color'
            theme_color_meta['content'] = '#0a0a0a'  # Dark background - matches brutalist theme
            soup.head.append(theme_color_meta)
            print("   🎨 Added theme-color meta tag")
        else:
            # Update existing theme-color to match brutalist theme
            existing_theme_color['content'] = '#0a0a0a'
            print("   🎨 Updated theme-color meta tag to dark theme")

        # Add favicon links
        self.add_favicon_links(soup)

        # Inject brutalist theme CSS
        self.add_brutalist_theme_css(soup)

        # Add Plausible analytics if not already present
        self.add_plausible_analytics(soup)

        # Font preloads were removed: the inline critical CSS pins body to a
        # system-font stack, fonts.css uses font-display: optional (fonts that
        # arrive after the ~100 ms swap window are never rendered), and on
        # mobile the 138 KB of high-priority preloads contended with the LCP
        # image. See html_transformer._deep_clean_head for the matching
        # idempotent strip on previously-built pages.


        # Add preload hints for critical resources (with duplicate detection)
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                href = link['href']
                # Check if preload already exists for this href
                existing_preload = soup.find('link', rel='preload', href=href)
                if not existing_preload:
                    preload = soup.new_tag('link')
                    preload['rel'] = 'preload'
                    preload['as'] = 'style'
                    preload['href'] = href
                    soup.head.insert(0, preload)

    def add_favicon_links(self, soup):
        """Add favicon links for better browser support and performance"""
        if not soup.head:
            return

        # Check if favicon links already exist
        existing_favicon = soup.find('link', rel=lambda x: x and 'icon' in x)
        if existing_favicon:
            return  # Already has favicon links

        # Add favicon.ico (legacy browser support)
        favicon_ico = soup.new_tag('link')
        favicon_ico['rel'] = 'icon'
        favicon_ico['type'] = 'image/x-icon'
        favicon_ico['href'] = '/favicon.ico'
        soup.head.append(favicon_ico)

        # Add PNG favicon for modern browsers
        favicon_32 = soup.new_tag('link')
        favicon_32['rel'] = 'icon'
        favicon_32['type'] = 'image/png'
        favicon_32['sizes'] = '32x32'
        favicon_32['href'] = '/favicon-32x32.png'
        soup.head.append(favicon_32)

        favicon_16 = soup.new_tag('link')
        favicon_16['rel'] = 'icon'
        favicon_16['type'] = 'image/png'
        favicon_16['sizes'] = '16x16'
        favicon_16['href'] = '/favicon-16x16.png'
        soup.head.append(favicon_16)

        # Add Apple touch icon
        apple_touch = soup.new_tag('link')
        apple_touch['rel'] = 'apple-touch-icon'
        apple_touch['sizes'] = '180x180'
        apple_touch['href'] = '/apple-touch-icon.png'
        soup.head.append(apple_touch)

        # Add web app manifest
        manifest = soup.new_tag('link')
        manifest['rel'] = 'manifest'
        manifest['href'] = '/site.webmanifest'
        soup.head.append(manifest)

        print("   🐞 Added favicon links for browser support")

    def consolidate_inline_css_files(self, soup):
        """Strip WP-leaked inline CSS link tags. Previously concatenated them
        into consolidated-inline-styles.min.css; now we drop them entirely
        because the brutalist theme overrides everything visible.
        """
        if not soup.head:
            return

        dropped = []
        for link in list(soup.find_all('link', rel='stylesheet')):
            href = link.get('href', '')
            if any(p in href for p in self._WP_INLINE_CSS_DROP_PATTERNS):
                link.decompose()
                dropped.append(href)

        # Also strip the link to the previously-generated consolidated file
        # so seeded pages from older builds don't keep fetching it.
        for link in list(soup.find_all('link', rel='stylesheet')):
            if link.get('href', '').endswith('/consolidated-inline-styles.min.css'):
                link.decompose()
                dropped.append(link.get('href', ''))
        for preload in list(soup.find_all('link', rel='preload')):
            if (preload.get('href') or '').endswith('/consolidated-inline-styles.min.css'):
                preload.decompose()

        if dropped:
            print(f"   🧹 Dropped {len(dropped)} WP-leaked inline CSS link(s)")

    def _sync_brutalist_css(self):
        """Copy brutalist-theme.css into the output tree when its CONTENT differs.

        Runs at most once per build (instance-guarded). Compares bytes rather
        than mtimes: the self-hosted runner reuses its workspace and git-checkout
        timestamps are unreliable, so the old `source.mtime > dest.mtime` gate
        could skip a genuine CSS-only edit. Because brutalist-theme.css is
        excluded from critical-CSS inlining and only ships as the external
        /assets/css/brutalist-theme.css file, that skip meant a CSS-only change
        silently failed to deploy on an incremental build (no content change to
        force a recopy). A byte compare is deterministic regardless of mtimes.
        """
        if getattr(self, '_brutalist_css_synced', False):
            return
        source = Path(__file__).parent / 'brutalist-theme.css'
        dest = self.output_dir / 'assets' / 'css' / 'brutalist-theme.css'
        if not source.exists():
            print(f"   ⚠️  Brutalist theme CSS not found at {source}")
            return
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists() or source.read_bytes() != dest.read_bytes():
                shutil.copy(source, dest)
                print(f"   📋 Synced brutalist theme CSS → {dest}")
            self._brutalist_css_synced = True
        except OSError as e:
            print(f"   ⚠️  Failed to sync brutalist theme CSS: {e}")

    def add_brutalist_theme_css(self, soup):
        """Add brutalist theme CSS with critical mobile CSS inlined"""
        if not soup.head:
            return

        # Check if brutalist theme link is already injected
        existing_brutalist = soup.find('link', href='/assets/css/brutalist-theme.css')
        if existing_brutalist:
            return

        # Ensure the stylesheet is deployed to the output tree. Content-based
        # and idempotent (see _sync_brutalist_css); generate_static_site() also
        # calls it once up front, so this per-page call is normally a no-op.
        self._sync_brutalist_css()

        try:
            # Inline critical mobile CSS for faster FCP
            critical_css_path = Path(__file__).parent / 'critical-mobile.css'
            if critical_css_path.exists():
                try:
                    critical_css = critical_css_path.read_text(encoding='utf-8')
                    # Minify: remove comments and extra whitespace
                    import re
                    critical_css = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', critical_css)  # Remove comments
                    critical_css = re.sub(r'\s+', ' ', critical_css)  # Collapse whitespace
                    critical_css = critical_css.strip()

                    # Create inline style tag with media query for mobile
                    style_tag = soup.new_tag('style')
                    style_tag['media'] = 'screen and (max-width: 768px)'
                    style_tag.string = critical_css
                    # Insert at beginning of head for highest priority
                    soup.head.insert(0, style_tag)
                    print(f"   📱 Inlined critical mobile CSS ({len(critical_css)} bytes)")
                except Exception as e:
                    print(f"   ⚠️  Failed to inline critical CSS: {str(e)}")

            # Link to external file with media query and preload
            # Add preload for faster loading
            preload = soup.new_tag('link')
            preload['rel'] = 'preload'
            preload['as'] = 'style'
            preload['href'] = '/assets/css/brutalist-theme.css'
            soup.head.append(preload)

            # Add main stylesheet link
            # IMPORTANT: Load synchronously (not media="print" trick) because this
            # CSS contains the @font-face declarations inline — the browser needs
            # to parse it to discover the font URLs and start downloading them.
            link = soup.new_tag('link', rel='stylesheet', href='/assets/css/brutalist-theme.css')
            link['media'] = 'all'
            soup.head.append(link)

            print("   🎨 Added brutalist theme CSS with non-blocking load")
        except Exception as e:
            print(f"   ❌ Failed to add brutalist theme CSS: {str(e)}")

    def add_plausible_analytics(self, soup):
        """Add Plausible Analytics script to the page if not already present.

        The script is served from a same-origin path (/js/script.js) via the
        Cloudflare Worker, which proxies to the Plausible CE instance. No
        DNS prefetch / preconnect needed — the request is to our own host."""
        if not soup.head:
            return

        # Import config for Plausible settings
        from config import Config

        plausible_script_url = Config.get_plausible_script_url()
        target_analytics_domain = Config.get_plausible_domain()

        # Drop any historical dns-prefetch / preconnect hints to the upstream
        # Plausible host — same-origin now, so they're noise that delays the
        # actual critical preconnects.
        legacy_plausible_host = Config.PLAUSIBLE_URL
        for hint in soup.find_all('link', rel=lambda r: r in ('dns-prefetch', 'preconnect')):
            href = hint.get('href') or ''
            if legacy_plausible_host in href:
                hint.decompose()

        # Look for existing Plausible script — historical pages may have the
        # absolute upstream URL; this also catches any third-party plugin
        # injection that snuck through.
        existing_plausible = soup.find('script', src=lambda x: x and 'script.js' in x and ('plausible' in x or x == plausible_script_url))

        if existing_plausible:
            # Update the data-domain attribute to ensure it's correct
            existing_plausible['data-domain'] = target_analytics_domain
            existing_plausible['defer'] = ''  # Use defer for better preconnect timing
            existing_plausible['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader
            # Remove async if it exists
            if existing_plausible.get('async'):
                del existing_plausible['async']
            print("   📊 Updated existing Plausible analytics configuration")
        else:
            # Add new Plausible script
            plausible_script = soup.new_tag('script')
            plausible_script['data-domain'] = target_analytics_domain
            plausible_script['defer'] = ''  # Use defer for better preconnect timing
            plausible_script['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader
            plausible_script['src'] = plausible_script_url
            soup.head.append(plausible_script)
            print("   📊 Added Plausible analytics script to page")
