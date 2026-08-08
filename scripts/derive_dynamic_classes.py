#!/usr/bin/env python3
"""
Derive the JS-applied class allowlist used by optimize_css.py.

Why this exists
---------------
`optimize_css.py` removes CSS selectors that don't appear in any built HTML
file. Classes that only ever exist *after* JavaScript runs (mobile menu
toggles, sticky-header states, header layout modes) are invisible to that
scan, so their rules would be purged and the UI would silently break the
moment a user interacts with it. `optimize_css._DYNAMIC_CLASSES` is the
allowlist that prevents this.

That allowlist used to be maintained by grepping wpo-minify-footer-*.min.js
by hand. WP-Optimize's minify feature is now disabled (its cache path
embedded a timestamp that rewrote every page on each WordPress-side
rebuild), so there is no single bundle left to grep — WordPress emits every
plugin and theme script separately. This script walks all of them instead.

Usage
-----
    python3 scripts/derive_dynamic_classes.py ./public
    python3 scripts/derive_dynamic_classes.py ./public --check

`--check` exits non-zero if the built site writes a class that
_DYNAMIC_CLASSES doesn't cover, which is the useful mode for CI.
"""

import argparse
import re
import sys
from pathlib import Path

# classList.add/remove/toggle/contains/replace with string-literal arguments
_CLASSLIST_RE = re.compile(
    r'classList\s*\.\s*(?:add|remove|toggle|contains|replace)\s*\(([^)]*)\)'
)
# jQuery-style addClass('x') / removeClass / toggleClass / hasClass
_JQUERY_RE = re.compile(
    r'\.\s*(?:addClass|removeClass|toggleClass|hasClass)\s*\(([^)]*)\)'
)
# className = "x"  /  className += " x"
_CLASSNAME_RE = re.compile(r'className\s*\+?=\s*(["\'])(.*?)\1')
# setAttribute("class", "x")
_SETATTR_RE = re.compile(
    r'setAttribute\s*\(\s*["\']class["\']\s*,\s*(["\'])(.*?)\1'
)

_STRING_LITERAL_RE = re.compile(r'(["\'])(.*?)\1')
# A plausible CSS class token. Filters out the minified variable names and
# selector fragments that leak into these call sites.
_VALID_CLASS_RE = re.compile(r'^[A-Za-z_][\w-]*$')

# Server-side script — its string literals are route paths, not CSS classes.
_EXCLUDED_FILENAMES = {'_worker.js'}


def extract_classes(js_source):
    """Return the set of class names this JS source writes to the DOM."""
    classes = set()

    for regex in (_CLASSLIST_RE, _JQUERY_RE):
        for match in regex.finditer(js_source):
            for literal in _STRING_LITERAL_RE.finditer(match.group(1)):
                for token in literal.group(2).split():
                    if _VALID_CLASS_RE.match(token):
                        classes.add(token)

    for regex in (_CLASSNAME_RE, _SETATTR_RE):
        for match in regex.finditer(js_source):
            for token in match.group(2).split():
                if _VALID_CLASS_RE.match(token):
                    classes.add(token)

    return classes


def scan(site_dir):
    """Return {class_name: sorted list of files that write it}."""
    site_dir = Path(site_dir)
    found = {}

    for js_file in sorted(site_dir.rglob('*.js')):
        if js_file.name in _EXCLUDED_FILENAMES:
            continue
        try:
            source = js_file.read_text(encoding='utf-8', errors='replace')
        except OSError as e:
            print(f"   ⚠️  Could not read {js_file}: {e}")
            continue
        rel = js_file.relative_to(site_dir).as_posix()
        for cls in extract_classes(source):
            found.setdefault(cls, set()).add(rel)

    return {k: sorted(v) for k, v in sorted(found.items())}


def main():
    parser = argparse.ArgumentParser(
        description="Derive JS-applied CSS classes from the built site."
    )
    parser.add_argument("site_dir", nargs="?", default="public",
                        help="Directory containing the built site")
    parser.add_argument("--check", action="store_true",
                        help="Exit non-zero if optimize_css._DYNAMIC_CLASSES "
                             "is missing any discovered class")
    args = parser.parse_args()

    site_dir = Path(args.site_dir)
    if not site_dir.is_dir():
        print(f"❌ Not a directory: {site_dir}")
        sys.exit(1)

    found = scan(site_dir)
    if not found:
        print(f"⚠️  No JS-applied classes found under {site_dir} — "
              f"is the site built?")
        sys.exit(1)

    print(f"🔍 {len(found)} JS-applied classes found under {site_dir}\n")

    sys.path.insert(0, str(Path(__file__).parent))
    from optimize_css import CSSOptimizer
    allowlist = CSSOptimizer._DYNAMIC_CLASSES

    missing = sorted(set(found) - set(allowlist))
    unused = sorted(set(allowlist) - set(found))

    if missing:
        print(f"❌ {len(missing)} class(es) written by JS but NOT in "
              f"_DYNAMIC_CLASSES — their CSS rules can be purged:")
        for cls in missing:
            print(f"   + {cls:42s} {', '.join(found[cls])}")
    else:
        print("✅ _DYNAMIC_CLASSES covers every class written by the built JS")

    if unused:
        # Not an error: entries may guard against classes applied by inline
        # <script> blocks or by code paths this regex scan can't see. Listed
        # so the set can be pruned deliberately rather than by accident.
        print(f"\nℹ️  {len(unused)} allowlist entr(ies) not found in the "
              f"current JS (kept deliberately — review before removing):")
        for cls in unused:
            print(f"   - {cls}")

    if args.check and missing:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
