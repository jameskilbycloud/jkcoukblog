#!/usr/bin/env python3
"""
Inline path-manifest.json into public/_worker.js at deploy time.

The Advanced Mode Worker template (_worker.template.js) contains the
placeholder:

    const PATH_MANIFEST_RAW = /*__PATH_MANIFEST_START__*/null/*__PATH_MANIFEST_END__*/;

This script replaces `null` with a JS array literal of every legitimate
content path, then writes the result to public/_worker.js.  That replaces
the `cp _worker.template.js public/_worker.js` step in the deploy workflow.

Usage:
    python3 scripts/stamp_worker_manifest.py
    python3 scripts/stamp_worker_manifest.py <public_dir>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = Path(
    sys.argv[1] if len(sys.argv) > 1 else REPO_ROOT / "public"
).resolve()
TEMPLATE = REPO_ROOT / "_worker.template.js"
OUTPUT = PUBLIC_DIR / "_worker.js"
MANIFEST = PUBLIC_DIR / "path-manifest.json"

PLACEHOLDER_RE = re.compile(
    r"/\*__PATH_MANIFEST_START__\*/.*?/\*__PATH_MANIFEST_END__\*/",
    re.DOTALL,
)


def main() -> int:
    if not TEMPLATE.exists():
        print(f"❌ {TEMPLATE} not found", file=sys.stderr)
        return 1
    if not MANIFEST.exists():
        print(
            f"❌ {MANIFEST} not found — run scripts/generate_soft404_artefacts.py first",
            file=sys.stderr,
        )
        return 1

    paths = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(paths, list) or not paths:
        print(f"❌ {MANIFEST} is empty or malformed", file=sys.stderr)
        return 1

    source = TEMPLATE.read_text(encoding="utf-8")
    if not PLACEHOLDER_RE.search(source):
        print(
            "❌ placeholder /*__PATH_MANIFEST_START__*/…/*__PATH_MANIFEST_END__*/ "
            "not found in _worker.template.js — template was edited without "
            "preserving the injection point",
            file=sys.stderr,
        )
        return 1

    literal = json.dumps(paths, separators=(",", ":"))
    stamped = PLACEHOLDER_RE.sub(
        f"/*__PATH_MANIFEST_START__*/{literal}/*__PATH_MANIFEST_END__*/",
        source,
        count=1,
    )

    OUTPUT.write_text(stamped, encoding="utf-8")
    print(
        f"✅ _worker.js stamped: {len(paths)} paths baked in "
        f"({len(literal)} bytes of manifest, {len(stamped)} bytes total) → {OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
