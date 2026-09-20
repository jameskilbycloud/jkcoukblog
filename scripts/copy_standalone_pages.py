#!/usr/bin/env python3
"""
Copy standalone pages into the built site.

Why this exists
---------------
Some pages are self-contained static apps (single HTML file, inline JS/CSS,
no WordPress content and no dependency on the site theme). The VMC analyzer
tool at `/vmc-analyzer/` is the first of these.

They must NOT go through the normal HTML pipeline: `html_transformer.py`
(critical-CSS extraction, picture conversion, head dedup, minify) and the
search-script / power-widget injection all assume a WordPress-shaped page and
would rewrite or break a self-contained app. The generator's own asset copy
runs *before* those transforms, so anything it writes gets processed.

So this script runs LATE — after every HTML transform, before compression —
and copies the standalone tree verbatim into the output. Nothing downstream
parses these files as site pages, and because they are added after the
sitemap and search index are built they stay out of both (intentional: these
tools are linked deliberately, not discovered).

Source: scripts/standalone/<path>  ->  <output_dir>/<path>

Usage:
    python3 scripts/copy_standalone_pages.py ./static-output
"""

import shutil
import sys
from pathlib import Path

SRC = Path(__file__).parent / "standalone"


def copy_standalone_pages(output_dir):
    output_dir = Path(output_dir)
    if not SRC.exists():
        print(f"   ℹ️  No standalone directory at {SRC} — nothing to copy")
        return 0

    files = [p for p in SRC.rglob("*") if p.is_file()]
    if not files:
        print(f"   ℹ️  {SRC} is empty — nothing to copy")
        return 0

    copied = 0
    for src in files:
        rel = src.relative_to(SRC)
        dest = output_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied += 1
        print(f"   ✅ {rel} -> {dest}")

    print(f"   📁 Copied {copied} standalone file(s) into {output_dir}")
    return copied


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "./static-output"
    print("📄 Copying standalone pages...")
    copy_standalone_pages(out)
