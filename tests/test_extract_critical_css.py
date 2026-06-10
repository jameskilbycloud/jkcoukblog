"""Tests for critical-CSS extraction — above all that the size cap can never
produce unbalanced braces (the pre-2026-06 slice-at-15000-chars bug)."""

from bs4 import BeautifulSoup

from extract_critical_css import CriticalCSSExtractor


def _brace_depth_ok(css: str) -> bool:
    depth = 0
    for ch in css:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if depth < 0:
            return False
    return depth == 0


def _soup(css: str) -> BeautifulSoup:
    return BeautifulSoup(
        f'<html><head><style>{css}</style></head>'
        f'<body><main><h1>t</h1><p>x</p></main></body></html>',
        'html.parser')


def test_small_input_passes_through():
    ex = CriticalCSSExtractor()
    out = ex._extract_matching_css_rules(_soup('p{color:red}h1{margin:0}'), {'p', 'h1'})
    assert 'color:red' in out
    assert 'margin:0' in out
    assert ex.css_truncated == 0


def test_truncation_keeps_braces_balanced():
    ex = CriticalCSSExtractor()
    # Enough rules to blow the cap, with the boundary landing inside @media.
    rules = ''.join(f'p{{padding:{i}px;color:#0{i % 10}{i % 10}}}' for i in range(300))
    media = '@media (max-width:600px){' + ''.join(f'h1{{margin:{i}px}}' for i in range(600)) + '}'
    out = ex._extract_matching_css_rules(_soup(rules + media), {'p', 'h1'}, 'test.html')

    assert 0 < len(out) <= ex.max_critical_css
    assert _brace_depth_ok(out), 'truncated critical CSS has unbalanced braces'
    assert ex.css_truncated == 1


def test_media_query_rules_are_wrapped():
    ex = CriticalCSSExtractor()
    out = ex._extract_matching_css_rules(
        _soup('@media (max-width:600px){h1{margin:0}}'), {'h1'})
    assert '@media' in out
    assert _brace_depth_ok(out)


def test_keyframes_are_skipped():
    ex = CriticalCSSExtractor()
    out = ex._extract_matching_css_rules(
        _soup('@keyframes spin{from{opacity:0}to{opacity:1}}p{color:red}'), {'p'})
    assert '@keyframes' not in out
    assert 'color:red' in out
