#!/usr/bin/env python3
"""
Related-posts index + injection — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the fourteenth cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

Two-phase, build_post_index() run once per build and add_related_posts()
run once per single-post page:
- build_post_index(): bulk-fetches every published post's id/link/date/
  categories/tags/title once and stores it in self.post_index, keyed by
  relative URL. Replaces what used to be a per-post WordPress API call from
  inside add_related_posts() — after this runs, related-post scoring is a
  pure in-memory operation against integer category/tag ID sets.
- add_related_posts(): scores every other indexed post against the current
  one (3 * shared tags + 2 * shared categories — see internal_links.py for
  the sibling formula that scores real in-body links the same way), picks
  the top 3, and injects a "Related Posts" section. Falls back to the
  newest 3 posts sharing any category when nothing scores above zero.

Needs session/wp_url for the index fetch. WordPressStaticGenerator wires
this via a RelatedPosts instance (self.related_posts): generate_static_site()
calls build_post_index() once, before the parallel processing pool starts
(so worker-thread reads of self.related_posts.post_index are safe), and
process_html() calls add_related_posts() per single-post page. Behaviour is
unchanged from the pre-extraction version — this is a pure move, not a
rewrite.
"""

import json


class RelatedPosts:
    """Builds an in-memory post index once per build and injects a scored
    'Related Posts' section into single-post pages. Needs session/wp_url."""

    def __init__(self, session, wp_url):
        self.session = session
        self.wp_url = wp_url
        # Map of relative_url -> {'cats': set[int], 'tags': set[int],
        # 'date': str, 'title': str}. Populated once per build by
        # build_post_index() and consumed by add_related_posts(); writes
        # finish before the parallel processing pool starts, so reads from
        # worker threads are safe.
        self.post_index = {}

    def build_post_index(self):
        """Bulk-fetch all published posts once and store in self.post_index.

        Replaces the per-post WordPress API calls previously made from
        add_related_posts(). After this runs, related-post scoring is a pure
        in-memory operation against integer category/tag ID sets.

        Index entry shape:
            {
                'cats':  set[int],   # category term IDs
                'tags':  set[int],   # tag term IDs
                'date':  str,        # ISO 8601 published date
                'title': str,        # rendered title (may contain HTML entities)
            }

        Keyed by relative URL (`post['link']` minus `self.wp_url`), matching
        the `current_url` argument that process_html() passes to
        add_related_posts().
        """
        print("📚 Building post index for related-posts scoring...")
        index = {}
        page = 1
        while True:
            resp = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={
                    'per_page': 100,
                    'page': page,
                    'status': 'publish',
                    '_fields': 'id,link,date,categories,tags,title',
                },
            )
            if resp.status_code != 200:
                # 400 = past the last page on WP REST; anything else is a real
                # failure but should not break the rest of the build — the
                # related-posts section just won't render.
                if resp.status_code not in (400,):
                    print(f"   ⚠️  Post index fetch returned {resp.status_code} on page {page}")
                break
            try:
                posts = resp.json()
            except (json.JSONDecodeError, ValueError):
                print(f"   ⚠️  Invalid JSON on post-index page {page}")
                break
            if not posts:
                break
            for post in posts:
                relative_url = post['link'].replace(self.wp_url, '')
                index[relative_url] = {
                    'cats': set(post.get('categories') or []),
                    'tags': set(post.get('tags') or []),
                    'date': post.get('date') or '',
                    'title': (post.get('title') or {}).get('rendered', ''),
                }
            page += 1

        self.post_index = index
        total_cats = sum(len(p['cats']) for p in index.values())
        total_tags = sum(len(p['tags']) for p in index.values())
        print(f"   ✅ Indexed {len(index)} posts ({total_tags} tag refs, {total_cats} category refs)")

    def add_related_posts(self, soup, current_url):
        """Inject a 'Related Posts' section scored against self.post_index.

        Score formula:
            score = 3 * |shared_tags| + 2 * |shared_categories|
        Ties broken by recency (newer first). Top 3 selected.

        Tags are weighted higher than categories because categories are
        coarse hubs ("Homelab") while tags are specific facets ("packer",
        "vsan") — overlap on a tag is a stronger topical signal.

        Fallback when no candidate has any overlap: newest 3 posts that
        share at least one category (matches the legacy behaviour). This
        preserves the section's existence on posts whose tags/categories
        are unique enough to score zero against the rest of the corpus.
        """
        body = soup.find('body')
        if not body:
            return

        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()
        if 'single-post' not in body_class_str and 'single' not in body_classes:
            return

        # Avoid double-injection on repeat process_html passes
        for existing in soup.find_all('section', class_='related-posts-section'):
            existing.decompose()

        current_entry = self.post_index.get(current_url)
        if not current_entry:
            # Post isn't in the index — index didn't build, or this is a
            # page/archive misclassified as a single post. Skip silently.
            return

        cur_cats = current_entry['cats']
        cur_tags = current_entry['tags']
        if not cur_cats and not cur_tags:
            return

        scored = []
        for url, entry in self.post_index.items():
            if url == current_url:
                continue
            shared_tags = len(cur_tags & entry['tags'])
            shared_cats = len(cur_cats & entry['cats'])
            score = 3 * shared_tags + 2 * shared_cats
            if score > 0:
                scored.append((score, entry['date'], url, entry['title']))

        if scored:
            # Sort by score desc, then date desc (newer breaks ties). ISO 8601
            # dates sort lexicographically the same as chronologically, so a
            # single tuple sort works.
            scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
            selected = scored[:3]
        else:
            # Fallback: newest 3 sharing any category
            fallback = [
                (entry['date'], url, entry['title'])
                for url, entry in self.post_index.items()
                if url != current_url and (cur_cats & entry['cats'])
            ]
            fallback.sort(reverse=True)  # date desc
            selected = [(0, d, u, t) for d, u, t in fallback[:3]]

        if not selected:
            return

        # Styling lives in brutalist-theme.css (.related-posts-section) using
        # theme tokens — no inline light-theme styles (they were off-palette
        # blue/rounded/shadowed and only survived via global !important resets).
        related_section = soup.new_tag('section')
        related_section['class'] = 'related-posts-section'

        heading = soup.new_tag('h2')
        heading.string = '📚 Related Posts'
        related_section.append(heading)

        posts_list = soup.new_tag('ul')
        posts_list['class'] = 'related-posts-list'

        for _score, _date, rel_url, title in selected:
            li = soup.new_tag('li')
            li['class'] = 'related-posts-item'
            link = soup.new_tag('a')
            link['href'] = rel_url
            link.string = title
            li.append(link)
            posts_list.append(li)

        related_section.append(posts_list)

        entry_content = soup.find('div', class_=lambda x: x and 'entry-content' in x)
        if entry_content:
            article = entry_content.find_parent('article')
            if article:
                comments = article.find('div', id='comments')
                if comments:
                    comments.insert_after(related_section)
                else:
                    entry_content.insert_after(related_section)
                print(f"   📚 Added {len(selected)} related posts (score-based)")
