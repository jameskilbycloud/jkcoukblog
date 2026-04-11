#!/usr/bin/env python3
"""
One-shot cleanup script: removes duplicate resource hint tags that accumulated
in public/ HTML files due to a bug in extract_critical_css.py being applied on
every pipeline run without idempotency guards.

Strategy (operates only within <head>):
  1. Strip ALL <noscript> blocks — they're exclusively CSS fallbacks and all
     the accumulated ones are either duplicates or have been left empty.
  2. Deduplicate <link> tags by href — keep the first occurrence of each.
  3. Rebuild exactly ONE correct noscript fallback after each async-CSS
     preload link (<link rel="preload" as="style" onload="..."  href="...">).

Safe to re-run: files are only written if they actually changed.
"""

import re
import sys
from pathlib import Path

# Matches any <noscript>...</noscript> block (including nested / empty ones).
# We strip ALL of these from <head> — they are only ever CSS fallbacks there.
_NOSCRIPT_RE = re.compile(r'<noscript\b[^>]*>.*?</noscript>', re.IGNORECASE | re.DOTALL)

# Matches a self-closing or void <link> tag.
_LINK_RE = re.compile(r'<link\b[^>]*/?\s*>', re.IGNORECASE | re.DOTALL)

# Extracts the href from a tag string.
_HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.IGNORECASE)

# Detects an async-CSS preload link (the ones that need a noscript fallback).
# Attributes can appear in any order, so use three independent lookaheads.
_ASYNC_CSS_RE = re.compile(
    r'(?=.*\brel=["\']preload["\'])(?=.*\bas=["\']style["\'])(?=.*\bonload=)',
    re.IGNORECASE | re.DOTALL,
)


def _clean_head(head_body: str) -> tuple:
    """Return (cleaned_head_body, removed_count)."""
    original = head_body

    # ── 1. Strip all <noscript> blocks ────────────────────────────────────
    head_body = _NOSCRIPT_RE.sub('', head_body)

    # ── 2. Deduplicate <link> tags by href ────────────────────────────────
    seen_hrefs: set = set()
    kept_links = []
    dedup_removals = 0

    def _dedup_link(m):
        tag = m.group(0)
        href_m = _HREF_RE.search(tag)
        if not href_m:
            return tag  # no href — keep as-is (e.g. rel=canonical without href is unusual but safe)
        href = href_m.group(1)
        if href in seen_hrefs:
            nonlocal dedup_removals
            dedup_removals += 1
            return ''
        seen_hrefs.add(href)
        return tag

    head_body = _LINK_RE.sub(_dedup_link, head_body)

    # ── 3. Rebuild one noscript fallback per async-CSS preload link ────────
    def _add_noscript(m):
        tag = m.group(0)
        if not _ASYNC_CSS_RE.search(tag):
            return tag
        href_m = _HREF_RE.search(tag)
        if not href_m:
            return tag
        href = href_m.group(1)
        fallback = f'<noscript><link rel="stylesheet" href="{href}"/></noscript>'
        return tag + fallback

    head_body = _LINK_RE.sub(_add_noscript, head_body)

    # ── 4. Collapse blank lines ────────────────────────────────────────────
    head_body = re.sub(r'\n{3,}', '\n\n', head_body)

    removed = len(original) - len(head_body)  # rough size reduction
    changed = head_body != original
    return head_body, changed


def clean_file(file_path: Path) -> bool:
    html = file_path.read_text(encoding='utf-8', errors='replace')

    head_match = re.search(
        r'(<head\b[^>]*>)(.*?)(</head>)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not head_match:
        return False

    before_head = html[:head_match.start()]
    head_open   = head_match.group(1)
    head_body   = head_match.group(2)
    head_close  = head_match.group(3)
    after_head  = html[head_match.end():]

    cleaned_head, changed = _clean_head(head_body)
    if not changed:
        return False

    file_path.write_text(
        before_head + head_open + cleaned_head + head_close + after_head,
        encoding='utf-8',
    )
    return True


def main():
    public_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('public')
    html_files = list(public_dir.rglob('*.html'))
    print(f"🧹 Scanning {len(html_files)} HTML files for duplicate resource hints…")

    fixed = 0
    for f in html_files:
        try:
            if clean_file(f):
                fixed += 1
        except Exception as e:
            print(f"  ⚠️  {f.relative_to(public_dir)}: {e}")

    print(f"✅ Cleaned {fixed} / {len(html_files)} files")


if __name__ == '__main__':
    main()
