#!/usr/bin/env python3
"""
Site artifacts builder — post-build output-file generation.

Extracted from WordPressStaticGenerator (wp_to_static_generator.py), which
had grown into a single 5,600+ line class. This module holds every step that
runs AFTER the per-page HTML pipeline finishes: it only reads already-written
HTML files back off disk and writes standalone site-level artifacts
(sitemap.xml, feed/index.xml, robots.txt, _headers, _redirects,
search-index.json, the search script/power-widget injection passes). None of
it touches WordPress, a requests.Session, or any per-page soup — the only
inputs are `output_dir` and `target_domain`, which is what made this the
first, cleanest cut out of the god object (see the code review that flagged
it — "finding 1").

WordPressStaticGenerator.generate_static_site() drives these in a fixed
order via a SiteArtifactsBuilder instance (self.artifacts); see that method
for the sequence. Behaviour here is unchanged from the pre-extraction
version — this is a pure move, not a rewrite.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup


def image_url_to_output_path(loc, target_domain, output_dir):
    """Resolve a same-domain image URL back to its on-disk path in output_dir.

    Returns a Path inside output_dir, or None when the URL is not under
    target_domain (external / CDN images have no local file to verify).
    Query strings and fragments are stripped and percent-encoding is decoded
    before the path is built.
    """
    output_dir = Path(output_dir)
    target_domain = (target_domain or '').rstrip('/')
    clean = loc.split('#', 1)[0].split('?', 1)[0]
    if target_domain and clean.startswith(target_domain):
        rel = clean[len(target_domain):]
    elif clean.startswith('/'):
        rel = clean
    else:
        return None
    rel = unquote(rel).lstrip('/')
    if not rel:
        return None
    return output_dir / rel


def image_file_present(loc, target_domain, output_dir):
    """True only when an image URL maps to a real, non-empty file on disk.

    Keeps sitemap <image:loc> entries honest: WordPress sometimes references
    thumbnail variants that were never generated, and those 404 when Google
    fetches the image sitemap. Defensive — zero-byte files are treated as
    absent too.
    """
    path = image_url_to_output_path(loc, target_domain, output_dir)
    if path is None:
        return False
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False

# Pre-compiled url-path regexes for sitemap noindex policy. Single source of
# truth is Config.NOINDEX_PATH_PATTERNS. Compiled once at import.
# scripts/fix_seo_issues.py reads the same list to inject the meta tag.
try:
    from config import Config as _NIPathConfig
    _NOINDEX_URL_PATH_PATTERNS = tuple(
        re.compile(p) for p in _NIPathConfig.NOINDEX_PATH_PATTERNS
    )
    del _NIPathConfig
except (ImportError, AttributeError):
    _NOINDEX_URL_PATH_PATTERNS = ()

# Matches an already-injected homelab power widget: its root element through the
# end of its IIFE <script>. The optional `-block` covers pre-explainer builds
# whose root was the card itself, so a stale widget from any prior version is
# still found and replaced. DOTALL: the span covers markup + CSS + JS.
#
# The leading optional comment matters: the partial opens with its maintainer
# comment, so the span has to swallow an adjacent one or replacing a stale
# widget would leave the old comment behind and duplicate it. (Only reachable in
# unminified output — minify_html strips comments in a real build.)
_POWER_WIDGET_SPAN_RE = re.compile(
    r'(?:<!--(?:(?!-->).)*?-->\s*)?'
    r'<div\b[^>]*\bid="homelab-power(?:-block)?"[^>]*>.*?\}\)\(\);\s*</script>',
    re.IGNORECASE | re.DOTALL,
)
_POWER_WIDGET_VERSION_RE = re.compile(r'data-power-widget-version="([^"]+)"')
_POWER_WIDGET_ROOT_RE = re.compile(r'(<div\b[^>]*\bid="homelab-power-block")')


class SiteArtifactsBuilder:
    """Post-build site artifact generation: sitemap, RSS, robots.txt,
    _headers/_redirects, search index, and the search-script/power-widget
    injection passes. Stateless beyond output_dir/target_domain — every
    method reads already-written HTML back off disk."""

    def __init__(self, output_dir, target_domain):
        self.output_dir = output_dir
        self.target_domain = target_domain

    def create_security_headers(self):
        """Copy the canonical _headers file (repo root) to public/_headers.

        The repo-root `_headers` file is the single source of truth for
        Cloudflare Pages header rules — edit it directly. scripts/test_csp.py
        also reads it for CSP validation, and the pipeline copies it verbatim
        here so the deployed file stays in lockstep with what humans edit.
        """
        print("🔒 Copying _headers to output directory...")

        src = Path(__file__).resolve().parent.parent / '_headers'
        if not src.is_file():
            raise FileNotFoundError(
                f"Canonical _headers not found at {src}. Restore it before re-running."
            )

        dest = self.output_dir / '_headers'
        dest.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

        print(f"   ✅ Copied {src.name} → {dest}")
        print("   🔒 Security headers: X-Frame-Options, X-Content-Type-Options, CSP, HSTS, Permissions-Policy")

    def create_redirects_file(self):
        """Create redirects for old URLs (Netlify/Cloudflare format)"""
        redirects_content = [
            "# Redirect www to non-www (canonical URL)",
            "# Note: Cloudflare's 'Always Use HTTPS' runs first, so HTTP www gets 2 hops",
            "# This is normal and acceptable for the rare HTTP www case",
            "# (NB: www must also be added as a Custom Domain in the Cloudflare",
            "#  Pages dashboard for this rule to take effect — without that,",
            "#  www doesn't route to Pages and the apex zone returns 522.)",
            "www.jameskilby.co.uk/* https://jameskilby.co.uk/:splat 301!",
            "",
            "# Note: /feed/ → /feed/index.xml redirect lives in _worker.template.js,",
            "# not here. _redirects is IGNORED in Cloudflare Pages Advanced Worker",
            "# mode (when public/_worker.js exists). Same reason the www redirect",
            "# above is also duplicated inside the worker.",
            "",
            "# Automatic redirects for spelling corrections",
            "/2025/04/warp-the-inteligent-terminal/ /2025/04/warp-the-intelligent-terminal/ 301",
            "/category/artificial-inteligence/ /category/artificial-intelligence/ 301"
        ]

        redirects_file = self.output_dir / '_redirects'
        redirects_file.write_text('\n'.join(redirects_content))
        print("✅ Created _redirects file for URL corrections and www redirect")

    def create_robots_txt(self):
        """Generate a clean robots.txt for the static site"""
        print("🤖 Creating robots.txt...")
        robots_content = [
            "User-agent: *",
            "Allow: /",
            "",
            "# Stop crawlers from wasting crawl budget on per-archive feed URLs",
            "# (e.g. /category/foo/feed/) and the JSON API directory — neither",
            "# is indexable content. The root /feed/ is allowed because it 301s",
            "# to /feed/index.xml which is the canonical RSS feed.",
            "Disallow: /*/feed/",
            "Disallow: /api/",
            "",
            "# The 404 page carries <meta name=\"robots\" content=\"noindex,follow\">",
            "# and Cloudflare also sends X-Robots-Tag: noindex on it. We do NOT",
            "# Disallow noindex pages here — Google must be allowed to crawl them",
            "# in order to see the directive. Blocking crawl leaves the URLs in",
            "# the index as URL-only entries and prevents clean removal.",
            "",
            "# AI crawler policy",
            "# ────────────────────",
            "# GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended,",
            "# Bytespider and the rest of the LLM ingestion fleet are deliberately",
            "# NOT Disallowed. This site publishes a markdown mirror at /markdown/,",
            "# a JSON API mirror at /api/, an llmstxt.org index at /llms.txt and a",
            "# full-content corpus at /llms-full.txt — all built for AI ingestion.",
            "# Blocking the crawlers would defeat that on-purpose investment.",
            "# Steering happens via /llms.txt, not robots.txt.",
            "",
            f"Sitemap: {self.target_domain}/sitemap.xml",
            ""
        ]
        robots_file = self.output_dir / 'robots.txt'
        robots_file.write_text('\n'.join(robots_content))
        print("   ✅ Created robots.txt")

    def _extract_page_images(self, html_file):
        """Return a list of image dicts for the image sitemap.

        Each dict has:
          - loc:     absolute URL of the image (required by Google)
          - title:   image title attribute or filename stem (optional)
          - caption: alt text (optional but recommended)

        Only images served from the same domain are included; external CDN
        images (e.g. third-party embeds) are skipped.  AVIF/WebP <source>
        elements inside <picture> are ignored — only the <img> src (the
        canonical fallback) is used to avoid duplicate entries.
        """
        try:
            from bs4 import BeautifulSoup
            with open(html_file, 'r', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            # Only look at images inside the main article/post body
            content = soup.find('article') or soup.find('main') or soup.find('body')
            if not content:
                return []

            images = []
            seen_locs = set()

            for img in content.find_all('img'):
                src = img.get('src', '').strip()
                if not src:
                    continue

                # Convert to absolute URL
                if src.startswith('/'):
                    abs_src = f'{self.target_domain}{src}'
                elif src.startswith('http'):
                    # Skip external images
                    if self.target_domain not in src:
                        continue
                    abs_src = src
                else:
                    continue  # relative path without leading slash — skip

                # Only include images whose file actually exists in the output
                # dir. WordPress sometimes references thumbnail variants that
                # were never generated; emitting them as <image:loc> makes
                # Google fetch a 404 (a sitemap/crawl error). Defensive: also
                # drops zero-byte files.
                if not image_file_present(abs_src, self.target_domain, self.output_dir):
                    continue

                # Skip duplicates (e.g. responsive srcset variations already seen)
                loc_key = abs_src.split('?')[0]
                if loc_key in seen_locs:
                    continue
                seen_locs.add(loc_key)

                alt   = img.get('alt', '').strip()
                title = img.get('title', '').strip()

                # Derive a title from alt text, explicit title, or filename
                if not title and alt:
                    title = alt
                if not title:
                    from pathlib import Path as _Path
                    title = _Path(src).stem.replace('-', ' ').replace('_', ' ').title()

                images.append({
                    'loc':     abs_src,
                    'title':   title[:200],          # Google recommends ≤200 chars
                    'caption': alt[:200] if alt else '',
                })

            return images

        except Exception as e:
            print(f"   ⚠️  Image extraction failed for {html_file.name}: {e}")
            return []

    def create_sitemap(self):
        """Generate an XML sitemap with image extensions (Google Image Sitemap)."""
        urls_for_sitemap = []

        # Collect all HTML files with their modification dates
        for html_file in self.output_dir.rglob('*.html'):
            relative_path = html_file.relative_to(self.output_dir)
            if relative_path.name == 'index.html':
                if relative_path.parent == Path('.'):
                    url_path = '/'
                else:
                    url_path = f'/{relative_path.parent}/'
            else:
                url_path = f'/{relative_path.with_suffix("")}/'

            # Extract modification date from HTML
            lastmod_date = self._extract_modified_date(html_file)

            urls_for_sitemap.append({
                'url':      f'{self.target_domain}{url_path}',
                'lastmod':  lastmod_date,
                'priority': self._get_sitemap_priority(url_path),
                'html_file': html_file,   # kept for image extraction below
            })

        # Exclude pages that should never appear in the sitemap. Three classes:
        #   1. noindex pages — sending them as sitemap entries is a mixed
        #      signal and triggers "Submitted URL marked 'noindex'" in GSC.
        #   2. Non-canonical shims — pages whose only purpose is a meta
        #      refresh (e.g. /feed/index.html → /feed/index.xml). Google treats
        #      these as soft redirects when submitted via sitemap.
        #   3. The 404 page itself — returns HTTP 404 + noindex, so listing
        #      it triggers BOTH "Submitted URL returns 404" and "noindex".
        SITEMAP_BLOCKED_PATHS = ('/404/', '/feed/')
        before_count = len(urls_for_sitemap)
        urls_for_sitemap = [
            item for item in urls_for_sitemap
            if not self._should_exclude_from_sitemap(item, SITEMAP_BLOCKED_PATHS)
        ]
        excluded = before_count - len(urls_for_sitemap)
        if excluded:
            print(f"   🚫 Excluded {excluded} non-indexable pages from sitemap")

        # Fix lastmod for any remaining archive pages that aren't noindex:
        # Use the most recent post date linked from each archive page
        # instead of the file modification time (which is always the build date)
        post_dates = {item['url']: item['lastmod'] for item in urls_for_sitemap}
        archive_fixes = 0
        for item in urls_for_sitemap:
            url_path = item['url'].replace(self.target_domain, '')
            if '/category/' in url_path or '/tag/' in url_path:
                html_file = self.output_dir / url_path.strip('/') / 'index.html'
                if html_file.exists():
                    most_recent = self._get_archive_latest_post_date(html_file, post_dates)
                    if most_recent:
                        item['lastmod'] = most_recent
                        archive_fixes += 1
        if archive_fixes:
            print(f"   📅 Fixed lastmod dates for {archive_fixes} archive pages")

        # Generate XML — include Google Image Sitemap namespace
        sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap_content.append(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
            '\n        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
        )

        # Sort by URL and remove duplicates
        seen_urls = set()
        total_images = 0

        def _xml_escape(s):
            return (s.replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;'))

        for item in sorted(urls_for_sitemap, key=lambda x: x['url']):
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                sitemap_content.append('  <url>')
                sitemap_content.append(f'    <loc>{item["url"]}</loc>')
                sitemap_content.append(f'    <lastmod>{item["lastmod"]}</lastmod>')
                if item.get('priority'):
                    sitemap_content.append(f'    <priority>{item["priority"]}</priority>')

                # Add image entries for post/page URLs (skip feeds, api, assets, etc.)
                url_path = item['url'].replace(self.target_domain, '')
                is_content_page = (
                    html_file := item.get('html_file')
                ) and html_file is not None and any(
                    url_path.startswith(f'/{y}/') for y in range(2010, 2035)
                ) or url_path in (
                    '/',
                    '/about-james-kilby-solution-architect/',  # was '/about-me/' — renamed in WP
                    '/lab/',
                    '/homelab-software/',
                    '/media/',
                    '/vmc/',
                )

                if is_content_page and item.get('html_file'):
                    images = self._extract_page_images(item['html_file'])
                    for img in images[:20]:   # Google recommends ≤1000 per URL; 20 is generous
                        sitemap_content.append('    <image:image>')
                        sitemap_content.append(f'      <image:loc>{_xml_escape(img["loc"])}</image:loc>')
                        if img.get('title'):
                            sitemap_content.append(f'      <image:title>{_xml_escape(img["title"])}</image:title>')
                        if img.get('caption'):
                            sitemap_content.append(f'      <image:caption>{_xml_escape(img["caption"])}</image:caption>')
                        sitemap_content.append('    </image:image>')
                        total_images += 1

                sitemap_content.append('  </url>')

        sitemap_content.append('</urlset>')

        sitemap_file = self.output_dir / 'sitemap.xml'
        sitemap_file.write_text('\n'.join(sitemap_content))
        print(f"✅ Created sitemap.xml with {len(seen_urls)} URLs and {total_images} image entries")

    def _extract_modified_date(self, html_file):
        """Best <lastmod> date for the sitemap, most-trustworthy source first.

        Order of preference:
          1. <meta property="article:modified_time"> — the real WordPress
             "last edited" timestamp from Rank Math. Present on every post and,
             crucially, available even on incrementally-seeded HTML that skipped
             JSON-LD re-injection.
          2. JSON-LD dateModified on any Article-family / WebPage node
             (TechArticle, Article, BlogPosting, WebPage, …). The previous code
             only matched Article/BlogPosting/WebPage, so posts (typed
             TechArticle) never matched and silently fell through to mtime.
          3. <meta property="article:published_time"> — fall back to the publish
             date rather than inventing one.
          4. File mtime — last resort. For a freshly generated file this is the
             BUILD date, so the old behaviour stamped every post with "today",
             clustering all <lastmod> on the deploy date and training Google to
             distrust the freshness signal.

        Any future date (clock skew / bad CMS data) is clamped to today — a
        future <lastmod> is an SEO red flag.
        """
        def _to_date(value):
            if not value:
                return None
            try:
                parsed = datetime.fromisoformat(str(value).strip().replace('Z', '+00:00'))
            except (ValueError, AttributeError, TypeError):
                return None
            # Compare on the naive date so aware/naive datetimes never clash.
            return min(parsed.date(), datetime.now().date())

        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')

            # 1. article:modified_time meta (primary)
            tag = soup.find('meta', attrs={'property': 'article:modified_time'})
            d = _to_date(tag.get('content')) if tag else None
            if d:
                return d.strftime('%Y-%m-%d')

            # 2. JSON-LD dateModified on any *Article / WebPage node
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(data, dict):
                    items = data.get('@graph', [data])
                elif isinstance(data, list):
                    items = data
                else:
                    items = [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    t = item.get('@type', '')
                    types = t if isinstance(t, list) else [t]
                    if any(str(x).endswith('Article') or x == 'WebPage' for x in types):
                        d = _to_date(item.get('dateModified'))
                        if d:
                            return d.strftime('%Y-%m-%d')

            # 3. article:published_time meta
            tag = soup.find('meta', attrs={'property': 'article:published_time'})
            d = _to_date(tag.get('content')) if tag else None
            if d:
                return d.strftime('%Y-%m-%d')

            # 4. file mtime (build date — last resort)
            return datetime.fromtimestamp(html_file.stat().st_mtime).strftime('%Y-%m-%d')

        except Exception:
            # Ultimate fallback: today.
            return datetime.now().strftime('%Y-%m-%d')

    def _get_archive_latest_post_date(self, html_file, post_dates):
        """Get the most recent post date from an archive (category/tag) page.

        Parses the archive HTML for internal links to blog posts,
        looks up their dates from the already-collected sitemap data,
        and returns the most recent one.
        """
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all internal links that look like blog post URLs (year/month/slug pattern)
            post_link_pattern = re.compile(r'^(?:https?://[^/]+)?/\d{4}/\d{2}/[^/]+/?$')
            latest_date = None

            for link in soup.find_all('a', href=True):
                href = link['href']
                if post_link_pattern.match(href):
                    # Normalise to full URL for lookup
                    if href.startswith('/'):
                        full_url = f"{self.target_domain}{href}"
                    else:
                        full_url = href
                    # Ensure trailing slash for consistent lookup
                    if not full_url.endswith('/'):
                        full_url += '/'

                    date = post_dates.get(full_url)
                    if date and (latest_date is None or date > latest_date):
                        latest_date = date

            return latest_date

        except Exception as e:
            print(f"   ⚠️  Could not determine latest post date: {e}")
            return None

    def _get_sitemap_priority(self, url_path):
        """Determine <priority> for a sitemap entry based on URL pattern and post age.

        - Homepage: 1.0
        - Posts published in the last 6 months: 0.9
        - Older posts: 0.7
        - Category pages: 0.5
        - Anything else: None (omit <priority>; crawlers default to 0.5)

        Post age is derived from the /YYYY/MM/ segment of the URL, which matches
        the permalink structure produced by wp_to_static_generator.
        """
        if url_path == '/':
            return '1.0'

        if '/category/' in url_path:
            return '0.5'

        post_match = re.match(r'^/(\d{4})/(\d{2})/', url_path)
        if post_match:
            year = int(post_match.group(1))
            month = int(post_match.group(2))
            now = datetime.now()
            age_months = (now.year - year) * 12 + (now.month - month)
            return '0.9' if age_months <= 6 else '0.7'

        return None

    def _is_noindex_page(self, html_file):
        """Check if a page has a noindex robots meta tag."""
        try:
            if not html_file.exists():
                return False
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Only read the first 4KB — robots meta is always in <head>
                head_content = f.read(4096)
            return 'noindex' in head_content.lower() and 'name="robots"' in head_content.lower()
        except Exception as e:
            print(f"   ⚠️  noindex check failed for {html_file}: {e}")
            return False

    def _is_meta_refresh_shim(self, html_file):
        """Check if a page is a meta-refresh redirect shim (non-canonical)."""
        try:
            if not html_file.exists():
                return False
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                head_content = f.read(2048)
            return 'http-equiv="refresh"' in head_content.lower()
        except Exception as e:
            print(f"   ⚠️  meta-refresh check failed for {html_file}: {e}")
            return False

    def _matches_noindex_pattern(self, url_path):
        """Return True if url_path matches any Config.NOINDEX_PATH_PATTERNS."""
        return any(p.match(url_path) for p in _NOINDEX_URL_PATH_PATTERNS)

    def _should_exclude_from_sitemap(self, item, blocked_paths):
        """Decide whether a sitemap candidate URL should be dropped.

        Use the html_file already on the item dict (don't re-derive — paths
        like /404/ map to public/404.html, not public/404/index.html).

        Layered check:
          1. Explicit path blocklist (blocked_paths) — /404/, /feed/.
          2. Config.NOINDEX_PATH_PATTERNS — pattern-level noindex policy.
             Runs even before fix_seo_issues injects the meta tag, so the
             sitemap stays clean regardless of pipeline-step ordering.
          3. _is_noindex_page (reads HTML head) — catches anything WordPress
             or Rank Math has already marked noindex.
          4. _is_meta_refresh_shim — non-canonical redirect pages.
        """
        url_path = item['url'].replace(self.target_domain, '') or '/'
        if url_path in blocked_paths:
            return True
        if self._matches_noindex_pattern(url_path):
            return True
        html_file = item.get('html_file')
        if html_file is None:
            return False
        if self._is_noindex_page(html_file):
            return True
        if self._is_meta_refresh_shim(html_file):
            return True
        return False

    def generate_rss_feed(self):
        """Generate RSS feed from posts"""
        print("📡 Generating RSS feed...")

        # Collect all post information
        posts = []

        # Look for post directories (year/month pattern)
        for year_dir in sorted(self.output_dir.glob('[0-9][0-9][0-9][0-9]'), reverse=True):
            for month_dir in sorted(year_dir.glob('[0-9][0-9]'), reverse=True):
                for post_dir in month_dir.iterdir():
                    if post_dir.is_dir():
                        index_file = post_dir / 'index.html'
                        if index_file.exists():
                            try:
                                with open(index_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    html_content = f.read()

                                soup = BeautifulSoup(html_content, 'html.parser')

                                # Extract title
                                title_tag = soup.find('h1', class_=re.compile(r'entry-title', re.I))
                                if not title_tag:
                                    title_tag = soup.find('title')
                                title = title_tag.get_text().strip() if title_tag else 'Untitled'
                                title = re.sub(r'\s*[-–|]\s*jameskilby.*$', '', title, flags=re.IGNORECASE)

                                # Extract description
                                meta_desc = soup.find('meta', attrs={'name': 'description'})
                                description = meta_desc.get('content', '').strip() if meta_desc else ''

                                if not description:
                                    # Try to get excerpt from content
                                    content_div = soup.find('div', class_=re.compile(r'entry-content|entry-summary', re.I))
                                    if content_div:
                                        for script in content_div(["script", "style"]):
                                            script.decompose()
                                        text = content_div.get_text()
                                        words = text.split()[:50]
                                        description = ' '.join(words) + ('...' if len(words) >= 50 else '')

                                # Extract date — prefer the <time class=published>
                                # element, fall back to the article:published_time
                                # meta (always present from Rank Math). Keep a
                                # parsed datetime (pub_dt) so the feed can be sorted
                                # reliably before it is truncated to the latest 20.
                                from email.utils import format_datetime
                                from datetime import datetime as dt, timezone
                                datetime_str = ''
                                date_elem = soup.find('time', class_=re.compile(r'published', re.I))
                                if date_elem:
                                    datetime_str = date_elem.get('datetime', '') or ''
                                if not datetime_str:
                                    meta_pub = soup.find('meta', attrs={'property': 'article:published_time'})
                                    if meta_pub:
                                        datetime_str = (meta_pub.get('content') or '').strip()
                                pub_date = ''
                                pub_dt = None
                                if datetime_str:
                                    try:
                                        dt_obj = dt.fromisoformat(datetime_str.replace('Z', '+00:00'))
                                        # Normalise to aware UTC so the later sort
                                        # never mixes aware and naive datetimes.
                                        if dt_obj.tzinfo is None:
                                            dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                                        pub_dt = dt_obj
                                        pub_date = format_datetime(dt_obj)
                                    except (ValueError, AttributeError, TypeError):
                                        pub_date = datetime_str

                                # Extract author
                                author_elem = soup.find('a', class_=re.compile(r'author|fn', re.I))
                                author = author_elem.get_text().strip() if author_elem else 'James Kilby'

                                # Construct URL
                                relative_path = post_dir.relative_to(self.output_dir)
                                url = f"{self.target_domain}/{relative_path}/"

                                posts.append({
                                    'title': title,
                                    'description': description,
                                    'link': url,
                                    'pub_date': pub_date,
                                    'pub_dt': pub_dt,
                                    'author': author
                                })
                            except Exception as e:
                                print(f"   ⚠️  Error processing {post_dir}: {str(e)}")
                                continue

        # Sort posts by publication date (newest first), THEN take the top 20.
        # post_dir.iterdir() yields posts in arbitrary order, so without this
        # the "latest 20" could omit genuinely recent posts and mis-order the
        # feed. Posts with an unparseable/absent date sink to the bottom.
        from datetime import timezone
        _oldest = datetime.min.replace(tzinfo=timezone.utc)
        posts.sort(key=lambda p: p.get('pub_dt') or _oldest, reverse=True)
        posts = posts[:20]

        if not posts:
            print("   ⚠️  No posts found for RSS feed")
            return

        # Generate RSS XML
        from xml.sax.saxutils import escape

        rss_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            '  <channel>',
            '    <title>James Kilby</title>',
            f'    <link>{self.target_domain}/</link>',
            '    <description>VMware and cloud infrastructure tutorials, homelab guides, and DevOps insights</description>',
            '    <language>en-gb</language>',
            f'    <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>',
            f'    <atom:link href="{self.target_domain}/feed/index.xml" rel="self" type="application/rss+xml" />',
        ]

        for post in posts:
            rss_lines.extend([
                '    <item>',
                f'      <title>{escape(post["title"])}</title>',
                f'      <link>{escape(post["link"])}</link>',
                f'      <description>{escape(post["description"])}</description>',
                f'      <author>{escape(post["author"])}</author>',
                f'      <guid isPermaLink="true">{escape(post["link"])}</guid>',
            ])
            if post['pub_date']:
                rss_lines.append(f'      <pubDate>{escape(post["pub_date"])}</pubDate>')
            rss_lines.append('    </item>')

        rss_lines.extend([
            '  </channel>',
            '</rss>'
        ])

        # Save RSS feed
        feed_dir = self.output_dir / 'feed'
        feed_dir.mkdir(exist_ok=True)

        feed_file = feed_dir / 'index.xml'
        feed_file.write_text('\n'.join(rss_lines), encoding='utf-8')

        # /feed/ → /feed/index.xml is handled by a 301 rule in _redirects
        # (create_redirects_file). A previous meta-refresh HTML shim here
        # was treated by Google as a soft redirect and triggered "Page with
        # redirect" in GSC when listed in the sitemap. Drop any stale shim
        # from earlier builds so Cloudflare honours the 301.
        stale_shim = feed_dir / 'index.html'
        if stale_shim.exists():
            stale_shim.unlink()

        print(f"   ✅ Created RSS feed with {len(posts)} posts")
        print(f"   📡 Feed URL: {self.target_domain}/feed/index.xml")

    def copy_assets(self):
        """Copy assets directory (fonts, CSS, etc.) to output"""
        print("📦 Copying static assets...")

        # Copy assets directory from project root
        assets_src = Path(__file__).parent / 'assets'
        assets_dest = self.output_dir / 'assets'

        if assets_src.exists():
            shutil.copytree(assets_src, assets_dest, dirs_exist_ok=True)

            # Count files copied
            file_count = sum(1 for _ in assets_dest.rglob('*') if _.is_file())
            total_size = sum(f.stat().st_size for f in assets_dest.rglob('*') if f.is_file())

            print(f"   ✅ Copied {file_count} asset files ({total_size / 1024:.1f}KB)")
            print(f"   📁 Assets directory: {assets_dest}")
        else:
            print(f"   ℹ️  No assets directory found at {assets_src}")

    def copy_search_script(self):
        """Copy search script to public/js directory"""
        print("📋 Copying search script...")

        # Create js directory
        js_dir = self.output_dir / 'js'
        js_dir.mkdir(exist_ok=True)

        # Copy search.js from scripts/assets/js (shipped site assets live
        # there, next to the fonts — not mixed in with the Python tooling)
        search_script_src = Path(__file__).parent / 'assets' / 'js' / 'search.js'
        search_script_dest = js_dir / 'search.js'

        if search_script_src.exists():
            shutil.copy(search_script_src, search_script_dest)
            print("   ✅ Copied search.js to public/js/search.js")
        else:
            print(f"   ⚠️  search.js not found at {search_script_src}")

        # Vendor fuse.min.js and splide.min.js — both are loaded from /js/ to
        # avoid third-party CDN dependencies at runtime.
        for vendor_name in ('fuse.min.js', 'splide.min.js'):
            vendor_src = Path(__file__).parent / 'assets' / 'js' / vendor_name
            vendor_dest = js_dir / vendor_name
            if vendor_src.exists():
                shutil.copy(vendor_src, vendor_dest)
                print(f"   ✅ Copied {vendor_name} to public/js/{vendor_name}")
            else:
                print(f"   ⚠️  {vendor_name} not found at {vendor_src}")

    def copy_static_root_files(self):
        """Copy static files (favicons, manifest) to public root"""
        print("🎨 Copying favicon and manifest files...")

        # Source directory for static root files
        static_src = Path(__file__).parent / 'static-files'

        if not static_src.exists():
            print(f"   ℹ️  No static-files directory found at {static_src}")
            return

        # Copy all files from static-files to public root
        file_count = 0
        for file_path in static_src.iterdir():
            if file_path.is_file():
                dest_path = self.output_dir / file_path.name
                shutil.copy(file_path, dest_path)
                file_count += 1
                print(f"   ✅ Copied {file_path.name} to public root")

        if file_count > 0:
            print(f"   📁 Total files copied: {file_count}")
        else:
            print(f"   ℹ️  No files to copy from {static_src}")

    # Match any <script> tag whose src is /js/search.js, regardless of
    # attribute order or whitespace, and with an optional `?v=<hash>`
    # cache-busting query. The previous literal-substring guard
    # (`'<script src="/js/search.js"' in html_content`) only matched when
    # `src` was the FIRST attribute on the tag — but html_transformer.py
    # later adds `defer` and `data-cfasync` before `src`. As a result every
    # rebuild's seeded HTML failed the duplicate check and got ANOTHER
    # script tag appended. Older posts accumulated 10–20+ duplicates.
    # The `ver` group lets inject_search_script tell whether a seeded tag
    # already carries the current content hash (skip) or a stale one (replace).
    _SEARCH_SCRIPT_TAG_RE = re.compile(
        r'<script\b[^>]*\bsrc=(["\'])/js/search\.js'
        r'(?:\?v=(?P<ver>[^"\'\s>]+))?\1[^>]*>\s*</script>',
        re.IGNORECASE,
    )

    def _search_script_version(self):
        """Short content hash of the shipped search.js, for cache-busting.

        /js/search.js is served with a ~186-day max-age and no version, so
        returning visitors keep a stale copy long after a fix ships. Appending
        `?v=<hash>` to the <script src> changes the URL only when the file's
        bytes change, so the long cache lifetime stays but updates propagate
        immediately. Returns '' if the file can't be read, in which case the
        reference falls back to the plain unversioned path.
        """
        import hashlib
        src = Path(__file__).parent / 'assets' / 'js' / 'search.js'
        try:
            return hashlib.blake2b(src.read_bytes(), digest_size=6).hexdigest()
        except OSError:
            return ''

    def inject_search_script(self):
        """Inject the search script into every HTML file exactly once.

        Idempotent + self-healing: collapses any duplicate tags in seeded HTML
        (from the pre-fix bug above) to a single canonical tag at the end of
        <body>, and keeps the `?v=<hash>` cache-buster current — a tag carrying
        a stale hash (or none) is replaced so returning visitors fetch the new
        file instead of a long-cached copy.
        """
        print("📝 Injecting search script into HTML files...")

        injected_count = 0
        updated_count = 0
        deduped_count = 0
        version = self._search_script_version()
        src = '/js/search.js' + (f'?v={version}' if version else '')
        canonical_tag = f'<script src="{src}" data-cfasync="false"></script>'

        for html_file in self.output_dir.rglob('*.html'):
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()

                existing = list(self._SEARCH_SCRIPT_TAG_RE.finditer(html_content))

                # Exactly one tag already carrying the current hash → nothing to
                # do. Attribute order may differ (html_transformer adds defer /
                # data-cfasync), so we compare the version, not the whole tag.
                if (len(existing) == 1 and version
                        and existing[0].group('ver') == version):
                    continue

                if existing:
                    # Strip every existing copy (stale version and/or duplicates)
                    # so we can re-add exactly one canonical tag below.
                    html_content = self._SEARCH_SCRIPT_TAG_RE.sub('', html_content)
                    if len(existing) > 1:
                        deduped_count += 1
                    else:
                        updated_count += 1

                if '</body>' in html_content:
                    html_content = html_content.replace(
                        '</body>',
                        f'{canonical_tag}\n</body>',
                    )
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    if not existing:
                        injected_count += 1
            except Exception as e:
                print(f"   ⚠️  Error injecting script into {html_file}: {str(e)}")
                continue

        if deduped_count:
            print(f"   🧹 Collapsed duplicate search scripts in {deduped_count} files")
        if updated_count:
            print(f"   ♻️  Refreshed cache-bust hash in {updated_count} files")
        if injected_count > 0:
            print(f"   ✅ Injected search script into {injected_count} HTML files")
        elif not deduped_count and not updated_count:
            print("   ℹ️  No HTML files needed script injection")

    # Anchors on the lab page, most-preferred first. The widget is inserted
    # immediately *before* the first anchor found, so it lands after the intro
    # and above the Table of Contents / article body.
    _POWER_WIDGET_ANCHORS = (
        '<div class="wp-block-rank-math-toc-block" id="rank-math-toc">',
        '<div class="entry-content single-content">',
    )

    def inject_power_widget(self):
        """Insert the live homelab power widget into the lab page at build time.

        The widget is a repo-maintained partial (scripts/partials/
        homelab-power-widget.html), NOT WordPress content — so its markup and
        styling are versioned and reviewed like the rest of the pipeline. It
        polls the same-origin /api/power endpoint served by the Pages worker.

        Idempotent AND self-updating, mirroring inject_search_script's `?v=`
        cache-buster. The injected root is stamped with a content hash of the
        partial, so we can tell three cases apart:

          - no widget present     -> inject before the first matching anchor
          - present, hash current -> leave alone (no churn in public/)
          - present, hash stale   -> replace in place, keeping its position

        The stale case matters because public/ is committed: a previous build's
        lab page already carries a widget, and an unchanged page is kept as-is
        by the incremental build. The original guard only asked "is a widget
        present?", so once any copy was baked into public/ the partial was
        frozen — edits to it could never reach the site. Comparing the hash is
        what makes an edit actually ship. Only the lab page is touched.
        """
        print("🔌 Injecting homelab power widget...")

        target = self.output_dir / 'lab' / 'index.html'
        if not target.exists():
            print("   ℹ️  Lab page not found; skipping power widget")
            return

        # Lives in scripts/partials/ (NOT scripts/assets/, which is copied
        # wholesale into public/ — a standalone HTML fragment there fails the
        # HTML/SEO validators).
        partial_src = Path(__file__).parent / 'partials' / 'homelab-power-widget.html'
        try:
            partial = partial_src.read_text(encoding='utf-8')
        except OSError:
            print(f"   ⚠️  Power widget partial missing at {partial_src}")
            return

        try:
            html = target.read_text(encoding='utf-8', errors='ignore')
        except OSError as e:
            print(f"   ⚠️  Could not read lab page: {e}")
            return

        import hashlib
        version = hashlib.blake2b(partial.encode('utf-8'), digest_size=6).hexdigest()
        stamped, stamp_count = _POWER_WIDGET_ROOT_RE.subn(
            r'\1 data-power-widget-version="%s"' % version, partial, count=1)
        if stamp_count != 1:
            # Without the stamp we cannot tell current from stale, and would
            # rewrite the widget on every build. Fail loudly rather than churn.
            print("   ⚠️  Could not stamp widget version (partial root changed?);"
                  " power widget not injected")
            return
        # Normalise the edges so both paths below emit byte-identical markup:
        # the span matched on a refresh ends at </script>, but the partial file
        # carries a trailing newline, which would otherwise accumulate.
        stamped = stamped.strip()

        existing = _POWER_WIDGET_SPAN_RE.search(html)
        if existing:
            found = _POWER_WIDGET_VERSION_RE.search(existing.group(0))
            if found and found.group(1) == version:
                print("   ℹ️  Power widget already current on lab page")
                return
            # Stale (or unversioned, i.e. pre-dating the stamp). Swap it in
            # place so it keeps whatever position the earlier build chose.
            html = html[:existing.start()] + stamped + html[existing.end():]
            target.write_text(html, encoding='utf-8')
            print("   ♻️  Refreshed stale power widget on lab page")
            return

        for anchor in self._POWER_WIDGET_ANCHORS:
            if anchor in html:
                # Insert once, before the anchor.
                html = html.replace(anchor, stamped + '\n' + anchor, 1)
                target.write_text(html, encoding='utf-8')
                print("   ✅ Injected homelab power widget into lab page")
                return

        print("   ⚠️  No anchor found on lab page; power widget not injected")

    def generate_search_index(self):
        """Generate search index for client-side search functionality"""
        print("🔍 Generating search index...")

        search_index = []

        # Process all HTML files. sorted() because rglob walks in filesystem
        # order, which is not stable between builds — search-index.json and
        # its .min sibling were being rewritten (and re-uploaded to KV) every
        # deploy with the same entries in a different order.
        for html_file in sorted(self.output_dir.rglob('*.html')):
            try:
                relative_path = html_file.relative_to(self.output_dir)

                # Convert file path to URL path
                if relative_path.name == 'index.html':
                    if relative_path.parent == Path('.'):
                        url_path = '/'
                    else:
                        url_path = f'/{relative_path.parent}/'
                else:
                    url_path = f'/{relative_path}'

                # Read and parse HTML
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Skip redirects and error pages
                if soup.find('meta', attrs={'http-equiv': 'refresh'}):
                    continue

                # Extract metadata
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else "Untitled"

                # Clean up title (remove site name)
                title = re.sub(r'\s*[-–|]\s*jameskilby.*$', '', title, flags=re.IGNORECASE)

                # Skip if no meaningful title
                if not title or title.lower() in ['untitled', 'page not found', '404']:
                    continue

                # Meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '').strip() if meta_desc else ''

                # Extract excerpt from content if no description
                if not description:
                    content_areas = soup.find_all(['div'], class_=re.compile(r'(content|entry|post|article)', re.I))
                    if content_areas:
                        # Remove script and style elements
                        for script in content_areas[0](["script", "style", "nav", "footer"]):
                            script.decompose()

                        content_text = content_areas[0].get_text()
                        # Clean up whitespace
                        lines = (line.strip() for line in content_text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        content_text = ' '.join(chunk for chunk in chunks if chunk)

                        # Take first 150 words as excerpt
                        words = content_text.split()
                        description = ' '.join(words[:150]) + ('...' if len(words) > 150 else '')

                # Extract full content for searching (limit to 1000 chars).
                # Scope to <main>/<article> first — the previous "strip nav/
                # footer" approach left Kadence site-chrome ("Skip to content
                # James Kilby Toggle Menu...") at the front of every entry,
                # bloating the index by ~40 KB and matching every search.
                content_soup = BeautifulSoup(html_content, 'html.parser')
                content_root = (
                    content_soup.find('main')
                    or content_soup.find('article')
                    or content_soup  # fall back to whole doc on list pages
                )
                for junk in content_root(["script", "style", "nav", "footer", "header"]):
                    junk.decompose()

                full_content = content_root.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in full_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                full_content = ' '.join(chunk for chunk in chunks if chunk)

                # Skip if content is too short (likely navigation pages)
                if len(full_content.split()) < 50:
                    continue

                # Create search entry. Only fields actually consumed by
                # scripts/search.js (Fuse keys + display). The previous version
                # shipped `categories`/`tags`/`date` which were never read by
                # the UI — ~24 KB / 12 % of payload for nothing.
                entry = {
                    'title': title,
                    'url': f"{self.target_domain}{url_path}",
                    'description': description[:200] if description else '',
                    'content': full_content[:1000],
                }

                search_index.append(entry)

            except Exception as e:
                print(f"❌ Error indexing {html_file}: {str(e)}")
                continue

        # Save search index
        if search_index:
            # Save full version
            search_index_file = self.output_dir / 'search-index.json'
            with open(search_index_file, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, ensure_ascii=False, indent=2)

            # Save minified version
            search_index_min_file = self.output_dir / 'search-index.min.json'
            with open(search_index_min_file, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, ensure_ascii=False, separators=(',', ':'))

            print(f"✅ Generated search index with {len(search_index)} entries")
            print(f"   📄 Full: search-index.json ({search_index_file.stat().st_size / 1024:.1f}KB)")
            print(f"   📄 Min: search-index.min.json ({search_index_min_file.stat().st_size / 1024:.1f}KB)")
        else:
            print("⚠️  No content found for search index")
