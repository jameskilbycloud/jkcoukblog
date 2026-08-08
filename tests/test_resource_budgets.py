"""Tests for the per-page resource-budget validator.

On 2026-08-08 a build shipped 172 of 254 pages over the Lighthouse stylesheet
budget — and 0.63 CLS with it — while every existing validator passed and
Slack reported success. The pipeline measured how much work it did, never
whether the output was correct. This validator is the assertion that was
missing, so its counting has to be exactly right.
"""

import json

from validate_deployment import DeploymentValidator

BUDGET = 5


def _page(hrefs, stale=False):
    links = []
    for h in hrefs:
        links.append(
            f'<link as="style" href="{h}" media="all" '
            f'onload="this.onload=null;this.rel=\'stylesheet\'" rel="preload"/>'
        )
        # noscript fallback duplicates the href — must not be double-counted
        links.append(f'<noscript><link rel="stylesheet" href="{h}"/></noscript>')
    marker = '<script src="/wp-content/cache/wpo-minify/123/a.js"></script>' if stale else ''
    return f'<html><head>{"".join(links)}</head><body>{marker}</body></html>'


def _site(tmp_path, pages):
    for name, html in pages.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding='utf-8')
    budget = tmp_path / 'budget.json'
    budget.write_text(json.dumps([{
        "path": "/*",
        "resourceCounts": [{"resourceType": "stylesheet", "budget": BUDGET}],
    }]), encoding='utf-8')
    v = DeploymentValidator(tmp_path)
    v.BUDGET_PATH = budget
    return v


def test_reads_budget_from_lighthouse_config(tmp_path):
    v = _site(tmp_path, {'index.html': _page(['/a.css'])})
    assert v._stylesheet_budget() == BUDGET


def test_page_within_budget_produces_no_warning(tmp_path):
    v = _site(tmp_path, {'index.html': _page([f'/c{i}.css' for i in range(BUDGET)])})
    v.validate_resource_budgets()

    assert v.warnings == []
    assert v.stats['Pages over stylesheet budget'] == 0
    assert v.stats['Max stylesheets/page'] == f"{BUDGET} (budget {BUDGET})"


def test_page_over_budget_warns_without_erroring(tmp_path):
    """A slower page shouldn't block a content deploy — it should be visible."""
    v = _site(tmp_path, {'index.html': _page([f'/c{i}.css' for i in range(7)])})
    v.validate_resource_budgets()

    assert v.stats['Pages over stylesheet budget'] == 1
    assert len(v.warnings) == 1
    assert 'exceed the stylesheet budget' in v.warnings[0]
    assert v.errors == []


def test_noscript_duplicates_are_not_double_counted(tmp_path):
    """Each stylesheet appears twice in the served HTML (async preload plus its
    noscript fallback) but is one network request."""
    v = _site(tmp_path, {'index.html': _page(['/a.css', '/b.css'])})
    v.validate_resource_budgets()

    assert v.stats['Max stylesheets/page'] == f"2 (budget {BUDGET})"


def test_stale_build_markers_are_reported(tmp_path):
    """wpo-minify paths mean the page came from a stale incremental cache
    rather than being regenerated — 82 pages were in that state."""
    v = _site(tmp_path, {'index.html': _page(['/a.css'], stale=True)})
    v.validate_resource_budgets()

    assert v.stats['Pages with stale markers'] == 1
    assert any('stale build markers' in w for w in v.warnings)


def test_missing_budget_file_degrades_to_warning(tmp_path):
    v = _site(tmp_path, {'index.html': _page(['/a.css'])})
    v.BUDGET_PATH = tmp_path / 'does-not-exist.json'
    v.validate_resource_budgets()

    assert any('could not read' in w for w in v.warnings)
    assert v.errors == []


def test_github_output_export(tmp_path, monkeypatch):
    out = tmp_path / 'gh_output'
    monkeypatch.setenv('GITHUB_OUTPUT', str(out))

    v = _site(tmp_path, {'index.html': _page([f'/c{i}.css' for i in range(7)])})
    v.validate_resource_budgets()
    v.write_github_output()

    written = out.read_text()
    assert 'pages_over_budget=1' in written
    assert 'max_stylesheets=7 (budget 5)' in written
    assert 'pages_stale=0' in written
