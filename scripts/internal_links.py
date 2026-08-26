#!/usr/bin/env python3
"""Contextual internal-linking pass for orphan posts.

SEO finding #17 (2026-08 triage): 13 posts receive **zero inbound editorial
links from other post bodies**. They still get home/archive/category links and
the appended "Related posts" block, but no *contextual* in-content link — the
kind that actually carries topical link equity and that Google weights most.

This pass closes that gap deterministically, at build time:

  1. build_inbound_graph()  — parse every post's ``.entry-content`` prose and
     record which posts link to which (footer "related-posts" block excluded,
     so it measures the same thing the triage did).
  2. find_orphans()         — posts with no inbound prose link.
  3. assign_hosts()         — give each orphan the single most topically
     relevant host post (score = 3·shared_tags + 2·shared_categories, the same
     formula add_related_posts() uses; recency breaks ties). A zero-overlap
     orphan falls back to the newest post sharing a category, then newest overall
     — so every orphan always gets a host.
  4. inject_related_link()  — add ONE contextual link into the host's
     ``.entry-content`` (after its first paragraph), idempotently.

The functions are pure and unit-tested; ``apply_to_output()`` wires them over a
built site directory (used both by the generator's finalize step and standalone:
``python3 scripts/internal_links.py <output_dir>``). It only ever edits the host
posts it chooses — never public/ by hand.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - bs4 is a build dependency
    BeautifulSoup = None

# Marks an injected link so re-runs are idempotent and CSS can style it.
INJECTED_CLASS = "internal-related-link"

# Matches an internal post URL path: /YYYY/MM/slug/ (trailing slash optional).
_POST_PATH = re.compile(r"^/(?:19|20)\d\d/\d\d/[^/]+/?$")


def normalise_post_url(href: str) -> str | None:
    """Return the canonical ``/YYYY/MM/slug/`` path for an internal post href,
    or None if the href is not an internal post link."""
    if not href:
        return None
    p = href.split("#", 1)[0].split("?", 1)[0]
    for prefix in ("https://jameskilby.co.uk", "https://jkcoukblog.pages.dev",
                   "http://jameskilby.co.uk"):
        if p.startswith(prefix):
            p = p[len(prefix):]
    if not p.startswith("/"):
        return None
    if not _POST_PATH.match(p):
        return None
    return p if p.endswith("/") else p + "/"


def body_post_links(html: str) -> set:
    """Internal post URLs linked from a post's editorial *body* — the
    ``<article>`` element (its ``.entry-content`` prose plus the appended
    related-posts block). Site header/nav/footer and archive/category listing
    links live outside ``<article>`` and are deliberately excluded, matching the
    triage's "post-to-post body link" measure. Falls back to ``.entry-content``
    then ``<main>`` when a theme omits ``<article>``."""
    if BeautifulSoup is None:  # pragma: no cover
        return set()
    soup = BeautifulSoup(html, "html.parser")
    scope = soup.find("article") or soup.select_one(".entry-content") or soup.find("main")
    if scope is None:
        return set()
    out = set()
    for a in scope.find_all("a", href=True):
        u = normalise_post_url(a["href"])
        if u:
            out.add(u)
    return out


def build_inbound_graph(posts: dict) -> dict:
    """posts: {url: html}. Return {url: set(urls that link to it in their body)}.

    Only genuine post-to-post links inside the source's ``<article>`` count."""
    known = set(posts)
    inbound = {u: set() for u in posts}
    for src, html in posts.items():
        for tgt in body_post_links(html):
            if tgt in known and tgt != src:
                inbound[tgt].add(src)
    return inbound


def find_orphans(inbound: dict) -> list:
    """Posts with zero inbound prose links, in stable (sorted) order."""
    return sorted(u for u, srcs in inbound.items() if not srcs)


def _relevance(a: dict, b: dict) -> int:
    return 3 * len(a["tags"] & b["tags"]) + 2 * len(a["cats"] & b["cats"])


def assign_hosts(orphans: list, index: dict, exclude_hosts: set | None = None) -> dict:
    """For each orphan pick the single most relevant host post.

    index: {url: {'cats': set, 'tags': set, 'date': str}}.
    Score = 3·shared_tags + 2·shared_cats; newer date then URL break ties.
    Zero-overlap orphans fall back to newest post sharing a category, then the
    newest post overall — so the result always contains every orphan.
    exclude_hosts: URLs never eligible as hosts (e.g. the orphan set itself, to
    avoid linking orphans from other orphans)."""
    exclude = set(exclude_hosts or ())
    result = {}
    for orphan in orphans:
        if orphan not in index:
            continue
        oe = index[orphan]
        best = None  # (score, date, url)
        for url, e in index.items():
            if url == orphan or url in exclude:
                continue
            score = _relevance(oe, e)
            key = (score, e.get("date", ""), url)
            if best is None or key > best:
                best = key
        if best and best[0] > 0:
            result[orphan] = best[2]
            continue
        # Fallback: newest post sharing any category, else newest overall.
        cat_share = [
            (e.get("date", ""), url) for url, e in index.items()
            if url != orphan and url not in exclude and (oe["cats"] & e["cats"])
        ]
        pool = cat_share or [
            (e.get("date", ""), url) for url, e in index.items()
            if url != orphan and url not in exclude
        ]
        if pool:
            result[orphan] = max(pool)[1]
    return result


