#!/usr/bin/env python3
"""
Critical CSS Extraction and Inlining Script

Extracts above-the-fold CSS and inlines it in <head> to eliminate render-blocking CSS.
Converts external CSS to preload with async loading.

This significantly improves First Contentful Paint (FCP) by 30-50%.
"""

import sys
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup
import re
import subprocess
import json

import soupsieve as sv

from enhance_html_performance import normalize_self_href


class _AboveFold:
    """Per-page matching context: which elements count as above the fold."""
    __slots__ = ('soup', 'elements', 'tokens', 'memo')

    def __init__(self, soup, elements, tokens):
        self.soup = soup
        self.elements = elements    # id() of every above-fold element
        self.tokens = tokens        # '.class' / '#id' present above the fold
        self.memo = {}              # selector -> bool, per page


# Pseudo-classes for states the page isn't in at first paint, and
# pseudo-elements; the element they hang off is what decides visibility.
_STATE_PSEUDO = re.compile(
    r'::?(?:before|after|first-line|first-letter|placeholder|selection|marker|backdrop|'
    r'file-selector-button|-webkit-[\w-]+|-moz-[\w-]+|-ms-[\w-]+)(?:\([^)]*\))?'
    r'|:(?:hover|focus|focus-within|focus-visible|active|visited|link|checked|disabled|'
    r'enabled|target|indeterminate|placeholder-shown|autofill)\b')
_ROOT_OR_DOCUMENT = re.compile(r'(?:^|[\s>+~]):root\b|^(?:html|body|\*)$')
_CLASS_OR_ID = re.compile(r'([.#])(-?[_a-zA-Z][\w-]*)')


