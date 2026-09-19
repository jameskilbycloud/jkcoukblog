#!/usr/bin/env python3
"""
Header/footer brand chrome — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the third cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first, and
scripts/content_schema_rewriter.py for the second).

Everything here runs once per page, inside process_html(), and only ever
touches the soup it's handed plus two class-level markup constants
(JK_LOGO_SVG, SEARCH_BOX_HTML) — no wp_url, no target_domain, no session,
no state shared with any other group. That makes it the cleanest cut yet:
the header and footer are global Kadence structures common to every page,
so this is a single, self-contained "brand the chrome" pass.

WordPressStaticGenerator.process_html() drives this via a
HeaderFooterChrome instance (self.chrome); see that method for where it
runs. Behaviour is unchanged from the pre-extraction version — this is a
pure move, not a rewrite.
"""

from datetime import datetime

from bs4 import BeautifulSoup


class HeaderFooterChrome:
    """Header logo lockup, search button/box, relocated social icons, and a
    slimmed footer credit line — applied to every page's header/footer.
    Fully stateless: takes no constructor arguments."""

    # Locked JK monogram (designed in the JK Blog design project): black tile,
    # orange rule, Anton "JK" reversed out in the accent. {s} = pixel size.
    # Depends on the Anton webfont, which is loaded site-wide.
    JK_LOGO_SVG = (
        '<svg class="jk-mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"'
        ' width="{s}" height="{s}" role="img" aria-label="JK — James Kilby" focusable="false">'
        '<rect x="4" y="4" width="92" height="92" fill="#0a0a0a" stroke="#f6821f" stroke-width="5"></rect>'
        '<text x="50" y="52" text-anchor="middle" dominant-baseline="central"'
        ' font-family="Anton, sans-serif" font-size="56" fill="#f6821f" letter-spacing="-2">JK</text>'
        '</svg>'
    )

    def _jk_mark(self, size=40):
        """Return a freshly-parsed JK monogram <svg> tag at the given pixel size."""
        return BeautifulSoup(self.JK_LOGO_SVG.format(s=size), 'html.parser').find('svg')

    def brand_and_relocate_social(self, soup):
        """Header logo lockup + relocate footer socials + slim footer (every page).

        The header and footer are global Kadence structures, so this runs on
        every page. Each step is independent and guarded — a markup shift in one
        area can't break the others.
        """
        for step in (self._inject_brand_logo, self._inject_search_button,
                     self._inject_search_box, self._relocate_search_into_top,
                     self._relocate_social, self._slim_footer):
            try:
                step(soup)
            except Exception as e:
                print(f"   ⚠️  {step.__name__}: {e}")

    def _relocate_search_into_top(self, soup):
        """Move the homepage search box into the top band, beside the headline.

        _inject_search_box drops the box at main[0] (so its space is reserved at
        first paint — see that method's CLS note). On the homepage the redesign
        has already emitted a .jkr-headline-row slot; relocating the box into it
        turns the lonely centered search island — which sat in a dead band under
        the header, misaligned with the left-aligned grid below — into part of
        the top band, filling the empty gutter beside the capped headline. The
        node (and its reserved height) simply moves within the static HTML, so
        first-paint layout stability is preserved. Idempotent and homepage-only:
        the .jkr-headline-row exists only where inject_homepage_redesign ran.
        """
        row = soup.find(class_='jkr-headline-row')
        box = soup.find(id='blog-search-container')
        if not row or not box:
            return
        if box.find_parent(class_='jkr-headline-row') is row:
            return  # already relocated
        box.extract()
        row.append(box)

    def _inject_search_button(self, soup):
        """Add a real search button to the header (focuses the search box).

        Replaces the old CSS ::after that looked like a search control but
        couldn't be clicked. The click handler lives in search.js.
        """
        header_right = soup.find(class_='site-header-main-section-right')
        if not header_right or header_right.find(class_='jk-search'):
            return
        header_right.append(BeautifulSoup(
            '<button class="jk-search" type="button" aria-label="Search posts"'
            ' aria-keyshortcuts="Meta+K Control+K">Search <kbd>⌘K</kbd></button>',
            'html.parser'))

    # Kept byte-identical to the fallback template in
    # scripts/assets/js/search.js — see _inject_search_box. The JS builds this
    # only when the build-time copy is missing, so any drift between the two
    # shows up as the box changing shape after load. tests/
    # test_search_box_injection.py pins them together.
    SEARCH_BOX_HTML = (
        '<div id="blog-search-container" style="padding: 0; margin-bottom: 16px;">'
        '<div style="max-width: 480px; margin: 0 auto;">'
        '<div style="position: relative;">'
        '<input type="text" id="blog-search-input" placeholder="Search posts…"'
        ' style="width: 100%; padding: 10px 44px 10px 14px; font-size: 15px;'
        ' border: 1px solid #262625; border-radius: 0; outline: none;'
        ' box-sizing: border-box; background: #111110; color: #f5f3ee;'
        ' transition: border-color 0.2s ease, box-shadow 0.2s ease;'
        ' font-family: inherit;">'
        '<span style="position: absolute; right: 12px; top: 50%;'
        ' transform: translateY(-50%); color: #7a766c; pointer-events: none;'
        ' font-size: 12px; font-family: \'JetBrains Mono\', monospace;">⌘K</span>'
        '</div></div></div>'
    )

    def _inject_search_box(self, soup):
        """Pre-render the blog search box as the first child of <main>.

        search.js used to build this at runtime and
        `main.insertAdjacentHTML('afterbegin', …)` it in, which inserted an
        82px block above the content ~2s after load — on every page, since
        every page has a <main>. Measured on a throttled Pixel 7 profile it
        moved #primary down 82px for 0.079 CLS on the homepage and 0.099 on
        posts, and it is what took the origin's p75 CLS from 0.05 (stable
        through July) to 0.22 by the CrUX window ending 2026-08-22.

        Rendering it at build time means the space is occupied at first paint
        and nothing moves. search.js keeps its own copy of the markup purely
        as a fallback, and now attaches its listeners to whichever copy it
        finds.
        """
        main = soup.find('main')
        if not main or soup.find(id='blog-search-container'):
            return  # no <main> on this template, or already injected
        body = soup.find('body')
        if not body or 'home' not in (body.get('class') or []):
            # Homepage only. Interior pages (posts, archives, About) rely on the
            # header ⌘K button, so the full-width box doesn't duplicate that
            # affordance and push content down the fold on every page. The
            # front page carries the WP `home` body class.
            return
        main.insert(0, BeautifulSoup(self.SEARCH_BOX_HTML, 'html.parser'))

    def _inject_brand_logo(self, soup):
        """Prepend the JK monogram to each .brand and add a mono subline → lockup."""
        for brand in soup.select('.site-branding a.brand'):
            if brand.find(class_='jk-mark'):
                continue  # idempotent
            brand['class'] = brand.get('class', []) + ['jk-brand-lockup']
            brand.insert(0, self._jk_mark(40))  # mark sits left of the wordmark
            title_wrap = brand.find(class_='site-title-wrap')
            if title_wrap and not title_wrap.find(class_='jk-brand-sub'):
                sub = soup.new_tag('span', attrs={'class': 'jk-brand-sub'})
                sub.string = 'VMware · Homelab · Infrastructure'
                title_wrap.append(sub)

    def _relocate_social(self, soup):
        """Move the footer social icons into the header (and mobile drawer)."""
        anchors = soup.select('.footer-social a')
        if not anchors:
            return
        socials = []
        for a in anchors:
            svg = a.find('svg')
            if not svg:
                continue
            socials.append((a.get('aria-label', ''), a.get('href', '#'), str(svg)))
        if not socials:
            return

        def cluster(extra_cls):
            items = ''.join(
                f'<a class="jk-social-link" href="{href}" aria-label="{label}"'
                f' rel="noopener noreferrer" target="_blank">{svg}</a>'
                for label, href, svg in socials
            )
            return BeautifulSoup(f'<div class="jk-social {extra_cls}">{items}</div>',
                                 'html.parser')

        header_right = soup.find(class_='site-header-main-section-right')
        if header_right:
            header_right.append(cluster('jk-social-header'))
        drawer = soup.find(class_='drawer-content')
        if drawer:
            drawer.append(cluster('jk-social-drawer'))

        # Drop the now-empty Kadence footer social widget.
        widget = soup.find(class_='footer-social')
        if widget:
            widget.decompose()

    def _slim_footer(self, soup):
        """Add a logo + copyright line to the footer credit area."""
        info = soup.find(class_='footer-html-inner') or soup.find(class_='site-info-inner')
        if not info or info.find(class_='jk-footer-row'):
            return
        year = datetime.now().year
        row = BeautifulSoup(
            '<div class="jk-footer-row">'
            '<a class="jk-footer-brand" href="/" aria-label="James Kilby — home">'
            f'{self.JK_LOGO_SVG.format(s=26)}<span class="jk-footer-name">James Kilby</span></a>'
            f'<span class="jk-footer-copy">© {year} James Kilby · VMware vExpert</span>'
            '</div>',
            'html.parser')
        info.append(row)