def _already_links(entry, orphan_url: str) -> bool:
    for a in entry.find_all("a", href=True):
        if normalise_post_url(a["href"]) == orphan_url:
            return True
    return False


def inject_related_link(html: str, orphan_url: str, orphan_title: str):
    """Insert one contextual link to `orphan_url` into the host's
    ``.entry-content`` (after its first paragraph, else appended). Returns
    (new_html, changed). Idempotent: a no-op if that link is already present."""
    if BeautifulSoup is None:  # pragma: no cover
        return html, False
    soup = BeautifulSoup(html, "html.parser")
    entry = soup.select_one(".entry-content")
    if entry is None:
        return html, False
    if _already_links(entry, orphan_url):
        return html, False

    p = soup.new_tag("p")
    p["class"] = [INJECTED_CLASS]
    label = soup.new_string("Related: ")
    a = soup.new_tag("a", href=orphan_url)
    a.string = orphan_title or orphan_url
    p.append(label)
    p.append(a)

    first_p = entry.find("p", recursive=False) or entry.find("p")
    if first_p is not None:
        first_p.insert_after(p)
    else:
        entry.append(p)
    return str(soup), True


# --------------------------------------------------------------------------
# Wiring over a built output directory
# --------------------------------------------------------------------------
def _post_files(output_dir: Path) -> dict:
    """{url: Path} for every built post page (/YYYY/MM/slug/index.html)."""
    out = {}
    for f in output_dir.glob("[12][0-9][0-9][0-9]/[0-1][0-9]/*/index.html"):
        rel = "/" + f.parent.relative_to(output_dir).as_posix() + "/"
        if _POST_PATH.match(rel[:-1]) or _POST_PATH.match(rel):
            out[rel] = f
    return out


def _taxonomy_from_html(html: str) -> dict:
    cats = set(re.findall(r"/category/([a-z0-9-]+)/", html))
    tags = set(re.findall(r"/tag/([a-z0-9-]+)/", html))
    mt = re.search(r"<title>(.*?)</title>", html, re.S)
    title = (mt.group(1) if mt else "").split("|")[0].split(" - James Kilby")[0].strip()
    return {"cats": cats, "tags": tags, "title": title, "date": ""}


def apply_to_output(output_dir, index: dict | None = None, log=print) -> list:
    """Add a contextual inbound link to every orphan post under `output_dir`.

    index (optional): {url: {'cats','tags','date','title'}} — the generator
    passes its authoritative post_index. When omitted, taxonomy/title are
    derived from the built HTML (used by the standalone entry point).

    Returns the list of (orphan_url, host_url) mappings applied.
    """
    output_dir = Path(output_dir)
    files = _post_files(output_dir)
    if not files:
        return []
    htmls = {u: p.read_text(encoding="utf-8", errors="replace") for u, p in files.items()}

    if index is None:
        index = {u: _taxonomy_from_html(h) for u, h in htmls.items()}
    else:
        # Restrict to posts we actually have files for; carry titles from HTML
        # when the index entry lacks one.
        index = {u: dict(e) for u, e in index.items() if u in files}
        for u, e in index.items():
            e.setdefault("title", _taxonomy_from_html(htmls[u])["title"])
            e["cats"] = set(e.get("cats", ()))
            e["tags"] = set(e.get("tags", ()))

    inbound = build_inbound_graph(htmls)
    orphans = [o for o in find_orphans(inbound) if o in index]
    if not orphans:
        log("🔗 Internal links: no orphan posts — nothing to do.")
        return []

    mapping = assign_hosts(orphans, index, exclude_hosts=set(orphans))
    applied = []
    for orphan, host in sorted(mapping.items()):
        if host not in files:
            continue
        title = index.get(orphan, {}).get("title") or orphan
        new_html, changed = inject_related_link(htmls[host], orphan, title)
        if changed:
            files[host].write_text(new_html, encoding="utf-8")
            htmls[host] = new_html
            applied.append((orphan, host))
            log(f"   🔗 {host}  →  {orphan}")
    log(f"🔗 Internal links: linked {len(applied)}/{len(orphans)} orphan post(s).")
    return applied


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "public"
    applied = apply_to_output(out)
    print(f"\nDone. {len(applied)} orphan link(s) injected under {out}.")
