#!/usr/bin/env python3
"""
Breadcrumb navigation + BreadcrumbList schema — extracted from
WordPressStaticGenerator (wp_to_static_generator.py), the ninth cut out of
that god object (see scripts/site_artifacts_builder.py's docstring for the
first).

One per-page pass: builds a breadcrumb trail (category archive, tag
archive, single post, or generic page) and injects both the visible <nav>
markup and — when the page doesn't already carry one in an existing
@graph — the matching BreadcrumbList JSON-LD. Only needs target_domain.

WordPressStaticGenerator.process_html() drives this via a
BreadcrumbNavigation instance (self.breadcrumbs); see that method for
where it runs. Behaviour is unchanged from the pre-extraction version —
this is a pure move, not a rewrite.
"""

import json


class BreadcrumbNavigation:
    """Breadcrumb trail + BreadcrumbList schema for a single page's
    already-parsed soup. Only needs target_domain."""

    def __init__(self, target_domain):
        self.target_domain = target_domain

    def add_breadcrumb_navigation(self, soup, current_url):
        """Add breadcrumb navigation with schema markup for better site hierarchy and SEO"""

        # Only add breadcrumbs to non-homepage pages
        if current_url == '/' or current_url == '':
            return

        # Check if this is a single post or page
        body = soup.find('body')
        if not body:
            return

        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()

        # Parse URL to build breadcrumb path
        url_parts = [p for p in current_url.strip('/').split('/') if p]

        if not url_parts:
            return

        # Build breadcrumb items
        breadcrumb_items = [{
            'name': 'Home',
            'url': self.target_domain,
            'position': 1
        }]

        cumulative_path = ''
        position = 2

        # Determine breadcrumb structure based on URL pattern
        if 'category' in url_parts:
            # Category archive: Home > Category Name
            category_index = url_parts.index('category')
            if category_index + 1 < len(url_parts):
                category_slug = url_parts[category_index + 1]
                category_name = category_slug.replace('-', ' ').title()
                breadcrumb_items.append({
                    'name': category_name,
                    'url': f"{self.target_domain}/category/{category_slug}/",
                    'position': position
                })

        elif 'tag' in url_parts:
            # Tag archive: Home > Tags > Tag Name
            breadcrumb_items.append({
                'name': 'Tags',
                'url': f"{self.target_domain}/tag/",
                'position': position
            })
            position += 1
            tag_index = url_parts.index('tag')
            if tag_index + 1 < len(url_parts):
                tag_slug = url_parts[tag_index + 1]
                tag_name = tag_slug.replace('-', ' ').title()
                breadcrumb_items.append({
                    'name': tag_name,
                    'url': f"{self.target_domain}/tag/{tag_slug}/",
                    'position': position
                })

        elif len(url_parts) >= 3 and url_parts[0].isdigit():
            # Single post: Home > Category > Post Title
            # Extract category from page if available
            categories = soup.find_all('a', rel='tag', href=lambda x: x and '/category/' in x)
            if categories:
                # Use first category
                first_category = categories[0]
                category_url = first_category.get('href', '')
                category_name = first_category.get_text(strip=True)

                breadcrumb_items.append({
                    'name': category_name,
                    'url': category_url if category_url.startswith('http') else f"{self.target_domain}{category_url}",
                    'position': position
                })
                position += 1

            # Add current page (extract title from h1)
            h1 = soup.find('h1', class_=lambda x: x and 'entry-title' in x)
            if h1:
                page_title = h1.get_text(strip=True)
                breadcrumb_items.append({
                    'name': page_title,
                    'url': f"{self.target_domain}{current_url}",
                    'position': position
                })

        else:
            # Generic page: Home > Page Title
            h1 = soup.find('h1')
            if h1:
                page_title = h1.get_text(strip=True)
                breadcrumb_items.append({
                    'name': page_title,
                    'url': f"{self.target_domain}{current_url}",
                    'position': position
                })

        # Only proceed if we have more than just Home
        if len(breadcrumb_items) <= 1:
            return

        # Create breadcrumb HTML
        breadcrumb_nav = soup.new_tag('nav')
        breadcrumb_nav['class'] = 'breadcrumb-navigation site-container'
        breadcrumb_nav['aria-label'] = 'Breadcrumb'

        breadcrumb_ol = soup.new_tag('ol')
        breadcrumb_ol['class'] = 'breadcrumb-list'

        for i, item in enumerate(breadcrumb_items):
            li = soup.new_tag('li')
            li['style'] = 'display: inline-flex; align-items: center;'

            # Add separator for non-first items
            if i > 0:
                separator = soup.new_tag('span')
                separator['class'] = 'breadcrumb-separator'
                separator.string = '/'
                li.append(separator)

            # Last item is current page (no link)
            if i == len(breadcrumb_items) - 1:
                current_span = soup.new_tag('span')
                current_span['class'] = 'breadcrumb-current'
                current_span['aria-current'] = 'page'
                current_span.string = item['name']
                li.append(current_span)
            else:
                link = soup.new_tag('a')
                link['href'] = item['url']
                link['class'] = 'breadcrumb-link'
                link.string = item['name']
                li.append(link)

            breadcrumb_ol.append(li)

        breadcrumb_nav.append(breadcrumb_ol)

        # Find insertion point (after header, before main content)
        main_wrap = soup.find('main', id='inner-wrap')
        if main_wrap:
            # Insert at the beginning of main
            first_child = main_wrap.find()
            if first_child:
                first_child.insert_before(breadcrumb_nav)
            else:
                main_wrap.insert(0, breadcrumb_nav)

            # Add BreadcrumbList JSON-LD schema — but only if the page
            # doesn't already have one in an existing @graph block. Rank
            # Math emits its own BreadcrumbList inside the main @graph on
            # most posts; emitting a second standalone copy here triggers
            # "Breadcrumbs item not specified" warnings in Search Console
            # and dilutes the rich-result signal.
            if soup.head and not self._has_existing_breadcrumblist(soup):
                schema_script = soup.new_tag('script')
                schema_script['type'] = 'application/ld+json'

                breadcrumb_list = {
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": item['position'],
                            "name": item['name'],
                            "item": item['url']
                        }
                        for item in breadcrumb_items
                    ]
                }

                schema_script.string = json.dumps(breadcrumb_list, ensure_ascii=False, separators=(',', ':'))
                soup.head.append(schema_script)

                print(f"   🍞 Added breadcrumb navigation: {' > '.join([item['name'] for item in breadcrumb_items])}")
            else:
                print(f"   🍞 Added breadcrumb nav (HTML only — existing BreadcrumbList in @graph): {' > '.join([item['name'] for item in breadcrumb_items])}")

    @staticmethod
    def _has_existing_breadcrumblist(soup):
        """Return True if any JSON-LD block on the page already declares a
        BreadcrumbList (standalone or inside an @graph).
        """
        for script in soup.find_all('script', type='application/ld+json'):
            raw = script.string or ''
            if not raw.strip():
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                if data.get('@type') == 'BreadcrumbList':
                    return True
                graph = data.get('@graph')
                if isinstance(graph, list) and any(
                    isinstance(n, dict) and n.get('@type') == 'BreadcrumbList'
                    for n in graph
                ):
                    return True
        return False
