#!/usr/bin/env python3
"""
Inline build-time data into public/_worker.js at deploy time.

The Advanced Mode Worker template (_worker.template.js) contains two
placeholders that this script replaces:

    const PATH_MANIFEST_RAW = /*__PATH_MANIFEST_START__*/null/*__PATH_MANIFEST_END__*/;
    const CSP_FROM_HEADERS = /*__CSP_FROM_HEADERS_START__*/null/*__CSP_FROM_HEADERS_END__*/;

* PATH_MANIFEST_RAW gets a JS array literal of every legitimate content
  path (read from <public>/path-manifest.json, produced by
  scripts/generate_soft404_artefacts.py).
* CSP_FROM_HEADERS gets a JS string literal of the Content-Security-Policy
  line read from the repo-root `_headers` file. Cloudflare Pages only
  applies `_headers` rules to responses fetched via env.ASSETS — `Response`
  objects built inside _worker.js (e.g. the KV-cached HTML path) skip those
  rules, so the worker must emit CSP itself. `_headers` stays the single
  source of truth; the worker just consumes it at build time.

This replaces the `cp _worker.template.js public/_worker.js` step in the
deploy workflow.

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
HEADERS_FILE = REPO_ROOT / "_headers"

PATH_PLACEHOLDER_RE = re.compile(
    r"/\*__PATH_MANIFEST_START__\*/.*?/\*__PATH_MANIFEST_END__\*/",
    re.DOTALL,
)
CSP_PLACEHOLDER_RE = re.compile(
    r"/\*__CSP_FROM_HEADERS_START__\*/.*?/\*__CSP_FROM_HEADERS_END__\*/",
    re.DOTALL,
)
# Matches the global `/*` block's Content-Security-Policy line in _headers.
CSP_LINE_RE = re.compile(
    r"^\s*Content-Security-Policy:\s*(.+)$",
    re.MULTILINE,
)


def extract_csp() -> str | None:
    """Read the Content-Security-Policy value from the repo-root _headers."""
    if not HEADERS_FILE.exists():
        return None
    match = CSP_LINE_RE.search(HEADERS_FILE.read_text(encoding="utf-8"))
    if not match:
        return None
    return match.group(1).strip()


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
    if not PATH_PLACEHOLDER_RE.search(source):
        print(
            "❌ placeholder /*__PATH_MANIFEST_START__*/…/*__PATH_MANIFEST_END__*/ "
            "not found in _worker.template.js — template was edited without "
            "preserving the injection point",
            file=sys.stderr,
        )
        return 1
    if not CSP_PLACEHOLDER_RE.search(source):
        print(
            "❌ placeholder /*__CSP_FROM_HEADERS_START__*/…/*__CSP_FROM_HEADERS_END__*/ "
            "not found in _worker.template.js — template was edited without "
            "preserving the injection point",
            file=sys.stderr,
        )
        return 1

    path_literal = json.dumps(paths, separators=(",", ":"))
    stamped = PATH_PLACEHOLDER_RE.sub(
        f"/*__PATH_MANIFEST_START__*/{path_literal}/*__PATH_MANIFEST_END__*/",
        source,
        count=1,
    )

    csp = extract_csp()
    if not csp:
        print(
            f"❌ Content-Security-Policy not found in {HEADERS_FILE} — "
            "worker would ship without CSP",
            file=sys.stderr,
        )
        return 1

    # json.dumps gives us a JS-safe string literal with escapes and quoting.
    csp_literal = json.dumps(csp)
    stamped = CSP_PLACEHOLDER_RE.sub(
        f"/*__CSP_FROM_HEADERS_START__*/{csp_literal}/*__CSP_FROM_HEADERS_END__*/",
        stamped,
        count=1,
    )

    OUTPUT.write_text(stamped, encoding="utf-8")
    print(
        f"✅ _worker.js stamped: {len(paths)} paths baked in "
        f"({len(path_literal)} bytes of manifest), CSP "
        f"({len(csp)} bytes) baked in, {len(stamped)} bytes total → {OUTPUT}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
