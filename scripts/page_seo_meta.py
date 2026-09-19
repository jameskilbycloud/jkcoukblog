#!/usr/bin/env python3
"""
Per-page SEO meta fixes — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the sixth cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

Four small, independent per-page passes: generating meta descriptions for
thin taxonomy archive pages, de-duplicating meta descriptions across
paginated archives, marking thin tag pages noindex, and the homepage-H1
structural fallback. All four take only (soup, current_url) and touch no
instance state at all — the cleanest possible extraction, no constructor
arguments needed.

WordPressStaticGenerator.process_html() drives these via a PageSeoMeta
instance (self.seo_meta); see that method for where they run. Behaviour is
unchanged from the pre-extraction version — this is a pure move, not a
rewrite.
"""

import re


class PageSeoMeta:
    """Per-page SEO meta fixes for a single page's already-parsed soup.
    Fully stateless: takes no constructor arguments."""

    def add_taxonomy_meta_description(self, soup, current_url):
        """Add meta descriptions to tag and category archive pages"""
        # Check if this is a taxonomy page (tag or category)
        if '/tag/' not in current_url and '/category/' not in current_url:
            return

        # Check if description already exists
        existing_desc = soup.find('meta', attrs={'name': 'description'})
        if existing_desc and existing_desc.get('content'):
            # Check if it's the default site description
            content = existing_desc.get('content', '')
            if 'James Kilby' in content and 'technical blog' in content:
                # This is the generic site description, replace it
                pass
            else:
                # Already has a specific description
                return

        # Extract taxonomy name from URL and title
        taxonomy_type = 'tag' if '/tag/' in current_url else 'category'

        # Try to get taxonomy name from the page title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            # Extract taxonomy name from title (e.g., "Docker Archives - James Kilby" -> "Docker")
            import re
            match = re.match(r'^(.+?)\s+Archives\s+[-|]', title)
            if not match:
                match = re.match(r'^([^-|]+)\s+[-|]', title)
            if match:
                taxonomy_name = match.group(1).strip()
            else:
                # Fallback to URL
                taxonomy_name = current_url.strip('/').split('/')[-1].replace('-', ' ').title()
        else:
            # Fallback to URL
            taxonomy_name = current_url.strip('/').split('/')[-1].replace('-', ' ').title()

        # Generate appropriate description
        if taxonomy_type == 'tag':
            description = f"Articles tagged with {taxonomy_name}. Explore technical guides, tutorials, and insights about {taxonomy_name} from James Kilby's blog."
        else:
            description = f"Browse all {taxonomy_name} articles. In-depth technical content covering {taxonomy_name} topics, best practices, and real-world solutions."

        # Update or create meta description
        if existing_desc:
            existing_desc['content'] = description
            print(f"   🏷️  Updated meta description for {taxonomy_type}: {taxonomy_name}")
        else:
            # Create new meta description
            if soup.head:
                meta_desc = soup.new_tag('meta')
                meta_desc['name'] = 'description'
                meta_desc['content'] = description
                soup.head.append(meta_desc)
                print(f"   🏷️  Added meta description for {taxonomy_type}: {taxonomy_name}")

        # Also update og:description and twitter:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            og_desc['content'] = description
        elif soup.head:
            og_desc = soup.new_tag('meta')
            og_desc['property'] = 'og:description'
            og_desc['content'] = description
            soup.head.append(og_desc)

        twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
        if twitter_desc:
            twitter_desc['content'] = description
        elif soup.head:
            twitter_desc = soup.new_tag('meta')
            twitter_desc['name'] = 'twitter:description'
            twitter_desc['content'] = description
            soup.head.append(twitter_desc)

    def fix_pagination_meta_description(self, soup, current_url):
        """Append page number to meta descriptions on paginated archive pages.

        WordPress/Rank Math outputs the same meta description for /page/2/,
        /page/3/, etc. as for the parent archive.  Duplicate descriptions
        hurt SEO, so we make each one unique by appending "- Page N".
        """
        import re
        match = re.search(r'/page/(\d+)/?$', current_url)
        if not match:
            return

        page_num = match.group(1)
        suffix = f" - Page {page_num}"

        for tag_spec in [
            {'attrs': {'name': 'description'}},
            {'attrs': {'property': 'og:description'}},
            {'attrs': {'name': 'twitter:description'}},
        ]:
            tag = soup.find('meta', **tag_spec)
            if tag and tag.get('content'):
                content = tag['content'].rstrip('.')
                # Truncate if adding suffix would exceed 160 chars
                max_len = 160 - len(suffix)
                if len(content) > max_len:
                    content = content[:max_len - 3].rstrip() + '...'
                tag['content'] = content + suffix
                print(f"   📄 Deduplicated meta description for page {page_num}")

    def add_noindex_to_thin_pages(self, soup, current_url):
        """Add noindex, follow to tag archive pages only.

        Tag pages are thin listing pages (auto-generated by WordPress taxonomy)
        that Google will not index meaningfully. Marking them noindex:
          - Saves crawl budget for real content pages
          - Prevents quality dilution from duplicate/thin pages

        Category pages are intentionally excluded from this treatment because
        they serve as navigable topic hubs and should be indexed by Google.
        """
        # Only tag pages are considered thin; category pages are indexable hubs
        thin_patterns = ('/tag/',)
        is_thin = any(p in current_url for p in thin_patterns)
        if not is_thin:
            return

        if not soup.head:
            return

        # Skip if noindex already present
        existing = soup.find('meta', attrs={'name': 'robots'})
        if existing:
            content = existing.get('content', '').lower()
            if 'noindex' in content:
                return
            # Existing robots tag present but no noindex — update it
            existing['content'] = 'noindex, follow'
            print(f"   🚫 Updated robots meta → noindex, follow: {current_url}")
            return

        # Insert as the first element inside <head>
        robots_meta = soup.new_tag('meta')
        robots_meta['name'] = 'robots'
        robots_meta['content'] = 'noindex, follow'
        soup.head.insert(0, robots_meta)
        print(f"   🚫 Added noindex, follow: {current_url}")

    def ensure_homepage_h1(self, soup, current_url):
        """Fix missing H1 tag on homepage by converting site title to H1"""
        # Only apply to homepage
        if current_url not in ['/', '']:
            return

        # Check if H1 already exists
        if soup.find('h1'):
            print("   ℹ️  H1 already exists on homepage")
            return

        # Find site-title elements (both desktop and mobile versions)
        site_titles = soup.find_all(class_='site-title')

        if not site_titles:
            print("   ⚠️  Could not find site-title element on homepage")
            return

        # Convert each site-title to H1
        for title_elem in site_titles:
            # Get the current tag name (p, div, etc.)
            old_tag_name = title_elem.name

            # Create new H1 tag with same attributes and content
            h1_tag = soup.new_tag('h1')

            # Copy all attributes except class (we'll reconstruct it)
            for attr, value in title_elem.attrs.items():
                if attr == 'class':
                    # Keep site-title class but ensure h1 semantics
                    h1_tag['class'] = value
                else:
                    h1_tag[attr] = value

            # Copy all children (preserves inner structure)
            for child in title_elem.children:
                h1_tag.append(child)

            # Replace old tag with H1
            title_elem.replace_with(h1_tag)

            print(f"   ✅ Converted {old_tag_name}.site-title to H1 on homepage")
