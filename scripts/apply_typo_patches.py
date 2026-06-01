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


def slug_candidates(url: str) -> list[str]:
    """Slug variants worth trying when the canonical one doesn't resolve.

    Some WP pages have a slug that drifts from their live URL (e.g. /about-me/
    might be 'about-me', 'about', 'about_me', etc.). We try a few obvious
    transforms.
    """
    primary = slug_from_url(url)
    if not primary:
        return []
    cands = [primary]
    # Underscore/hyphen swap
    if '-' in primary:
        cands.append(primary.replace('-', '_'))
    if '_' in primary:
        cands.append(primary.replace('_', '-'))
    # Compound first-token (e.g. 'about-me' -> 'about')
    if '-' in primary:
        cands.append(primary.split('-', 1)[0])
    # De-dupe, preserve order
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def is_post_url(url: str) -> bool:
    """Posts have a date prefix; pages do not. The homepage has no slug."""
    path = urlparse(url).path.rstrip('/')
    if not path:
        return False
    parts = path.strip('/').split('/')
    return len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit()


def _query_slug(session: requests.Session, kind: str, slug: str) -> int | None:
    """One slug lookup against /posts or /pages. Returns the post id or None."""
    # status: list-form filters across draft/publish/private/etc. — covers any
    # page state. The REST API accepts comma-separated values for this param.
    for status_arg in ('any', 'publish,draft,pending,private,future'):
        resp = session.get(f'{WP_URL}/wp-json/wp/v2/{kind}',
                           params={'slug': slug, 'context': 'edit', 'status': status_arg})
        if resp.status_code == 200:
            items = resp.json()
            if items:
                return items[0]['id']
    return None


def lookup_post_id(session: requests.Session, url: str) -> tuple[int | None, str]:
    """Find WP post or page ID. Returns (id, kind) where kind in {'posts','pages',''}.

    Tries the natural kind first (posts for /YYYY/MM/.../, pages for the rest),
    falls back to the other kind, and tries a small list of slug variants for
    drift cases like /about-me/ -> 'about'.
    """
    primary_kind = 'posts' if is_post_url(url) else 'pages'
    other_kind = 'pages' if primary_kind == 'posts' else 'posts'

    for slug in slug_candidates(url):
        for kind in (primary_kind, other_kind):
            post_id = _query_slug(session, kind, slug)
            if post_id is not None:
                return post_id, kind
    return None, ''


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


# Pairs of (rendered-HTML-character, WP-raw-character). When a find string
# from the audit (which came from rendered HTML) doesn't hit the raw content,
# try progressively rolling these back to widen the match. The replacement is
# transformed with the same rules so the resulting raw content stays in WP's
# native punctuation style.
_RENDERED_TO_RAW = [
    ('‘', "'"),   # left single curly quote → straight
    ('’', "'"),   # right single curly quote → straight (also apostrophe)
    ('“', '"'),   # left double curly → straight
    ('”', '"'),   # right double curly → straight
    ('—', '--'),  # em-dash → two hyphens (WP source typically uses --)
    ('–', '-'),   # en-dash → single hyphen
    ('…', '...'), # ellipsis → three dots
    ('\xa0', ' '),     # non-breaking space → regular
]


def _normalised_variants(s: str) -> Iterable[str]:
    """Yield candidate strings to try, ordered most-specific to most-loose."""
    yielded = set()

    def push(x):
        if x and x not in yielded:
            yielded.add(x)
            return x
        return None

    pushed = push(s)
    if pushed is not None: yield pushed
    # Strip trailing whitespace/newline noise from the find string (audit data
    # sometimes captured a trailing \n from the rendered body extraction).
    pushed = push(s.rstrip())
    if pushed is not None: yield pushed
    # Apply each transform individually then all-at-once.
    for rendered_ch, raw_ch in _RENDERED_TO_RAW:
        if rendered_ch in s:
            pushed = push(s.replace(rendered_ch, raw_ch))
            if pushed is not None: yield pushed
    # All transforms combined.
    s_all = s
    for rendered_ch, raw_ch in _RENDERED_TO_RAW:
        s_all = s_all.replace(rendered_ch, raw_ch)
    pushed = push(s_all)
    if pushed is not None: yield pushed
    pushed = push(s_all.rstrip())
    if pushed is not None: yield pushed


def _matching_variant(raw: str, s: str) -> str | None:
    """Find the first variant of s that occurs EXACTLY ONCE in raw. None if no unique match."""
    for variant in _normalised_variants(s):
        if raw.count(variant) == 1:
            return variant
    return None


def _apply_same_transform(find_original: str, find_variant: str, replace_original: str) -> str:
    """If we matched via a normalised variant, apply the same character transforms
    to the replacement so the post stays in WP's native punctuation style.
    """
    if find_variant == find_original:
        return replace_original
    # Detect which transforms were applied to find_original to produce find_variant
    # by running each one and seeing if the result is closer to find_variant. Simpler:
    # just apply all transforms whose 'from' is present in find_original but not in find_variant.
    out = replace_original
    if find_original.rstrip() == find_variant and find_original.endswith(('\n', ' ', '\t')):
        out = out.rstrip()
    for rendered_ch, raw_ch in _RENDERED_TO_RAW:
        if rendered_ch in find_original and rendered_ch not in find_variant:
            out = out.replace(rendered_ch, raw_ch)
    return out


def apply_patches_to_content(raw: str, patches: list[dict]) -> tuple[str, list[dict]]:
    """Apply find/replace patches to a single content string.

    Tries the raw find first, then progressively normalised variants
    (smart quotes, em-dashes, NBSP, trailing whitespace) to bridge the
    gap between rendered HTML and WP's raw editable content.

    Returns (new_content, results) where each result records what happened.
    """
    new = raw
    results = []
    for p in patches:
        find = p['find']
        replace = p['replace']
        variant = _matching_variant(new, find)
        result = {'find': find[:80], 'replace': replace[:80]}
        if variant is None:
            total = new.count(find)
            if total > 1:
                result.update(ok=False, reason=f'find appears {total} times in raw — refusing to bulk replace')
            else:
                result.update(ok=False, reason='find string (or any normalised variant) not present in raw content')
        else:
            adjusted_replace = _apply_same_transform(find, variant, replace)
            new = new.replace(variant, adjusted_replace, 1)
            result.update(ok=True, matched_via=('exact' if variant == find else 'normalised'))
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

    # Route each patch to whichever field actually contains it. The variant-aware
    # matcher tries the original find, then progressively normalised forms (smart
    # quotes / em-dash / NBSP / trailing whitespace), so we use it here too.
    def _present(field: str, p: dict) -> bool:
        return _matching_variant(field, p['find']) is not None

    content_patches, title_patches, excerpt_patches, not_found = [], [], [], []
    for p in patches:
        if _present(raw_content, p):
            content_patches.append(p)
        elif _present(raw_title, p):
            title_patches.append(p)
        elif _present(raw_excerpt, p):
            excerpt_patches.append(p)
        else:
            not_found.append(p)

    new_content, content_results = apply_patches_to_content(raw_content, content_patches)
    new_title, title_results = apply_patches_to_content(raw_title, title_patches)
    new_excerpt, excerpt_results = apply_patches_to_content(raw_excerpt, excerpt_patches)

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
