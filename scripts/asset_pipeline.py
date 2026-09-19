#!/usr/bin/env python3
"""
Static asset extraction + download — extracted from WordPressStaticGenerator
(wp_to_static_generator.py), the thirteenth cut out of that god object (see
scripts/site_artifacts_builder.py's docstring for the first).

Two-phase pipeline, run once per page then once per build:
- extract_assets(): per-page pass over a parsed soup that finds every asset
  reference (img/link/script/source/video/audio, srcset entries, inline
  background-image URLs, fonts/images referenced from linked CSS files, and
  WPO-minify/wp-content/cache files matched by regex against the raw HTML)
  and queues each one's absolute WordPress URL into the shared
  downloaded_assets set.
- download_assets(): one pass at the end of the build that downloads every
  queued asset concurrently (5 workers), rewriting CSS file contents to use
  relative URLs as it writes them to disk.

downloaded_assets is a set shared with wp_content_discovery.py's
WPContentDiscovery (which also adds WordPress media-library URLs to it) —
both extract_assets() and get_all_media_assets() write into the same
instance so download_assets() sees everything either source found.

Needs session/wp_url/target_domain/output_dir plus that shared
downloaded_assets set. WordPressStaticGenerator.process_html() and
generate_static_site() drive this via an AssetPipeline instance
(self.assets); see those methods for where each phase runs. Behaviour is
unchanged from the pre-extraction version — this is a pure move, not a
rewrite.
"""

import re
import concurrent.futures


