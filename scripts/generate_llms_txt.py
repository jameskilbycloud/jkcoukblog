#!/usr/bin/env python3
"""
llms.txt generator

Produces a curated index of site content for LLM ingestion at
<output_dir>/llms.txt, following the llmstxt.org spec, plus an
optional full-content concatenation at <output_dir>/llms-full.txt.

Reads from the markdown export tree produced by
scripts/markdown_exporter.py (one .md per post with YAML frontmatter)
so this step assumes that has already run.

Usage:
    python3 scripts/generate_llms_txt.py <markdown_dir> <output_dir> [--with-full]

Example (used in CI):
    python3 scripts/generate_llms_txt.py ./static-output/markdown ./static-output --with-full
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
try:
    from config import Config
    TARGET_DOMAIN = Config.TARGET_DOMAIN.rstrip('/')
    HOMEPAGE_TITLE = getattr(Config, 'HOMEPAGE_TITLE', None) or 'James Kilby'
except ImportError:
    TARGET_DOMAIN = 'https://jameskilby.co.uk'
    HOMEPAGE_TITLE = 'James Kilby'

SITE_SUMMARY = (
    "Technical blog by James Kilby — VMware vExpert and Cloud / Infrastructure "
    "Architect. In-depth guides on VMware vSphere, VMware Cloud on AWS, homelab "
    "infrastructure, self-hosted AI, Cloudflare, Ansible, and storage."
)

# Maximum entries to surface under "Recent posts". The rest live under
# per-category sections further down.
RECENT_LIMIT = 12

# Minimum posts a category needs before it gets its own section. Below
# this they all fall through to "Other".
CATEGORY_MIN_POSTS = 2


def parse_post(md_file: Path) -> dict | None:
    """Read one .md file's frontmatter. Returns None if it can't be parsed."""
    try:
        text = md_file.read_text(encoding='utf-8')
    except OSError:
        return None
    m = re.match(r'^---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not m:
        return None
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None

    date = meta.get('date', '')
    if isinstance(date, datetime):
        date_str = date.strftime('%Y-%m-%d')
        sort_key = date.timestamp()
    elif isinstance(date, str) and date:
        try:
            sort_key = datetime.fromisoformat(date.replace('Z', '+00:00')).timestamp()
        except ValueError:
            sort_key = 0
        date_str = date[:10]
    else:
        date_str = ''
        sort_key = 0

    cats = meta.get('categories') or []
    if isinstance(cats, str):
        cats = [cats]
    cats = [c for c in cats if c]

    return {
        'slug': md_file.stem,
        'title': (meta.get('title') or '').strip(),
        'description': (meta.get('description') or '').strip(),
        'url': (meta.get('url') or '').strip(),
        'date': date_str,
        'sort_key': sort_key,
        'categories': cats,
        'markdown_path': f"/markdown/posts/{md_file.name}",
        'body': m.group(2).strip(),
    }


def format_entry(post: dict) -> str:
    """Format one post as a llms.txt bullet."""
    title = post['title'] or post['slug']
    url = post['url'] or f"{TARGET_DOMAIN}{post['markdown_path']}"
    desc = post['description'] or ''
    desc = re.sub(r'\s+', ' ', desc).strip()
    # Cap description to keep llms.txt scannable
    if len(desc) > 180:
        desc = desc[:177].rstrip() + '...'
    if desc:
        return f"- [{title}]({url}): {desc}"
    return f"- [{title}]({url})"


def group_by_category(posts: list[dict]) -> tuple[dict[str, list[dict]], list[dict]]:
    """Bucket posts by primary category. Posts whose category falls below
    CATEGORY_MIN_POSTS go to the 'Other' bucket (returned as the second
    tuple element).
    """
    buckets: dict[str, list[dict]] = {}
    for p in posts:
        cat = p['categories'][0] if p['categories'] else None
        if not cat:
            continue
        buckets.setdefault(cat, []).append(p)

    big = {c: ps for c, ps in buckets.items() if len(ps) >= CATEGORY_MIN_POSTS}
    small_cats = {c for c, ps in buckets.items() if len(ps) < CATEGORY_MIN_POSTS}
    other = [p for p in posts if not p['categories']
             or p['categories'][0] in small_cats]
    return big, other


def build_llms_txt(posts: list[dict], include_full_pointer: bool) -> str:
    """Build the llms.txt body."""
    out: list[str] = []
    out.append(f"# {HOMEPAGE_TITLE}")
    out.append("")
    out.append(f"> {SITE_SUMMARY}")
    out.append("")
    out.append(
        "All posts are also available as raw markdown under "
        f"`{TARGET_DOMAIN}/markdown/posts/<slug>.md` and as JSON under "
        f"`{TARGET_DOMAIN}/api/posts/<slug>.json`."
    )
    if include_full_pointer:
        out.append("")
        out.append(
            "The full content corpus (every post inlined) is available at "
            f"[{TARGET_DOMAIN}/llms-full.txt]({TARGET_DOMAIN}/llms-full.txt)."
        )
    out.append("")

    # Recent posts: top N by date
    by_date = sorted(posts, key=lambda p: p['sort_key'], reverse=True)
    if by_date:
        out.append("## Recent posts")
        out.append("")
        for p in by_date[:RECENT_LIMIT]:
            out.append(format_entry(p))
        out.append("")

    # Per-category sections (alphabetised for stability across builds)
    big_cats, other = group_by_category(posts)
    for cat in sorted(big_cats):
        out.append(f"## {cat}")
        out.append("")
        for p in sorted(big_cats[cat], key=lambda p: p['sort_key'], reverse=True):
            out.append(format_entry(p))
        out.append("")

    if other:
        out.append("## Other")
        out.append("")
        for p in sorted(other, key=lambda p: p['sort_key'], reverse=True):
            out.append(format_entry(p))
        out.append("")

    return '\n'.join(out).rstrip() + '\n'


def build_llms_full_txt(posts: list[dict]) -> str:
    """Build the llms-full.txt body: every post's full markdown inlined,
    sorted newest-first, separated by '---'.
    """
    out: list[str] = []
    out.append(f"# {HOMEPAGE_TITLE} — full content corpus")
    out.append("")
    out.append(f"> {SITE_SUMMARY}")
    out.append("")
    out.append(
        "Generated for LLM ingestion. Each section below is one post in full. "
        "See `/llms.txt` for the curated index. Each post's canonical URL is "
        "given in its heading; cite from there."
    )
    out.append("")
    out.append("---")
    out.append("")

    for p in sorted(posts, key=lambda p: p['sort_key'], reverse=True):
        title = p['title'] or p['slug']
        url = p['url'] or f"{TARGET_DOMAIN}{p['markdown_path']}"
        out.append(f"# {title}")
        out.append("")
        out.append(f"Source: {url}")
        if p['date']:
            out.append(f"Date: {p['date']}")
        if p['categories']:
            out.append(f"Categories: {', '.join(p['categories'])}")
        out.append("")
        out.append(p['body'])
        out.append("")
        out.append("---")
        out.append("")

    return '\n'.join(out).rstrip() + '\n'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('markdown_dir', help='Directory containing posts/*.md')
    ap.add_argument('output_dir', help='Directory to write llms.txt into')
    ap.add_argument('--with-full', action='store_true',
                    help='Also generate llms-full.txt (full content corpus)')
    args = ap.parse_args()

    markdown_dir = Path(args.markdown_dir)
    output_dir = Path(args.output_dir)
    posts_dir = markdown_dir / 'posts'

    if not posts_dir.is_dir():
        print(f"❌ posts directory not found: {posts_dir}")
        return 1

    posts = [p for p in (parse_post(f) for f in posts_dir.glob('*.md')) if p]
    if not posts:
        print(f"❌ no parsable posts in {posts_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    llms_path = output_dir / 'llms.txt'
    llms_path.write_text(
        build_llms_txt(posts, include_full_pointer=args.with_full),
        encoding='utf-8',
    )
    print(f"📝 Wrote {llms_path} ({len(posts)} posts indexed)")

    if args.with_full:
        full_path = output_dir / 'llms-full.txt'
        body = build_llms_full_txt(posts)
        full_path.write_text(body, encoding='utf-8')
        print(f"📚 Wrote {full_path} ({len(body):,} chars)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
