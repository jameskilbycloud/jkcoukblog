#!/usr/bin/env python3
"""
WordPress artifact cleanup and embed conversion — extracted from
WordPressStaticGenerator (wp_to_static_generator.py), the fourth cut out of
that god object (see scripts/site_artifacts_builder.py's docstring for the
first).

Two related per-page jobs on the same already-parsed soup: stripping
WordPress-specific cruft that has no place in a static site (admin bar,
wp-embed script, generator meta tag, RSD/wlwmanifest links, Rank Math HTML
comments, the Kadence theme footer credit, the wp-emoji loader), and
converting WordPress embed blocks (Acast, YouTube, Vimeo, Twitter, generic)
into plain iframes. Only clean_wordpress_ajax_urls needs wp_url — everything
else here only touches the soup it's handed.

WordPressStaticGenerator.process_html() drives these via a WordPressCleanup
instance (self.wp_cleanup); see that method for the call order. Behaviour
is unchanged from the pre-extraction version — this is a pure move, not a
rewrite.
"""

import re


class WordPressCleanup:
    """Strip WordPress-specific artifacts and convert embed blocks to plain
    iframes. Only clean_wordpress_ajax_urls needs wp_url; the rest is
    stateless."""

    def __init__(self, wp_url):
        self.wp_url = wp_url

    def remove_wordpress_elements(self, soup):
        """Remove WordPress-specific dynamic elements and artifacts"""
        # Remove admin bar
        for element in soup.find_all(id='wpadminbar'):
            element.decompose()

        # Remove wp-embed scripts
        for script in soup.find_all('script'):
            if script.get('src') and 'wp-embed' in script.get('src'):
                script.decompose()

        # Remove WordPress generator meta tag
        for meta in soup.find_all('meta', attrs={'name': 'generator'}):
            if 'wordpress' in meta.get('content', '').lower():
                meta.decompose()

        # Remove WordPress REST API links
        for link in soup.find_all('link', rel='https://api.w.org/'):
            link.decompose()

        # Remove xmlrpc.php RSD (Really Simple Discovery) links
        for link in soup.find_all('link', rel='EditURI'):
            if link.get('href') and 'xmlrpc.php' in link.get('href'):
                link.decompose()
                print("   🗑️  Removed xmlrpc.php RSD link")

        # Remove Windows Live Writer manifest links
        for link in soup.find_all('link', rel='wlwmanifest'):
            link.decompose()
            print("   🗑️  Removed wlwmanifest link")

        # Remove Rank Math HTML comments
        import re
        comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!-- Search Engine Optimization by Rank Math' in text)
        for comment in comments:
            comment.extract()

        # Also remove the closing Rank Math comment
        comments = soup.find_all(string=lambda text: isinstance(text, str) and '/Rank Math WordPress SEO plugin' in text)
        for comment in comments:
            comment.extract()
            print("   🗑️  Removed Rank Math HTML comments")

        # Remove Kadence WP footer credit/links
        for link in soup.find_all('a', href=lambda x: x and 'kadencewp.com' in x):
            # Remove the parent paragraph or just the link
            parent = link.parent
            if parent and parent.name == 'p' and 'WordPress Theme by' in parent.get_text():
                parent.decompose()
                print("   🗑️  Removed Kadence WP footer credit")
            else:
                link.decompose()

        # Remove the wp-emoji loader. WordPress inlines an emoji-detection script
        # that spins up a Web Worker from a blob: URL to test emoji rendering.
        # The site CSP has no worker-src, so worker creation falls back to
        # default-src 'self' and the blob worker is blocked — throwing a console
        # error on every page (a Lighthouse Best-Practices ding). The polyfill is
        # dead weight on a static site (modern browsers render emoji natively), so
        # strip the settings JSON, the inline loader, and its <style>.
        removed_emoji = 0
        for script in soup.find_all('script'):
            sid = script.get('id') or ''
            body = script.string or ''
            if sid.startswith('wp-emoji') or '_wpemojiSettings' in body \
                    or 'wpEmojiSettingsSupports' in body:
                script.decompose()
                removed_emoji += 1
        for style in soup.find_all('style'):
            if 'img.wp-smiley' in (style.string or ''):
                style.decompose()
                removed_emoji += 1
        if removed_emoji:
            print(f"   🗑️  Removed wp-emoji loader ({removed_emoji} node(s))")

    def process_wordpress_embeds(self, soup):
        """Convert WordPress embed blocks to proper iframe embeds"""
        # Handle wp-block-embed elements
        embed_blocks = soup.find_all('figure', class_=lambda x: x and 'wp-block-embed' in x)

        for embed_block in embed_blocks:
            embed_wrapper = embed_block.find('div', class_='wp-block-embed__wrapper')
            if not embed_wrapper:
                continue

            # Get the URL from the wrapper
            url_text = embed_wrapper.get_text(strip=True)
            if not url_text.startswith('http'):
                continue

            embed_url = url_text.strip()
            print(f"   🎬 Processing embed URL: {embed_url}")

            # Handle different embed providers
            if 'acast.com' in embed_url:
                iframe = self.create_acast_embed(embed_url, soup)
            elif 'youtube.com' in embed_url or 'youtu.be' in embed_url:
                iframe = self.create_youtube_embed(embed_url, soup)
            elif 'vimeo.com' in embed_url:
                iframe = self.create_vimeo_embed(embed_url, soup)
            elif 'twitter.com' in embed_url:
                iframe = self.create_twitter_embed(embed_url, soup)
            else:
                # Generic iframe embed
                iframe = self.create_generic_embed(embed_url, soup)

            if iframe:
                # Replace the embed wrapper with the iframe
                embed_wrapper.clear()
                embed_wrapper.append(iframe)
                print(f"   ✅ Converted embed to iframe: {embed_url}")
            else:
                print(f"   ⚠️  Could not convert embed: {embed_url}")

    def create_acast_embed(self, url, soup):
        """Create an iframe for Acast podcast embeds"""
        # Extract episode ID from Acast URL
        import re

        # Pattern: https://shows.acast.com/show-name/episodes/episode-name
        if '/episodes/' in url:
            try:
                # Convert to embeddable URL
                embed_url = url.replace('shows.acast.com', 'embed.acast.com')

                iframe = soup.new_tag('iframe')
                iframe['src'] = embed_url
                iframe['width'] = '100%'
                iframe['height'] = '190'
                iframe['frameborder'] = '0'
                iframe['scrolling'] = 'no'
                iframe['style'] = 'border: none;'
                iframe['loading'] = 'lazy'

                return iframe
            except Exception as e:
                print(f"   ⚠️  Error creating Acast embed: {e}")
                return None
        return None

    def create_youtube_embed(self, url, soup):
        """Create an iframe for YouTube embeds"""
        import re

        # Extract video ID from various YouTube URL formats
        video_id = None
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/watch?v=' in url:
            video_id = url.split('v=')[1].split('&')[0]
        elif 'youtube.com/embed/' in url:
            video_id = url.split('/embed/')[1].split('?')[0]

        if video_id:
            iframe = soup.new_tag('iframe')
            iframe['src'] = f'https://www.youtube.com/embed/{video_id}'
            iframe['width'] = '560'
            iframe['height'] = '315'
            iframe['frameborder'] = '0'
            iframe['allowfullscreen'] = ''
            iframe['loading'] = 'lazy'

            return iframe
        return None

    def create_vimeo_embed(self, url, soup):
        """Create an iframe for Vimeo embeds"""
        import re

        # Extract video ID from Vimeo URL
        video_match = re.search(r'vimeo\.com/(\d+)', url)
        if video_match:
            video_id = video_match.group(1)

            iframe = soup.new_tag('iframe')
            iframe['src'] = f'https://player.vimeo.com/video/{video_id}'
            iframe['width'] = '640'
            iframe['height'] = '360'
            iframe['frameborder'] = '0'
            iframe['allowfullscreen'] = ''
            iframe['loading'] = 'lazy'

            return iframe
        return None

    def create_twitter_embed(self, url, soup):
        """Create a Twitter embed (simplified)"""
        # For Twitter, we'll create a simple link since Twitter embeds require JS
        link = soup.new_tag('a')
        link['href'] = url
        link['target'] = '_blank'
        link['rel'] = 'noopener noreferrer'
        link.string = f'View Tweet: {url}'

        return link

    def create_generic_embed(self, url, soup):
        """Create a generic iframe embed"""
        iframe = soup.new_tag('iframe')
        iframe['src'] = url
        iframe['width'] = '100%'
        iframe['height'] = '400'
        iframe['frameborder'] = '0'
        iframe['loading'] = 'lazy'

        return iframe

    def clean_wordpress_ajax_urls(self, soup):
        """Clean up WordPress admin AJAX URLs that won't work in static site"""
        # Find all script tags with WordPress admin AJAX URLs
        for script in soup.find_all('script'):
            if script.string:
                script_content = script.string
                # Replace WordPress admin AJAX URLs
                if 'wp-admin/admin-ajax.php' in script_content:
                    # Comment out or remove the AJAX URL since it won't work in static site
                    wp_domain = self.wp_url.replace('https://', '').replace('http://', '')
                    updated_content = script_content.replace(
                        f'"ajaxurl":"https:\\/\\/{wp_domain}\\/wp-admin\\/admin-ajax.php"',
                        '"ajaxurl":"#" /* Static site - AJAX disabled */'
                    )
                    if updated_content != script_content:
                        script.string = updated_content
                        print("   🧹 Cleaned WordPress AJAX URL in script")