class AssetPipeline:
    """Extracts asset URLs from parsed pages and downloads them to disk.
    Needs session/wp_url/target_domain/output_dir/downloaded_assets."""

    def __init__(self, session, wp_url, target_domain, output_dir, downloaded_assets):
        self.session = session
        self.wp_url = wp_url
        self.target_domain = target_domain
        self.output_dir = output_dir
        self.downloaded_assets = downloaded_assets

    def extract_assets(self, soup, current_url):
        """Extract asset URLs for later download"""
        # Enhanced asset selectors including WordPress-specific patterns
        asset_selectors = [
            ('img', 'src'),
            ('img', 'data-src'),  # Lazy loading images
            ('link[rel="stylesheet"]', 'href'),
            ('link[rel="preload"]', 'href'),  # Preload stylesheets
            ('script[src]', 'src'),
            ('source', 'src'),
            ('source', 'srcset'),
            ('video', 'src'),
            ('video', 'poster'),
            ('audio', 'src')
        ]

        for selector, attr in asset_selectors:
            for element in soup.select(selector):
                asset_url = element.get(attr)
                if asset_url:
                    # Handle both WordPress URL and relative URLs
                    if asset_url.startswith(self.wp_url):
                        self.downloaded_assets.add(asset_url)
                        print(f"   🔍 Found absolute asset: {asset_url}")
                    elif asset_url.startswith('/wp-content/') or asset_url.startswith('/wp-includes/'):
                        # WordPress files - including cache, media, and core files
                        full_url = self.wp_url + asset_url
                        self.downloaded_assets.add(full_url)
                        print(f"   🔍 Found relative asset: {asset_url} -> {full_url}")
                    elif asset_url.startswith('/') and not asset_url.startswith('//'):
                        # Any other relative URLs (could be theme files, etc.)
                        full_url = self.wp_url + asset_url
                        self.downloaded_assets.add(full_url)
                        print(f"   🔍 Found other relative asset: {asset_url} -> {full_url}")

        # Extract srcset URLs (multiple images for responsive design)
        for img in soup.find_all('img', srcset=True):
            srcset = img.get('srcset', '')
            for srcset_item in srcset.split(','):
                item = srcset_item.strip()
                if item:
                    url = item.split(' ')[0]  # Get URL part (before size descriptor)
                    if url.startswith(self.wp_url):
                        self.downloaded_assets.add(url)
                    elif url.startswith('/wp-content/'):
                        full_url = self.wp_url + url
                        self.downloaded_assets.add(full_url)

        # Extract background images from inline styles
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            # Look for background-image URLs
            import re
            bg_urls = re.findall(r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)', style)
            for bg_url in bg_urls:
                if bg_url.startswith(self.wp_url):
                    self.downloaded_assets.add(bg_url)
                elif bg_url.startswith('/wp-content/') or bg_url.startswith('/wp-includes/'):
                    full_url = self.wp_url + bg_url
                    self.downloaded_assets.add(full_url)

        # Parse CSS files referenced and queue their font files if they contain font URLs
        css_links = soup.find_all('link', rel=['stylesheet', 'preload'])
        for link in css_links:
            href = link.get('href', '')
            if href:
                # Build full CSS URL
                if href.startswith('http'):
                    css_url = href
                elif href.startswith('//'):
                    # Protocol-relative URL (external CDN) - skip
                    print(f"   ⏭️  Skipping external protocol-relative URL: {href}")
                    continue
                elif href.startswith('/'):
                    css_url = self.wp_url + href
                else:
                    css_url = self.wp_url + '/' + href

                print(f"   🎨 Parsing CSS for embedded assets: {href}")
                try:
                    css_resp = self.session.get(css_url, timeout=30)
                    if css_resp.status_code == 200:
                        css_text = css_resp.text
                        # Find all URL references in CSS (fonts, images, etc.)
                        import re
                        url_patterns = [
                            r'url\(["\']?([^"\')]+)["\']?\)',  # Standard URL pattern
                            r'@font-face[^}]*src:[^}]*url\(["\']?([^"\')]+)["\']?\)',  # Font face URLs
                        ]

                        for pattern in url_patterns:
                            urls_found = re.findall(pattern, css_text)
                            for found_url in urls_found:
                                clean_url = found_url.strip('"\' ')
                                if clean_url.startswith('data:') or not clean_url:
                                    continue

                                if clean_url.startswith('http'):
                                    if clean_url.startswith(self.wp_url):
                                        self.downloaded_assets.add(clean_url)
                                        print(f"   📦 Found CSS asset (absolute): {clean_url}")
                                elif clean_url.startswith('//'):
                                    # Protocol-relative URL (external CDN) - skip
                                    continue
                                elif clean_url.startswith('/'):
                                    full_asset_url = self.wp_url + clean_url
                                    self.downloaded_assets.add(full_asset_url)
                                    print(f"   📦 Found CSS asset (relative): {clean_url} -> {full_asset_url}")
                                else:
                                    # Relative to CSS file location
                                    base_path = '/'.join(href.split('/')[:-1]) if '/' in href else ''
                                    if base_path:
                                        full_asset_url = self.wp_url + '/' + base_path + '/' + clean_url
                                    else:
                                        full_asset_url = self.wp_url + '/' + clean_url
                                    self.downloaded_assets.add(full_asset_url)
                                    print(f"   📦 Found CSS asset (relative to CSS): {clean_url} -> {full_asset_url}")
                    else:
                        print(f"   ⚠️  Failed to fetch CSS: {css_url} (status: {css_resp.status_code})")
                except Exception as e:
                    print(f"   ⚠️  Error parsing CSS {css_url}: {str(e)}")

        # Manually detect and queue WordPress minified cache files
        print("   🔍 Manually detecting WordPress minified cache files...")
        import re

        # Look for WPO minify CSS files
        wpo_css_matches = re.findall(r'href="([^"]*wpo-minify[^"]*\.min\.css[^"]*)"', str(soup))
        for css_match in wpo_css_matches:
            # Always convert to WordPress domain for downloading, regardless of current URL
            if css_match.startswith('/'):
                full_css_url = self.wp_url + css_match
            elif css_match.startswith(self.target_domain):
                # Convert target domain back to WordPress domain for downloading
                full_css_url = css_match.replace(self.target_domain, self.wp_url)
            else:
                full_css_url = css_match
            self.downloaded_assets.add(full_css_url)
            print(f"   🎨 Found WPO minified CSS: {css_match} -> {full_css_url}")

        # Look for WPO minify JS files
        wpo_js_matches = re.findall(r'src="([^"]*wpo-minify[^"]*\.min\.js[^"]*)"', str(soup))
        for js_match in wpo_js_matches:
            # Always convert to WordPress domain for downloading, regardless of current URL
            if js_match.startswith('/'):
                full_js_url = self.wp_url + js_match
            elif js_match.startswith(self.target_domain):
                # Convert target domain back to WordPress domain for downloading
                full_js_url = js_match.replace(self.target_domain, self.wp_url)
            else:
                full_js_url = js_match
            self.downloaded_assets.add(full_js_url)
            print(f"   📜 Found WPO minified JS: {js_match} -> {full_js_url}")

        # Look for any other cache files (general pattern)
        cache_matches = re.findall(r'(?:href|src)="([^"]*wp-content/cache[^"]+)"', str(soup))
        for cache_match in cache_matches:
            # Always convert to WordPress domain for downloading, regardless of current URL
            if cache_match.startswith('/'):
                full_cache_url = self.wp_url + cache_match
            elif cache_match.startswith(self.target_domain):
                # Convert target domain back to WordPress domain for downloading
                full_cache_url = cache_match.replace(self.target_domain, self.wp_url)
            else:
                full_cache_url = cache_match
            self.downloaded_assets.add(full_cache_url)
            print(f"   📦 Found cache file: {cache_match} -> {full_cache_url}")

    def download_assets(self):
        """Download all discovered assets"""
        if not self.downloaded_assets:
            print("   ⚠️  No assets discovered to download")
            return

        print(f"📁 Downloading {len(self.downloaded_assets)} assets...")

        def download_single_asset(asset_url):
            try:
                # Convert to relative path - handle both wp_url and target_domain
                if asset_url.startswith(self.wp_url):
                    relative_path = asset_url.replace(self.wp_url, '').lstrip('/')
                elif asset_url.startswith(self.target_domain):
                    relative_path = asset_url.replace(self.target_domain, '').lstrip('/')
                else:
                    # Fallback - extract path after domain
                    from urllib.parse import urlparse
                    parsed = urlparse(asset_url)
                    relative_path = parsed.path.lstrip('/')

                # Strip query strings (e.g. ?ver=1.4.5) from file paths
                import re as _re
                relative_path = _re.sub(r'\?.*$', '', relative_path)

                output_path = self.output_dir / relative_path

                # Skip if already downloaded
                if output_path.exists():
                    return f"⏭️  {relative_path} (exists)"

                # Create directory
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Download with proper headers
                response = self.session.get(asset_url, timeout=30, stream=True)
                if response.status_code == 200:
                    # Validate content type matches expected file type
                    content_type = response.headers.get('content-type', '').lower()

                    # Check for mismatched content type (e.g., HTML returned for CSS request)
                    if asset_url.endswith('.css') and 'text/css' not in content_type:
                        if 'text/html' in content_type:
                            return f"❌ {relative_path} (HTML returned instead of CSS - authentication/access issue)"
                        else:
                            return f"❌ {relative_path} (Wrong content-type: {content_type})"
                    elif asset_url.endswith('.js') and 'javascript' not in content_type and 'text/plain' not in content_type:
                        if 'text/html' in content_type:
                            return f"❌ {relative_path} (HTML returned instead of JS - authentication/access issue)"
                        else:
                            return f"❌ {relative_path} (Wrong content-type: {content_type})"

                    # Special handling for CSS files - need to process URLs
                    if asset_url.endswith('.css'):
                        css_content = response.text

                        # Validate CSS content by checking for HTML doctype or tags
                        if css_content.strip().startswith('<!DOCTYPE') or '<html' in css_content[:200].lower():
                            return f"❌ {relative_path} (HTML content returned instead of CSS)"

                        # Convert absolute WordPress URLs to relative URLs
                        css_content = css_content.replace(self.wp_url + '/wp-content/', '/wp-content/')
                        css_content = css_content.replace(self.wp_url + '/wp-includes/', '/wp-includes/')
                        # Also convert the target domain URLs to relative
                        if self.target_domain:
                            css_content = css_content.replace(self.target_domain + '/wp-content/', '/wp-content/')
                            css_content = css_content.replace(self.target_domain + '/wp-includes/', '/wp-includes/')

                        # Convert font URLs in CSS files to relative paths
                        import re

                        # Pattern to match font URLs in CSS @font-face declarations
                        font_url_pattern = r"url\(([^)]+)\)"

                        def replace_font_url(match):
                            url = match.group(1).strip('"\'')
                            if url.startswith(self.wp_url):
                                # Convert absolute WordPress URL to relative
                                relative_url = url.replace(self.wp_url, '')
                                return f"url({relative_url})"
                            elif url.startswith('http'):
                                # Leave external URLs as-is
                                return match.group(0)
                            else:
                                # Already relative or data URL
                                return match.group(0)

                        css_content = re.sub(font_url_pattern, replace_font_url, css_content)

                        output_path.write_text(css_content, encoding='utf-8')
                    else:
                        # Write in chunks for large files
                        with open(output_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)

                    # Get file size for reporting
                    file_size = output_path.stat().st_size
                    size_mb = file_size / 1024 / 1024
                    if size_mb > 1:
                        return f"✅ {relative_path} ({size_mb:.1f}MB)"
                    else:
                        return f"✅ {relative_path} ({file_size/1024:.1f}KB)"
                else:
                    return f"❌ {relative_path} ({response.status_code})"

            except Exception as e:
                return f"❌ {relative_path} (Error: {str(e)[:50]})"

        # Download assets concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(download_single_asset, self.downloaded_assets))

        # Count and categorize results
        success_results = [r for r in results if r.startswith('✅')]
        error_results = [r for r in results if r.startswith('❌')]
        skipped_results = [r for r in results if r.startswith('⏭️')]

        print(f"   ✅ Downloaded: {len(success_results)}")
        print(f"   ⏭️  Skipped: {len(skipped_results)}")
        print(f"   ❌ Failed: {len(error_results)}")

        # Show some example results
        if success_results:
            print("   Recent downloads:")
            for result in success_results[:5]:
                print(f"     {result}")

        if error_results:
            print("   ⚠️  Some download errors:")
            for result in error_results[:3]:
                print(f"     {result}")
