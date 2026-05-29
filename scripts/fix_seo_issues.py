#!/usr/bin/env python3
"""
SEO Issues Fixer
Fixes common SEO problems in generated HTML files
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

# Import config for target domain
sys.path.insert(0, str(Path(__file__).parent))
try:
    from config import Config
    TARGET_DOMAIN = Config.TARGET_DOMAIN
except (ImportError, AttributeError):
    TARGET_DOMAIN = 'https://jameskilby.co.uk'


class SEOFixer:
    """Fix SEO issues in HTML files"""

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_fixed = 0
        self.issues_fixed = 0

    def process_all_files(self):
        """Process all HTML files"""
        html_files = list(self.public_dir.rglob('*.html'))

        # Exclude feeds and sitemaps
        html_files = [f for f in html_files if not any(
            pattern in str(f) for pattern in ['feed/', 'sitemap']
        )]

        print(f"🔧 Fixing SEO issues in {len(html_files)} HTML files...")

        for html_file in html_files:
            if self.process_file(html_file):
                self.files_fixed += 1

        print(f"\n✅ Fixed {self.files_fixed} files")
        print(f"   Resolved {self.issues_fixed} SEO issues")

    def process_file(self, file_path):
        """Process a single HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            modified = False

            # Apply fixes
            if self.fix_title_length(soup, file_path):
                modified = True

            if self.fix_meta_description(soup, file_path):
                modified = True

            if self.fix_multiple_h1(soup, file_path):
                modified = True

            if self.ensure_image_alt_text(soup, file_path):
                modified = True

            if self.fix_canonical_url(soup, file_path):
                modified = True

            if self.fix_og_absolute_urls(soup, file_path):
                modified = True

            if self.fix_jsonld_absolute_ids(soup, file_path):
                modified = True

            if self.fix_blogposting_to_techarticle(soup, file_path):
                modified = True

            if self.fix_breadcrumb_positions(soup, file_path):
                modified = True

            if self.fix_person_name(soup, file_path):
                modified = True

            if self.fix_og_site_name(soup, file_path):
                modified = True

            if self.fix_malformed_stylesheet_attr(soup, file_path):
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

    # When a previous build truncated the <title>, it ends with this literal
    # ellipsis. We restore the full title from JSON-LD if we can find it.
    _TRUNCATED_TITLE_SUFFIX = '...'

    def fix_title_length(self, soup, file_path):
        """Repair broken <title> tags from previous builds and normalize.

        Older versions of this method brutally truncated any <title> over
        60 chars by chopping it at 57 chars and appending a literal '...'.
        That signalled "broken/auto-generated content" to Google and was
        the dominant cause of "Crawled — currently not indexed" in GSC
        (40 of 72 posts had it). Restore the full title from JSON-LD
        TechArticle.headline / Article.headline / WebPage.name when we
        find a previously-truncated title; otherwise leave the title
        alone so Google handles display truncation itself.
        """
        title_tag = soup.find('title')
        if not title_tag:
            return False

        title_text = title_tag.get_text().strip()
        if not title_text.endswith(self._TRUNCATED_TITLE_SUFFIX):
            return False

        full_title = self._extract_title_from_jsonld(soup)
        if not full_title or full_title == title_text:
            return False

        # HTML-entity-decode (JSON-LD often holds &amp; / &#039; etc.)
        import html as _html
        full_title = _html.unescape(full_title).strip()
        if not full_title or full_title == title_text:
            return False

        title_tag.string = full_title
        self.issues_fixed += 1
        print(f"   📏 Restored truncated title from JSON-LD: {file_path.name}")
        return True

    @staticmethod
    def _extract_title_from_jsonld(soup):
        """Pull the first plausible full-length title out of any JSON-LD
        block in the page. Order of preference: TechArticle.headline,
        Article.headline, BlogPosting.headline, WebPage.name.
        """
        import json as _json

        preferred = (
            ('TechArticle', 'headline'),
            ('Article', 'headline'),
            ('BlogPosting', 'headline'),
            ('WebPage', 'name'),
            ('CollectionPage', 'name'),
        )

        candidates = {}
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = _json.loads(script.string or '')
            except Exception:
                continue
            graph = data.get('@graph', [data]) if isinstance(data, dict) else [data]
            for item in graph:
                if not isinstance(item, dict):
                    continue
                t = item.get('@type')
                types = t if isinstance(t, list) else [t]
                for tt in types:
                    for needle_type, needle_field in preferred:
                        if tt == needle_type and item.get(needle_field):
                            candidates.setdefault(needle_type, item[needle_field])

        for needle_type, _field in preferred:
            if needle_type in candidates:
                return candidates[needle_type]
        return None

    def fix_meta_description(self, soup, file_path):
        """Fix meta description length"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            return False

        desc = meta_desc.get('content', '')
        modified = False

        # Long meta descriptions are not truncated here (Google rewrites
        # snippets and a literal '...' suffix signals broken content).
        # Two repair paths follow:
        #   - desc ends in '...' from a previous build: regenerate cleanly
        #     from the first article paragraph (truncated to a word/sentence
        #     boundary, NOT with another ellipsis)
        #   - desc is too short (<120 chars): expand from article content
        #     using the same clean truncation
        too_long = len(desc) > 160
        broken = desc.endswith('...')
        too_short = len(desc) < 120

        if too_long and not broken:
            return modified

        if not (broken or too_short):
            return modified

        content_area = (
            soup.find('article') or
            soup.find('main') or
            soup.find(class_=re.compile(
                r'entry.?content|post.?content|article.?body', re.I
            )) or
            soup
        )
        first_p = content_area.find('p')
        if not first_p:
            return modified

        p_text = first_p.get_text().strip()
        if not p_text:
            return modified

        if broken:
            new_desc = self._clean_truncate(p_text, 155)
            label = 'Restored truncated description'
        elif len(p_text) >= 120:
            new_desc = self._clean_truncate(p_text, 155)
            label = 'Expanded short description'
        elif len(desc + ' ' + p_text) <= 160:
            new_desc = f"{desc} {p_text}"
            label = 'Expanded short description (concat)'
        else:
            return modified

        if not new_desc or new_desc == desc:
            return modified

        meta_desc['content'] = new_desc
        self.issues_fixed += 1
        print(f"   📝 {label}: {file_path.name}")
        return True

    @staticmethod
    def _clean_truncate(text: str, max_len: int) -> str:
        """Trim text to <=max_len chars at a sentence-end or word boundary.

        Avoids two anti-patterns Google's quality signal picks up on:
        breaking mid-word, and tacking a literal '...' onto the end.
        """
        if len(text) <= max_len:
            return text.strip()
        window = text[:max_len]
        # Prefer cutting at the last sentence terminator.
        for term in ('. ', '! ', '? '):
            idx = window.rfind(term)
            if idx >= max_len // 2:
                return window[: idx + 1].strip()
        # Otherwise fall back to the last word boundary.
        idx = window.rfind(' ')
        if idx > 0:
            return window[:idx].rstrip(',;:—–-').strip()
        return window.strip()

    def fix_multiple_h1(self, soup, file_path):
        """Ensure only one H1 tag per page"""
        h1_tags = soup.find_all('h1')

        if len(h1_tags) <= 1:
            return False

        # Keep the first H1, convert others to H2
        for h1 in h1_tags[1:]:
            h1.name = 'h2'
            self.issues_fixed += 1

        print(f"   🏷️  Fixed multiple H1 tags: {file_path.name} ({len(h1_tags)} → 1)")
        return True

    def ensure_image_alt_text(self, soup, file_path):
        """Add generic alt text to images missing it"""
        modified = False

        for img in soup.find_all('img'):
            if not img.get('alt'):
                # Try to generate alt text from image filename
                src = img.get('src', '')
                if src:
                    # Extract filename without extension
                    filename = Path(src).stem
                    # Convert dashes/underscores to spaces and capitalize
                    alt_text = filename.replace('-', ' ').replace('_', ' ').title()
                    img['alt'] = alt_text
                    self.issues_fixed += 1
                    modified = True
                else:
                    # Generic fallback
                    img['alt'] = 'Image'
                    self.issues_fixed += 1
                    modified = True

        if modified:
            print(f"   🖼️  Added alt text to images: {file_path.name}")

        return modified

    def fix_jsonld_absolute_ids(self, soup, file_path):
        """Ensure JSON-LD @id and url values use absolute URLs.

        convert_to_staging.py strips all domain prefixes including those inside
        <script type="application/ld+json"> blocks, turning @id and url values
        like 'https://jameskilby.co.uk/about/' into '/about/'.  Search engines
        and validators require fully-qualified IRIs for @id.
        """
        import json as _json

        modified = False
        # Keys whose string values should be made absolute.
        # Note: values for these keys can also be nested objects (e.g. "image"
        # can be an ImageObject dict), so we always recurse into dicts/lists
        # regardless of the key name.
        URL_KEYS = {'@id', 'url', 'logo', 'image', 'thumbnailUrl', 'contentUrl',
                    'sameAs', 'item'}

        def absolutify(value):
            """Return absolute URL if value is a root-relative path."""
            if isinstance(value, str) and value.startswith('/'):
                return f"{TARGET_DOMAIN}{value}"
            return value

        def fix_node(obj):
            """Recursively walk a JSON-LD node and absolutify URL fields."""
            nonlocal modified
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key == 'sameAs':
                        if isinstance(val, list):
                            new_list = [absolutify(v) for v in val]
                            if new_list != val:
                                obj[key] = new_list
                                modified = True
                        else:
                            new_val = absolutify(val)
                            if new_val != val:
                                obj[key] = new_val
                                modified = True
                    elif key in URL_KEYS and isinstance(val, str):
                        # String value — absolutify directly
                        new_val = absolutify(val)
                        if new_val != val:
                            obj[key] = new_val
                            modified = True
                    # Always recurse into nested dicts/lists so that e.g.
                    # "image": {"@id": "/#logo", "url": "/..."} gets fixed too.
                    if isinstance(val, (dict, list)):
                        fix_node(val)
            elif isinstance(obj, list):
                for item in obj:
                    fix_node(item)

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = _json.loads(script.string or '')
                fix_node(data)
                if modified:
                    script.string = _json.dumps(data, ensure_ascii=False,
                                                separators=(',', ':'))
            except (_json.JSONDecodeError, TypeError):
                continue  # malformed JSON-LD – skip silently

        if modified:
            self.issues_fixed += 1
            print(f"   🔗 Fixed relative JSON-LD @id/url values: {file_path.name}")

        return modified

    def fix_canonical_url(self, soup, file_path):
        """Ensure every page has an absolute canonical <link> in <head>.

        Two failure modes are handled:
        1. Canonical tag present but relative (href starts with "/") — fix it.
        2. Canonical tag absent entirely — inject one.  This happens when
           WordPress/Rank Math fails to emit a canonical tag, which causes
           the static build to inherit that omission.  Without a canonical,
           Google may treat jameskilby.co.uk and jkcoukblog.pages.dev as
           separate duplicate sites and split index credit between them.

        URL derivation priority (most→least reliable):
          a) og:url meta tag — already fixed to absolute by fix_og_absolute_urls
          b) File path relative to public_dir — always available as fallback
        """
        head = soup.find('head')
        if not head:
            return False

        canon = soup.find('link', rel='canonical')

        # ── Case 1: tag exists but href is relative ──────────────────────────
        if canon:
            href = canon.get('href', '')
            if href.startswith('/'):
                canon['href'] = f"{TARGET_DOMAIN}{href}"
                self.issues_fixed += 1
                print(f"   🔗 Fixed relative canonical URL: {file_path.name}")
                return True
            return False  # already absolute — nothing to do

        # ── Case 2: tag is missing entirely — derive and inject ──────────────
        canonical_url = self._derive_canonical_url(soup, file_path)
        if not canonical_url:
            return False

        new_tag = soup.new_tag('link', rel='canonical', href=canonical_url)
        head.append(new_tag)
        self.issues_fixed += 1
        print(f"   🔗 Injected missing canonical URL ({canonical_url}): {file_path.name}")
        return True

    def _derive_canonical_url(self, soup, file_path):
        """Return the absolute canonical URL for this page.

        Tries og:url first (most accurate), falls back to file-path derivation.
        """
        # Prefer og:url — it's set by WordPress/Rank Math and already
        # absolutified by fix_og_absolute_urls earlier in the pipeline.
        og_url = soup.find('meta', property='og:url')
        if og_url:
            content = og_url.get('content', '').strip()
            if content.startswith('https://') or content.startswith('http://'):
                return content

        # Fallback: derive from file path relative to the public dir.
        # e.g. .../public/2022/11/some-post/index.html → /2022/11/some-post/
        try:
            rel = file_path.relative_to(self.public_dir)
            parts = rel.parts
            # Strip trailing index.html
            if parts and parts[-1] == 'index.html':
                parts = parts[:-1]
            url_path = '/' + '/'.join(parts)
            if url_path != '/' and not url_path.endswith('/'):
                url_path += '/'
            return f"{TARGET_DOMAIN}{url_path}"
        except ValueError:
            return None

    def fix_blogposting_to_techarticle(self, soup, file_path):
        """Upgrade BlogPosting @type to TechArticle for technical posts.

        TechArticle is a schema.org subtype of Article targeted at technical
        documentation.  Upgrading from BlogPosting signals to Google that the
        content is expert-level technical writing, which improves eligibility
        for rich results in technical search queries.
        """
        import json as _json

        modified = False

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = _json.loads(script.string or '')
                script_modified = False

                # Walk both flat docs and @graph arrays
                nodes = (
                    data.get('@graph', [data])
                    if isinstance(data, dict) and '@graph' in data
                    else ([data] if isinstance(data, dict) else data)
                )

                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    schema_type = node.get('@type', '')
                    is_blogpost = (
                        schema_type == 'BlogPosting'
                        or (isinstance(schema_type, list) and 'BlogPosting' in schema_type)
                    )
                    if is_blogpost:
                        node['@type'] = 'TechArticle'
                        if 'proficiencyLevel' not in node:
                            node['proficiencyLevel'] = 'Expert'
                        script_modified = True

                if script_modified:
                    modified = True
                    script.string = _json.dumps(
                        data, ensure_ascii=False, separators=(',', ':')
                    )

            except (_json.JSONDecodeError, TypeError):
                continue

        if modified:
            self.issues_fixed += 1
            print(f"   📄 Upgraded BlogPosting → TechArticle: {file_path.name}")

        return modified

    def fix_breadcrumb_positions(self, soup, file_path):
        """Coerce BreadcrumbList position values from strings to integers.

        The schema.org spec defines position as an Integer.  Rank Math sometimes
        outputs it as a JSON string ("1") which causes warnings in Google's Rich
        Results Test.
        """
        import json as _json

        modified = False

        def _coerce(obj):
            nonlocal modified
            if isinstance(obj, dict):
                if obj.get('@type') == 'ListItem' and 'position' in obj:
                    pos = obj['position']
                    if isinstance(pos, str):
                        try:
                            obj['position'] = int(pos)
                            modified = True
                        except ValueError:
                            pass
                for val in obj.values():
                    if isinstance(val, (dict, list)):
                        _coerce(val)
            elif isinstance(obj, list):
                for item in obj:
                    _coerce(item)

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = _json.loads(script.string or '')
                before = modified
                _coerce(data)
                if modified != before:
                    script.string = _json.dumps(
                        data, ensure_ascii=False, separators=(',', ':')
                    )
            except (_json.JSONDecodeError, TypeError):
                continue

        if modified:
            self.issues_fixed += 1
            print(f"   🍞 Fixed BreadcrumbList position types: {file_path.name}")

        return modified

    def fix_person_name(self, soup, file_path):
        """Fix incorrect Person/Organization name 'Jameskilbycouk' → 'James Kilby'.

        Older posts were built before the Rank Math site-name fix and still carry
        the concatenated slug as the name value in JSON-LD.
        """
        import json as _json

        WRONG = 'Jameskilbycouk'
        RIGHT = 'James Kilby'
        modified = False

        def _fix(obj):
            nonlocal modified
            if isinstance(obj, dict):
                if obj.get('name') == WRONG:
                    obj['name'] = RIGHT
                    modified = True
                for val in obj.values():
                    if isinstance(val, (dict, list)):
                        _fix(val)
            elif isinstance(obj, list):
                for item in obj:
                    _fix(item)

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = _json.loads(script.string or '')
                before = modified
                _fix(data)
                if modified != before:
                    script.string = _json.dumps(
                        data, ensure_ascii=False, separators=(',', ':')
                    )
            except (_json.JSONDecodeError, TypeError):
                continue

        if modified:
            self.issues_fixed += 1
            print(f"   👤 Fixed Person name (Jameskilbycouk → James Kilby): {file_path.name}")

        return modified

    def fix_og_site_name(self, soup, file_path):
        """Fix og:site_name when it contains the old concatenated slug 'Jameskilbycouk'.

        Some older posts were built before the Rank Math site-name fix and still
        carry the concatenated slug as the og:site_name content value.  This
        parallels fix_person_name() which already fixes the same value inside
        JSON-LD blocks.
        """
        WRONG = 'Jameskilbycouk'
        RIGHT = 'James Kilby'
        modified = False

        tag = soup.find('meta', property='og:site_name')
        if tag and tag.get('content', '') == WRONG:
            tag['content'] = RIGHT
            modified = True

        if modified:
            self.issues_fixed += 1
            print(f"   🏷️  Fixed og:site_name (Jameskilbycouk → James Kilby): {file_path.name}")

        return modified

    def fix_malformed_stylesheet_attr(self, soup, file_path):
        """Remove the bogus stylesheet'\"=\"\" attribute injected by WPO-Minify.

        The WPO-Minify WordPress plugin emits CSS preload <link> tags with an
        onload handler that uses single quotes inside a double-quoted attribute
        value:

            <link … onload="this.onload=null;this.rel='stylesheet'" rel="preload">

        When BeautifulSoup's html.parser encounters this it sometimes serialises
        a spurious attribute literal  stylesheet'"=""  into the output.  That
        bogus attribute makes the <link> invalid HTML and can confuse Googlebot's
        renderer, preventing correct CSS application during crawl.

        This method strips any attribute whose name matches that pattern from
        every <link> tag in the page.
        """
        import re as _re
        # The actual attribute key BeautifulSoup stores is  stylesheet'"
        # (literal single-quote + double-quote suffix).  Match any key that
        # starts with "stylesheet" and contains at least one quote character.
        BOGUS_PATTERN = _re.compile(r"^stylesheet['\"]", _re.IGNORECASE)
        modified = False

        for tag in soup.find_all('link'):
            # tag.attrs is a dict; iterate over a copy so we can mutate safely
            bogus_keys = [k for k in list(tag.attrs.keys()) if BOGUS_PATTERN.match(str(k))]
            for k in bogus_keys:
                del tag.attrs[k]
                modified = True

        if modified:
            self.issues_fixed += 1
            print(f"   🔗 Removed bogus stylesheet attribute from <link> tags: {file_path.name}")

        return modified

    def fix_og_absolute_urls(self, soup, file_path):
        """Ensure og:image, og:url, and twitter:image use absolute URLs.

        Social platforms require absolute https:// URLs for link previews.
        Relative paths like /wp-content/uploads/... produce broken previews
        on Facebook, Twitter/X, LinkedIn, and Slack.
        """
        modified = False
        # Open Graph meta tags with property attribute
        OG_URL_PROPS = {'og:image', 'og:image:secure_url', 'og:url'}
        for meta in soup.find_all('meta', property=lambda p: p in OG_URL_PROPS):
            content = meta.get('content', '')
            if content.startswith('/'):
                meta['content'] = f"{TARGET_DOMAIN}{content}"
                modified = True

        # Twitter Card meta tags with name attribute
        for meta in soup.find_all('meta', attrs={'name': 'twitter:image'}):
            content = meta.get('content', '')
            if content.startswith('/'):
                meta['content'] = f"{TARGET_DOMAIN}{content}"
                modified = True

        if modified:
            self.issues_fixed += 1
            print(f"   🔗 Fixed relative og:image/og:url to absolute: {file_path.name}")

        return modified


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        public_dir = sys.argv[1]
    else:
        public_dir = 'public'

    fixer = SEOFixer(public_dir)
    fixer.process_all_files()

    sys.exit(0)


if __name__ == '__main__':
    main()
