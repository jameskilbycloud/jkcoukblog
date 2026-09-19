#!/usr/bin/env python3
"""
Social media links footer — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the tenth cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

One per-page pass: appends a "Connect with me" links section after
entry-content on single posts and regular pages, sourced from
Config.SOCIAL_PROFILES (the same list feeding the JSON-LD sameAs graph).
Fully stateless — takes no constructor arguments.

WordPressStaticGenerator.process_html() drives this via a SocialLinks
instance (self.social); see that method for where it runs. Behaviour is
unchanged from the pre-extraction version — this is a pure move, not a
rewrite.
"""


class SocialLinks:
    """Appends the "Connect with me" social links section to a single
    page's already-parsed soup. Fully stateless: takes no constructor
    arguments."""

    def add_social_media_links(self, soup):
        """Add social media links (GitHub, Twitter, LinkedIn) to the bottom of each post"""

        # Only add to single post pages and regular pages
        body = soup.find('body')
        if not body:
            return

        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()

        # Add to single posts and pages (not archive/list pages)
        is_single_post = 'single-post' in body_class_str or 'single' in body_classes
        is_page = 'page-template' in body_class_str or ('page' in body_classes and 'single' not in body_class_str)

        if not (is_single_post or is_page):
            return  # Not a single post/page, skip social links

        # Find the entry-content div to add social links after it
        entry_content = soup.find('div', class_=lambda x: x and 'entry-content' in x)

        if not entry_content:
            return

        # Create social media section
        social_section = soup.new_tag('div')
        social_section['class'] = 'social-media-links'
        social_section['style'] = '''margin: 40px 0 20px 0; padding: 20px 0; border-top: 2px solid #e2e8f0; text-align: center;'''

        # Heading
        heading = soup.new_tag('p')
        heading['style'] = 'margin: 0 0 15px 0; font-size: 16px; color: #4a5568; font-weight: 500;'
        heading.string = 'Connect with me:'
        social_section.append(heading)

        # Links container
        links_container = soup.new_tag('div')
        links_container['style'] = 'display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;'

        # Social media links — Config.SOCIAL_PROFILES is the single source of
        # truth, shared with the JSON-LD sameAs graph.
        from config import Config as _social_config
        social_links = list(_social_config.SOCIAL_PROFILES)

        # Create link for each platform
        for platform in social_links:
            link = soup.new_tag('a')
            link['href'] = platform['url']
            link['target'] = '_blank'
            link['rel'] = 'noopener noreferrer'
            link['style'] = f'''display: inline-block; padding: 8px 16px;
                background: transparent; border: 1px solid {platform['color']}; border-radius: 4px;
                color: {platform['color']}; text-decoration: none; font-weight: 500; font-size: 14px;
                transition: all 0.2s; hover: background: {platform['color']}; hover: color: white;'''
            link.string = platform['name']

            links_container.append(link)

        social_section.append(links_container)

        # Insert after the entry-content
        entry_content.insert_after(social_section)

        print("   🔗 Added social media links (GitHub, Twitter, LinkedIn)")
