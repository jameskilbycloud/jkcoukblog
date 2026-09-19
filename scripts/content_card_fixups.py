#!/usr/bin/env python3
"""
Footer/card/content DOM fixups — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the seventh cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

Four small, independent per-page passes, all fully stateless (no
self. usage at all — not even wp_url or target_domain): footer
markdown/API mirror links on post pages, the byline published/updated
date separator, capping archive-card category links, and converting a
table's first row into a proper <thead>.

WordPressStaticGenerator.process_html() drives these via a
ContentCardFixups instance (self.card_fixups); see that method for where
they run. Behaviour is unchanged from the pre-extraction version — this is
a pure move, not a rewrite.
"""


class ContentCardFixups:
    """Footer links, byline date formatting, archive-card category
    trimming, and table header semantics for a single page's already-parsed
    soup. Fully stateless: takes no constructor arguments."""

    def add_markdown_api_links(self, soup, current_url):
        """Add links to markdown and API versions in footer.

        Only rendered on post pages (/YYYY/MM/slug/) where a per-post markdown
        export exists. Bare /markdown/ and /api/ are directories — Cloudflare
        Pages 404s on the directory itself, so linking to them site-wide
        produced hundreds of broken internal links (visible in GSC).
        """
        import re

        post_match = re.match(r'^/(\d{4})/(\d{2})/([^/]+)/?$', current_url or '')
        if not post_match:
            return

        footer = soup.find('footer', class_=re.compile(r'site-footer', re.I))
        if not footer:
            return

        year, month, slug = post_match.groups()
        md_href = f'/markdown/{year}/{month}/{slug}/index.md'
        api_href = '/api/posts-page-1.json'

        formats_div = soup.new_tag('div')
        formats_div['class'] = 'content-formats'
        formats_div['style'] = 'margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--gray-mid);'

        p = soup.new_tag('p')
        p.string = 'Content also available in: '

        # rel="nofollow": these mirrors are noindex'd via X-Robots-Tag (see
        # _headers) and exist for AI ingestion, not search. nofollow stops
        # Googlebot following the link and wasting crawl budget re-fetching
        # the ~80 .md / JSON duplicates of the HTML posts.
        md_link = soup.new_tag('a', href=md_href, rel='nofollow')
        md_link.string = 'Markdown'
        p.append(md_link)

        p.append(' | ')

        api_link = soup.new_tag('a', href=api_href, rel='nofollow')
        api_link.string = 'JSON API'
        p.append(api_link)

        formats_div.append(p)
        footer.append(formats_div)
        print("   🔗 Added markdown and API links to footer")

    def fix_byline_dates(self, soup):
        """Insert a visible separator + 'Updated' label between adjacent
        published/updated time elements in entry-meta bylines.

        WordPress + Kadence renders:
            <span class="posted-on">
              <time class="entry-date published" ...>May 29, 2017</time>
              <time class="updated" ...>June 1, 2026</time>
            </span>
        Plain text: "May 29, 2017 June 1, 2026" — confusing.

        After this pass:
            <span class="posted-on">
              <time class="entry-date published" ...>May 29, 2017</time>
              <span class="byline-sep"> · </span>
              <span class="meta-label">Updated</span>
              <time class="updated" ...>June 1, 2026</time>
            </span>

        If both <time> elements render identically (same date string), the
        updated element is removed entirely so we don't show "May 29, 2017
        May 29, 2017". Idempotent — checks for an already-injected sep.
        """
        spans = soup.find_all('span', class_='posted-on')
        if not spans:
            return

        fixed = 0
        deduped = 0
        for span in spans:
            published = span.find('time', class_=lambda c: c and 'published' in c)
            updated = span.find('time', class_='updated')
            if not (published and updated):
                continue

            # Already fixed?
            if span.find('span', class_='byline-sep'):
                continue

            pub_text = published.get_text(strip=True)
            upd_text = updated.get_text(strip=True)

            if pub_text == upd_text:
                # Same rendered date → drop the updated <time> to avoid duplication
                updated.decompose()
                deduped += 1
                continue

            # Insert separator + label between the two <time> elements
            sep = soup.new_tag('span', attrs={'class': 'byline-sep'})
            sep.string = ' · '
            label = soup.new_tag('span', attrs={'class': 'meta-label byline-updated-label'})
            label.string = 'Updated '
            updated.insert_before(sep)
            updated.insert_before(label)
            fixed += 1

        if fixed or deduped:
            print(f"   🗓️  Byline dates: separated {fixed}, deduplicated {deduped}")

    def trim_card_categories(self, soup, max_categories=2):
        """Keep at most `max_categories` category links on archive / loop /
        related cards, dropping the extras AND their separators.

        Kadence renders a post's categories inside `.category-links` as
        <a> elements joined by literal " | " NavigableString text nodes:

            <a>Homelab</a> | <a>Networking</a> | <a>Unifi</a>

        A CSS `nth-of-type(n+3)` cap can hide the extra <a> elements, but a
        bare text node is not an element and cannot be hidden by CSS, so
        cards for posts with 3+ categories showed dangling "| | |" pipes.
        Fixing it in the DOM removes both the surplus links and the orphaned
        separators. Single-post pages (`.single-entry`) are untouched — they
        keep the full category list.
        """
        from bs4 import NavigableString

        cards = soup.select('.loop-entry .category-links, '
                            '.entry-list-item .category-links')
        trimmed = 0
        for links in cards:
            anchors = links.find_all('a', recursive=False)
            if len(anchors) <= max_categories:
                continue

            # Remove the surplus anchor and everything after it (later anchors
            # and the separator text nodes between them).
            node = anchors[max_categories]
            while node is not None:
                nxt = node.next_sibling
                node.extract()
                node = nxt

            # Strip any separator/whitespace text left trailing after the last
            # kept anchor (the " | " that used to sit before the removed one).
            last = links.find_all('a', recursive=False)[-1]
            node = last.next_sibling
            while node is not None:
                nxt = node.next_sibling
                if isinstance(node, NavigableString):
                    node.extract()
                node = nxt
            trimmed += 1

        if trimmed:
            print(f"   🏷️  Trimmed categories to {max_categories} on {trimmed} cards")

    def fix_table_headers(self, soup):
        """Fix table structure by converting first row to proper thead with th elements"""
        # Find all tables
        tables = soup.find_all('table')

        if not tables:
            return

        fixed_count = 0

        for table in tables:
            # Check if table already has a thead
            if table.find('thead'):
                continue

            # Find tbody
            tbody = table.find('tbody')
            if not tbody:
                continue

            # Get the first row
            first_row = tbody.find('tr')
            if not first_row:
                continue

            # Check if first row contains only td elements (potential header)
            cells = first_row.find_all(['td', 'th'])
            if not cells:
                continue

            # Only convert if all cells are td (not already th)
            all_td = all(cell.name == 'td' for cell in cells)
            if not all_td:
                continue

            # Create new thead element
            thead = soup.new_tag('thead')

            # Create new tr for the header
            header_row = soup.new_tag('tr')

            # Convert each td to th
            for cell in cells:
                th = soup.new_tag('th')
                # Copy all attributes
                for attr, value in cell.attrs.items():
                    th[attr] = value
                # Column headers — set scope so screen readers associate each
                # header with its column's cells.
                th['scope'] = 'col'
                # Copy all children (preserves inner structure)
                for child in list(cell.children):
                    th.append(child.extract())
                header_row.append(th)

            # Add the header row to thead
            thead.append(header_row)

            # Remove the first row from tbody
            first_row.decompose()

            # Insert thead before tbody in the table
            tbody.insert_before(thead)

            fixed_count += 1
            print("   📊 Converted table first row to proper header (thead with th elements)")

        if fixed_count > 0:
            print(f"   ✅ Fixed {fixed_count} table(s) with proper semantic structure")
