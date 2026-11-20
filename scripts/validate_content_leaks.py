#!/usr/bin/env python3
"""
Fail the build when WordPress leftovers or banned words reach the published
site.

The generator strips WordPress cruft from pages it regenerates, but an
incremental build copies every unchanged page from the previous deploy
untouched. A fix to the cleanup code only reaches pages rebuilt after it, so
the only way to know the whole site is clean is to check the final output.

Checked on every HTML page:
  - the Kadence footer credit ("WordPress Theme by Kadence WP")
  - the WordPress generator meta tag, admin bar, wp-embed script, emoji loader
  - REST API / RSD / pingback / wlwmanifest discovery links
  - the private WordPress hostname in any attribute, <style> block or
    sourceURL comment (prose that mentions it, e.g. a post about the
    migration, is fine)
  - footer structure: a page with a <footer> has exactly one .jk-footer-row
    and no empty <p> left behind by a strip

Checked on /markdown/, /api/, llms*.txt, the search index, feeds and sitemaps:
  - the Kadence credit
  - links to WordPress assets (wp-content / wp-includes on the private host),
    which are behind Cloudflare Access and break for readers

Checked everywhere: Config.PUBLIC_CONTENT_DENYLIST (whole word, case
sensitive) and the comma-separated PUBLIC_CONTENT_DENYLIST_EXTRA environment
variable (whole word, case-insensitive; the term itself is never printed).

Usage:
    python3 scripts/validate_content_leaks.py ./static-output
"""

import argparse
import os
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from config import Config

WP_HOST = Config.WP_URL.split('://', 1)[-1].rstrip('/')
KADENCE_RE = re.compile(r'Theme by\s+Kadence|kadencewp\.com', re.I)
WP_ASSET_RE = re.compile(r'https?://' + re.escape(WP_HOST) + r'/wp-(?:content|includes)/', re.I)
WP_SOURCEURL_RE = re.compile(r'sourceURL=https?://' + re.escape(WP_HOST), re.I)

TEXT_SUFFIXES = {'.md', '.json', '.txt', '.xml'}
MAX_PER_RULE = 10


def _terms_from_env():
    raw = os.environ.get('PUBLIC_CONTENT_DENYLIST_EXTRA', '')
    return [t.strip() for t in raw.split(',') if t.strip()]


def check_denylist(text, public_terms=Config.PUBLIC_CONTENT_DENYLIST, private_terms=()):
    """Return (rule, detail) pairs for banned words. Private terms are
    reported by position only, so the build log never prints them."""
    issues = []
    for term in public_terms:
        if re.search(r'\b' + re.escape(term) + r'\b', text):
            issues.append(('denylist', f'contains "{term}"'))
    for i, term in enumerate(private_terms, 1):
        if re.search(r'\b' + re.escape(term) + r'\b', text, re.I):
            issues.append(('denylist', f'contains private denylist term #{i}'))
    return issues


def check_text(text):
    """Checks for the non-HTML outputs (markdown, API JSON, llms.txt, feeds)."""
    issues = []
    if KADENCE_RE.search(text):
        issues.append(('kadence-credit', 'Kadence theme credit present'))
    m = WP_ASSET_RE.search(text)
    if m:
        issues.append(('wp-asset-link', f'links to a WordPress asset ({m.group(0)}…)'))
    return issues


def check_html(html):
    """Checks for a built HTML page."""
    issues = []
    soup = BeautifulSoup(html, 'html.parser')

    if KADENCE_RE.search(soup.get_text()) or soup.find('a', href=KADENCE_RE):
        issues.append(('kadence-credit', 'Kadence theme credit present'))

    if soup.find('meta', attrs={'name': 'generator', 'content': re.compile('wordpress', re.I)}):
        issues.append(('wp-generator', 'WordPress generator meta tag'))
    if soup.find(id='wpadminbar'):
        issues.append(('wp-admin-bar', 'WordPress admin bar'))
    if soup.find('script', src=re.compile('wp-embed', re.I)):
        issues.append(('wp-embed', 'wp-embed script'))
    if soup.find('script', id=re.compile('^wp-emoji')) or '_wpemojiSettings' in html:
        issues.append(('wp-emoji', 'wp-emoji loader'))
    for rel in ('https://api.w.org/', 'EditURI', 'pingback', 'wlwmanifest'):
        if soup.find('link', rel=rel):
            issues.append(('wp-discovery-link', f'<link rel="{rel}">'))

    if WP_SOURCEURL_RE.search(html):
        issues.append(('wp-host', f'sourceURL comment names {WP_HOST}'))
    else:
        for style in soup.find_all('style'):
            if style.string and WP_HOST in style.string:
                issues.append(('wp-host', f'{WP_HOST} inside a <style> block'))
                break
    for tag in soup.find_all(True):
        hit = next((a for a, v in tag.attrs.items()
                    if WP_HOST in (' '.join(v) if isinstance(v, list) else str(v))), None)
        if hit:
            issues.append(('wp-host', f'{WP_HOST} in <{tag.name} {hit}=…>'))
            break

    footer = soup.find('footer')
    if footer is not None:
        rows = len(soup.select('.jk-footer-row'))
        if rows != 1:
            issues.append(('footer', f'{rows} .jk-footer-row elements (expected 1)'))
        empty = [p for p in footer.find_all('p')
                 if not p.get_text(strip=True) and not p.find(['img', 'svg', 'picture', 'a'])]
        if empty:
            issues.append(('footer', f'{len(empty)} empty <p> in the footer'))

    return issues


def scan(site_dir, private_terms=(), public_terms=Config.PUBLIC_CONTENT_DENYLIST):
    """Return {rule: [(relative path, detail), ...]} for the whole build."""
    site = Path(site_dir)
    found = {}
    for path in sorted(site.rglob('*')):
        if not path.is_file():
            continue
        is_html = path.suffix == '.html'
        if not is_html and path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        issues = check_html(text) if is_html else check_text(text)
        issues += check_denylist(text, public_terms=public_terms, private_terms=private_terms)
        rel = str(path.relative_to(site))
        for rule, detail in issues:
            found.setdefault(rule, []).append((rel, detail))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('site_dir', help='built site directory, e.g. ./static-output')
    args = parser.parse_args()

    if not Path(args.site_dir).is_dir():
        print(f"❌ Not a directory: {args.site_dir}")
        sys.exit(1)

    found = scan(args.site_dir, private_terms=_terms_from_env())
    if not found:
        print("✅ No WordPress leftovers or denylisted words in the build")
        return

    total = sum(len(v) for v in found.values())
    print(f"❌ {total} content leak(s) in {args.site_dir}")
    for rule, hits in sorted(found.items()):
        print(f"\n  {rule}: {len(hits)} file(s)")
        for rel, detail in hits[:MAX_PER_RULE]:
            print(f"    {rel}: {detail}")
        if len(hits) > MAX_PER_RULE:
            print(f"    … and {len(hits) - MAX_PER_RULE} more")
        if os.environ.get('GITHUB_ACTIONS'):
            rel, detail = hits[0]
            print(f"::error title=Content leak ({rule})::{rel}: {detail}")
    sys.exit(1)


if __name__ == '__main__':
    main()
