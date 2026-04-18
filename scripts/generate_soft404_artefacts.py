#!/usr/bin/env python3
"""
Generate the three artefacts that defeat the soft-404 problem described in
docs/SEO.md > "Soft-404 guard":

  1. public/path-manifest.json     — list of every legitimate content URL
  2. public/404.html                — real 404 body served by the Worker
  3. Legacy-permalink redirects appended to public/_redirects

Run once after `make optimize` / after the static site is complete. The
deploy workflow wires this in between "generate" and the Worker copy step
so that the manifest is present before the Worker template gets stamped.

Exit codes:
  0 — success
  1 — public/ missing or empty
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

LEGACY_REDIRECT_MARKER_START = "# --- BEGIN legacy-permalink redirects (generated) ---"
LEGACY_REDIRECT_MARKER_END = "# --- END legacy-permalink redirects (generated) ---"

YEAR_MONTH_SLUG_RE = re.compile(r"^/(\d{4})/(\d{2})/([^/]+)/?$")


def collect_content_paths(public_dir: Path) -> list[str]:
    """Every URL path that resolves to a real HTML document.

    Normalised form: no trailing slash except '/'. Includes both '/foo' and
    '/foo/' semantics at lookup time (see isKnownContentPath in the Worker).
    """
    paths: set[str] = set()
    for html in public_dir.rglob("*.html"):
        rel = html.relative_to(public_dir)
        if rel.name == "index.html":
            if rel.parent == Path("."):
                paths.add("/")
            else:
                paths.add("/" + rel.parent.as_posix())
        else:
            # Flat .html (unusual in this project but supported)
            paths.add("/" + rel.with_suffix("").as_posix())
    return sorted(paths)


def write_manifest(public_dir: Path, paths: list[str]) -> Path:
    manifest_file = public_dir / "path-manifest.json"
    manifest_file.write_text(json.dumps(paths, separators=(",", ":")))
    print(f"✅ path-manifest.json: {len(paths)} paths → {manifest_file}")
    return manifest_file


def write_404_html(public_dir: Path) -> Path:
    """Minimal, theme-consistent 404 body.

    Kept deliberately small (~2KB) so Cloudflare's runtime doesn't have to
    stream a huge payload for every ghost URL. The page is noindex via
    meta + X-Robots-Tag header (set by the Worker).
    """
    body = """<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,follow">
  <title>Not Found — James Kilby</title>
  <link rel="canonical" href="https://jameskilby.co.uk/">
  <link rel="stylesheet" href="/assets/css/brutalist-theme.css" media="all">
  <style>
    body{background:#0a0a0a;color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;padding:2rem;display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center}
    main{max-width:40rem}
    h1{font-size:3rem;margin:0 0 1rem;letter-spacing:.02em;text-transform:uppercase}
    p{line-height:1.6;color:#bbb}
    a{color:#ff6a00;text-decoration:none;border-bottom:1px solid currentColor}
    a:hover{opacity:.8}
    ul{list-style:none;padding:0;margin:2rem 0 0}
    li{margin:.5rem 0}
  </style>
</head>
<body>
  <main>
    <h1>404 — Page Not Found</h1>
    <p>The URL you requested is no longer on this site. The permalink structure changed a while back — old flat URLs like <code>/nutanix-ce</code> now live under dated paths like <code>/2018/01/nutanix-ce/</code>.</p>
    <ul>
      <li><a href="/">Go to the homepage</a></li>
      <li><a href="/changelog/">See what's new</a></li>
      <li><a href="/sitemap.xml">Browse the sitemap</a></li>
    </ul>
  </main>
</body>
</html>
"""
    out = public_dir / "404.html"
    out.write_text(body, encoding="utf-8")
    print(f"✅ 404.html written: {out} ({len(body)} bytes)")
    return out


def build_legacy_redirects(paths: list[str]) -> list[str]:
    """Derive `/slug/ → /YYYY/MM/slug/` redirects from the content manifest.

    The site was originally at flat `/slug/` permalinks; WordPress moved to
    dated paths at some point. Bing / external backlinks still hit the flat
    form — without redirects they fall into the SPA fallback (soft-404).
    """
    rules: list[tuple[str, str]] = []
    seen_slugs: set[str] = set()
    # Known non-post top-level slugs that must NOT be redirected (they are
    # real pages at the root).
    RESERVED = {
        "about-me", "changelog", "contact", "evs", "feed", "homelab-software",
        "lab", "markdown", "media", "privacy-policy", "privacy-policy-2",
        "stats", "vmc", "api", "blog", "page", "category", "tag",
        "wp-content", "wp-includes", "assets", "js",
    }
    for path in paths:
        m = YEAR_MONTH_SLUG_RE.match(path + ("/" if not path.endswith("/") else ""))
        if not m:
            continue
        slug = m.group(3)
        if slug in RESERVED or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        rules.append((f"/{slug}", f"{path}/" if not path.endswith("/") else path))
        rules.append((f"/{slug}/", f"{path}/" if not path.endswith("/") else path))
    return sorted({f"{src} {dst} 301" for src, dst in rules})


def update_redirects(public_dir: Path, rules: list[str]) -> Path:
    redirects = public_dir / "_redirects"
    existing = redirects.read_text(encoding="utf-8") if redirects.exists() else ""

    # Strip any previous generated block so reruns are idempotent.
    pattern = re.compile(
        re.escape(LEGACY_REDIRECT_MARKER_START)
        + r".*?"
        + re.escape(LEGACY_REDIRECT_MARKER_END)
        + r"\n?",
        re.DOTALL,
    )
    existing_stripped = pattern.sub("", existing).rstrip() + "\n"

    block = "\n".join(
        [
            "",
            LEGACY_REDIRECT_MARKER_START,
            "# Auto-generated by scripts/generate_soft404_artefacts.py.",
            "# Maps pre-date-prefix WordPress permalinks (/slug/) to the",
            "# current /YYYY/MM/slug/ form so external backlinks and Bing's",
            "# historical index stop 200-ing into the SPA fallback.",
            *rules,
            LEGACY_REDIRECT_MARKER_END,
            "",
        ]
    )
    redirects.write_text(existing_stripped + block, encoding="utf-8")
    print(f"✅ _redirects: {len(rules)} legacy redirects appended")
    return redirects


def main() -> int:
    if not PUBLIC_DIR.exists():
        print(f"❌ {PUBLIC_DIR} does not exist", file=sys.stderr)
        return 1

    paths = collect_content_paths(PUBLIC_DIR)
    if not paths:
        print(f"❌ {PUBLIC_DIR} contains no HTML files", file=sys.stderr)
        return 1

    write_manifest(PUBLIC_DIR, paths)
    write_404_html(PUBLIC_DIR)
    rules = build_legacy_redirects(paths)
    update_redirects(PUBLIC_DIR, rules)
    return 0


if __name__ == "__main__":
    sys.exit(main())
