#!/usr/bin/env python3
"""
SEO quality validator — runs at the end of the build, before deployment.

Catches the specific class of bugs that put pages into Google's
"Crawled — currently not indexed" bucket:

  - <title> chopped with a literal "..." (the bug that affected
    42 of 72 post pages until fix_seo_issues was repaired)
  - <title> / meta description missing or empty on post pages
  - <meta name="description"> chopped with a literal "..."
  - More than one <title> or <h1> tag
  - JSON-LD that can't be parsed
  - Canonical URL missing on post pages
  - noindex on a page that isn't a tag/archive

Errors fail the build. Warnings show in the summary but don't fail.

Usage:
    python3 scripts/validate_seo.py [public_dir]
"""

import json
import sys
import re
from collections import defaultdict
from pathlib import Path

from bs4 import BeautifulSoup


# ── thresholds ───────────────────────────────────────────────────────────────
# Tuned against the post-fix baseline. Tighten as content quality improves;
# every threshold should map to a documented Google quality signal, not just
# a personal preference.
TITLE_MIN_LEN          = 15    # under this is suspicious (auto-generated?)
# Google's SERP title pixel budget is ~580px, which works out to roughly
# 55-65 characters depending on character mix (i, l vs M, W). 65 is the
# pragmatic threshold — anything past gets display-truncated and Google
# may rewrite the title in SERPs, so the declared title is not what users
# actually see. Previous threshold (80) let titles slip through that were
# guaranteed to be rewritten. Warnings here are non-failing.
TITLE_MAX_LEN          = 65
META_DESC_MIN_LEN      = 50
META_DESC_MAX_LEN      = 200
THIN_CONTENT_WORDS     = 150   # post pages under this are flagged warn

# Globs that we treat as post pages (the "Article" form factor) where
# canonical, description, h1, and JSON-LD are all required. Other pages
# (homepage, archive list pages, tag/category) get a looser check.
POST_PATH_RE = re.compile(r'/20\d{2}/\d{2}/[^/]+/index\.html$')

# Pages we deliberately skip — these are non-content artefacts.
SKIP_PATH_PARTS = (
    '/markdown/',  # plain-text mirrors
    '/api/',       # JSON endpoints
    '/changelog/', # auto-generated changelog
    '/evs/',       # raw event log
    '/feed/',      # RSS XML doesn't need SEO meta
)


class Issue:
    """An SEO problem discovered in a page. Severity decides build outcome."""

    __slots__ = ('severity', 'category', 'detail', 'path')

    def __init__(self, severity: str, category: str, detail: str, path: Path):
        assert severity in ('error', 'warning')
        self.severity = severity
        self.category = category
        self.detail = detail
        self.path = path

    def __str__(self) -> str:
        return f'{self.severity.upper():7}  {self.category:30}  {self.path}  — {self.detail}'


def _is_post_page(rel_path: str) -> bool:
    return bool(POST_PATH_RE.search(rel_path))


def _skipped(rel_path: str) -> bool:
    return any(part in rel_path for part in SKIP_PATH_PARTS)


