#!/usr/bin/env python3
"""
HTML Performance Enhancement Script
Post-processes generated HTML files to add performance optimizations
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

try:
    from config import Config
    _SITE_ORIGIN = Config.TARGET_DOMAIN.rstrip('/')
except ImportError:
    _SITE_ORIGIN = 'https://jameskilby.co.uk'


def normalize_self_href(href):
    """Map absolute same-site URLs to their relative form.

    Different pipeline stages leave hrefs in different forms — e.g.
    restore_seeded_urls keeps `/wp-content/...` link hrefs relative but
    absolutifies srcset/imagesrcset. Comparing hrefs without normalising
    made duplicate detection miss existing tags (two identical LCP
    preloads shipped on every page).
    """
    if href and href.startswith(_SITE_ORIGIN + '/'):
        return href[len(_SITE_ORIGIN):]
    return href


class HTMLPerformanceEnhancer:
    """Enhance HTML files with performance optimizations"""

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_processed = 0
        self.optimizations_applied = 0

    def process_all_files(self):
        """Process all HTML files in the public directory"""
        html_files = list(self.public_dir.rglob('*.html'))

        print(f"🚀 Processing {len(html_files)} HTML files for performance enhancements...")

        for html_file in html_files:
            if self.process_file(html_file):
                self.files_processed += 1

        print(f"\n✅ Enhanced {self.files_processed} files")
        print(f"   Applied {self.optimizations_applied} optimizations")

    def process_file(self, file_path):
        """Process a single HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            modified = False

            # Apply optimizations
            if self.add_async_defer_to_scripts(soup):
                modified = True

            if self.add_media_attributes_to_css(soup):
                modified = True

            if self.strip_http_equiv_meta(soup):
                modified = True

            if self.optimize_external_scripts(soup):
                modified = True

            if self.add_resource_hints(soup):
                modified = True

            if self.optimize_fonts(soup):
                modified = True

            if self.add_preload_hints(soup):
                modified = True

            if self.optimize_images(soup):
                modified = True

            # Save if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                return True

            return False

        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
            return False

    def add_async_defer_to_scripts(self, soup):
        """Add async or defer attributes to external scripts"""
        modified = False

        for script in soup.find_all('script', src=True):
            # Skip scripts that already have async or defer
            if script.get('async') is not None or script.get('defer') is not None:
                continue

            src = script.get('src', '')

            # Analytics scripts should be async
            if any(keyword in src for keyword in ['plausible', 'analytics', 'gtag', 'ga.js']):
                script['async'] = ''
                modified = True
                self.optimizations_applied += 1

            # Other external scripts should use defer (maintains execution order)
            elif src.startswith('http') or src.startswith('//'):
                script['defer'] = ''
                modified = True
                self.optimizations_applied += 1

            # Internal scripts can use defer too (unless they're critical)
            elif not any(keyword in src for keyword in ['critical', 'inline']):
                script['defer'] = ''
                modified = True
                self.optimizations_applied += 1

        return modified

    def add_media_attributes_to_css(self, soup):
        """Add media attributes to non-critical CSS"""
        modified = False

        for link in soup.find_all('link', rel='stylesheet'):
            # Skip if already has media attribute
            if link.get('media'):
                continue

            href = link.get('href', '')

            # Skip critical CSS
            if 'critical' in href or 'inline' in href:
                continue

            # Print/PDF specific styles
            if 'print' in href:
                link['media'] = 'print'
                modified = True
                self.optimizations_applied += 1

            # Mobile-specific styles
            elif 'mobile' in href:
                link['media'] = 'screen and (max-width: 768px)'
                modified = True
                self.optimizations_applied += 1

            # Default to 'all' to make it explicit (helps with preload)
            else:
                link['media'] = 'all'
                modified = True
                self.optimizations_applied += 1

        return modified

    def optimize_external_scripts(self, soup):
        """Manage <link rel="dns-prefetch"> hints.

        Three passes:
          1. Collect the set of external hosts actually referenced by any
             script/link/img on the page.
          2. Walk every existing dns-prefetch tag: drop duplicates (by
             normalized host) and drop hints whose host is no longer
             referenced (e.g. cdn.jsdelivr.net after we vendored fuse/splide).
          3. Add a dns-prefetch hint for any referenced external host that
             doesn't already have one.
        """
        modified = False

        if not soup.head:
            return False

        # Skip same-origin hosts — a dns-prefetch hint to the document's own
        # host is a no-op and just adds bytes. Pull the canonical host from
        # Config so we don't need to hardcode it here.
        try:
            from config import Config
            same_origin_hosts = {Config.TARGET_DOMAIN.split('//', 1)[-1].rstrip('/')}
        except Exception:
            same_origin_hosts = set()

        def _host(href):
            """Extract the bare host from `//x`, `https://x/...`, or `x`."""
            if not href:
                return ''
            h = href.strip()
            if h.startswith('//'):
                h = h[2:]
            elif '://' in h:
                h = h.split('://', 1)[1]
            return h.split('/', 1)[0].lower()

        # 1. External hosts the page actually uses. Resource hints
        #    (dns-prefetch, preconnect, prefetch, preload to a remote host)
        #    are hints, not real references — exclude them or stale hints
        #    self-reference their own host and never get pruned.
        hint_rels = {'dns-prefetch', 'preconnect', 'prefetch', 'preload'}
        referenced_hosts = set()
        for tag in soup.find_all(['script', 'link', 'img']):
            if tag.name == 'link':
                rels = tag.get('rel') or []
                if isinstance(rels, str):
                    rels = [rels]
                if any(r.lower() in hint_rels for r in rels):
                    continue
            src = tag.get('src') or tag.get('href', '')
            if not src or not (src.startswith('http') or src.startswith('//')):
                continue
            host = _host(src)
            if host and host not in same_origin_hosts:
                referenced_hosts.add(host)

        # 2. Prune existing dns-prefetch tags: dedupe and drop stale hosts.
        seen_hosts = set()
        for link in soup.find_all('link', rel='dns-prefetch'):
            host = _host(link.get('href', ''))
            if not host or host not in referenced_hosts or host in seen_hosts:
                link.decompose()
                modified = True
                self.optimizations_applied += 1
                continue
            seen_hosts.add(host)

        # 3. Add dns-prefetch for any referenced host without one.
        #
        # sorted(): a bare set difference iterates in hash order, which varies
        # between processes. Each new tag is inserted at head[0], so the walk
        # order becomes the document order — the same page emitted its hints
        # in a different sequence run to run and landed in the deploy diff.
        #
        # href before rel to match how the parser preserves attribute order on
        # tags that already exist: otherwise a hint that gets pruned and
        # recreated flips from `href rel` to `rel href` and rewrites the page
        # again for no semantic change.
        for host in sorted(referenced_hosts - seen_hosts):
            dns_prefetch = soup.new_tag('link')
            dns_prefetch['href'] = f'//{host}'
            dns_prefetch['rel'] = 'dns-prefetch'
            soup.head.insert(0, dns_prefetch)
            modified = True
            self.optimizations_applied += 1

        return modified

    def strip_http_equiv_meta(self, soup):
        """Remove <meta http-equiv> tags for headers that must come from HTTP.

        The HTML payload carries `<meta http-equiv="Cache-Control" ...>` etc.
        from upstream WordPress; the real HTTP response from Cloudflare Pages
        already sets these (often to different values). Some intermediaries
        and audit tools honour the meta tag, producing confusing divergence.
        Strip them so the HTTP headers are the only source of truth.
        """
        if not soup.head:
            return False

        stripped = {'cache-control', 'pragma', 'expires'}
        modified = False
        for meta in soup.find_all('meta', attrs={'http-equiv': True}):
            if meta.get('http-equiv', '').lower() in stripped:
                meta.decompose()
                modified = True
                self.optimizations_applied += 1

        return modified

    def add_resource_hints(self, soup):
        """Add preconnect hints for critical external domains"""
        if not soup.head:
            return False

        modified = False

        # Critical domains that should use preconnect (stronger than dns-prefetch).
        # Plausible used to live here; it's now served same-origin via the
        # Cloudflare Worker proxy, so no third-party preconnect is required.
        critical_domains = set()

        for domain in critical_domains:
            # Check if this domain is actually used in the page
            domain_used = False
            for tag in soup.find_all(['script', 'link', 'img']):
                src = tag.get('src') or tag.get('href', '')
                if domain in src:
                    domain_used = True
                    break

            if not domain_used:
                continue

            # Check if preconnect already exists
            existing = soup.find('link', rel='preconnect', href=domain)
            if not existing:
                preconnect = soup.new_tag('link')
                preconnect['rel'] = 'preconnect'
                preconnect['href'] = domain

                soup.head.insert(0, preconnect)
                modified = True
                self.optimizations_applied += 1

        return modified

    # Explicit allowlist of WOFF2 basenames that get a high-priority preload
    # hint. Every other @font-face URL relies on `font-display: optional`
    # silently falling back to the system stack if it misses the ~100 ms
    # window — no CLS, no preload pressure on the LCP image.
    #
    # Why explicit instead of "all optional fonts"? brutalist-theme.css uses
    # `font-display: optional` on ALL six weights to keep CLS at zero (June
    # 2026 PSI showed JetBrains Mono + Space Grotesk 500/700 swaps causing a
    # 0.27 shift on <main>). Preloading all six would burn ~570 KB of high-
    # priority bandwidth on first visit and push the LCP image down the
    # queue. Only the body font and the heading font are needed above the
    # fold; the others can wait for the disk cache on repeat visits.
    PRELOAD_FONT_BASENAMES = frozenset({
        'spacegrotesk-v22-latin-400.woff2',  # body
        'anton-v27-latin-400.woff2',         # h1–h6
    })

    def optimize_fonts(self, soup):
        """Preload the small allowlist of WOFF2 fonts that render above the fold.

        See PRELOAD_FONT_BASENAMES for the policy. Only fonts whose
        @font-face block declares `font-display: optional` AND whose URL
        basename is in the allowlist get a preload hint.

        Idempotent: any existing `<link rel="preload" as="font">` tag is
        stripped first, so re-running this function (e.g. before AND
        after stylesheet inlining) converges on the correct preload set.
        """
        if not soup.head:
            return False

        modified = False

        # Strip any pre-existing font preloads — they may have been
        # injected by a previous pipeline run that saw stale @font-face
        # values. We re-derive from the current soup state below.
        for stale in list(soup.find_all('link', rel='preload', attrs={'as': 'font'})):
            stale.decompose()
            modified = True
            self.optimizations_applied += 1

        # Match each @font-face { ... } block and capture its body so we
        # can inspect font-display and the src url() together.
        font_face_re = re.compile(r'@font-face\s*\{([^}]*)\}', re.IGNORECASE)
        url_re = re.compile(r'url\(["\']?([^"\')]+\.woff2)["\']?\)', re.IGNORECASE)
        display_re = re.compile(r'font-display\s*:\s*([a-z]+)', re.IGNORECASE)

        for style in soup.find_all('style'):
            if not style.string or '@font-face' not in style.string:
                continue

            for block in font_face_re.finditer(style.string):
                body = block.group(1)
                display_match = display_re.search(body)
                if not display_match or display_match.group(1).lower() != 'optional':
                    continue

                for url_match in url_re.finditer(body):
                    font_url = url_match.group(1).strip()
                    if font_url.rsplit('/', 1)[-1] not in self.PRELOAD_FONT_BASENAMES:
                        continue

                    existing = soup.find('link', rel='preload', href=font_url)
                    if existing:
                        continue

                    preload = soup.new_tag('link')
                    preload['rel'] = 'preload'
                    preload['href'] = font_url
                    preload['as'] = 'font'
                    preload['type'] = 'font/woff2'
                    preload['crossorigin'] = ''
                    soup.head.insert(0, preload)
                    modified = True
                    self.optimizations_applied += 1

        return modified

    def add_preload_hints(self, soup):
        """Add preload hints for critical resources"""
        if not soup.head:
            return False

        modified = False

        # Find hero/first image in main content for preloading
        main_content = soup.find(['main', 'article', 'div'])
        if main_content:
            first_img = main_content.find('img')
            if first_img and first_img.get('src'):
                width = first_img.get('width', '')
                try:
                    if width and int(width) > 200:
                        # If the <img> sits inside a <picture> the browser will
                        # pick the first matching <source> (AVIF > WebP > fallback).
                        # Preloading the <img> src then double-downloads. Pick the
                        # source the browser will actually use.
                        preload_href, preload_type, preload_srcset, preload_sizes = (
                            self._pick_lcp_preload(first_img)
                        )

                        # Compare normalised hrefs — preload_href derives from
                        # the (absolutified) srcset while an existing preload's
                        # href may be relative; an exact-string find misses it.
                        target = normalize_self_href(preload_href)
                        existing = next(
                            (lnk for lnk in soup.find_all('link', rel='preload')
                             if normalize_self_href(lnk.get('href', '')) == target),
                            None
                        )
                        if not existing:
                            preload = soup.new_tag('link')
                            preload['rel'] = 'preload'
                            preload['href'] = preload_href
                            preload['as'] = 'image'
                            preload['fetchpriority'] = 'high'
                            if preload_type:
                                preload['type'] = preload_type
                            if preload_srcset:
                                preload['imagesrcset'] = preload_srcset
                                if preload_sizes:
                                    preload['imagesizes'] = preload_sizes
                            soup.head.insert(0, preload)
                            modified = True
                            self.optimizations_applied += 1
                except (ValueError, AttributeError):
                    pass

        # Preload the primary stylesheet — but only if its *filename* exactly
        # matches a known critical/main pattern.  The previous check used
        # `'style' in href` which matched every stylesheet (e.g. bootstrap.css,
        # theme-styles.css), preloading the entire stylesheet list.
        # H: restrict to exact stems: critical, main, styles (with optional .min)
        _CSS_NAME_RE = re.compile(
            r'(?:^|/)(?:critical|main|styles)(?:\.min)?\.css(?:[?#]|$)',
            re.IGNORECASE
        )
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if not href or 'print' in href:
                continue
            if not _CSS_NAME_RE.search(href):
                continue
            existing = soup.find('link', rel='preload', href=href)
            if not existing:
                preload = soup.new_tag('link')
                preload['rel'] = 'preload'
                preload['href'] = href
                preload['as'] = 'style'
                soup.head.insert(0, preload)
                modified = True
                self.optimizations_applied += 1
                break  # Only preload one critical CSS file

        return modified

    def optimize_images(self, soup):
        """Normalise image loading hints around a single LCP candidate.

        Exactly one image — the first inside <main>/<article> — gets
        fetchpriority="high" and no lazy hint. Every other image is
        force-set to loading="lazy" and any inherited fetchpriority="high"
        is stripped. WordPress emits loading="eager" on every post
        thumbnail in archive listings; without this, multiple eager
        images compete with the real LCP and burn its priority slot.
        """
        if not soup.body:
            return False

        modified = False

        # Identify the first content image (LCP candidate).
        content_root = soup.find(['main', 'article'])
        lcp_img = content_root.find('img') if content_root else None

        for img in soup.find_all('img'):
            if img is lcp_img:
                # Likely LCP element — fetch early, never lazy.
                if img.get('fetchpriority') != 'high':
                    img['fetchpriority'] = 'high'
                    modified = True
                    self.optimizations_applied += 1
                if img.get('loading') == 'lazy':
                    del img['loading']
                    modified = True
                    self.optimizations_applied += 1
            else:
                # Everything else: force lazy and drop any stray high priority.
                if img.get('loading') != 'lazy':
                    img['loading'] = 'lazy'
                    modified = True
                    self.optimizations_applied += 1
                if img.get('fetchpriority') == 'high':
                    del img['fetchpriority']
                    modified = True
                    self.optimizations_applied += 1

            # Async decoding for all images — prevents blocking the main thread.
            if not img.get('decoding'):
                img['decoding'] = 'async'
                modified = True
                self.optimizations_applied += 1

        return modified

    def _get_image_type(self, src):
        """Get MIME type from image extension"""
        if src.endswith('.avif'):
            return 'image/avif'
        elif src.endswith('.webp'):
            return 'image/webp'
        elif src.endswith(('.jpg', '.jpeg')):
            return 'image/jpeg'
        elif src.endswith('.png'):
            return 'image/png'
        elif src.endswith('.svg'):
            return 'image/svg+xml'
        return None

    def _pick_lcp_preload(self, img):
        """Return (href, type, srcset, sizes) the browser will actually paint.

        If the img is wrapped in <picture>, prefer the first AVIF <source>,
        then WebP, then fall back to the img itself. Returns srcset/sizes
        when the chosen source declares them so the preload matches the
        responsive pick the picture element will make.
        """
        picture = img.find_parent('picture')
        if picture:
            for source in picture.find_all('source'):
                mime = (source.get('type') or '').lower()
                if mime not in ('image/avif', 'image/webp'):
                    continue
                srcset = source.get('srcset', '').strip()
                if not srcset:
                    continue
                first_url = srcset.split(',')[0].strip().split()[0]
                sizes = source.get('sizes') or img.get('sizes')
                return first_url, mime, srcset, sizes
        src = img.get('src', '')
        return src, self._get_image_type(src), img.get('srcset'), img.get('sizes')


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        public_dir = sys.argv[1]
    else:
        public_dir = 'public'

    enhancer = HTMLPerformanceEnhancer(public_dir)
    enhancer.process_all_files()

    sys.exit(0)


if __name__ == '__main__':
    main()
