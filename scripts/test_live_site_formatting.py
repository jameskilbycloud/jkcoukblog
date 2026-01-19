#!/usr/bin/env python3
"""
Test script to validate the formatting and structure of jameskilby.co.uk live site.

This script performs comprehensive checks on the live site to ensure:
- Proper HTML structure and validity
- CSS and JavaScript assets load correctly
- Analytics tracking is properly configured
- SEO meta tags are present and valid
- Images have proper alt attributes
- Links are not broken (404s)
- Responsive image srcset attributes are present
- No WordPress-specific elements remain
- Plausible Analytics is correctly injected
- Utterances comments widget is properly configured
"""

import requests
import sys
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Tuple, Set
import time
import re


class LiveSiteFormattingTester:
    """Test the live site formatting and structure."""
    
    def __init__(self, base_url: str = "https://jameskilby.co.uk"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Site-Formatting-Test/1.0'
        })
        self.errors = []
        self.warnings = []
        self.info = []
        
    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        print(f"❌ ERROR: {message}")
        
    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")
        
    def log_info(self, message: str):
        """Log informational message."""
        self.info.append(message)
        print(f"ℹ️  INFO: {message}")
        
    def log_success(self, message: str):
        """Log a success message."""
        print(f"✅ {message}")
        
    def fetch_url(self, url: str, timeout: int = 10) -> Tuple[requests.Response, str]:
        """Fetch a URL and return response and error message if any."""
        try:
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            return response, None
        except requests.exceptions.RequestException as e:
            return None, str(e)
            
    def test_homepage_loads(self) -> bool:
        """Test that the homepage loads successfully."""
        print("\n🔍 Testing homepage load...")
        response, error = self.fetch_url(self.base_url)
        
        if error:
            self.log_error(f"Homepage failed to load: {error}")
            return False
            
        if response.status_code != 200:
            self.log_error(f"Homepage returned status code {response.status_code}")
            return False
            
        if len(response.text) < 1000:
            self.log_warning("Homepage content seems unusually short")
            
        self.log_success("Homepage loads successfully")
        return True
        
    def test_html_structure(self, html: str) -> bool:
        """Test basic HTML structure and validity."""
        print("\n🔍 Testing HTML structure...")
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for doctype
        if not html.strip().upper().startswith('<!DOCTYPE'):
            self.log_error("Missing DOCTYPE declaration")
            return False
            
        # Check for required elements
        if not soup.find('html'):
            self.log_error("Missing <html> tag")
            return False
            
        if not soup.find('head'):
            self.log_error("Missing <head> tag")
            return False
            
        if not soup.find('body'):
            self.log_error("Missing <body> tag")
            return False
            
        self.log_success("HTML structure is valid")
        return True
        
    def test_meta_tags(self, html: str) -> bool:
        """Test presence and validity of meta tags."""
        print("\n🔍 Testing meta tags...")
        soup = BeautifulSoup(html, 'html.parser')
        all_good = True
        
        # Required meta tags
        meta_charset = soup.find('meta', attrs={'charset': True})
        if not meta_charset:
            self.log_error("Missing charset meta tag")
            all_good = False
        else:
            self.log_success("Charset meta tag present")
            
        meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not meta_viewport:
            self.log_error("Missing viewport meta tag")
            all_good = False
        else:
            self.log_success("Viewport meta tag present")
            
        # SEO meta tags
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if not meta_description:
            self.log_warning("Missing description meta tag")
            all_good = False
        elif meta_description.get('content'):
            self.log_success(f"Description meta tag present: {meta_description['content'][:60]}...")
        else:
            self.log_warning("Description meta tag is empty")
            
        # Open Graph tags
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        
        if og_title and og_description and og_image:
            self.log_success("Open Graph tags present")
        else:
            self.log_warning("Some Open Graph tags are missing")
            
        # Twitter Card tags
        twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
        if twitter_card:
            self.log_success("Twitter Card meta tag present")
        else:
            self.log_warning("Twitter Card meta tag missing")
            
        return all_good
        
    def test_plausible_analytics(self, html: str) -> bool:
        """Test that Plausible Analytics is properly configured."""
        print("\n🔍 Testing Plausible Analytics...")
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find Plausible script
        plausible_scripts = soup.find_all('script', src=lambda x: x and 'plausible' in x.lower())
        
        if not plausible_scripts:
            self.log_error("Plausible Analytics script not found")
            return False
            
        if len(plausible_scripts) > 1:
            self.log_warning(f"Multiple Plausible scripts found ({len(plausible_scripts)})")
            
        script = plausible_scripts[0]
        src = script.get('src', '')
        data_domain = script.get('data-domain', '')
        
        # Check script source
        if 'plausible.jameskilby.cloud' not in src:
            self.log_error(f"Incorrect Plausible script source: {src}")
            return False
        else:
            self.log_success(f"Plausible script source correct: {src}")
            
        # Check data-domain attribute
        if data_domain != 'jameskilby.co.uk':
            self.log_error(f"Incorrect data-domain attribute: '{data_domain}' (should be 'jameskilby.co.uk')")
            return False
        else:
            self.log_success(f"Plausible data-domain correct: {data_domain}")
            
        # Check defer attribute
        if not script.has_attr('defer'):
            self.log_warning("Plausible script missing 'defer' attribute")
        else:
            self.log_success("Plausible script has 'defer' attribute")
            
        return True
        
    def test_wordpress_cleanup(self, html: str) -> bool:
        """Test that WordPress-specific elements have been removed."""
        print("\n🔍 Testing WordPress cleanup...")
        soup = BeautifulSoup(html, 'html.parser')
        all_good = True
        
        # Check for WordPress generator meta tag
        wp_generator = soup.find('meta', attrs={'name': 'generator', 'content': lambda x: x and 'WordPress' in x})
        if wp_generator:
            self.log_warning("WordPress generator meta tag still present")
            all_good = False
        else:
            self.log_success("WordPress generator meta tag removed")
            
        # Check for REST API discovery links
        rest_api_link = soup.find('link', rel=lambda x: x and 'https://api.w.org/' in str(x))
        if rest_api_link:
            self.log_warning("WordPress REST API discovery link still present")
            all_good = False
        else:
            self.log_success("WordPress REST API discovery link removed")
            
        # Check for wp-embed script
        wp_embed_scripts = soup.find_all('script', src=lambda x: x and 'wp-embed' in x.lower())
        if wp_embed_scripts:
            self.log_warning(f"Found {len(wp_embed_scripts)} wp-embed script(s)")
            all_good = False
        else:
            self.log_success("No wp-embed scripts found")
            
        # Check for admin bar
        admin_bar = soup.find(id='wpadminbar')
        if admin_bar:
            self.log_error("WordPress admin bar still present")
            all_good = False
        else:
            self.log_success("WordPress admin bar removed")
            
        return all_good
        
    def test_images(self, html: str, sample_size: int = 10) -> bool:
        """Test image tags for proper attributes."""
        print(f"\n🔍 Testing images (sampling up to {sample_size})...")
        soup = BeautifulSoup(html, 'html.parser')
        images = soup.find_all('img')
        pictures = soup.find_all('picture')

        if not images:
            self.log_warning("No images found on page")
            return True

        self.log_info(f"Found {len(images)} image(s) on page")
        if pictures:
            self.log_info(f"Found {len(pictures)} <picture> element(s) with modern format support")

        # Count modern format usage
        webp_sources = soup.find_all('source', type='image/webp')
        avif_sources = soup.find_all('source', type='image/avif')

        if webp_sources:
            self.log_success(f"WebP format used in {len(webp_sources)} source element(s)")
        else:
            self.log_warning("No WebP images found - consider image optimization")

        if avif_sources:
            self.log_success(f"AVIF format used in {len(avif_sources)} source element(s)")
        else:
            self.log_warning("No AVIF images found - consider image optimization")

        # Sample images
        test_images = images[:sample_size]
        issues = 0
        lazy_count = 0

        for idx, img in enumerate(test_images, 1):
            src = img.get('src', '')
            alt = img.get('alt', '')

            if not src:
                self.log_error(f"Image #{idx} missing src attribute")
                issues += 1
                continue

            if not alt and alt != '':  # Empty alt is valid for decorative images
                self.log_warning(f"Image #{idx} missing alt attribute: {src[:60]}")
                issues += 1

            # Check for responsive images
            srcset = img.get('srcset', '')
            if srcset:
                self.log_info(f"Image #{idx} has responsive srcset")

            # Check for loading attribute
            loading = img.get('loading', '')
            if loading == 'lazy':
                lazy_count += 1
            elif loading not in ['lazy', 'eager'] and idx > 1:  # First image should load eagerly
                self.log_info(f"Image #{idx} could benefit from loading='lazy'")

            # Check for width/height attributes (prevent layout shift)
            width = img.get('width', '')
            height = img.get('height', '')
            if not width or not height:
                self.log_info(f"Image #{idx} missing width/height (may cause CLS)")

        if lazy_count > 0:
            self.log_success(f"{lazy_count} image(s) use lazy loading")

        if issues == 0:
            self.log_success(f"All {len(test_images)} tested images have proper attributes")
            return True
        else:
            self.log_warning(f"Found {issues} image issue(s)")
            return False
            
    def test_css_assets(self, html: str, sample_size: int = 5) -> bool:
        """Test that CSS assets load correctly."""
        print(f"\n🔍 Testing CSS assets (sampling up to {sample_size})...")
        soup = BeautifulSoup(html, 'html.parser')
        
        css_links = soup.find_all('link', rel=lambda x: x and 'stylesheet' in str(x).lower())
        
        if not css_links:
            self.log_warning("No CSS stylesheets found")
            return True
            
        self.log_info(f"Found {len(css_links)} CSS stylesheet(s)")
        
        # Test a sample
        test_links = css_links[:sample_size]
        all_good = True
        
        for idx, link in enumerate(test_links, 1):
            href = link.get('href', '')
            if not href:
                self.log_warning(f"CSS link #{idx} has no href attribute")
                continue
                
            # Build absolute URL
            css_url = urljoin(self.base_url, href)
            
            # Test if CSS loads
            response, error = self.fetch_url(css_url)
            if error:
                self.log_error(f"CSS #{idx} failed to load: {css_url} - {error}")
                all_good = False
            elif response.status_code != 200:
                self.log_error(f"CSS #{idx} returned status {response.status_code}: {css_url}")
                all_good = False
            else:
                self.log_success(f"CSS #{idx} loads successfully: {href[:60]}")
                
            time.sleep(0.1)  # Be nice to the server
            
        return all_good
        
    def test_js_assets(self, html: str, sample_size: int = 5) -> bool:
        """Test that JavaScript assets load correctly."""
        print(f"\n🔍 Testing JavaScript assets (sampling up to {sample_size})...")
        soup = BeautifulSoup(html, 'html.parser')
        
        js_scripts = soup.find_all('script', src=True)
        
        if not js_scripts:
            self.log_warning("No external JavaScript files found")
            return True
            
        self.log_info(f"Found {len(js_scripts)} external JavaScript file(s)")
        
        # Test a sample
        test_scripts = js_scripts[:sample_size]
        all_good = True
        
        for idx, script in enumerate(test_scripts, 1):
            src = script.get('src', '')
            if not src:
                continue
                
            # Build absolute URL
            js_url = urljoin(self.base_url, src)
            
            # Skip external domains (CDNs, etc.)
            parsed = urlparse(js_url)
            if parsed.netloc and parsed.netloc not in ['jameskilby.co.uk', 'plausible.jameskilby.cloud']:
                self.log_info(f"Skipping external JS: {parsed.netloc}")
                continue
            
            # Test if JS loads
            response, error = self.fetch_url(js_url)
            if error:
                self.log_error(f"JS #{idx} failed to load: {js_url} - {error}")
                all_good = False
            elif response.status_code != 200:
                self.log_error(f"JS #{idx} returned status {response.status_code}: {js_url}")
                all_good = False
            else:
                self.log_success(f"JS #{idx} loads successfully: {src[:60]}")
                
            time.sleep(0.1)  # Be nice to the server
            
        return all_good
        
    def test_links(self, html: str, sample_size: int = 10) -> bool:
        """Test that internal links are not broken."""
        print(f"\n🔍 Testing internal links (sampling up to {sample_size})...")
        soup = BeautifulSoup(html, 'html.parser')
        
        links = soup.find_all('a', href=True)
        
        if not links:
            self.log_warning("No links found on page")
            return True
            
        # Filter for internal links
        internal_links = []
        for link in links:
            href = link.get('href', '')
            parsed = urlparse(href)
            
            # Check if it's internal
            if not parsed.netloc or parsed.netloc == 'jameskilby.co.uk':
                if href and not href.startswith('#') and not href.startswith('mailto:'):
                    internal_links.append(href)
                    
        if not internal_links:
            self.log_info("No internal links to test")
            return True
            
        self.log_info(f"Found {len(internal_links)} internal link(s)")
        
        # Test a sample
        test_links = list(set(internal_links[:sample_size]))  # Remove duplicates
        all_good = True
        
        for idx, href in enumerate(test_links, 1):
            link_url = urljoin(self.base_url, href)
            
            response, error = self.fetch_url(link_url)
            if error:
                self.log_warning(f"Link #{idx} failed: {link_url} - {error}")
                all_good = False
            elif response.status_code == 404:
                self.log_error(f"Link #{idx} is broken (404): {link_url}")
                all_good = False
            elif response.status_code >= 400:
                self.log_warning(f"Link #{idx} returned status {response.status_code}: {link_url}")
                all_good = False
            else:
                self.log_success(f"Link #{idx} works: {href[:60]}")
                
            time.sleep(0.2)  # Be nice to the server
            
        return all_good
        
    def test_title_tag(self, html: str) -> bool:
        """Test that the title tag is present and reasonable."""
        print("\n🔍 Testing title tag...")
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.find('title')
        if not title:
            self.log_error("Missing <title> tag")
            return False
            
        title_text = title.get_text().strip()
        if not title_text:
            self.log_error("Empty <title> tag")
            return False
            
        if len(title_text) < 10:
            self.log_warning(f"Title seems too short: '{title_text}'")
            return False
            
        if len(title_text) > 60:
            self.log_info(f"Title is {len(title_text)} characters (recommended < 60)")
            
        self.log_success(f"Title tag present: '{title_text}'")
        return True
        
    def test_canonical_url(self, html: str) -> bool:
        """Test that canonical URL is present and correct."""
        print("\n🔍 Testing canonical URL...")
        soup = BeautifulSoup(html, 'html.parser')
        
        canonical = soup.find('link', rel='canonical')
        if not canonical:
            self.log_warning("Missing canonical URL")
            return False
            
        href = canonical.get('href', '')
        if not href:
            self.log_error("Canonical link has no href")
            return False
            
        # Convert relative URLs to absolute
        canonical_url = urljoin(self.base_url, href)
        
        # Check if it's the correct domain
        parsed = urlparse(canonical_url)
        if parsed.netloc != 'jameskilby.co.uk':
            self.log_error(f"Canonical URL points to wrong domain: {canonical_url}")
            return False
            
        self.log_success(f"Canonical URL present: {canonical_url}")
        return True
        
    def test_structured_data(self, html: str) -> bool:
        """Test for presence of structured data (JSON-LD)."""
        print("\n🔍 Testing structured data...")
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find JSON-LD script tags
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        if not json_ld_scripts:
            self.log_warning("No structured data (JSON-LD) found")
            return False
            
        self.log_info(f"Found {len(json_ld_scripts)} structured data block(s)")
        
        # Try to parse JSON
        for idx, script in enumerate(json_ld_scripts, 1):
            try:
                data = json.loads(script.string)
                # Determine schema type
                schema_type = 'Unknown'
                if isinstance(data, dict):
                    if '@type' in data:
                        schema_type = data['@type']
                    elif '@graph' in data:
                        graph = data['@graph']
                        if isinstance(graph, list) and len(graph) > 0 and isinstance(graph[0], dict):
                            schema_type = graph[0].get('@type', 'Unknown')
                elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    schema_type = data[0].get('@type', 'Unknown')
                self.log_success(f"Structured data #{idx} is valid JSON (type: {schema_type})")
            except json.JSONDecodeError as e:
                self.log_error(f"Structured data #{idx} has invalid JSON: {e}")
                return False
            except Exception as e:
                self.log_info(f"Structured data #{idx} parsed but type detection uncertain")
                
        return True
        
    def test_cache_control(self, html: str) -> bool:
        """Test for cache control meta tag."""
        print("\n🔍 Testing cache control...")
        soup = BeautifulSoup(html, 'html.parser')
        
        cache_meta = soup.find('meta', attrs={'http-equiv': 'Cache-Control'})
        if cache_meta:
            content = cache_meta.get('content', '')
            self.log_success(f"Cache-Control meta tag present: {content}")
            return True
        else:
            self.log_info("No Cache-Control meta tag found (this is optional)")
            return True
            
    def test_utterances_comments(self, html: str) -> bool:
        """Test that utterances comments widget is properly configured."""
        print("\n🔍 Testing utterances comments...")
        soup = BeautifulSoup(html, 'html.parser')

        # Find utterances script
        utterances_scripts = soup.find_all('script', src=lambda x: x and 'utteranc.es' in x.lower())

        if not utterances_scripts:
            self.log_info("Utterances comments script not found (may only be on post pages)")
            return True

        if len(utterances_scripts) > 1:
            self.log_warning(f"Multiple utterances scripts found ({len(utterances_scripts)})")

        script = utterances_scripts[0]
        src = script.get('src', '')
        repo = script.get('data-repo', '')
        theme = script.get('data-theme', '')
        issue_term = script.get('data-issue-term', '')

        # Check script source
        if 'utteranc.es/client.js' not in src:
            self.log_error(f"Incorrect utterances script source: {src}")
            return False
        else:
            self.log_success(f"Utterances script source correct: {src}")

        # Check data-repo attribute
        if not repo:
            self.log_error("Missing data-repo attribute for utterances")
            return False
        elif repo != 'jameskilbynet/jkcoukblog':
            self.log_warning(f"Unexpected data-repo: '{repo}' (expected 'jameskilbynet/jkcoukblog')")
        else:
            self.log_success(f"Utterances data-repo correct: {repo}")

        # Check data-theme attribute
        if not theme:
            self.log_warning("Missing data-theme attribute for utterances")
        else:
            self.log_success(f"Utterances theme configured: {theme}")

        # Check data-issue-term attribute
        if not issue_term:
            self.log_warning("Missing data-issue-term attribute for utterances")
        else:
            self.log_success(f"Utterances issue-term configured: {issue_term}")

        # Check crossorigin attribute
        if not script.has_attr('crossorigin'):
            self.log_warning("Utterances script missing 'crossorigin' attribute")
        else:
            self.log_success("Utterances script has 'crossorigin' attribute")

        return True

    def test_security_headers(self) -> bool:
        """Test for important security headers."""
        print("\n🔍 Testing security headers...")
        response, error = self.fetch_url(self.base_url)

        if error or not response:
            self.log_warning("Could not fetch headers for security test")
            return True

        headers = response.headers
        all_good = True

        # Content-Security-Policy
        csp = headers.get('Content-Security-Policy', '')
        if csp:
            self.log_success(f"Content-Security-Policy header present")
        else:
            self.log_warning("Content-Security-Policy header missing")
            all_good = False

        # X-Frame-Options
        xfo = headers.get('X-Frame-Options', '')
        if xfo:
            self.log_success(f"X-Frame-Options: {xfo}")
        else:
            self.log_warning("X-Frame-Options header missing (clickjacking protection)")
            all_good = False

        # X-Content-Type-Options
        xcto = headers.get('X-Content-Type-Options', '')
        if xcto == 'nosniff':
            self.log_success("X-Content-Type-Options: nosniff")
        else:
            self.log_warning("X-Content-Type-Options: nosniff header missing")
            all_good = False

        # Strict-Transport-Security (HSTS)
        hsts = headers.get('Strict-Transport-Security', '')
        if hsts:
            self.log_success(f"Strict-Transport-Security header present")
        else:
            self.log_warning("Strict-Transport-Security header missing (HTTPS enforcement)")
            all_good = False

        # Referrer-Policy
        referrer = headers.get('Referrer-Policy', '')
        if referrer:
            self.log_success(f"Referrer-Policy: {referrer}")
        else:
            self.log_info("Referrer-Policy header not set")

        # Permissions-Policy
        perms = headers.get('Permissions-Policy', '')
        if perms:
            self.log_success("Permissions-Policy header present")
        else:
            self.log_info("Permissions-Policy header not set")

        return all_good

    def test_performance_hints(self, html: str) -> bool:
        """Test for performance optimization hints."""
        print("\n🔍 Testing performance hints...")
        soup = BeautifulSoup(html, 'html.parser')
        all_good = True

        # Preconnect hints
        preconnects = soup.find_all('link', rel='preconnect')
        if preconnects:
            self.log_success(f"Found {len(preconnects)} preconnect hint(s)")
            for pc in preconnects[:3]:
                href = pc.get('href', '')
                self.log_info(f"  Preconnect: {href}")
        else:
            self.log_info("No preconnect hints found")

        # DNS prefetch
        dns_prefetch = soup.find_all('link', rel='dns-prefetch')
        if dns_prefetch:
            self.log_success(f"Found {len(dns_prefetch)} dns-prefetch hint(s)")

        # Preload hints
        preloads = soup.find_all('link', rel='preload')
        if preloads:
            self.log_success(f"Found {len(preloads)} preload hint(s)")
            for pl in preloads[:3]:
                href = pl.get('href', '')
                as_type = pl.get('as', '')
                self.log_info(f"  Preload: {href} (as: {as_type})")
        else:
            self.log_info("No preload hints found (consider for critical assets)")

        # Check for async/defer on scripts
        scripts = soup.find_all('script', src=True)
        async_count = sum(1 for s in scripts if s.has_attr('async'))
        defer_count = sum(1 for s in scripts if s.has_attr('defer'))

        if async_count + defer_count > 0:
            self.log_success(f"Scripts optimized: {async_count} async, {defer_count} defer")
        else:
            self.log_warning("No async/defer scripts found - blocking scripts may slow page load")
            all_good = False

        return all_good

    def test_accessibility(self, html: str) -> bool:
        """Test for basic accessibility features."""
        print("\n🔍 Testing accessibility features...")
        soup = BeautifulSoup(html, 'html.parser')
        all_good = True

        # HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            self.log_success(f"HTML lang attribute present: {html_tag['lang']}")
        else:
            self.log_error("HTML lang attribute missing (required for screen readers)")
            all_good = False

        # Skip to content link
        skip_links = soup.find_all('a', href='#main-content') + soup.find_all('a', href='#content')
        if skip_links:
            self.log_success("Skip to content link found")
        else:
            self.log_info("No skip to content link (helpful for keyboard navigation)")

        # ARIA landmarks
        main_tag = soup.find('main')
        nav_tags = soup.find_all('nav')
        header_tag = soup.find('header')
        footer_tag = soup.find('footer')

        landmark_count = sum([1 for x in [main_tag, header_tag, footer_tag] if x])
        landmark_count += len(nav_tags)

        if landmark_count >= 3:
            self.log_success(f"Found {landmark_count} semantic landmarks (main, nav, header, footer)")
        else:
            self.log_warning("Limited semantic landmarks - consider using <main>, <nav>, <header>, <footer>")
            all_good = False

        # Form labels
        inputs = soup.find_all(['input', 'textarea', 'select'])
        if inputs:
            inputs_with_labels = 0
            for inp in inputs[:5]:  # Sample first 5
                input_id = inp.get('id', '')
                aria_label = inp.get('aria-label', '')
                if input_id:
                    label = soup.find('label', attrs={'for': input_id})
                    if label or aria_label:
                        inputs_with_labels += 1

            if inputs_with_labels == len(inputs[:5]):
                self.log_success("Form inputs have associated labels")
            else:
                self.log_warning(f"Some form inputs missing labels ({inputs_with_labels}/{len(inputs[:5])})")
                all_good = False

        # Heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        h1_count = len(soup.find_all('h1'))

        if h1_count == 1:
            self.log_success("Exactly one H1 heading (good heading hierarchy)")
        elif h1_count == 0:
            self.log_error("No H1 heading found")
            all_good = False
        else:
            self.log_warning(f"Multiple H1 headings found ({h1_count})")
            all_good = False

        if len(headings) > 1:
            self.log_success(f"Found {len(headings)} heading elements")

        return all_good

    def test_mobile_optimization(self, html: str) -> bool:
        """Test for mobile optimization features."""
        print("\n🔍 Testing mobile optimization...")
        soup = BeautifulSoup(html, 'html.parser')
        all_good = True

        # Viewport meta tag (already tested, but check content)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            content = viewport.get('content', '')
            if 'width=device-width' in content and 'initial-scale=1' in content:
                self.log_success("Viewport properly configured for mobile")
            else:
                self.log_warning(f"Viewport content may not be optimal: {content}")
                all_good = False

        # Touch icons
        apple_touch_icons = soup.find_all('link', rel=lambda x: x and 'apple-touch-icon' in str(x))
        if apple_touch_icons:
            self.log_success(f"Found {len(apple_touch_icons)} Apple touch icon(s)")
        else:
            self.log_info("No Apple touch icons found (improves mobile UX)")

        # Manifest
        manifest = soup.find('link', rel='manifest')
        if manifest:
            self.log_success("Web app manifest present (PWA support)")
        else:
            self.log_info("No web app manifest found (needed for PWA)")

        # Theme color
        theme_color = soup.find('meta', attrs={'name': 'theme-color'})
        if theme_color:
            self.log_success(f"Theme color defined: {theme_color.get('content', '')}")
        else:
            self.log_info("No theme-color meta tag (improves mobile browser UI)")

        return all_good
            
    def run_all_tests(self) -> bool:
        """Run all formatting tests."""
        print("=" * 70)
        print("🚀 Starting Live Site Formatting Tests")
        print(f"🌐 Testing: {self.base_url}")
        print("=" * 70)

        # Fetch homepage
        response, error = self.fetch_url(self.base_url)
        if error or not response:
            self.log_error(f"Failed to fetch homepage: {error}")
            return False

        html = response.text

        # Run all tests - organized by category
        test_results = {
            # Core functionality
            "Homepage Loads": self.test_homepage_loads(),
            "HTML Structure": self.test_html_structure(html),

            # SEO & Meta
            "Meta Tags": self.test_meta_tags(html),
            "Title Tag": self.test_title_tag(html),
            "Canonical URL": self.test_canonical_url(html),
            "Structured Data": self.test_structured_data(html),

            # Analytics & Tracking
            "Plausible Analytics": self.test_plausible_analytics(html),

            # Content & Assets
            "WordPress Cleanup": self.test_wordpress_cleanup(html),
            "Utterances Comments": self.test_utterances_comments(html),
            "Images": self.test_images(html),
            "CSS Assets": self.test_css_assets(html),
            "JavaScript Assets": self.test_js_assets(html),
            "Internal Links": self.test_links(html),

            # Performance & Security
            "Security Headers": self.test_security_headers(),
            "Performance Hints": self.test_performance_hints(html),
            "Cache Control": self.test_cache_control(html),

            # Accessibility & Mobile
            "Accessibility": self.test_accessibility(html),
            "Mobile Optimization": self.test_mobile_optimization(html),
        }
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            
        print("\n" + "=" * 70)
        print(f"📈 Results: {passed}/{total} tests passed")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"ℹ️  Info: {len(self.info)}")
        print("=" * 70)
        
        if self.errors:
            print("\n🚨 ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        return len(self.errors) == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test jameskilby.co.uk live site formatting',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--url',
        default='https://jameskilby.co.uk',
        help='Base URL to test (default: https://jameskilby.co.uk)'
    )
    
    args = parser.parse_args()
    
    tester = LiveSiteFormattingTester(base_url=args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