def _split_selector_list(selector):
    """Split on top-level commas only — `:is(a, b)` stays whole."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(selector):
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif ch == ',' and depth == 0:
            parts.append(selector[start:i])
            start = i + 1
    parts.append(selector[start:])
    return parts


class CriticalCSSExtractor:
    """Extract and inline critical CSS for faster rendering"""

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_processed = 0
        self.css_inlined = 0
        self.css_truncated = 0
        self.css_dropped_rules = 0
        self.css_dropped_bytes = 0
        self.sample_truncated = None
        # ~16 KB raw → ~5 KB on the wire after brotli. Below this we always
        # inline so the browser doesn't pay a render-blocking round-trip for
        # critical CSS. Measured: p90 page produces ~15 KB of critical CSS.
        self.max_inline_critical = 16384
        # Hard cap on critical CSS per page; rules beyond this are dropped.
        #
        # Pinned to max_inline_critical, not below it. The old value (15000)
        # was tuned while _resolve_css_path silently failed on absolute hrefs
        # and harvested almost nothing, so no page ever reached it. Once the
        # resolver was fixed (#151) all 252 pages saturated the cap on the
        # first deploy, dropping 13-31 above-fold rules each. Raising it to
        # the inline threshold recovers ~1.4 KB per page of what was being
        # discarded.
        #
        # It must never exceed max_inline_critical, the most critical CSS
        # worth duplicating into every HTML document. (Above it, the block
        # used to be externalised to its own file — an extra render-blocking
        # request; that path is gone, and the cap is what keeps it unneeded.)
        # _assert_cap_invariant() enforces the relationship.
        self.max_critical_css = self.max_inline_critical
        self._assert_cap_invariant()
        # Tokenized stylesheets keyed by path — the extractor runs once per
        # HTML page, and without this every page re-read and re-tokenized
        # every linked sheet (N pages × M sheets), the dominant cost of the
        # critical-CSS phase. Plain dict: worst case under the thread pool
        # is a duplicate parse, never a wrong result.
        self._sheet_cache = {}

    def process_all_files(self):
        """Process all HTML files in the public directory"""
        html_files = list(self.public_dir.rglob('*.html'))

        print(f"🎨 Processing {len(html_files)} HTML files for critical CSS extraction...")

        for html_file in html_files:
            if self.process_file(html_file):
                self.files_processed += 1

        print(f"\n✅ Processed {self.files_processed} files")
        print(f"   Inlined critical CSS in {self.css_inlined} files")
        if self.css_truncated:
            print(f"   ⚠️  Truncated critical CSS in {self.css_truncated} files "
                  f"(over {self.max_critical_css} byte cap)")

    def process_file(self, file_path):
        """Process a single HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_html = f.read()

            # Pre-parse cleanup: strip accumulated noscript fallbacks and
            # deduplicate <link> tags by href so BeautifulSoup sees a clean doc.
            html = self._dedup_head_links(original_html)

            soup = BeautifulSoup(html, 'html.parser')

            # Extract critical CSS
            blocks = self._extract_critical_blocks(soup, file_path)
            # Always called: it also clears stale critical CSS from an
            # earlier build when this run extracts nothing.
            self._inline_critical_css(soup, blocks, file_path)
            inlined = bool(blocks)

            # Convert external CSS to async preload even when there was
            # nothing to inline — a page whose async-eligible sheets match no
            # critical selectors must still not ship them render-blocking,
            # and the dedup/noscript self-healing must still persist. The
            # old early-return on empty critical_css skipped both, leaving
            # such pages render-blocking forever.
            self._convert_css_to_preload(soup)

            # Write only when the document actually changed. Comparing
            # against the original as BS4 would serialize it means
            # formatting-only parse differences don't force rewrites on
            # every run.
            output = str(soup)
            if output != str(BeautifulSoup(original_html, 'html.parser')):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                if inlined:
                    self.css_inlined += 1
                return True

            return False

        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
            return False

    # How far into <main> counts as "above the fold": everything in document
    # order from the top of <body> to this many elements into <main>, plus the
    # ancestors of all of it (layout wrappers), minus the footer. Measured on
    # the live build by rendering the first viewport (1350x940 and 360x640)
    # with the async sheets blocked: 40 left desktop layout rules out; 100 and
    # 250 rendered identically to the fully-styled page.
    ABOVE_FOLD_MAIN_ELEMENTS = 100

    def _above_fold(self, soup):
        """The elements a reader can see before scrolling, for _is_critical_selector.

        Returned as a context object rather than stored on self: the
        transformer runs pages on a thread pool against one extractor.
        """
        body = soup.body or soup
        main = soup.find('main') or soup.find('article')
        cutoff = None
        if main is not None:
            inner = main.find_all(True)
            cutoff = inner[min(self.ABOVE_FOLD_MAIN_ELEMENTS, len(inner)) - 1] if inner else main

        elements = set()
        tokens = set()
        for el in body.find_all(True):
            if el.name == 'footer' or el.find_parent('footer') is not None:
                continue
            for node in (el, *el.parents):
                if id(node) in elements:
                    break
                elements.add(id(node))
                if getattr(node, 'attrs', None) is not None:
                    tokens.update('.' + c for c in (node.get('class') or []))
                    if node.get('id'):
                        tokens.add('#' + node['id'])
            if el is cutoff:
                break
        return _AboveFold(soup, elements, tokens)

    def _extract_critical_blocks(self, soup, file_path=None):
        """Critical CSS per async stylesheet: [(link, css), ...] in document order."""
        return self._extract_matching_css_rules(soup, self._above_fold(soup), file_path)

    def _extract_critical_css(self, soup, file_path=None):
        """All of a page's critical CSS as one string (standalone use and tests)."""
        return ''.join(css for _, css in self._extract_critical_blocks(soup, file_path))

    # Stylesheets that stay render-blocking. Single source of truth, used in
    # two places: _extract_matching_css_rules skips them (their above-fold
    # rules are already applied at first paint, so inlining them into the
    # critical block is duplication that wastes the cap) and
    # _convert_css_to_preload leaves them synchronous (brutalist-theme ships
    # the @font-face declarations; consolidated-inline-styles is theming
    # layered above critical CSS).
    def _assert_cap_invariant(self):
        """Fail loudly if the harvest cap exceeds the per-page inline budget.

        The two are set independently, so a well-meaning bump to
        max_critical_css would otherwise just grow every HTML document past
        the budget rather than fail here.
        """
        if self.max_critical_css > self.max_inline_critical:
            raise ValueError(
                f"max_critical_css ({self.max_critical_css}) exceeds "
                f"max_inline_critical ({self.max_inline_critical}): every page "
                "would inline more critical CSS than the per-page budget. "
                "Raise max_inline_critical first."
            )

    RENDER_BLOCKING_CSS = ('brutalist-theme', 'fonts.css', 'consolidated-inline-styles')

    # Harvest order decides what survives truncation: rules are kept in order
    # until max_critical_css, so whatever is harvested last is what gets
    # dropped. Document order was actively wrong for that purpose — the
    # homepage links footer.min.css, content.min.css, header.min.css in that
    # sequence, so the cap dropped HEADER rules (the most above-the-fold CSS
    # on the page) while keeping footer rules for content a reader has to
    # scroll past everything to reach.
    #
    # Matched on the href, first hit wins. Sheets that match nothing sit in
    # the middle tier, and document order is preserved within a tier, so an
    # unrecognised sheet keeps today's behaviour relative to its peers.
    SHEET_PRIORITY = (
        # Above the fold on every page: masthead, nav, global layout/typography.
        (0, ('header', 'global', 'nav', 'menu', 'layout')),
        # Main content — above the fold from the first paragraph down.
        # No 'post' needle: it also matches related-posts.min.css, which is
        # below-fold, and tier 1 is tested before tier 2. 'single'/'entry'/
        # 'archive' cover the post-content sheets without the ambiguity.
        (1, ('content', 'entry', 'single', 'archive')),
        # Reached only by scrolling; last to be inlined, first to be dropped.
        (2, ('footer', 'comment', 'related', 'pagination', 'widget', 'sidebar')),
    )
    _DEFAULT_SHEET_PRIORITY = 1

    @classmethod
    def _sheet_priority(cls, href):
        """Lower sorts earlier, so it survives truncation.

        Matched against the file name only. Matching the whole href puts every
        sheet on the site into the 'content' tier, because they all live under
        /wp-content/ — footer.min.css included, which is the one sheet this
        ordering most needs to rank last.
        """
        name = (href or '').split('?', 1)[0].rstrip('/').rsplit('/', 1)[-1].lower()
        for rank, needles in cls.SHEET_PRIORITY:
            if any(n in name for n in needles):
                return rank
        return cls._DEFAULT_SHEET_PRIORITY

    def _extract_matching_css_rules(self, soup, fold, file_path=None):
        """Critical rules per stylesheet — only from the sheets that load ASYNC.

        Only async-converted external sheets need their above-fold rules
        inlined. Inline <style> blocks and the render-blocking sheets
        (RENDER_BLOCKING_CSS) are already applied before first paint, so
        scanning them just duplicates CSS into the critical <style> and blows
        the byte cap — crowding out the async rules that genuinely prevent
        FOUC. So we skip both.

        Returns [(link, css), ...] in document order, one entry per sheet that
        contributed rules. Each block is inlined right before its own <link>
        (_inline_critical_css), so its rules hold the same cascade position
        the full sheet will.
        """
        candidates = []
        for order, link in enumerate(soup.find_all('link', rel='stylesheet')):
            href = link.get('href', '')
            if not href or any(x in href for x in self.RENDER_BLOCKING_CSS):
                continue
            candidates.append((self._sheet_priority(href), order, link))

        # Stable within a tier: (priority, document order). Each entry is
        # (document order, link, [minified rules]).
        per_sheet = []
        for _, order, link in sorted(candidates, key=lambda c: c[:2]):
            css_path = self._resolve_css_path(link.get('href', ''))
            if css_path and css_path.exists():
                nodes = self._get_sheet_nodes(css_path)
                if nodes:
                    rules = [r for r in (self._minify_css(rule)
                                         for rule in self._filter_rules(nodes, fold)) if r]
                    if rules:
                        per_sheet.append((order, link, rules))

        # Keep whole minified rules, in priority order, until the size cap.
        # Each rule is complete and brace-balanced, so this can never cut
        # inside a @media block — the old slice-at-15000-chars approach could,
        # leaving an unbalanced brace that made the browser discard every rule
        # after it.
        minified_rules = [r for _, _, rules in per_sheet for r in rules]
        kept = []
        size = 0
        for i, rule in enumerate(minified_rules):
            if size + len(rule) > self.max_critical_css:
                dropped_rules = len(minified_rules) - i
                dropped_bytes = sum(len(r) for r in minified_rules[i:])
                # One sample line, not one per page. When the cap binds it
                # binds on essentially every page (252/252 after #151), and
                # 252 near-identical warnings buried the signal rather than
                # carrying it. The totals go to the run summary instead.
                if self.css_truncated == 0:
                    where = f" in {file_path}" if file_path else ""
                    print(f"   ⚠️  Critical CSS over {self.max_critical_css}B cap{where}: "
                          f"dropped {dropped_rules}/{len(minified_rules)} rules "
                          f"({dropped_bytes}B) — first of possibly many, "
                          f"totals in the summary")
                    self.sample_truncated = str(file_path) if file_path else None
                self.css_truncated += 1
                self.css_dropped_rules += dropped_rules
                self.css_dropped_bytes += dropped_bytes
                break
            kept.append(rule)
            size += len(rule)

        # Hand the kept rules back to their sheets (they were kept as a
        # prefix of minified_rules, so slicing per sheet in the same order
        # recovers them), then return in document order.
        blocks = []
        remaining = len(kept)
        for order, link, rules in per_sheet:
            take = rules[:remaining]
            remaining -= len(take)
            if take:
                blocks.append((order, link, ''.join(take)))
        return [(link, css) for _, link, css in sorted(blocks, key=lambda b: b[0])]

    def _parse_css_rules(self, css_content, fold):
        """Parse CSS and extract the rules that apply above the fold.

        Thin wrapper over _tokenize_css_rules (selector-independent, cached
        per stylesheet via _get_sheet_nodes) + _filter_rules (cheap per-page
        matching). Kept as the single entry point for raw CSS strings.
        """
        return self._filter_rules(self._tokenize_css_rules(css_content), fold)

    def _tokenize_css_rules(self, css_content, _strip_comments=True):
        """Tokenize CSS into (selector, body) nodes — no selector matching.

        Uses a brace-depth tokenizer rather than a regex so that nested
        at-rules (@media, @supports) and minified CSS are handled correctly.

        Node shapes:
          - Plain rule: (selector, block_content_str)
          - Conditional group (@media, @supports, @layer …):
            (at_selector, [inner nodes]) — body is a list, recursed into.

        Skipped entirely:
          - @keyframes / @font-face blocks (their inner tokens are not
            selector-based and would produce false matches downstream).
          - @import / @charset / @namespace — they end with ';' before the
            next '{'; detected by finding the semicolon first.
        """
        if _strip_comments:
            # Strip comments before parsing so that '{' / '}' inside comments
            # don't confuse the depth tracker. Recursive calls receive block
            # content that is already comment-free.
            css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

        nodes = []
        i = 0
        n = len(css_content)

        # At-rules whose blocks contain keyframe stops or font descriptors —
        # not selector-based, so we must not recurse.
        SKIP_AT_RULES = ('@keyframes', '@-webkit-keyframes', '@-moz-keyframes',
                         '@-o-keyframes', '@font-face')

        while i < n:
            # Skip whitespace
            while i < n and css_content[i].isspace():
                i += 1
            if i >= n:
                break

            brace_pos = css_content.find('{', i)
            if brace_pos == -1:
                break  # No more rules

            # If a ';' comes before the next '{' this is an at-statement
            # (@import, @charset, @namespace) with no block — skip it.
            semi_pos = css_content.find(';', i)
            if semi_pos != -1 and semi_pos < brace_pos:
                i = semi_pos + 1
                continue

            selector = css_content[i:brace_pos].strip()

            # Walk forward to find the matching closing brace, tracking depth.
            depth = 1
            j = brace_pos + 1
            while j < n and depth > 0:
                if css_content[j] == '{':
                    depth += 1
                elif css_content[j] == '}':
                    depth -= 1
                j += 1

            block_content = css_content[brace_pos + 1:j - 1]
            i = j  # Advance past the closing brace

            if selector.startswith('@'):
                # Normalise the at-keyword for comparison.
                at_keyword = re.split(r'[\s(]', selector, maxsplit=1)[0].lower()

                if at_keyword in SKIP_AT_RULES:
                    # Keyframes / font-face: skip entirely.
                    continue

                nodes.append(
                    (selector,
                     self._tokenize_css_rules(block_content,
                                              _strip_comments=False))
                )
            else:
                nodes.append((selector, block_content))

        return nodes

    def _filter_rules(self, nodes, fold):
        """Render the tokenized nodes whose selectors apply above the fold.

        Conditional group rules keep only their matching inner rules,
        wrapped back in the at-rule header. Source order is preserved.
        """
        rules = []
        for selector, body in nodes:
            if isinstance(body, list):
                inner = self._filter_rules(body, fold)
                if inner:
                    rules.append(f"{selector}{{{''.join(inner)}}}")
            elif self._is_critical_selector(selector, fold):
                rules.append(f"{selector}{{{body}}}")
        return rules

    def _get_sheet_nodes(self, css_path):
        """Tokenized top-level nodes for a stylesheet, cached per file.

        Keyed on (mtime_ns, size) so a sheet rewritten mid-run (earlier
        pipeline stages run before this one, but belt-and-braces) is
        re-tokenized rather than served stale.
        """
        try:
            stat = css_path.stat()
        except OSError:
            return None
        cache_key = str(css_path)
        fingerprint = (stat.st_mtime_ns, stat.st_size)
        cached = self._sheet_cache.get(cache_key)
        if cached and cached[0] == fingerprint:
            return cached[1]
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                nodes = self._tokenize_css_rules(f.read())
        except Exception:
            # Silently skip if we can't read the file
            return None
        self._sheet_cache[cache_key] = (fingerprint, nodes)
        return nodes

    def _is_critical_selector(self, selector, fold):
        """True if any selector in the list matches an element above the fold.

        Matching against the page's real DOM replaced a token test that took
        a rule whenever ANY part of its selector named something on a short
        list (`a`, `p`, `img`, `h2`, `section`, …) — so `.site-footer a` and
        `.widget p` counted, while the rules for the header's own descendants
        (the ones that hide the mobile header on desktop) didn't. With the
        async sheets blocked, the first paint differed from the final render
        on 43% of first-viewport pixels across a 20-page sample; with this,
        ~0.5% (anti-aliasing).

        State and pseudo-element parts are stripped first (`:hover`,
        `::before`, …): the rule matters if the element it hangs off is
        visible. Anything soupsieve can't evaluate is kept, as before.
        """
        if selector.startswith('@'):      # @font-face, @page, … — not element rules
            return False
        memo = fold.memo
        if selector in memo:
            return memo[selector]
        result = any(self._selector_part_is_critical(part.strip(), fold)
                     for part in _split_selector_list(selector) if part.strip())
        memo[selector] = result
        return result

    @staticmethod
    def _selector_part_is_critical(part, fold):
        if _ROOT_OR_DOCUMENT.search(part):
            return True
        cleaned = _STATE_PSEUDO.sub('', part).strip()
        cleaned = re.sub(r'[\s>+~]+$', '', cleaned).strip() or '*'
        # Cheap pre-check: a class or id that appears nowhere above the fold
        # can't match there. Skipped for escaped selectors (`.md\:flex`),
        # which the token regex can't read.
        if '\\' not in cleaned:
            positive = re.sub(r':not\([^)]*\)|\[[^\]]*\]', '', cleaned)
            if any(kind + name not in fold.tokens for kind, name in _CLASS_OR_ID.findall(positive)):
                return False
        try:
            return any(id(el) in fold.elements for el in sv.iselect(cleaned, fold.soup))
        except Exception:
            return True

    def _resolve_css_path(self, href):
        """Resolve CSS file path from href.

        Absolute same-site URLs and cache-busting query strings both have to
        come off before the disk lookup. At the point this runs the hrefs are
        absolute (`https://jameskilby.co.uk/wp-content/...`) —
        convert_to_staging.py doesn't rewrite them to relative until "Prepare
        output for deployment", long afterwards. lstrip('/') doesn't touch a
        scheme, so the lookup became
        `static-output/https:/jameskilby.co.uk/wp-content/...`, which never
        exists.

        This is the same defect #146 fixed in html_transformer's inliner; this
        second copy of the resolver was left behind, and it fails silently:
        an unresolvable sheet contributes no rules, and the caller can't tell
        that apart from a sheet with nothing above the fold.

        The cost was CLS. _convert_css_to_preload makes these same sheets load
        async, so header.min.css (13.7 KB) and content.min.css (19.1 KB) —
        which carry the above-fold layout — were being deferred with none of
        their rules inlined. The homepage's critical CSS came out at 4,302
        chars against the 11,684 it produces once the hrefs resolve, and
        Lighthouse measured 0.647 CLS / P73 on 2026-08-09 07:58 UTC.
        """
        href = normalize_self_href(href or '').lstrip('/').split('?', 1)[0]
        if not href:
            return None

        css_path = self.public_dir / href

        if css_path.exists():
            return css_path

        return None

    def _minify_css(self, css):
        """Minify CSS"""
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*{\s*', '{', css)
        css = re.sub(r'\s*}\s*', '}', css)
        css = re.sub(r'\s*:\s*', ':', css)
        css = re.sub(r'\s*;\s*', ';', css)
        css = re.sub(r'\s*,\s*', ',', css)

        # Remove trailing semicolons
        css = re.sub(r';}', '}', css)

        return css.strip()

    def _inline_critical_css(self, soup, blocks, file_path=None):
        """Inline each sheet's critical CSS right before that sheet's <link>.

        One <style data-critical-for="href"> per async sheet, at the sheet's
        own position, so its rules keep the cascade order the full sheet will
        have. A single block at the top of <head> lost to anything after it —
        e.g. global.min.css (inlined further down) beat the critical copy of
        kadence-global-inline-css's mobile .content-area margin, pushing
        mobile content 48 px down until the async sheet arrived.

        Stale critical CSS from an earlier build is always removed first,
        including the old single `<style id="critical-css">` and externalised
        `/assets/css/critical/` links. Returns True if the document changed.
        """
        if not soup.head:
            return False
        changed = False
        for old in soup.find_all('style', id='critical-css') + soup.find_all('style', attrs={'data-critical-for': True}):
            old.decompose()
            changed = True
        for link in soup.find_all(
            'link',
            href=lambda h: h and h.startswith('/assets/css/critical/critical-')
        ):
            link.decompose()
            changed = True

        for link, css in blocks:
            if link.parent is None or not css:
                continue
            style_tag = soup.new_tag('style')
            style_tag['data-critical-for'] = link.get('href', '')
            style_tag.string = css
            link.insert_before(style_tag)
            changed = True
        return changed

    @staticmethod
    def _dedup_head_links(html):
        """Pre-parse cleanup: strip accumulated <noscript> fallbacks and
        deduplicate <link> tags inside <head> by href attribute.

        Operates on the raw HTML string so it works even when the document is
        badly damaged (hundreds of duplicate links, deeply stacked noscript
        wrappers, etc.) and BeautifulSoup would struggle to parse it cleanly.

        After this pass every href appears exactly once inside <head> and
        there are no noscript-wrapped link fallbacks.  _convert_css_to_preload
        then re-adds exactly one fresh noscript per async-CSS preload link.
        """
        head_match = re.search(
            r'(<head\b[^>]*>)(.*?)(</head>)',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not head_match:
            return html

        head_open  = head_match.group(1)
        head_body  = head_match.group(2)
        head_close = head_match.group(3)

        # 1. Strip ALL <noscript> blocks that wrap a single <link>.
        #    _convert_css_to_preload re-adds exactly one per async-CSS link.
        head_body = re.sub(
            r'<noscript>\s*<link\b[^>]*/?\s*>\s*</noscript>',
            '',
            head_body,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # 2. Deduplicate <link> tags by href — keep the first occurrence.
        seen_hrefs = set()

        def _keep_unique_link(m):
            tag = m.group(0)
            href_m = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if not href_m:
                return tag  # No href attribute — keep unconditionally.
            href = href_m.group(1)
            if href in seen_hrefs:
                return ''
            seen_hrefs.add(href)
            return tag

        head_body = re.sub(
            r'<link\b[^>]*/?>',
            _keep_unique_link,
            head_body,
            flags=re.IGNORECASE,
        )

        new_head = head_open + head_body + head_close
        return html[:head_match.start()] + new_head + html[head_match.end():]

    def _convert_css_to_preload(self, soup):
        """Convert external CSS links to preload with async loading.

        Idempotent and self-healing.  The raw-string pre-pass in process_file
        (_dedup_head_links) removes accumulated noscript/link duplication
        before BS4 ever sees the document, so this method only needs to:

          1. Strip any residual noscript fallbacks still in <head>.
          2. Convert remaining stylesheet links to preload+onload.
          3. Add exactly one fresh noscript per async-CSS preload link.

        Steps 2 and 3 are intentionally separated so that links which were
        already converted to preload+onload in a prior pipeline run (and
        survived the dedup pass as-is) also receive a fresh noscript without
        the double-counting that occurred when noscripts were added in step 2
        *and* again in a former "step 3".

        Returns True when the document semantically changed. A noscript that
        is stripped in step 1 and re-added identically in step 3 does NOT
        count — idempotent runs must report unchanged so callers don't
        rewrite every file on every build.
        """
        EXCLUDED = self.RENDER_BLOCKING_CSS
        modified = False

        # ── Step 1: strip residual noscript blocks ───────────────────────
        # _dedup_head_links already removed them from the raw string (when
        # the caller ran it), but do a belt-and-suspenders BS4 cleanup for
        # safety. Remember what was removed, keyed by href, so step 3 can
        # tell a restoring re-add from a genuine change.
        stripped = Counter()
        if soup.head:
            for ns in list(soup.head.find_all('noscript')):
                inner = ns.find('link')
                if inner:
                    stripped[inner.get('href', '')] += 1
                    ns.decompose()

        # ── Step 2: convert stylesheet links → preload+onload ────────────
        # Do NOT add noscripts here — step 3 handles all of them uniformly.
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            # IMPORTANT: brutalist-theme.css ships the @font-face declarations
            # inline (no @import) and must load synchronously so fonts are
            # discovered as soon as it parses. consolidated-inline-styles is
            # excluded for the same reason: theming layered above critical CSS.
            if any(x in href for x in EXCLUDED):
                continue
            link['rel'] = 'preload'
            link['as'] = 'style'
            link['onload'] = "this.onload=null;this.rel='stylesheet'"
            modified = True

        # ── Step 3: add exactly one noscript per async-CSS preload link ───
        # This covers three cases:
        #   a) Links just converted to preload+onload in step 2.
        #   b) Links already preload+onload from a previous pipeline run.
        #   c) Plain preload-as-style links (no onload) left over from the old
        #      _externalize_critical_css bug — upgrade them to include onload
        #      so they actually apply the stylesheet at runtime.
        added = Counter()
        if soup.head:
            for link in list(soup.head.find_all('link')):
                rel  = link.get('rel') or []
                href = link.get('href', '')
                if 'preload' not in rel or link.get('as') != 'style':
                    continue
                if any(x in href for x in EXCLUDED):
                    continue
                # Upgrade plain preload to async onload if missing.
                if not link.get('onload'):
                    link['onload'] = "this.onload=null;this.rel='stylesheet'"
                    modified = True
                noscript = soup.new_tag('noscript')
                fallback = soup.new_tag('link')
                fallback['rel'] = 'stylesheet'
                fallback['href'] = href
                if link.get('media'):
                    fallback['media'] = link['media']
                noscript.append(fallback)
                link.insert_after(noscript)
                added[href] += 1

        # Noscript churn only counts when the set actually changed.
        if added != stripped:
            modified = True

        return modified


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        public_dir = sys.argv[1]
    else:
        public_dir = 'public'

    extractor = CriticalCSSExtractor(public_dir)
    extractor.process_all_files()

    sys.exit(0)


if __name__ == '__main__':
    main()
