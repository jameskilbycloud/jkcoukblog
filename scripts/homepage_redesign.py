#!/usr/bin/env python3
"""
Homepage stats ribbon + layout redesign — extracted from
WordPressStaticGenerator (wp_to_static_generator.py), the eleventh cut out
of that god object (see scripts/site_artifacts_builder.py's docstring for
the first).

Two coupled pieces, kept in one class because inject_homepage_redesign()
calls straight into the ribbon-stats and category-fetch methods:

- Ribbon stats: posts count, total words, days since last post, deploys
  this month, and the last Lighthouse performance score — each computed in
  isolation with a '—' (or None) fallback, cached on the instance so a
  build only computes them once.
- Homepage layout: the top band (strap/filter/headline/ribbon), the
  featured-post hero pulled out of the grid, a trailing-card trim so the
  grid always ends on a full row, and the topic index built from live WP
  category counts.

Needs session/wp_url (for the WP REST calls) and output_dir (for the
Lighthouse history fallback file). WordPressStaticGenerator.process_html()
drives this via a HomepageRedesign instance (self.homepage); see that
method for where it runs. Behaviour is unchanged from the pre-extraction
version — this is a pure move, not a rewrite.
"""

import json
import time
from pathlib import Path

from bs4 import BeautifulSoup


class HomepageRedesign:
    """Computes the homepage stats ribbon and injects the homepage top
    band/hero/topic-index layout into a single page's already-parsed soup.
    Needs session/wp_url/output_dir."""

    def __init__(self, session, wp_url, output_dir):
        self.session = session
        self.wp_url = wp_url
        self.output_dir = output_dir

    def _compute_ribbon_stats(self):
        """Return the five momentum/credibility stats for the homepage ribbon.

        Keeps posts·words·days-since-last·deploys/mo·lighthouse — the signals
        worth surfacing above the fold. Each is computed in isolation and falls
        back to '—' (or None for days) rather than breaking the build. Cached on
        the instance so it only runs once per build.
        """
        if hasattr(self, '_cached_ribbon_stats'):
            return self._cached_ribbon_stats

        print("   📊 Computing homepage ribbon stats...")

        stats = {
            'posts_count': self._stat_posts_count(),
            'words_total': self._stat_words_total(),
            'days_since_last': self._stat_last_post_days(),
            'deploys_month': self._stat_deploys_this_month(),
            'lighthouse': self._stat_lighthouse_performance(),
        }
        self._cached_ribbon_stats = stats
        print(
            f"   📊 Ribbon: posts={stats['posts_count']} words={stats['words_total']} "
            f"days={stats['days_since_last']} deploys={stats['deploys_month']} "
            f"LH={stats['lighthouse']}"
        )
        return stats

    def _stat_posts_count(self):
        try:
            r = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={'per_page': 1, 'status': 'publish', '_fields': 'id'},
                timeout=15,
            )
            if r.status_code == 200:
                return r.headers.get('X-WP-Total') or '—'
        except Exception as e:
            print(f"   ⚠️  posts.count: {e}")
        return '—'

    def _stat_last_post_days(self):
        """Integer days since the most recent post, or None if unavailable.

        The ribbon renders this as '{n}d since last post'; returning the raw
        integer (vs. the '8d ago' string) lets the markup format it inline.
        """
        try:
            r = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={
                    'per_page': 1, 'orderby': 'date', 'order': 'desc',
                    'status': 'publish', '_fields': 'date_gmt',
                },
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                if data and data[0].get('date_gmt'):
                    from datetime import datetime, timezone
                    d = datetime.fromisoformat(data[0]['date_gmt'])
                    if d.tzinfo is None:
                        d = d.replace(tzinfo=timezone.utc)
                    return max(0, (datetime.now(timezone.utc) - d).days)
        except Exception as e:
            print(f"   ⚠️  last_post days: {e}")
        return None

    def _stat_words_total(self):
        """Sum of words across all published posts (paginated).

        Cached to .image_optimization_cache/words_total.json for 24 h so we
        don't refetch hundreds of post bodies on every build.
        """
        from pathlib import Path
        cache = Path('.image_optimization_cache') / 'words_total.json'
        try:
            if cache.exists():
                payload = json.loads(cache.read_text(encoding='utf-8'))
                if time.time() - payload.get('computed_at', 0) < 24 * 3600:
                    return payload.get('formatted', '—')
        except Exception as e:
            # Fall through to live compute — but say why the cache was unusable
            print(f"   ⚠️  words.total cache unreadable ({e}), recomputing")

        try:
            total = 0
            page = 1
            while True:
                r = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/posts',
                    params={
                        'per_page': 100, 'page': page, 'status': 'publish',
                        '_fields': 'content',
                    },
                    timeout=60,
                )
                if r.status_code != 200:
                    if r.status_code == 400:
                        break  # past last page
                    print(f"   ⚠️  words.total: page {page} → {r.status_code}")
                    return '—'
                data = r.json()
                if not data:
                    break
                for post in data:
                    html = (post.get('content') or {}).get('rendered', '')
                    if html:
                        text = BeautifulSoup(html, 'html.parser').get_text(separator=' ')
                        total += len(text.split())
                if len(data) < 100:
                    break
                page += 1

            formatted = self._format_word_count(total)
            try:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({
                    'computed_at': time.time(),
                    'total': total,
                    'formatted': formatted,
                }))
            except Exception as e:
                print(f"   ⚠️  words.total cache write failed ({e}) — next build recomputes")
            return formatted
        except Exception as e:
            print(f"   ⚠️  words.total: {e}")
            return '—'

    @staticmethod
    def _format_word_count(n):
        if n >= 1_000_000:
            return f'{n/1_000_000:.1f}M'
        if n >= 1_000:
            return f'{round(n/1000)}k'
        return str(n) if n > 0 else '—'

    def _stat_deploys_this_month(self):
        try:
            import subprocess
            from datetime import date
            first = date.today().replace(day=1).isoformat()
            result = subprocess.run(
                ['git', 'log', f'--since={first}', '--oneline'],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                return str(sum(1 for line in result.stdout.splitlines() if line))
        except Exception as e:
            print(f"   ⚠️  deploys.month: {e}")
        return '—'

    def _fetch_top_categories(self, limit=9):
        """Return the top categories by post count: list of (name, href, count_str).

        href is the relative permalink (with parent prefix when nested), taken
        directly from WP's `link` field — this matters for child categories
        like `vmware-cloud-on-aws` whose real archive lives at
        `/category/vmware/vmware-cloud-on-aws/`, not `/category/vmware-cloud-on-aws/`.

        Pulls live from the WP REST API, sorts by count desc, caches on the
        instance. Returns [] on failure so callers can fall back.
        """
        if hasattr(self, '_cached_top_cats'):
            return self._cached_top_cats[:limit]
        try:
            cats = []
            page = 1
            while True:
                r = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/categories',
                    params={
                        'per_page': 100, 'page': page, 'hide_empty': 'true',
                        '_fields': 'name,slug,count,link',
                    },
                    timeout=15,
                )
                if r.status_code != 200:
                    break
                data = r.json()
                if not data:
                    break
                cats.extend(data)
                if len(data) < 100:
                    break
                page += 1
            cats.sort(key=lambda c: -int(c.get('count') or 0))
            result = []
            for c in cats:
                name = c.get('name')
                link = c.get('link') or ''
                count = str(c.get('count') or 0)
                if not name or not link:
                    continue
                # Strip WP URL prefix to get a relative path the static site
                # serves. Same approach as get_all_content_urls() so we stay
                # consistent with what was actually generated on disk.
                href = link.replace(self.wp_url, '')
                if not href.startswith('/'):
                    href = '/' + href.lstrip('/')
                result.append((name, href, count))
            self._cached_top_cats = result
            return result[:limit]
        except Exception as e:
            print(f"   ⚠️  top categories: {e}")
            return []

    def _stat_lighthouse_performance(self):
        # Primary source is data/lighthouse-latest.json — the committed,
        # always-present single source of truth that generate_changelog itself
        # reads (a dict: {"performance": 94, ...}). The changelog history files
        # are only a fallback: static-output/changelog isn't populated until
        # generate_changelog runs later in the pipeline, and the public/ copy
        # is not committed (nothing under public/changelog/ is tracked), so on a
        # clean checkout it is absent and the ribbon showed '—'. Reading the
        # latest file first also avoids surfacing a stale cold-cache outlier
        # that lingered in a persisted runner workspace's history file.
        latest = Path('data') / 'lighthouse-latest.json'
        try:
            if latest.exists():
                data = json.loads(latest.read_text(encoding='utf-8'))
                perf = data.get('performance') if isinstance(data, dict) else None
                if isinstance(perf, (int, float)):
                    return f'{int(perf)}/100'
        except Exception as e:
            print(f"   ⚠️  lighthouse ({latest}): {e}")

        candidates = [
            self.output_dir / 'changelog' / 'lighthouse-history.json',
            Path('public') / 'changelog' / 'lighthouse-history.json',
        ]
        for history in candidates:
            try:
                if history.exists():
                    data = json.loads(history.read_text(encoding='utf-8'))
                    if isinstance(data, list) and data:
                        perf = data[-1].get('performance')
                        if isinstance(perf, (int, float)):
                            return f'{int(perf)}/100'
            except Exception as e:
                print(f"   ⚠️  lighthouse ({history}): {e}")
        return '—'

    def inject_homepage_redesign(self, soup, current_url):
        """Inject the homepage top band (Option B) + topic index.

        Adds, above the post grid:
          - top band: strap + filter on one row, the editorial <h1> headline,
            and a single-line stats ribbon (posts · words · days-since-last ·
            deploys/mo · lighthouse · ● live)
          - featured hero (newest post promoted out of the grid)
        And appends a topic index after the post grid.

        Skips paginated homepage pages (/page/2/, /page/3/, ...).
        """
        if current_url not in ('/', ''):
            return

        # Idempotency guard — don't double-inject if process_html runs twice
        if soup.find(class_='jkr-top'):
            return

        # Kadence renders the loop as a <ul class="kadence-posts-list ...">,
        # but use a tag-agnostic lookup in case the markup shifts.
        posts_list = soup.find(class_='kadence-posts-list')
        if not posts_list:
            print("   ⚠️  Homepage redesign: no .kadence-posts-list found — skipping")
            return

        # ── 0. featured-post hero (page-1 only) ─────────────────────────
        # Promote the newest post (first .loop-entry) into a wide hero card
        # above the grid. Removed from the grid so it doesn't double-render.
        hero = self._build_homepage_hero(soup, posts_list)

        # Hero extraction leaves the grid one short of a clean row in the
        # 3-col layout (WP serves 12 → hero takes 1 → 11 cards = 3 full
        # rows + 2 + an empty slot). Trim trailing cards down to the
        # nearest multiple of 3 so the last row is always full.
        self._trim_grid_to_columns(posts_list, columns=3)

        # ── 1. top band (Option B) ──────────────────────────────────────
        # Strap + filter share one row; the editorial headline is the page's
        # single <h1>; a one-line stats ribbon replaces the old terminal box.
        top = soup.new_tag('header', attrs={'class': 'jkr-top'})

        top_row = soup.new_tag('div', attrs={'class': 'jkr-top-row'})
        strap = soup.new_tag('span', attrs={'class': 'jkr-strap'})
        strap.string = 'VMWARE VEXPERT · HOMELAB · INFRASTRUCTURE-AS-CODE'
        top_row.append(strap)

        nav = soup.new_tag('nav', attrs={'class': 'jkr-filter', 'aria-label': 'Filter posts'})
        filter_label = soup.new_tag('span', attrs={'class': 'jkr-filter-label'})
        filter_label.string = 'FILTER'
        nav.append(filter_label)
        # "All" lands the user back on the homepage; the rest go to category archives.
        chips = (
            ('All', '/'),
            ('VMware', '/category/vmware/'),
            ('Homelab', '/category/homelab/'),
            ('Automation', '/category/automation/'),
            ('AI', '/category/artificial-intelligence/'),
        )
        for label, href in chips:
            attrs = {'href': href}
            if label == 'All':
                attrs['class'] = 'is-active'
            chip = soup.new_tag('a', attrs=attrs)
            chip.string = label
            nav.append(chip)
        top_row.append(nav)
        top.append(top_row)

        # ── 2. headline ─────────────────────────────────────────────────
        # Visible headline is the editorial line (a <p>, for design voice). The
        # page's actual <h1> is a screen-reader-only canonical title: it keeps
        # the keyword-rich heading fix_seo_issues.py wants (HOMEPAGE_TITLE)
        # without that pass overwriting the editorial copy. Exactly one <h1>.
        try:
            from config import Config
            seo_title = Config.HOMEPAGE_TITLE
        except (ImportError, AttributeError):
            seo_title = 'James Kilby — VMware, Homelab & Cloud Infrastructure Notes'
        seo_h1 = soup.new_tag('h1', attrs={'class': 'screen-reader-text jkr-sr-title'})
        seo_h1.string = seo_title
        top.append(seo_h1)

        headline = soup.new_tag('p', attrs={'class': 'jkr-headline'})
        headline.string = 'Field notes from a homelab that costs real money to run.'
        # Headline shares a row with the homepage search box, which is relocated
        # here from main[0] once it's injected (see _relocate_search_into_top).
        # The search fills the dead right-gutter beside the capped headline and
        # removes the standalone centered search island — reclaiming both the
        # vertical dead-zone under the header and the empty gutter. The wrapper
        # is emitted even before the search exists so the relocation has a slot.
        headline_row = soup.new_tag('div', attrs={'class': 'jkr-headline-row'})
        headline_row.append(headline)
        top.append(headline_row)

        # ── 3. stats ribbon (replaces the terminal box) ─────────────────
        stats = self._compute_ribbon_stats()
        ribbon = soup.new_tag(
            'div',
            attrs={'class': 'jkr-ribbon', 'role': 'status', 'aria-label': 'Blog stats'},
        )

        def _ribbon_stat(prefix, value, suffix):
            span = soup.new_tag('span')
            if prefix:
                span.append(soup.new_string(prefix))
            bold = soup.new_tag('b')
            bold.string = str(value)
            span.append(bold)
            if suffix:
                span.append(soup.new_string(suffix))
            return span

        days = stats['days_since_last']
        days_label = f'{days}d' if days is not None else '—'

        # Separators are drawn by CSS (.jkr-ribbon > span + span::before) so the
        # middot is glued to the following stat and can never orphan at a wrap
        # point — no literal '·' spans that flex-wrap onto their own line.
        ribbon.append(_ribbon_stat('', stats['posts_count'], ' posts'))
        ribbon.append(_ribbon_stat('', stats['words_total'], ' words'))
        ribbon.append(_ribbon_stat('', days_label, ' since last post'))
        ribbon.append(_ribbon_stat('', stats['deploys_month'], ' deploys/mo'))
        ribbon.append(_ribbon_stat('lighthouse ', stats['lighthouse'], ''))

        live = soup.new_tag('span', attrs={'class': 'jkr-r-live'})
        live.string = '● live'
        ribbon.append(live)
        top.append(ribbon)

        # ── 4. topic index ──────────────────────────────────────────────
        topics = soup.new_tag('section', attrs={'class': 'jkr-topics'})
        topics_head = soup.new_tag('div', attrs={'class': 'jkr-topics-head'})
        eyebrow = soup.new_tag('span', attrs={'class': 'jkr-eyebrow'})
        eyebrow.string = 'EXPLORE BY TOPIC'
        topics_h2 = soup.new_tag('h2', attrs={'class': 'jkr-topics-h2'})
        topics_h2.string = 'Browse the archive'
        topics_head.append(eyebrow)
        topics_head.append(topics_h2)
        topics.append(topics_head)

        topics_grid = soup.new_tag('div', attrs={'class': 'jkr-topics-grid'})
        # Live list from WP API uses the API's permalink directly so nested
        # categories (e.g. /category/vmware/vmware-cloud-on-aws/) resolve to
        # the right archive. The curated fallback below is used when the API
        # is unreachable — entries are pre-resolved hrefs verified against
        # the existing public/category/ tree.
        topic_list = self._fetch_top_categories(limit=9) or (
            ('VMware', '/category/vmware/', '—'),
            ('Homelab', '/category/homelab/', '—'),
            ('Automation', '/category/automation/', '—'),
            ('Artificial Intelligence', '/category/artificial-intelligence/', '—'),
            ('Ansible', '/category/ansible/', '—'),
            ('NVIDIA', '/category/nvidia/', '—'),
            ('Cloudflare', '/category/cloudflare/', '—'),
            ('Docker', '/category/docker/', '—'),
            ('Containers', '/category/containers/', '—'),
        )
        for name, href, count in topic_list:
            t = soup.new_tag('a', href=href, attrs={'class': 'jkr-topic'})
            t_name = soup.new_tag('span', attrs={'class': 'jkr-topic-name'})
            t_name.string = name
            t_count = soup.new_tag('span', attrs={'class': 'jkr-topic-count'})
            t_count.string = count
            t.append(t_name)
            t.append(t_count)
            topics_grid.append(t)
        topics.append(topics_grid)

        # ── insert ──────────────────────────────────────────────────────
        # Top band → hero sit above the post grid. Each insert_before lands the
        # node directly adjacent to posts_list, so the last one inserted ends up
        # closest to the grid: the top band first, then the hero pulled up right
        # above the post stream (and above the fold).
        posts_list.insert_before(top)
        if hero is not None:
            posts_list.insert_before(hero)
        posts_list.insert_after(topics)

        bits = ['top-band']
        if hero is not None:
            bits.append('hero')
        bits.append('topics')
        print(f"   ✨ Injected homepage redesign sections ({', '.join(bits)})")

    def _build_homepage_hero(self, soup, posts_list):
        """Promote the newest post (first .loop-entry inside posts_list) into a
        featured hero card. Returns the new <a.jkr-hero> element ready to be
        inserted before posts_list, or None if no candidate post is found.

        Side-effect: removes the source .loop-entry from posts_list so the grid
        starts at post #2.

        Drives change 3 of the Jun 2026 homepage refresh — see
        Downloads/design_handoff_homepage_refresh/PATCH-hero-and-meta.md §3.
        """
        first_entry = posts_list.find(class_='loop-entry')
        if not first_entry:
            return None

        # ── pull data from the source card ──
        title_a = first_entry.select_one('.entry-title a')
        if not title_a:
            return None
        title_text = title_a.get_text(strip=True)
        permalink = title_a.get('href', '#')

        # Featured image: reuse the WP-rendered <picture> verbatim so AVIF/WebP
        # sources, srcsets, alt text, and sizes survive untouched.
        picture = first_entry.select_one('.post-thumbnail picture')
        img = first_entry.select_one('.post-thumbnail img') if not picture else None

        # Categories: first two, in source order.
        cat_links = first_entry.select('.category-links a, .entry-taxonomies a')
        cats = []
        seen_cats = set()
        for a in cat_links:
            t = a.get_text(strip=True)
            if t and t not in seen_cats:
                seen_cats.add(t)
                cats.append(t)
            if len(cats) >= 2:
                break

        # Published date — text only (the hero never shows the modified date).
        pub_time = first_entry.select_one('time.entry-date.published') \
            or first_entry.select_one('time.published') \
            or first_entry.select_one('time.entry-date')
        pub_text = pub_time.get_text(strip=True) if pub_time else ''
        pub_datetime = pub_time.get('datetime') if pub_time else None

        # Excerpt.
        excerpt_p = first_entry.select_one('.entry-summary p, .entry-summary')
        excerpt_text = excerpt_p.get_text(strip=True) if excerpt_p else ''

        # ── build the hero element ──
        hero = soup.new_tag('a', href=permalink, attrs={'class': 'jkr-hero'})
        hero['aria-label'] = title_text

        media = soup.new_tag('div', attrs={'class': 'jkr-hero-media'})
        if picture:
            # Clone the <picture> so the original is left alone when we drop the
            # source entry. extract() detaches; we reattach into the hero.
            media.append(picture.extract())
        elif img:
            media.append(img.extract())
        else:
            media.append(soup.new_tag('div', attrs={'class': 'jkr-hero-media-fallback'}))

        badge = soup.new_tag('span', attrs={'class': 'jkr-hero-badge'})
        badge.string = 'LATEST'
        media.append(badge)
        hero.append(media)

        body = soup.new_tag('div', attrs={'class': 'jkr-hero-body'})

        if cats:
            cats_wrap = soup.new_tag('div', attrs={'class': 'jkr-hero-cats'})
            for c in cats:
                chip = soup.new_tag('span')
                chip.string = c
                cats_wrap.append(chip)
            body.append(cats_wrap)

        h_title = soup.new_tag('h2', attrs={'class': 'jkr-hero-title'})
        h_title.string = title_text
        body.append(h_title)

        if excerpt_text:
            p_excerpt = soup.new_tag('p', attrs={'class': 'jkr-hero-excerpt'})
            p_excerpt.string = excerpt_text
            body.append(p_excerpt)

        meta = soup.new_tag('div', attrs={'class': 'jkr-hero-meta'})
        if pub_text:
            date_span = soup.new_tag('time', attrs={'class': 'jkr-hero-date'})
            if pub_datetime:
                date_span['datetime'] = pub_datetime
            date_span.string = pub_text
            meta.append(date_span)
        cta = soup.new_tag('span', attrs={'class': 'jkr-hero-cta'})
        cta.string = 'Read post →'
        meta.append(cta)
        body.append(meta)

        hero.append(body)

        # Remove the source card so the grid starts at post #2. Kadence wraps
        # each article in <li class="entry-list-item"> — decomposing the
        # <article> alone leaves an empty <li> behind that the grid still
        # counts as a slot, so walk up to the nearest list-item wrapper first.
        to_remove = first_entry
        wrapper = first_entry.find_parent('li')
        if wrapper is not None and wrapper is not posts_list:
            to_remove = wrapper
        to_remove.decompose()

        return hero

    def _trim_grid_to_columns(self, posts_list, columns=3):
        """Trim trailing grid items so the card count is a multiple of `columns`.

        The post grid is a `columns`-wide CSS grid. Any orphan card on the
        last row paints as an empty slot; drop them so the layout always
        ends on a full row. No-ops when the count is already aligned.
        """
        items = posts_list.find_all('li', class_='entry-list-item', recursive=False)
        if not items:
            return
        remainder = len(items) % columns
        if remainder == 0:
            return
        for item in items[-remainder:]:
            item.decompose()
        print(f"   ✂️  Trimmed {remainder} orphan grid slot(s) to keep the {columns}-col layout balanced")
