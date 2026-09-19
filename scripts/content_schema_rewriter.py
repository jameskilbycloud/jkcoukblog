#!/usr/bin/env python3
"""
Content schema and URL rewriting — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the second cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

Everything here runs once per page, inside process_html(), and does two
related jobs on the same already-parsed soup: rewriting WordPress URLs to
the target domain (in tag attributes, meta tags, and JSON-LD), and
enriching/injecting schema.org JSON-LD (BlogPosting reading-time/word-count,
FAQPage, WebSite/Organization). Both only ever read self.wp_url/
self.target_domain — no session, no per-page state shared with any other
group — which is what made this the next cleanest cut after the post-build
artifacts group.

WordPressStaticGenerator.process_html() drives these via a
ContentSchemaRewriter instance (self.schema); see that method for the call
order. Behaviour is unchanged from the pre-extraction version — this is a
pure move, not a rewrite.
"""

import json
import re


class ContentSchemaRewriter:
    """URL rewriting (tag attrs, meta tags, JSON-LD) and schema.org JSON-LD
    enrichment for a single page's already-parsed soup. Stateless beyond
    wp_url/target_domain."""

    def __init__(self, wp_url, target_domain):
        self.wp_url = wp_url
        self.target_domain = target_domain

    def replace_urls_in_soup(self, soup):
        """Replace WordPress URLs with target domain URLs"""
        url_attributes = {
            'a': ['href'],
            'link': ['href'],
            'img': ['src', 'srcset'],
            'script': ['src'],
            'source': ['src', 'srcset'],
            'iframe': ['src'],
            'form': ['action']
        }

        for tag_name, attributes in url_attributes.items():
            for tag in soup.find_all(tag_name):
                for attr in attributes:
                    if tag.get(attr):
                        original_url = tag[attr]

                        # Handle srcset specially (multiple URLs)
                        if attr == 'srcset':
                            new_srcset = []
                            for srcset_item in original_url.split(','):
                                item = srcset_item.strip()
                                if item:
                                    parts = item.split(' ')
                                    if parts[0].startswith(self.wp_url):
                                        parts[0] = parts[0].replace(self.wp_url, self.target_domain)
                                    new_srcset.append(' '.join(parts))
                            tag[attr] = ', '.join(new_srcset)
                        else:
                            # Regular URL replacement
                            if original_url.startswith(self.wp_url):
                                tag[attr] = original_url.replace(self.wp_url, self.target_domain)
                            elif original_url.startswith('/') and not original_url.startswith('//'):
                                # Relative URLs - keep them relative (don't make absolute)
                                pass  # Leave relative URLs as-is

        # Fix meta tags (Open Graph, Twitter Cards, canonical, etc.)
        self.fix_meta_tag_urls(soup)

        # Fix JSON-LD structured data
        self.fix_jsonld_urls(soup)

    def fix_meta_tag_urls(self, soup):
        """Fix URLs in meta tags (Open Graph, Twitter Cards, canonical)"""
        # Fix meta tags with property attribute (Open Graph)
        for meta in soup.find_all('meta', property=True):
            prop = meta.get('property', '')
            content = meta.get('content', '')

            if content:
                # Convert relative URLs to absolute (for og:image, og:url, etc.)
                if content.startswith('/'):
                    meta['content'] = f"{self.target_domain}{content}"
                    print(f"   🔧 Made {prop} absolute: {content} -> {self.target_domain}{content}")
                # Replace WordPress URLs in og:url, og:image, etc.
                elif self.wp_url in content:
                    meta['content'] = content.replace(self.wp_url, self.target_domain)
                    print(f"   🔧 Fixed meta property: {prop}")

        # Explicit pass: ensure URL-bearing OG properties are always absolute
        OG_URL_PROPS = {'og:image', 'og:url', 'og:image:secure_url'}
        for meta in soup.find_all('meta', property=lambda p: p in OG_URL_PROPS):
            content = meta.get('content', '')
            if content.startswith('/'):
                meta['content'] = f"{self.target_domain}{content}"
            elif self.wp_url in content:
                meta['content'] = content.replace(self.wp_url, self.target_domain)

        # Check if og:image exists, add default if missing
        og_image = soup.find('meta', property='og:image')
        if not og_image and soup.head:
            # Use the site logo as default Open Graph image
            from config import Config
            default_image_url = f"{self.target_domain}{Config.DEFAULT_OG_IMAGE_PATH}"

            og_image = soup.new_tag('meta')
            og_image['property'] = 'og:image'
            og_image['content'] = default_image_url
            soup.head.append(og_image)

            # Also add og:image:width and og:image:height
            og_image_width = soup.new_tag('meta')
            og_image_width['property'] = 'og:image:width'
            og_image_width['content'] = '1024'
            soup.head.append(og_image_width)

            og_image_height = soup.new_tag('meta')
            og_image_height['property'] = 'og:image:height'
            og_image_height['content'] = '1024'
            soup.head.append(og_image_height)

            print(f"   🇾added default og:image: {default_image_url}")

        # Add twitter:image if missing (use same as og:image)
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if not twitter_image and og_image and soup.head:
            twitter_image = soup.new_tag('meta')
            twitter_image['name'] = 'twitter:image'
            twitter_image['content'] = og_image.get('content', '')
            soup.head.append(twitter_image)
            print("   🐦 Added twitter:image from og:image")

        # Fix meta tags with name attribute (Twitter Cards)
        for meta in soup.find_all('meta', attrs={'name': True}):
            name = meta.get('name', '')
            content = meta.get('content', '')

            if content:
                # Convert relative URLs to absolute (for twitter:image, etc.)
                if content.startswith('/'):
                    meta['content'] = f"{self.target_domain}{content}"
                    print(f"   🔧 Made {name} absolute: {content} -> {self.target_domain}{content}")
                # Fix twitter:image, twitter:url, etc.
                elif self.wp_url in content:
                    meta['content'] = content.replace(self.wp_url, self.target_domain)
                    print(f"   🔧 Fixed meta name: {name}")

        # Fix canonical links - make them absolute
        for link in soup.find_all('link', rel='canonical'):
            href = link.get('href', '')
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    link['href'] = f"{self.target_domain}{href}"
                    print(f"   🔧 Made canonical URL absolute: {href} -> {self.target_domain}{href}")
                # Replace WordPress URLs
                elif self.wp_url in href:
                    link['href'] = href.replace(self.wp_url, self.target_domain)
                    print("   🔧 Fixed canonical URL")

        # Fix RSS feed links: point to the generated XML feed and
        # remove WordPress comments feed (doesn't exist on static site)
        for link in soup.find_all('link', type=['application/rss+xml', 'application/atom+xml']):
            href = link.get('href', '')
            # Remove comments feed — not generated for static site
            if 'comments/feed' in href:
                link.decompose()
                continue
            # Fix main feed URL to point to the actual XML file
            if href:
                link['href'] = f"{self.target_domain}/feed/index.xml"

    def fix_jsonld_urls(self, soup):
        """Fix URLs in JSON-LD structured data for rich results"""
        # Find all script tags with JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                try:
                    # Parse JSON properly
                    data = json.loads(script.string)

                    # Fix URLs recursively
                    modified = self._fix_jsonld_object(data)

                    # Enhance BlogPosting with reading time and word count
                    if self._enhance_blogposting_schema(data, soup):
                        modified = True

                    if modified:
                        # Convert back to JSON and update
                        script.string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
                        print("   🔧 Enhanced JSON-LD with reading time and word count")

                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Invalid JSON-LD: {str(e)}")
                except Exception as e:
                    print(f"   ⚠️  Error fixing JSON-LD: {str(e)}")

    def _fix_jsonld_object(self, obj):
        """Recursively fix URLs in JSON-LD object"""
        modified = False

        if isinstance(obj, dict):
            for key, value in obj.items():
                # Fix URL strings
                if isinstance(value, str):
                    # Convert relative URLs to absolute
                    if value.startswith('/'):
                        # Relative URL - make absolute
                        obj[key] = f"{self.target_domain}{value}"
                        modified = True
                    elif self.wp_url in value:
                        # WordPress URL - replace with target
                        obj[key] = value.replace(self.wp_url, self.target_domain)
                        modified = True

                # Recursively process nested objects/arrays
                elif isinstance(value, (dict, list)):
                    if self._fix_jsonld_object(value):
                        modified = True

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    if self._fix_jsonld_object(item):
                        modified = True

        return modified

    def _enhance_blogposting_schema(self, data, soup):
        """Add reading time, word count, and publisher URL to BlogPosting schema"""
        modified = False

        # Handle @graph structure (Rank Math uses this)
        items = data.get('@graph', [data]) if '@graph' in data else [data]

        # First pass: Ensure Organization/Person publishers have URL
        for item in items:
            if isinstance(item, dict):
                item_types = item.get('@type', [])
                # Handle both single type and array of types
                if not isinstance(item_types, list):
                    item_types = [item_types]

                # If this is an Organization or Person that acts as publisher
                if any(t in ['Organization', 'Person'] for t in item_types):
                    if '@id' in item and '/#person' in item['@id']:
                        if 'url' not in item:
                            item['url'] = self.target_domain
                            modified = True
                            print(f"      ➕ Added URL to publisher entity: {self.target_domain}")

        # Second pass: Process BlogPosting items
        for item in items:
            if isinstance(item, dict) and item.get('@type') == 'BlogPosting':
                # Ensure publisher reference has URL (for inline publisher objects)
                if 'publisher' in item and isinstance(item['publisher'], dict):
                    if '@id' not in item['publisher'] and 'url' not in item['publisher']:
                        # Inline publisher without @id reference
                        item['publisher']['url'] = self.target_domain
                        modified = True
                        print(f"      ➕ Added publisher URL to inline publisher: {self.target_domain}")

                # Extract article content for word count
                article_content = self._extract_article_text(soup)

                if article_content:
                    # Calculate word count
                    word_count = len(article_content.split())

                    # Calculate reading time (200 words per minute average)
                    reading_minutes = max(1, round(word_count / 200))

                    # Add properties if not already present
                    if 'wordCount' not in item:
                        item['wordCount'] = word_count
                        modified = True
                        print(f"      ➕ Added wordCount: {word_count}")

                    if 'timeRequired' not in item:
                        # Format as ISO 8601 duration (PT5M = 5 minutes)
                        item['timeRequired'] = f"PT{reading_minutes}M"
                        modified = True
                        print(f"      ➕ Added timeRequired: {reading_minutes} min")

                    # Optionally add article body (truncated to 5000 chars)
                    if 'articleBody' not in item and len(article_content) > 100:
                        item['articleBody'] = article_content[:5000]
                        modified = True
                        print(f"      ➕ Added articleBody: {len(article_content[:5000])} chars")

                # Add inLanguage if missing
                if 'inLanguage' not in item:
                    item['inLanguage'] = 'en-GB'
                    modified = True

                # Add mainEntityOfPage if missing
                if 'mainEntityOfPage' not in item:
                    url = item.get('url') or item.get('mainEntityOfPage', '')
                    if url:
                        item['mainEntityOfPage'] = {
                            '@type': 'WebPage',
                            '@id': url
                        }
                        modified = True

        return modified

    def _extract_article_text(self, soup):
        """Extract main article text for word count calculation"""
        # Try to find the main article content
        # Common WordPress content containers
        content_selectors = [
            'article .entry-content',
            '.entry-content',
            'article',
            '.post-content',
            '.content',
            'main'
        ]

        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Clone to avoid modifying original
                content_copy = content_div.__copy__()

                # Remove unwanted elements
                for tag in content_copy(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                    tag.decompose()

                # Get text content
                text = content_copy.get_text(separator=' ', strip=True)

                # Clean up whitespace
                text = ' '.join(text.split())

                # Only return if we found substantial content
                if len(text) > 100:
                    return text

        return None

    def add_blogposting_schema(self, soup, current_url):
        """Generate and inject a BlogPosting JSON-LD schema for single article pages"""

        # Only run on single post pages
        body = soup.find('body')
        if not body:
            return
        body_class_str = ' '.join(body.get('class', [])).lower()
        if 'single-post' not in body_class_str:
            return

        # Skip if a BlogPosting schema already exists (e.g. supplied by Rank Math)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string or '')
                items = data.get('@graph', [data])
                if any(
                    isinstance(i, dict) and i.get('@type') == 'BlogPosting'
                    for i in items
                ):
                    return  # Already present – nothing to do
            except (json.JSONDecodeError, TypeError):
                pass

        # ── Metadata extraction ───────────────────────────────────────────────

        def _meta(attr, value):
            tag = soup.find('meta', attrs={attr: value})
            return tag.get('content', '').strip() if tag else ''

        # Title
        h1 = soup.find('h1', class_='entry-title')
        title = h1.get_text(strip=True) if h1 else _meta('property', 'og:title')

        # Description
        description = _meta('name', 'description') or _meta('property', 'og:description')

        # Dates
        date_published = _meta('property', 'article:published_time')
        date_modified  = _meta('property', 'article:modified_time') or date_published
        if not date_published:
            time_tag = soup.find('time', class_='entry-date')
            if time_tag:
                date_published = time_tag.get('datetime', '')
            updated_tag = soup.find('time', class_='updated')
            date_modified = updated_tag.get('datetime', '') if updated_tag else date_published

        # Canonical URL
        canonical_tag = soup.find('link', rel='canonical')
        canonical_url = canonical_tag['href'] if canonical_tag and canonical_tag.get('href') else \
            f"{self.target_domain}{current_url}"
        if canonical_url.startswith('/'):
            canonical_url = f"{self.target_domain}{canonical_url}"

        # Featured image
        og_image = _meta('property', 'og:image')
        og_image_w = _meta('property', 'og:image:width')
        og_image_h = _meta('property', 'og:image:height')
        if og_image and og_image.startswith('/'):
            og_image = f"{self.target_domain}{og_image}"

        # Author
        author_tag = (
            soup.find('a', rel='author') or
            soup.find('span', class_='author') or
            soup.find('a', class_='author')
        )
        author_name = author_tag.get_text(strip=True) if author_tag else 'James Kilby'

        # Categories (article section = first category)
        category_links = soup.find_all(
            'a', href=lambda x: x and '/category/' in x
        )
        categories = list(dict.fromkeys(
            lnk.get('href', '').split('/category/')[1].strip('/').replace('-', ' ').title()
            for lnk in category_links
        ))
        article_section = categories[0] if categories else ''

        # Tags / keywords
        tag_links = soup.find_all(
            'a', href=lambda x: x and '/tag/' in x
        )
        keywords = list(dict.fromkeys(
            lnk.get_text(strip=True)
            for lnk in tag_links
            if lnk.get_text(strip=True)
        ))

        # Word count & reading time
        article_text = self._extract_article_text(soup)
        word_count = len(article_text.split()) if article_text else 0
        reading_minutes = max(1, round(word_count / 200)) if word_count else 1

        # ── Build schema ─────────────────────────────────────────────────────

        schema: dict = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "url": canonical_url,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": canonical_url
            },
            "inLanguage": "en-GB",
            "publisher": {
                "@type": "Person",
                "@id": f"{self.target_domain}/#person",
                "name": "James Kilby",
                "url": self.target_domain,
            },
        }

        if description:
            schema["description"] = description
        if date_published:
            schema["datePublished"] = date_published
        if date_modified:
            schema["dateModified"] = date_modified
        if author_name:
            schema["author"] = {
                "@type": "Person",
                "name": author_name,
                "url": self.target_domain,
            }
        if og_image:
            image_obj: dict = {"@type": "ImageObject", "url": og_image}
            if og_image_w:
                image_obj["width"] = int(og_image_w)
            if og_image_h:
                image_obj["height"] = int(og_image_h)
            schema["image"] = image_obj
        if article_section:
            schema["articleSection"] = article_section
        if keywords:
            schema["keywords"] = keywords
        if word_count:
            schema["wordCount"] = word_count
            schema["timeRequired"] = f"PT{reading_minutes}M"
        if article_text and len(article_text) > 100:
            schema["articleBody"] = article_text[:5000]

        # ── Inject into <head> ────────────────────────────────────────────────

        if soup.head:
            script_tag = soup.new_tag('script')
            script_tag['type'] = 'application/ld+json'
            script_tag.string = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
            soup.head.append(script_tag)
            print(f"   📋 Added BlogPosting schema: {title[:60]}")

    @staticmethod
    def _extract_faq_pairs(soup):
        """Find an FAQ section in the article and return an ordered list of
        ``{'question': str, 'answer': str}`` dicts.

        Conservative by design — it only fires when a heading explicitly marks
        a "FAQ" / "Frequently Asked Questions" section, so we never invent
        FAQ structured data for content that isn't actually a FAQ (which would
        violate Google's structured-data guidelines). Returns ``[]`` when no
        FAQ section is found.

        Two question/answer shapes are recognised inside that section:
          * a definition list — ``<dt>`` question, ``<dd>`` answer; and
          * sub-headings deeper than the section heading whose text ends with
            "?", followed by their answer paragraphs/lists.
        """
        def _level(tag):
            name = getattr(tag, 'name', '') or ''
            if len(name) == 2 and name[0] == 'h' and name[1].isdigit():
                return int(name[1])
            return None

        # Locate the FAQ section heading.
        faq_heading = None
        for h in soup.find_all(['h2', 'h3', 'h4']):
            text = h.get_text(strip=True).lower()
            if 'frequently asked question' in text or re.search(r'\bfaqs?\b', text):
                faq_heading = h
                break
        if not faq_heading:
            return []

        section_level = _level(faq_heading)
        pairs = []
        current_q = None
        current_answer_parts = []

        def _flush():
            if current_q:
                answer = ' '.join(p for p in current_answer_parts if p).strip()
                if answer:
                    pairs.append({'question': current_q, 'answer': answer})

        for el in faq_heading.find_all_next(
            ['h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'dl']
        ):
            lvl = _level(el)
            # A heading at or above the section level ends the FAQ section.
            if lvl is not None and lvl <= section_level:
                break
            if el.name == 'dl':
                for dt in el.find_all('dt'):
                    q = dt.get_text(strip=True)
                    dd = dt.find_next_sibling('dd')
                    a = dd.get_text(' ', strip=True) if dd else ''
                    if q and a:
                        pairs.append({'question': q, 'answer': a})
                continue
            if lvl is not None:
                # A deeper heading starts a new question.
                _flush()
                current_answer_parts = []
                q_text = el.get_text(strip=True)
                current_q = q_text if q_text.endswith('?') else None
            elif current_q:
                current_answer_parts.append(el.get_text(' ', strip=True))
        _flush()

        # Deduplicate by question text, preserving order.
        seen = set()
        unique = []
        for pair in pairs:
            key = pair['question'].lower()
            if key not in seen:
                seen.add(key)
                unique.append(pair)
        return unique

    def add_faq_schema(self, soup):
        """Inject FAQPage JSON-LD when an article contains a FAQ section.

        Purely additive: a no-op when no FAQ is detected, when a FAQPage
        schema is already present, or when fewer than two Q&A pairs are found
        (a single question is too thin for FAQ rich results and risks a
        structured-data / visible-content mismatch).
        """
        body = soup.find('body')
        if not body:
            return
        body_class_str = ' '.join(body.get('class', [])).lower()
        if 'single-post' not in body_class_str and 'page' not in body_class_str:
            return

        # Skip if a FAQPage schema already exists (e.g. supplied by Rank Math).
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string or '')
                items = data.get('@graph', [data]) if isinstance(data, dict) else data
                if any(
                    isinstance(i, dict) and i.get('@type') == 'FAQPage'
                    for i in items
                ):
                    return  # Already present – nothing to do
            except (json.JSONDecodeError, TypeError):
                pass

        pairs = self._extract_faq_pairs(soup)
        if len(pairs) < 2:
            return

        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": pair['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": pair['answer'],
                    },
                }
                for pair in pairs
            ],
        }

        if soup.head:
            script_tag = soup.new_tag('script')
            script_tag['type'] = 'application/ld+json'
            script_tag.string = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
            soup.head.append(script_tag)
            print(f"   ❓ Added FAQPage schema: {len(pairs)} Q&A pairs")

    def add_site_schema(self, soup):
        """Enrich or inject WebSite and Organization JSON-LD schema.

        If WordPress already supplies a WebSite schema, enrich it with
        SearchAction, inLanguage, and publisher reference. If Organization
        is missing from the @graph, add it. If no WebSite schema exists
        at all, inject the complete schema block.
        """
        if not soup.head:
            return

        from config import Config as _org_config

        org_schema = {
            "@type": "Organization",
            "@id": f"{self.target_domain}/#organization",
            "name": "James Kilby",
            "url": self.target_domain,
            "logo": {
                "@type": "ImageObject",
                "url": f"{self.target_domain}{_org_config.DEFAULT_OG_IMAGE_PATH}"
            },
            "sameAs": list(_org_config.PERSON_SAME_AS)
        }

        # Try to enrich existing schema
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string or '')
                if not isinstance(data, dict):
                    continue
                items = data.get('@graph', [])
                if not items:
                    continue

                # Find and enrich existing WebSite
                enriched = False
                has_org = False
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    if item.get('@type') == 'WebSite':
                        if 'inLanguage' not in item:
                            item['inLanguage'] = 'en-GB'
                        # Drop any SearchAction (Rank Math injects one pointing at
                        # the WordPress "/?s=" endpoint). The static site has no
                        # server-side search route — search is client-side JS with
                        # no deep-linkable results page — so a Sitelinks Search Box
                        # action would resolve to a dead URL. No action is better
                        # than a broken one. Re-add only if a real /search?q= route
                        # with query-param deep-linking is ever shipped.
                        item.pop('potentialAction', None)
                        if 'publisher' not in item:
                            item['publisher'] = {"@id": f"{self.target_domain}/#organization"}
                        enriched = True
                    if item.get('@type') == 'Organization':
                        has_org = True

                if enriched:
                    # Add Organization to @graph if missing
                    if not has_org:
                        items.append(org_schema)
                    script.string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
                    return  # Done — enriched existing schema

            except (json.JSONDecodeError, TypeError):
                continue

        # No existing WebSite schema found — inject complete block
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebSite",
                    "@id": f"{self.target_domain}/#website",
                    "url": self.target_domain,
                    "name": "James Kilby",
                    "description": "Technical blog covering VMware, homelab, AI, and cloud computing",
                    "inLanguage": "en-GB",
                    "publisher": {"@id": f"{self.target_domain}/#organization"}
                    # No SearchAction: the static site has no server-side search
                    # route (search is client-side JS, no deep-linkable results
                    # page), so a Sitelinks Search Box action would point at a
                    # dead "/?s=" URL. See the enrich path above.
                },
                org_schema
            ]
        }

        script_tag = soup.new_tag('script')
        script_tag['type'] = 'application/ld+json'
        script_tag.string = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
        soup.head.append(script_tag)
