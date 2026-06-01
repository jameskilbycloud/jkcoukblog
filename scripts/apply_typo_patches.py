#!/usr/bin/env python3
"""Apply audit-derived typo fixes to WordPress source posts.

Reads `typo-patches.json` at the repo root (URL -> list of {find, replace, ...}),
fetches each post via the WP REST API in `context=edit` mode (raw content),
sanity-checks that each `find` string exists, applies the replacements, and
posts the updated content back to WordPress.

By default this runs in DRY-RUN mode (prints what would change). Pass --apply
to actually write changes.

Auth (env vars):
  WP_AUTH_TOKEN              REQUIRED for --apply. Base64 of "user:application-password" for the WP REST API.
  CF_ACCESS_CLIENT_ID        Optional. Cloudflare Access service-token client id (only needed off-runner).
  CF_ACCESS_CLIENT_SECRET    Optional. Cloudflare Access service-token client secret (only needed off-runner).

On the self-hosted runner, CF Access is handled at the network layer and these
two CF_ vars are NOT required — same auth pattern as wp_spell_check_and_fix.py.

Usage:
  python3 scripts/apply_typo_patches.py                       # dry-run (no changes)
  python3 scripts/apply_typo_patches.py --apply               # actually write to WP
  python3 scripts/apply_typo_patches.py --apply --url <URL>   # one post only
  python3 scripts/apply_typo_patches.py --limit 5             # first 5 posts (dry-run)
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
PATCHES_PATH = REPO_ROOT / 'typo-patches.json'

# Single source of truth for these URLs is scripts/config.py — kept inline here
# for runner-side portability (this script can run standalone).
WP_URL = 'https://wordpress.jameskilby.cloud'
TARGET_DOMAIN = 'https://jameskilby.co.uk'


def build_session(auth_token: str, cf_id: str | None, cf_secret: str | None) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        'Authorization': f'Basic {auth_token}',
        'User-Agent': 'apply-typo-patches/1.0',
        'Accept': 'application/json',
    })
    if cf_id and cf_secret:
        s.headers['CF-Access-Client-Id'] = cf_id
        s.headers['CF-Access-Client-Secret'] = cf_secret
    return s


def slug_from_url(url: str) -> str:
    """Extract the WordPress post slug from a /YYYY/MM/<slug>/ URL.

    For static pages (e.g. /about-me/) returns the path slug too.
    """
    path = urlparse(url).path.rstrip('/')
    if not path or path == '':
        return ''  # homepage — not a single post
    return path.rsplit('/', 1)[-1]


def is_post_url(url: str) -> bool:
    """Posts have a date prefix; pages do not. The homepage has no slug."""
    path = urlparse(url).path.rstrip('/')
    if not path:
        return False
    parts = path.strip('/').split('/')
    return len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit()


def lookup_post_id(session: requests.Session, url: str) -> tuple[int | None, str]:
    """Find WP post or page ID for a given live URL. Returns (id, kind) where kind in {'posts','pages',''}."""
    slug = slug_from_url(url)
    if not slug:
        return None, ''
    kind = 'posts' if is_post_url(url) else 'pages'
    resp = session.get(f'{WP_URL}/wp-json/wp/v2/{kind}',
                       params={'slug': slug, 'context': 'edit', 'status': 'any'})
    if resp.status_code != 200:
        # Fallback: try the other kind
        other = 'pages' if kind == 'posts' else 'posts'
        resp = session.get(f'{WP_URL}/wp-json/wp/v2/{other}',
                           params={'slug': slug, 'context': 'edit', 'status': 'any'})
        kind = other
    if resp.status_code != 200:
        return None, ''
    items = resp.json()
    if not items:
        return None, ''
    return items[0]['id'], kind


def fetch_raw_content(session: requests.Session, kind: str, post_id: int) -> dict:
    """GET the post in edit context, returning the raw editable fields."""
    resp = session.get(f'{WP_URL}/wp-json/wp/v2/{kind}/{post_id}', params={'context': 'edit'})
    resp.raise_for_status()
    return resp.json()


def update_post(session: requests.Session, kind: str, post_id: int, payload: dict) -> bool:
    resp = session.post(f'{WP_URL}/wp-json/wp/v2/{kind}/{post_id}', json=payload)
    if resp.status_code == 200:
        return True
    print(f'   ❌ WP update failed {resp.status_code}: {resp.text[:200]}', file=sys.stderr)
    return False


def apply_patches_to_content(raw: str, patches: list[dict]) -> tuple[str, list[dict]]:
    """Apply find/replace patches to a single content string.

    Returns (new_content, results) where each result has {find, ok, occurrences_in_raw}.
    """
    new = raw
    results = []
    for p in patches:
        find = p['find']
        replace = p['replace']
        n = new.count(find)
        result = {'find': find[:80], 'replace': replace[:80], 'occurrences_in_raw': n}
        if n == 0:
            result['ok'] = False
            result['reason'] = 'find string not present in raw content'
        elif n > 1:
            result['ok'] = False
            result['reason'] = f'find appears {n} times — refusing to bulk replace (potentially ambiguous)'
        else:
            new = new.replace(find, replace, 1)
            result['ok'] = True
        results.append(result)
    return new, results


def process_url(session: requests.Session, url: str, patches: list[dict],
                apply_changes: bool) -> dict:
    print(f'\n=== {url} ({len(patches)} patch{"es" if len(patches) != 1 else ""}) ===')
    post_id, kind = lookup_post_id(session, url)
    if not post_id:
        print(f'   ❌ could not resolve to a WP post/page (slug={slug_from_url(url)})')
        return {'url': url, 'resolved': False, 'applied': 0, 'skipped': len(patches)}

    print(f'   → {kind} id={post_id}')
    post = fetch_raw_content(session, kind, post_id)
    raw_content = (post.get('content') or {}).get('raw') or ''
    raw_title = (post.get('title') or {}).get('raw') or ''
    raw_excerpt = (post.get('excerpt') or {}).get('raw') or ''

    # Try patches against content first, then fall back to title/excerpt if not found there.
    content_patches, leftover = [], []
    for p in patches:
        if raw_content.count(p['find']) >= 1:
            content_patches.append(p)
        else:
            leftover.append(p)

    new_content, content_results = apply_patches_to_content(raw_content, content_patches)
    new_title, title_results = apply_patches_to_content(raw_title, [p for p in leftover if raw_title.count(p['find']) >= 1])
    new_excerpt, excerpt_results = apply_patches_to_content(raw_excerpt, [p for p in leftover if raw_excerpt.count(p['find']) >= 1])

    # What patches remain unfound anywhere?
    found_finds = {r['find'][:80] for r in content_results + title_results + excerpt_results if r.get('ok')}
    not_found = [p for p in patches if p['find'][:80] not in found_finds and (raw_content.count(p['find']) + raw_title.count(p['find']) + raw_excerpt.count(p['find'])) == 0]

    applied = sum(1 for r in content_results + title_results + excerpt_results if r.get('ok'))
    skipped = len(patches) - applied
    print(f'   ✓ found-and-applied (in memory): {applied}')
    print(f'   ⚠ skipped: {skipped}')
    for r in content_results + title_results + excerpt_results:
        if not r.get('ok'):
            print(f'     - SKIP: {r["find"]!r}  reason={r.get("reason")}')
    for p in not_found:
        print(f'     - NOT FOUND in title/excerpt/content: {p["find"][:80]!r}')

    if applied == 0:
        print('   (nothing to write back)')
        return {'url': url, 'resolved': True, 'applied': 0, 'skipped': skipped}

    payload = {}
    if new_content != raw_content: payload['content'] = new_content
    if new_title != raw_title: payload['title'] = new_title
    if new_excerpt != raw_excerpt: payload['excerpt'] = new_excerpt

    if not apply_changes:
        print(f'   [DRY RUN] would POST {list(payload.keys())} to WP')
    else:
        print(f'   → POSTing {list(payload.keys())} to WP...')
        ok = update_post(session, kind, post_id, payload)
        if not ok:
            return {'url': url, 'resolved': True, 'applied': 0, 'skipped': skipped, 'wp_error': True}
        print('   ✅ written')
        time.sleep(0.5)  # be polite

    return {'url': url, 'resolved': True, 'applied': applied, 'skipped': skipped}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='actually write changes to WordPress')
    ap.add_argument('--url', help='process one URL only')
    ap.add_argument('--limit', type=int, default=0, help='process at most N URLs (0 = all)')
    args = ap.parse_args()

    if not PATCHES_PATH.exists():
        print(f'No patch file at {PATCHES_PATH}', file=sys.stderr)
        return 1

    patches_by_url: dict[str, list[dict]] = json.loads(PATCHES_PATH.read_text())
    urls = list(patches_by_url.keys())
    if args.url:
        if args.url not in patches_by_url:
            print(f'URL {args.url} not in patch file', file=sys.stderr)
            return 1
        urls = [args.url]
    if args.limit:
        urls = urls[:args.limit]

    auth = os.environ.get('WP_AUTH_TOKEN', '')
    cf_id = os.environ.get('CF_ACCESS_CLIENT_ID', '')
    cf_secret = os.environ.get('CF_ACCESS_CLIENT_SECRET', '')

    if args.apply and not auth:
        print('❌ --apply requires the WP_AUTH_TOKEN env var', file=sys.stderr)
        return 2

    session = build_session(auth, cf_id, cf_secret)

    print(f'Mode: {"APPLY (writing to WP)" if args.apply else "DRY RUN"}')
    print(f'Target: {WP_URL}')
    print(f'URLs to process: {len(urls)}')

    results = []
    for url in urls:
        try:
            results.append(process_url(session, url, patches_by_url[url], args.apply))
        except Exception as e:
            print(f'   💥 exception on {url}: {e}', file=sys.stderr)
            results.append({'url': url, 'resolved': False, 'applied': 0, 'skipped': len(patches_by_url[url]), 'error': str(e)})

    total_applied = sum(r['applied'] for r in results)
    total_skipped = sum(r['skipped'] for r in results)
    resolved = sum(1 for r in results if r.get('resolved'))
    print()
    print('=' * 60)
    print(f'Posts processed:    {len(results)}')
    print(f'Posts resolved:     {resolved}')
    print(f'Patches {"APPLIED" if args.apply else "would-apply"}: {total_applied}')
    print(f'Patches skipped:    {total_skipped}')
    print('=' * 60)

    # Always save a log
    log_path = REPO_ROOT / 'typo-patches-applied.log.json'
    log_path.write_text(json.dumps(results, indent=2))
    print(f'log: {log_path}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
