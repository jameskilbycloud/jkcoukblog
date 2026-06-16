#!/usr/bin/env python3
"""SEO drift baseline — catch silent regressions on unattended auto-deploys.

`main` regenerates `public/` and pushes it without a human in the loop, so a
pipeline bug (a step that stops emitting canonicals, a reintroduced
wordpress.jameskilby.cloud leak, a lost Article schema, a broken title policy)
can ship silently. This tool snapshots **policy-driven** SEO signals — the ones
the pipeline controls, not the ones content edits legitimately change — for the
homepage and every post page, then diffs a later build against that baseline.

Signals are deliberately structural (booleans / counts / type-sets), NOT raw
text: a meta description changing because the post was edited is not drift; a
post *losing* its meta description is.

Usage:
    python3 scripts/drift_baseline.py --snapshot public            # write baseline
    python3 scripts/drift_baseline.py --check public               # diff vs baseline
    python3 scripts/drift_baseline.py --check public --strict      # exit 1 on drift

Default baseline path: docs/seo-audit-2026-06/seo-baseline.json (override --baseline).
The `--check` run is non-blocking by default (exit 0, prints drift) so it can sit
in the deploy workflow without failing production; pass --strict to gate hard.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from config import Config
    TARGET_DOMAIN = Config.TARGET_DOMAIN
    HOMEPAGE_TITLE = getattr(Config, 'HOMEPAGE_TITLE', None)
    WP_HOST = (getattr(Config, 'WP_URL', '') or '').replace('https://', '').replace('http://', '').rstrip('/')
except (ImportError, AttributeError):
    TARGET_DOMAIN = 'https://jameskilby.co.uk'
    HOMEPAGE_TITLE = None
    WP_HOST = 'wordpress.jameskilby.cloud'

DEFAULT_BASELINE = 'docs/seo-audit-2026-06/seo-baseline.json'
_POST_PATH_RE = re.compile(r'^/\d{4}/\d{2}/[^/]+/$')


def _jsonld_types(soup):
    """Collected, de-duplicated, sorted set of JSON-LD @type values on the page."""
    types = set()

    def collect(node):
        if isinstance(node, dict):
            t = node.get('@type')
            for tt in (t if isinstance(t, list) else [t]):
                if isinstance(tt, str):
                    types.add(tt)
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for v in node:
                collect(v)

    for script in soup.find_all('script', type='application/ld+json'):
        raw = script.string or ''
        if not raw.strip():
            continue
        try:
            collect(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return sorted(types)


def extract_signals(html):
    """Derive the policy-driven SEO signals for one HTML document. Pure."""
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('title')
    title_text = title.get_text(strip=True) if title else ''

    canonical = soup.find('link', rel='canonical')
    canonical_href = canonical.get('href', '') if canonical else ''

    robots = soup.find('meta', attrs={'name': 'robots'})
    robots_content = (robots.get('content', '') if robots else '').lower()

    def has_meta(attr, val):
        return soup.find('meta', attrs={attr: val}) is not None

    return {
        'title_len': len(title_text),
        'title_has_brand_suffix': title_text.endswith('James Kilby'),
        'h1_count': len(soup.find_all('h1')),
        'has_canonical': bool(canonical_href),
        'canonical_absolute': canonical_href.startswith(TARGET_DOMAIN),
        'has_meta_description': has_meta('name', 'description'),
        'has_og_title': has_meta('property', 'og:title'),
        'has_og_description': has_meta('property', 'og:description'),
        'has_og_image': has_meta('property', 'og:image'),
        'has_twitter_card': has_meta('name', 'twitter:card'),
        'robots_noindex': 'noindex' in robots_content,
        'jsonld_types': _jsonld_types(soup),
        'wp_host_leak': bool(WP_HOST) and WP_HOST in html,
    }


def _path_for(index_html, root):
    """Map public/2024/10/foo/index.html → '/2024/10/foo/' (homepage → '/')."""
    rel = index_html.parent.relative_to(root).as_posix()
    return '/' if rel == '.' else f'/{rel}/'


def _selected_pages(root):
    """Homepage + every post-shaped page in the build, keyed by URL path."""
    pages = {}
    for index_html in sorted(root.rglob('index.html')):
        path = _path_for(index_html, root)
        if path == '/' or _POST_PATH_RE.match(path):
            pages[path] = index_html
    return pages


def build_snapshot(root):
    pages = _selected_pages(root)
    signals = {}
    for path, index_html in pages.items():
        try:
            signals[path] = extract_signals(index_html.read_text(encoding='utf-8'))
        except OSError as e:
            print(f"  ⚠️  could not read {index_html}: {e}", file=sys.stderr)
    return {
        'target_domain': TARGET_DOMAIN,
        'homepage_title': HOMEPAGE_TITLE,
        'page_count': len(signals),
        'pages': signals,
    }


def diff_signals(old, new):
    """Per-page signal diff. Returns {path: {signal: [old, new]}} for changed
    signals only, plus the set of paths missing from the new build."""
    drifted = {}
    missing = []
    for path, old_sig in old.items():
        new_sig = new.get(path)
        if new_sig is None:
            missing.append(path)
            continue
        changes = {
            k: [old_sig.get(k), new_sig.get(k)]
            for k in old_sig
            if old_sig.get(k) != new_sig.get(k)
        }
        if changes:
            drifted[path] = changes
    return drifted, missing


def _check(root, baseline_path, strict):
    if not baseline_path.exists():
        print(f"❌ No baseline at {baseline_path}. Run with --snapshot first.", file=sys.stderr)
        return 1
    baseline = json.loads(baseline_path.read_text())
    current = build_snapshot(root)

    drifted, missing = diff_signals(baseline.get('pages', {}), current['pages'])
    new_paths = sorted(set(current['pages']) - set(baseline.get('pages', {})))

    print(f"Checked {current['page_count']} pages against baseline "
          f"({baseline.get('page_count', 0)} pages).\n")

    if not drifted and not missing:
        print("🟢 No SEO drift on existing pages.")
    else:
        for path in sorted(drifted):
            print(f"  ⚠️  drift: {path}")
            for signal, (was, now) in sorted(drifted[path].items()):
                print(f"        {signal}: {was!r} → {now!r}")
        for path in missing:
            print(f"  ⚠️  gone from build: {path}")
        print(f"\n{len(drifted)} page(s) drifted, {len(missing)} page(s) removed.")

    if new_paths:
        print(f"\nℹ️  {len(new_paths)} new page(s) not yet in baseline "
              f"(run --snapshot to adopt). e.g. {new_paths[0]}")

    has_drift = bool(drifted or missing)
    if has_drift and strict:
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--snapshot', action='store_true', help='write a fresh baseline')
    mode.add_argument('--check', action='store_true', help='diff current build vs baseline')
    parser.add_argument('root', nargs='?', default='public',
                        help='built site directory (default: public)')
    parser.add_argument('--baseline', default=DEFAULT_BASELINE,
                        help=f'baseline JSON path (default: {DEFAULT_BASELINE})')
    parser.add_argument('--strict', action='store_true',
                        help='with --check, exit non-zero when drift is found')
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"❌ {root} is not a directory.", file=sys.stderr)
        return 1
    baseline_path = Path(args.baseline)

    if args.snapshot:
        snapshot = build_snapshot(root)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n')
        print(f"📄 Wrote baseline for {snapshot['page_count']} pages → {baseline_path}")
        return 0

    return _check(root, baseline_path, args.strict)


if __name__ == '__main__':
    sys.exit(main())
