#!/usr/bin/env python3
"""
Generate per-post Open Graph (og:image) images for posts using the fallback.

About 60% of the site (107 pages) used to ship the same generic ChatGPT-
generated image as og:image. Every social share looked identical and told a
reader nothing about which post was linked. This script replaces those
fallback uses with a 1200×630 PNG composed from the post's own title.

Workflow:
    1. Scan {site_dir}/**/*.html for <meta property="og:image">.
    2. For pages whose og:image points at the fallback URL pattern,
       generate a branded PNG with the post title.
    3. Write the PNG to {site_dir}/wp-content/uploads/og/<slug>.png and
       rewrite the og:image / og:image:secure_url / og:image:width /
       og:image:height / twitter:image meta tags in the HTML.
    4. Cache by (title + slug) hash so unchanged posts skip regeneration.

Dependencies:  Pillow, fontTools (woff2 reader needs brotli — already in
requirements.txt). The script bails out gracefully with a warning if any
import is missing — that way the deploy pipeline doesn't fail on machines
without the optional libraries.

Usage:
    python3 scripts/generate_og_images.py [site_dir]
"""

import json
import re
import sys
import tempfile
from hashlib import blake2b
from pathlib import Path

from config import Config

# Domain shown on the card and used in the rewritten og:image URL —
# never hardcode jameskilby.co.uk here, Config is the source of truth.
TARGET_DOMAIN = Config.TARGET_DOMAIN
DOMAIN_NAME = TARGET_DOMAIN.replace('https://', '').replace('http://', '')

# Import dependencies with a graceful fallback. The deploy pipeline shouldn't
# fail just because the runner is missing image tooling — we'd rather skip
# og:image generation and keep deploying than crash the build.
try:
    from PIL import Image, ImageDraw, ImageFont
    from fontTools.ttLib import TTFont
    _DEPS_OK = True
    _DEPS_ERROR = None
except ImportError as e:
    _DEPS_OK = False
    _DEPS_ERROR = str(e)

# Sites where this script is a no-op. The default fallback URL pattern is
# baked in — extend the tuple if WordPress starts assigning a new generic
# fallback or the editor swaps which image gets used.
FALLBACK_URL_PATTERNS = (
    'ChatGPT-Image',  # The 2025-12 fallback that 60% of posts ship
)

# Output canvas matches the OG 1.91:1 ratio. Open Graph crawlers downscale
# anything larger; below 1200×630 you start losing detail on big retina
# previews.
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 630

# Visual palette — sourced from brutalist-theme.css so generated cards
# feel consistent with the site chrome.
COLOR_BG = '#0a0a0a'
COLOR_FG = '#f5f5f5'
COLOR_ACCENT = '#ff6a00'
COLOR_MUTED = '#7a766c'

# Path conventions inside the static site.
ANTON_WOFF2_REL = 'assets/fonts/anton-v27-latin-400.woff2'
OG_OUTPUT_REL = 'wp-content/uploads/og'
CACHE_REL = '.og-image-cache.json'