def validate_page(html_path: Path, public_dir: Path) -> list:
    """Audit a single HTML file. Returns a list of Issue."""
    rel = '/' + str(html_path.relative_to(public_dir)).replace('\\', '/')
    if _skipped(rel):
        return []

    try:
        soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    except Exception as exc:
        return [Issue('error', 'parse-failure', f'BeautifulSoup raised {exc!r}', html_path)]

    issues = []
    is_post = _is_post_page(rel)

    # ── <title> ──────────────────────────────────────────────────────────────
    # SVG icons embed their own <title> tags for accessibility; only count
    # the document-level <title> inside <head>.
    titles = (
        soup.head.find_all('title', recursive=False)
        if soup.head else []
    )
    if not titles:
        issues.append(Issue('error', 'title-missing', 'no <title> tag in <head>', html_path))
    else:
        if len(titles) > 1:
            issues.append(Issue('error', 'title-duplicate',
                                f'page has {len(titles)} <title> tags', html_path))
        title_text = (titles[0].get_text() or '').strip()
        if not title_text:
            issues.append(Issue('error', 'title-empty', 'title is empty', html_path))
        else:
            if title_text.endswith('...'):
                issues.append(Issue('error', 'title-truncated-ellipsis',
                                    f'title literally ends in "..." — Google reads this as broken content. Source: {title_text!r}',
                                    html_path))
            if len(title_text) < TITLE_MIN_LEN:
                issues.append(Issue('warning', 'title-too-short',
                                    f'len={len(title_text)} (<{TITLE_MIN_LEN}): {title_text!r}',
                                    html_path))
            if len(title_text) > TITLE_MAX_LEN:
                issues.append(Issue('warning', 'title-too-long',
                                    f'len={len(title_text)} (>{TITLE_MAX_LEN}); Google will display-truncate',
                                    html_path))

    # ── <meta name="description"> ─────────────────────────────────────────────
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta is None:
        # Description is critical for post pages; optional elsewhere.
        sev = 'error' if is_post else 'warning'
        issues.append(Issue(sev, 'meta-description-missing',
                            'no <meta name="description"> tag', html_path))
    else:
        desc = (meta.get('content') or '').strip()
        if not desc:
            issues.append(Issue('error', 'meta-description-empty',
                                'description attribute is empty', html_path))
        else:
            if desc.endswith('...'):
                issues.append(Issue('error', 'meta-description-truncated-ellipsis',
                                    f'description literally ends in "..." — looks auto-truncated. Source: {desc!r}',
                                    html_path))
            if len(desc) < META_DESC_MIN_LEN:
                issues.append(Issue('warning', 'meta-description-too-short',
                                    f'len={len(desc)} (<{META_DESC_MIN_LEN})', html_path))
            if len(desc) > META_DESC_MAX_LEN:
                issues.append(Issue('warning', 'meta-description-too-long',
                                    f'len={len(desc)} (>{META_DESC_MAX_LEN})', html_path))

    # ── canonical URL ────────────────────────────────────────────────────────
    canonical = soup.find('link', rel='canonical')
    if canonical is None and is_post:
        issues.append(Issue('error', 'canonical-missing',
                            'post page has no <link rel="canonical">', html_path))

    # ── h1 ───────────────────────────────────────────────────────────────────
    h1s = soup.find_all('h1')
    if is_post:
        if not h1s:
            issues.append(Issue('error', 'h1-missing', 'post page has no <h1>', html_path))
        elif len(h1s) > 1:
            issues.append(Issue('error', 'h1-duplicate',
                                f'post page has {len(h1s)} <h1> tags', html_path))

    # ── JSON-LD parseability ─────────────────────────────────────────────────
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            json.loads(script.string or '')
        except Exception as exc:
            issues.append(Issue('error', 'jsonld-parse-error',
                                f'JSON-LD block failed to parse: {exc}', html_path))
            break  # one bad block is enough to surface

    # ── robots noindex on a post page ────────────────────────────────────────
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots and is_post:
        content = (robots.get('content') or '').lower()
        if 'noindex' in content:
            issues.append(Issue('error', 'noindex-on-post',
                                f'robots="{content}" on a post page — page will not be indexed',
                                html_path))

    # ── og:title / og:description / og:image ─────────────────────────────────
    # These power social-share previews. Missing them is a warn, not an error.
    if is_post:
        for og_key in ('og:title', 'og:description', 'og:image'):
            if not soup.find('meta', attrs={'property': og_key}):
                issues.append(Issue('warning', 'og-tag-missing',
                                    f'no <meta property="{og_key}">', html_path))

    # ── thin content ─────────────────────────────────────────────────────────
    if is_post:
        article = soup.find('article') or soup.find('main')
        if article:
            body_text = article.get_text(' ', strip=True)
            word_count = len(body_text.split())
            if word_count < THIN_CONTENT_WORDS:
                issues.append(Issue('warning', 'thin-content',
                                    f'~{word_count} words in <article> (<{THIN_CONTENT_WORDS}) — Google may treat as low-value',
                                    html_path))

    return issues


def main(argv):
    public_dir = Path(argv[1] if len(argv) > 1 else 'public').resolve()
    if not public_dir.is_dir():
        print(f'❌ {public_dir} is not a directory', file=sys.stderr)
        return 2

    html_files = sorted(public_dir.rglob('index.html')) + sorted(public_dir.rglob('*.html'))
    # rglob('index.html') and rglob('*.html') overlap — dedupe.
    html_files = sorted(set(html_files))

    print(f'🔍 Validating SEO on {len(html_files)} HTML files in {public_dir}')
    all_issues: list = []
    for f in html_files:
        all_issues.extend(validate_page(f, public_dir))

    errors    = [i for i in all_issues if i.severity == 'error']
    warnings  = [i for i in all_issues if i.severity == 'warning']

    # Group by category so the report stays readable.
    by_cat: dict = defaultdict(list)
    for issue in all_issues:
        by_cat[(issue.severity, issue.category)].append(issue)

    print()
    print('=' * 70)
    print('📊 SEO VALIDATION SUMMARY')
    print('=' * 70)
    print(f'📄 HTML files checked:    {len(html_files)}')
    print(f'❌ Errors:                {len(errors)}')
    print(f'⚠️  Warnings:              {len(warnings)}')
    print()

    if all_issues:
        print('--- by category ---')
        for (sev, cat), items in sorted(by_cat.items()):
            print(f'  {sev:8}  {cat:35}  {len(items)} page(s)')
        print()

    if errors:
        print('🚨 ERRORS — these will fail the build:')
        # Print first N per category so the log doesn't explode on a wide breakage.
        seen_cat: dict = defaultdict(int)
        for issue in errors:
            seen_cat[issue.category] += 1
            if seen_cat[issue.category] <= 5:
                print(f'   • {issue}')
            elif seen_cat[issue.category] == 6:
                # Count the rest silently.
                print(f'   ... (more {issue.category} errors suppressed)')

    if warnings:
        print()
        print('⚠️  WARNINGS — visible, not failing:')
        seen_cat = defaultdict(int)
        for issue in warnings:
            seen_cat[issue.category] += 1
            if seen_cat[issue.category] <= 3:
                print(f'   • {issue}')
            elif seen_cat[issue.category] == 4:
                print(f'   ... (more {issue.category} warnings suppressed)')

    print()
    if errors:
        print(f'❌ SEO validation failed ({len(errors)} error(s))')
        return 1
    print('✅ SEO validation passed')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
