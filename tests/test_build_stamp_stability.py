"""Generated indexes must not carry a wall-clock stamp.

api/index.json, markdown/index.json and markdown/SITEMAP.md each embedded
datetime.now(), so all three — plus their .br/.gz sidecars — were rewritten on
every deploy whether or not any content had changed. They still answer "how
fresh is this?"; they answer it about the content rather than the build
machine, which is both more useful and stable.

Also covers the dns-prefetch hint ordering: a bare set difference iterates in
hash order, and since each new tag is inserted at head[0] that ordering became
document order, so pages emitted their hints in a different sequence run to
run.
"""

import json
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

pytest.importorskip('yaml')
from bs4 import BeautifulSoup  # noqa: E402
from enhance_html_performance import HTMLPerformanceEnhancer  # noqa: E402
from markdown_api import MarkdownAPIGenerator  # noqa: E402

POST = """---
title: "A Post"
description: "d"
date: "2024-03-01T09:00:00Z"
modified: "2026-05-04T11:22:33Z"
categories:
  - Homelab
tags:
  - zfs
url: "https://jameskilby.co.uk/a-post/"
---

Body.
"""


def _build_api(tmp_path: Path, name: str) -> dict:
    md = tmp_path / name / 'markdown'
    (md / 'posts').mkdir(parents=True)
    (md / 'posts' / 'a-post.md').write_text(POST, encoding='utf-8')
    api = tmp_path / name / 'api'
    MarkdownAPIGenerator(md, api).generate_api()
    return json.loads((api / 'index.json').read_text(encoding='utf-8'))


def test_api_index_is_stable_across_builds(tmp_path):
    first = _build_api(tmp_path, 'first')
    time.sleep(1.1)
    second = _build_api(tmp_path, 'second')
    assert first == second, 'api/index.json changed with wall-clock time'


def test_api_index_stamp_tracks_content(tmp_path):
    """The field still has to mean something — newest content timestamp."""
    index = _build_api(tmp_path, 'content')
    assert index['generated'] == '2026-05-04T11:22:33Z'


def test_dns_prefetch_hints_are_emitted_in_a_stable_order():
    """Same input, same order — regardless of set iteration."""
    html = (
        '<html><head></head><body>'
        '<script src="https://cdn.example.com/a.js"></script>'
        '<script src="https://plausible.example.net/b.js"></script>'
        '<img src="https://images.example.org/c.png">'
        '<script src="https://utteranc.example/d.js"></script>'
        '</body></html>'
    )
    soup = BeautifulSoup(html, 'html.parser')
    HTMLPerformanceEnhancer().optimize_external_scripts(soup)
    hrefs = [link.get('href') for link in soup.find_all('link', rel='dns-prefetch')]

    assert len(hrefs) == 4
    # Assert the ordering property rather than comparing repeated runs: set
    # iteration is stable within a single process (PYTHONHASHSEED is fixed for
    # its lifetime), so a loop here would pass with the bug present and only
    # diverge between the separate build processes where it actually bit.
    #
    # Tags are inserted at head[0], so document order is the reverse of the
    # order they were added in.
    assert hrefs == sorted(hrefs, reverse=True), (
        f'dns-prefetch hints are not in a deterministic order: {hrefs}'
    )


def test_dns_prefetch_attribute_order_is_href_then_rel():
    """A pruned-and-recreated hint must serialise identically to one the
    parser preserved, or the page is rewritten for no semantic change."""
    soup = BeautifulSoup(
        '<html><head></head><body>'
        '<script src="https://cdn.example.com/a.js"></script>'
        '</body></html>', 'html.parser')
    HTMLPerformanceEnhancer().optimize_external_scripts(soup)
    link = soup.find('link', rel='dns-prefetch')
    assert list(link.attrs) == ['href', 'rel']