class OGImageGenerator:
    """Generate branded og:images for posts using the fallback URL."""

    def __init__(self, site_dir):
        self.site_dir = Path(site_dir)
        self.cache_path = self.site_dir / CACHE_REL
        self.output_dir = self.site_dir / OG_OUTPUT_REL
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()
        self._ttf_path = None  # lazily converted on first render
        # Stats
        self.generated = 0
        self.cached = 0
        self.skipped_no_fallback = 0
        self.skipped_no_title = 0

    def _load_cache(self):
        if not self.cache_path.exists():
            return {}
        try:
            return json.loads(self.cache_path.read_text())
        except Exception:
            return {}

    def _save_cache(self):
        try:
            self.cache_path.write_text(json.dumps(self.cache, indent=2))
        except Exception as e:
            print(f"   ⚠️  Could not write og-image cache: {e}")

    # ── Font handling ─────────────────────────────────────────────────────

    def _ensure_ttf(self):
        """Convert Anton woff2 → ttf once, cached for the run.

        PIL's ImageFont.truetype can't load woff2 directly. fontTools strips
        the woff2 wrapper and emits a regular TrueType file we can render
        with. The output is per-process temp; no need to ship a TTF in repo.
        """
        if self._ttf_path:
            return self._ttf_path
        woff2 = self.site_dir / ANTON_WOFF2_REL
        if not woff2.exists():
            raise FileNotFoundError(
                f"Anton font not found at {woff2} — required to render og:images"
            )
        tmp = tempfile.NamedTemporaryFile(
            suffix='.ttf', prefix='anton-', delete=False
        )
        tmp.close()
        font = TTFont(str(woff2))
        font.flavor = None
        font.save(tmp.name)
        self._ttf_path = tmp.name
        return self._ttf_path

    # ── HTML scanning + meta extraction ───────────────────────────────────

    OG_IMAGE_TAG_RE = re.compile(
        r'<meta\s+[^>]*property=["\']og:image["\'][^>]*>',
        re.IGNORECASE,
    )
    OG_TITLE_RE = re.compile(
        r'<meta\s+[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    TITLE_TAG_RE = re.compile(r'<title>([^<]+)</title>', re.IGNORECASE)
    CONTENT_ATTR_RE = re.compile(r'content=["\']([^"\']+)["\']', re.IGNORECASE)

    def _extract_og_image_url(self, html):
        tag = self.OG_IMAGE_TAG_RE.search(html)
        if not tag:
            return None
        m = self.CONTENT_ATTR_RE.search(tag.group(0))
        return m.group(1) if m else None

    def _is_fallback(self, url):
        return any(p in url for p in FALLBACK_URL_PATTERNS)

    def _extract_title(self, html):
        """Prefer og:title (already brand-trimmed by SEO fixer), fall back
        to the document title with the trailing "- James Kilby" stripped."""
        m = self.OG_TITLE_RE.search(html)
        if m:
            return self._normalise_title(m.group(1))
        m = self.TITLE_TAG_RE.search(html)
        if m:
            t = m.group(1).strip()
            t = re.sub(r'\s*[-–|]\s*James Kilby.*$', '', t, flags=re.IGNORECASE)
            return self._normalise_title(t)
        return None

    @staticmethod
    def _normalise_title(t):
        # Decode common HTML entities cheaply (no html.unescape import in
        # this file; we only see a handful of entities in titles).
        return (t.replace('&#038;', '&')
                 .replace('&amp;', '&')
                 .replace('&#8217;', "'")
                 .replace('&#8220;', '"')
                 .replace('&#8221;', '"')
                 .strip())

    # ── Rendering ─────────────────────────────────────────────────────────

    def _wrap_title(self, draw, text, font, max_width):
        """Greedy word-wrap that respects the font's measured width.

        Anton is a tall, condensed display face — we can fit a lot of caps
        per line, but with a Vercel-style template we typically want 2-3
        lines of large text. Cap at 4 lines and ellipsise the rest.
        """
        words = text.upper().split()
        lines = []
        current = ""
        for w in words:
            attempt = (current + " " + w).strip()
            if draw.textlength(attempt, font=font) <= max_width:
                current = attempt
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)

        if len(lines) > 4:
            lines = lines[:4]
            # Ellipsise the last line. Drop words until it fits with "…"
            while lines[-1] and draw.textlength(lines[-1] + "…", font=font) > max_width:
                parts = lines[-1].rsplit(' ', 1)
                if len(parts) == 1:
                    break
                lines[-1] = parts[0]
            lines[-1] = lines[-1].rstrip() + "…"
        return lines

    def _pick_title_font_size(self, draw, ttf_path, lines, max_width, max_height):
        """Pick the largest font size at which the wrapped title fits.

        Re-wraps at each candidate size — fewer big lines may fit where many
        small lines wouldn't.
        """
        for size in (84, 76, 68, 60, 52, 46, 40):
            font = ImageFont.truetype(ttf_path, size=size)
            wrapped = self._wrap_title_for_size(draw, lines, font, max_width)
            line_height = int(size * 1.1)
            total_h = line_height * len(wrapped)
            if total_h <= max_height and len(wrapped) <= 4:
                return font, wrapped, size, line_height
        # Smallest as last resort
        font = ImageFont.truetype(ttf_path, size=36)
        wrapped = self._wrap_title_for_size(draw, lines, font, max_width)
        return font, wrapped, 36, int(36 * 1.1)

    def _wrap_title_for_size(self, draw, raw, font, max_width):
        """Wrap `raw` (already a string) for a specific font instance."""
        if isinstance(raw, list):
            raw = " ".join(raw)
        return self._wrap_title(draw, raw, font, max_width)

    def _render_og_image(self, title, output_path):
        ttf_path = self._ensure_ttf()
        img = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        draw = ImageDraw.Draw(img)

        # Top accent bar — matches the orange highlight in the brutalist theme.
        draw.rectangle([(0, 0), (CANVAS_WIDTH, 8)], fill=COLOR_ACCENT)

        # Title block — fit-to-canvas with greedy word-wrap.
        padding_x = 80
        padding_top = 110
        padding_bottom = 130  # reserve room for the brand strip
        max_text_w = CANVAS_WIDTH - 2 * padding_x
        max_text_h = CANVAS_HEIGHT - padding_top - padding_bottom

        font, lines, size, line_h = self._pick_title_font_size(
            draw, ttf_path, title, max_text_w, max_text_h
        )
        # Vertical centre within the title block.
        title_block_h = line_h * len(lines)
        y = padding_top + (max_text_h - title_block_h) // 2
        for line in lines:
            draw.text((padding_x, y), line, font=font, fill=COLOR_FG)
            y += line_h

        # Brand strip at the bottom.
        brand_font = ImageFont.truetype(ttf_path, size=28)
        domain_font = ImageFont.truetype(ttf_path, size=22)
        bottom_y = CANVAS_HEIGHT - 60
        draw.text((padding_x, bottom_y - 8), "JAMES KILBY", font=brand_font, fill=COLOR_ACCENT)
        # Right-aligned domain
        domain = DOMAIN_NAME
        domain_w = draw.textlength(domain, font=domain_font)
        draw.text(
            (CANVAS_WIDTH - padding_x - domain_w, bottom_y),
            domain,
            font=domain_font,
            fill=COLOR_MUTED,
        )

        img.save(output_path, format='PNG', optimize=True)

    # ── HTML rewriting ───────────────────────────────────────────────────

    @staticmethod
    def _rewrite_meta(html, new_url):
        """Update every meta tag that should point at the post-specific
        image: og:image, og:image:secure_url, og:image:url, twitter:image.
        Also corrects width/height to our canvas dimensions.
        """
        def replace_content(tag_html, value):
            return re.sub(
                r'content=["\'][^"\']*["\']',
                f'content="{value}"',
                tag_html,
                count=1,
                flags=re.IGNORECASE,
            )

        targets = (
            ('og:image', new_url, 'property'),
            ('og:image:secure_url', new_url, 'property'),
            ('og:image:url', new_url, 'property'),
            ('twitter:image', new_url, 'name'),
            ('og:image:width', str(CANVAS_WIDTH), 'property'),
            ('og:image:height', str(CANVAS_HEIGHT), 'property'),
        )
        for prop, value, attr in targets:
            pattern = re.compile(
                rf'<meta\s+[^>]*{attr}=["\']{re.escape(prop)}["\'][^>]*>',
                re.IGNORECASE,
            )
            def _sub(m):
                tag = m.group(0)
                return replace_content(tag, value)
            html = pattern.sub(_sub, html)
        return html

    # ── Main loop ────────────────────────────────────────────────────────

    def process_all(self):
        if not _DEPS_OK:
            print(f"⚠️  og:image generator skipped — {_DEPS_ERROR}")
            print("   Install dependencies with: pip install Pillow 'fonttools[woff]'")
            return

        html_files = sorted(self.site_dir.rglob('*.html'))
        print(f"🖼️  Scanning {len(html_files)} HTML files for fallback og:images...")

        for html_file in html_files:
            try:
                self._process_one(html_file)
            except Exception as e:
                print(f"   ⚠️  {html_file.relative_to(self.site_dir)}: {e}")

        self._save_cache()
        print("\n✅ og:image generation complete")
        print(f"   Generated: {self.generated}")
        print(f"   Cached:    {self.cached}")
        print(f"   Skipped (no fallback): {self.skipped_no_fallback}")
        print(f"   Skipped (no title):    {self.skipped_no_title}")

    def _process_one(self, html_file):
        html = html_file.read_text(encoding='utf-8', errors='ignore')
        og_url = self._extract_og_image_url(html)
        if not og_url or not self._is_fallback(og_url):
            self.skipped_no_fallback += 1
            return

        title = self._extract_title(html)
        if not title:
            self.skipped_no_title += 1
            return

        # Cache key — slug + title hash. Slug comes from the URL path so
        # different posts with identical titles get different cards.
        slug = self._slug_for(html_file)
        cache_key = slug
        title_hash = blake2b(title.encode('utf-8'), digest_size=8).hexdigest()
        output_filename = f"{slug}.png"
        output_path = self.output_dir / output_filename
        new_url = f"{TARGET_DOMAIN}/{OG_OUTPUT_REL}/{output_filename}"

        prior = self.cache.get(cache_key, {})
        if (prior.get('title_hash') == title_hash
                and output_path.exists()):
            self.cached += 1
        else:
            self._render_og_image(title, output_path)
            self.cache[cache_key] = {
                'title_hash': title_hash,
                'title': title[:120],
            }
            self.generated += 1

        # Rewrite HTML to point at the new image.
        new_html = self._rewrite_meta(html, new_url)
        if new_html != html:
            html_file.write_text(new_html, encoding='utf-8')

    def _slug_for(self, html_file):
        """Stable filename for the generated image.

        For posts under YYYY/MM/<slug>/index.html, use <slug>. For other
        pages (homepage, pagination), use the relative directory path
        slugified. Keeps generated PNGs at /wp-content/uploads/og/<slug>.png.
        """
        rel = html_file.relative_to(self.site_dir).as_posix()
        # /YYYY/MM/<slug>/index.html
        m = re.match(r'\d{4}/\d{2}/([^/]+)/index\.html$', rel)
        if m:
            return m.group(1)
        # otherwise sanitise full path
        slug = rel.replace('/index.html', '').replace('/', '-')
        slug = re.sub(r'[^a-zA-Z0-9._-]', '-', slug)
        return slug or 'home'


def main():
    site_dir = sys.argv[1] if len(sys.argv) > 1 else 'public'
    gen = OGImageGenerator(site_dir)
    gen.process_all()
    sys.exit(0)


if __name__ == '__main__':
    main()
