#!/usr/bin/env python3
"""
WordPress REST API content/media discovery — extracted from
WordPressStaticGenerator (wp_to_static_generator.py), the twelfth cut out
of that god object (see scripts/site_artifacts_builder.py's docstring for
the first).

Runs once per build, before any page processing starts:
- get_all_content_urls(): discovers every URL to generate (posts, pages,
  categories/tags with posts, homepage and category/tag archive
  pagination), in either incremental
  mode (only changed posts/pages, via incremental_builder) or full-build
  mode (walks every WP REST endpoint).
- get_all_media_assets(): discovers every media-library URL (including size
  variants) and folds them into the shared downloaded_assets set so
  download_assets() (scripts/asset_pipeline.py) knows about media-library
  files even though extract_assets() only sees assets actually referenced
  in rendered HTML.
- _paginate_taxonomy(): shared pagination helper for categories/tags, used
  by both content discovery and (indirectly, via _fetch_top_categories) the
  homepage redesign's topic index.

Needs session/wp_url, the shared incremental_builder (or None for a full
build), and the same downloaded_assets set the asset-download pipeline
owns, so a write here is visible there.

WordPressStaticGenerator.generate_static_site() drives this via a
WPContentDiscovery instance (self.discovery); see that method for where it
runs. Behaviour is unchanged from the pre-extraction version — this is a
pure move, not a rewrite.
"""

import json


class WPContentDiscovery:
    """WordPress REST API content-URL and media-asset discovery, run once
    per build. Needs session/wp_url/incremental_builder/downloaded_assets."""

    def __init__(self, session, wp_url, incremental_builder, downloaded_assets):
        self.session = session
        self.wp_url = wp_url
        self.incremental_builder = incremental_builder
        self.downloaded_assets = downloaded_assets

    def _paginate_taxonomy(self, endpoint: str, kind: str) -> list:
        """Fetch every item from a WP taxonomy endpoint (tags, categories, ...).

        WP REST caps per_page at 100 and does NOT auto-paginate. Historically
        this code used per_page=100 with no page loop, silently dropping any
        taxonomy term past position 100. On jameskilby.co.uk WordPress there
        are more than 100 tags; the alphabetical tail (self-hosted, ubuntu,
        vmware, vsphere, zoom, …) was invisible to the generator, producing
        GSC 404s for /tag/vmware/ etc. that posts still linked to.

        Returns an empty list on any error.
        """
        items = []
        page = 1
        while True:
            resp = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/{endpoint}',
                params={'per_page': 100, 'page': page},
            )
            if resp.status_code == 400 and page > 1:
                # WP returns 400 with rest_post_invalid_page_number past the end
                break
            if resp.status_code != 200:
                print(f"   ⚠️  {kind} API returned status {resp.status_code} on page {page}")
                if page == 1:
                    return []
                break
            try:
                batch = resp.json()
            except (json.JSONDecodeError, ValueError):
                print(f"   ⚠️  Invalid JSON on {kind} page {page}, stopping")
                break
            if not isinstance(batch, list) or not batch:
                break
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

    def _probe_pagination(self, base_path: str) -> list:
        """Return the /page/N/ URLs WordPress actually serves under base_path.

        HEADs {base_path}page/2/, page/3/, ... until the first non-200.
        base_path is '/' for the homepage or a taxonomy archive such as
        '/category/homelab/'. Returns relative URLs, page 2 first.
        """
        found = []
        n = 2
        while True:
            pagination_url = f'{base_path}page/{n}/'
            try:
                resp = self.session.head(f'{self.wp_url}{pagination_url}',
                                         timeout=15, allow_redirects=False)
            except Exception as e:
                print(f"   ⚠️  Pagination discovery stopped at {pagination_url}: {e}")
                break
            if resp.status_code != 200:
                break
            found.append(pagination_url)
            n += 1
        return found

    def _discover_taxonomy_pagination(self, terms: list) -> list:
        """Return /category/<slug>/page/N/ and /tag/<slug>/page/N/ URLs.

        The archive pages render "page 2 / page 3" links and rel="next" for
        any term with more posts than WP's posts_per_page, so those pages
        must be generated too (they 404'd on the live site before this).
        Terms are probed in descending post count; whether page 2 exists
        depends only on the count, so once one term has no page 2 every
        smaller term is skipped. That keeps it to a handful of HEADs rather
        than one per tag.
        """
        urls = []
        for term in sorted(terms, key=lambda t: t.get('count', 0), reverse=True):
            if term.get('count', 0) <= 0:
                break
            base_path = term['link'].replace(self.wp_url, '')
            pages = self._probe_pagination(base_path)
            if not pages:
                break
            urls.extend(pages)
            print(f"   📄 Archive pages: {base_path} (+{len(pages)})")
        return urls

    def get_all_content_urls(self):
        """Get all content URLs from WordPress REST API"""
        urls = set()

        # Check if we should do incremental build
        if self.incremental_builder:
            print("📋 Discovering content (incremental mode)...")
            changed_posts = self.incremental_builder.get_changed_posts(self.session, self.wp_url)
            changed_pages = self.incremental_builder.get_changed_pages(self.session, self.wp_url)

            # Add changed post/page URLs
            for post in changed_posts:
                relative_url = post['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📄 Changed post: {post['title']['rendered']}")

            for page in changed_pages:
                relative_url = page['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📑 Changed page: {page['title']['rendered']}")

            # Check if we need to rebuild archives
            if changed_posts or changed_pages or self.incremental_builder.should_rebuild_archives():
                print("   🔄 Rebuilding archive pages...")
                # Add essential pages and archives. Per-category/per-tag URLs
                # are added below from the taxonomy listing; the bare
                # `/category/` and `/tag/` paths used to be in here too but
                # WordPress 404s them (they're not real pages, just taxonomy
                # roots), producing two failures per build that obscured
                # real errors.
                urls.add('/')

                # Get all categories and tags (archives need full list)
                categories = self._paginate_taxonomy('categories', 'Categories')
                for category in categories:
                    if category.get('count', 0) > 0:
                        relative_url = category['link'].replace(self.wp_url, '')
                        urls.add(relative_url)
                        print(f"   📁 Category: {category['name']}")

                tags = self._paginate_taxonomy('tags', 'Tags')
                for tag in tags:
                    if tag.get('count', 0) > 0:
                        relative_url = tag['link'].replace(self.wp_url, '')
                        urls.add(relative_url)
                        print(f"   🏷️  Tag: {tag['name']}")

                # Archive pagination: homepage (/page/N/) plus category/tag
                # archives (/category/<slug>/page/N/, /tag/<slug>/page/N/)
                for pagination_url in self._probe_pagination('/'):
                    urls.add(pagination_url)
                    print(f"   📄 Homepage page: {pagination_url}")
                urls.update(self._discover_taxonomy_pagination(categories))
                urls.update(self._discover_taxonomy_pagination(tags))

            print(f"\n✅ Incremental build: {len(urls)} URLs to process")
            return sorted(list(urls))

        # Full build mode
        print("📋 Discovering content from WordPress REST API...")

        # Get posts with pagination
        page = 1
        post_count = 0
        while True:
            print(f"   🔍 Fetching posts page {page}...")
            posts_response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={'per_page': 100, 'page': page, 'status': 'publish'}
            )

            if posts_response.status_code != 200:
                print(f"   ⚠️  Posts API returned status {posts_response.status_code} on page {page}")
                if posts_response.status_code == 400:
                    # Reached end of pagination
                    print(f"   ℹ️  Reached end of posts (page {page})")
                elif posts_response.status_code == 401:
                    print("   ❌ Authentication failed - check WP_AUTH_TOKEN")
                else:
                    print(f"   ❌ Error: {posts_response.text[:200]}")
                break

            try:
                posts = posts_response.json()
            except (json.JSONDecodeError, ValueError):
                print(f"   ⚠️  Invalid JSON on post page {page}, stopping")
                break
            if not posts:
                print(f"   ℹ️  No more posts on page {page}")
                break

            for post in posts:
                # Convert WordPress URL to relative path
                relative_url = post['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                post_count += 1
                print(f"   📄 Post: {post['title']['rendered']}")

            page += 1

        print(f"   ✅ Discovered {post_count} posts from REST API")

        # Get pages
        page = 1
        while True:
            pages_response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/pages',
                params={'per_page': 100, 'page': page, 'status': 'publish'}
            )
            if pages_response.status_code != 200:
                break

            try:
                pages = pages_response.json()
            except (json.JSONDecodeError, ValueError):
                break
            if not pages:
                break

            for page_item in pages:
                relative_url = page_item['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📑 Page: {page_item['title']['rendered']}")

            page += 1

        # Get categories
        categories = self._paginate_taxonomy('categories', 'Categories')
        for category in categories:
            if category.get('count', 0) > 0:  # Only categories with posts
                relative_url = category['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📁 Category: {category['name']}")

        # Get tags with posts (paginated — see _paginate_taxonomy for the
        # per_page=100 bug this fixes).
        tags = self._paginate_taxonomy('tags', 'Tags')
        for tag in tags:
            if tag.get('count', 0) > 0:
                relative_url = tag['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   🏷️  Tag: {tag['name']}")

        # Add essential pages. `/category/` and `/tag/` used to be in here
        # too but WordPress 404s those bare taxonomy roots (only the
        # individual `/category/<slug>/` and `/tag/<slug>/` URLs are real),
        # producing two ❌ Failed entries on every build that masked real
        # download errors.
        urls.add('/')

        # Discover homepage pagination pages (/page/2/, /page/3/, etc.)
        print("   🔍 Discovering homepage pagination pages...")
        home_pages = self._probe_pagination('/')
        for pagination_url in home_pages:
            urls.add(pagination_url)
            print(f"   📄 Homepage page: {pagination_url}")
        if home_pages:
            print(f"   ✅ Found {len(home_pages)} homepage pagination pages")

        # Category/tag archive pagination — linked via rel="next" from the
        # first archive page, so it must exist in the static build.
        print("   🔍 Discovering category/tag archive pagination...")
        archive_pages = (self._discover_taxonomy_pagination(categories)
                         + self._discover_taxonomy_pagination(tags))
        urls.update(archive_pages)
        if archive_pages:
            print(f"   ✅ Found {len(archive_pages)} category/tag pagination pages")

        print(f"\n✅ Total URLs to process: {len(urls)}")
        return sorted(list(urls))

    def get_all_media_assets(self):
        """Get all media assets from WordPress Media API"""
        print("🖼️  Discovering media assets from WordPress Media API...")
        media_assets = set()

        page = 1
        while True:
            media_response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/media',
                params={'per_page': 100, 'page': page}
            )
            if media_response.status_code != 200:
                break

            try:
                media_items = media_response.json()
            except (json.JSONDecodeError, ValueError):
                break
            if not media_items:
                break

            for media_item in media_items:
                # Get the main media URL
                if 'source_url' in media_item:
                    media_assets.add(media_item['source_url'])

                # Get different size variants if available
                if 'media_details' in media_item and 'sizes' in media_item['media_details']:
                    sizes = media_item['media_details']['sizes']
                    for size_name, size_data in sizes.items():
                        if 'source_url' in size_data:
                            media_assets.add(size_data['source_url'])

                print(f"   🖼️  Media: {media_item.get('title', {}).get('rendered', 'Untitled')}")

            page += 1

        # Add media assets to downloaded_assets set
        self.downloaded_assets.update(media_assets)
        print(f"✅ Found {len(media_assets)} media assets")
        return media_assets
