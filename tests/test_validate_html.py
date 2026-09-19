"""Tests for HTMLValidator — purely filesystem-driven (no network), so these
build small fixture trees under tmp_path rather than mocking anything."""

from pathlib import Path

import pytest

from validate_html import HTMLValidator


def _write(path: Path, content: str = ''):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return path


def _validator(site_dir):
    return HTMLValidator(str(site_dir))


# ── normalize_path ────────────────────────────────────────────────────────

class TestNormalizePath:
    def test_external_urls_are_skipped(self, tmp_path):
        v = _validator(tmp_path)
        current = tmp_path / 'index.html'
        for url in ('https://example.com/x', 'http://example.com/x',
                    'mailto:a@b.com', 'tel:+123', 'data:image/png;base64,AA=='):
            assert v.normalize_path(url, current) is None

    def test_fragment_only_is_skipped(self, tmp_path):
        v = _validator(tmp_path)
        assert v.normalize_path('#section', tmp_path / 'index.html') is None

    def test_absolute_path_resolves_from_site_root(self, tmp_path):
        v = _validator(tmp_path)
        current = tmp_path / 'posts' / '2026' / 'index.html'
        result = v.normalize_path('/about/', current)
        assert result == tmp_path / 'about'

    def test_relative_path_resolves_from_current_file_dir(self, tmp_path):
        v = _validator(tmp_path)
        current = tmp_path / 'posts' / '2026' / 'index.html'
        result = v.normalize_path('../other/', current)
        assert result == (tmp_path / 'posts' / 'other').resolve()

    def test_url_encoded_path_is_decoded(self, tmp_path):
        v = _validator(tmp_path)
        current = tmp_path / 'index.html'
        result = v.normalize_path('/my%20post/', current)
        assert result == tmp_path / 'my post'


# ── file_exists ───────────────────────────────────────────────────────────

class TestFileExists:
    def test_direct_file_match(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'style.css')
        assert v.file_exists(f) is True

    def test_html_suffix_fallback(self, tmp_path):
        v = _validator(tmp_path)
        _write(tmp_path / 'about.html')
        assert v.file_exists(tmp_path / 'about') is True

    def test_directory_with_index_html(self, tmp_path):
        v = _validator(tmp_path)
        _write(tmp_path / 'about' / 'index.html')
        assert v.file_exists(tmp_path / 'about') is True

    def test_missing_path_returns_false(self, tmp_path):
        v = _validator(tmp_path)
        assert v.file_exists(tmp_path / 'nope') is False


# ── validate_html_structure ─────────────────────────────────────────────

class TestValidateHtmlStructure:
    def test_well_formed_page_passes(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html',
                   '<html><head><title>T</title></head><body>hi</body></html>')
        assert v.validate_html_structure(f) is True
        assert v.errors == []

    def test_missing_html_tag_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html', '<body>no html/head wrapper</body>')
        assert v.validate_html_structure(f) is False
        assert 'Missing <html> tag' in v.errors[0]

    def test_missing_title_warns_not_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html',
                   '<html><head></head><body>hi</body></html>')
        assert v.validate_html_structure(f) is True
        assert any('Missing <title>' in w for w in v.warnings)

    def test_feed_files_skip_missing_title_warning(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'feed' / 'index.html',
                   '<html><head></head><body>hi</body></html>')
        v.validate_html_structure(f)
        assert v.warnings == []


# ── validate_links ────────────────────────────────────────────────────────

class TestValidateLinks:
    def test_broken_internal_link_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html', '<a href="/missing/">gone</a>')
        assert v.validate_links(f) is False
        assert "Broken link to '/missing/'" in v.errors[0]

    def test_link_to_existing_page_passes(self, tmp_path):
        v = _validator(tmp_path)
        _write(tmp_path / 'about' / 'index.html', '<p>about</p>')
        f = _write(tmp_path / 'index.html', '<a href="/about/">about</a>')
        assert v.validate_links(f) is True
        assert v.errors == []

    def test_external_and_special_schemes_are_skipped(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html', '''
            <a href="https://example.com">ext</a>
            <a href="mailto:a@b.com">mail</a>
            <a href="#frag">frag</a>
        ''')
        assert v.validate_links(f) is True

    def test_changelog_and_stats_paths_are_skipped(self, tmp_path):
        """Those pages are generated after validation runs in the pipeline."""
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html',
                   '<a href="/changelog/">log</a><a href="/stats/">stats</a>')
        assert v.validate_links(f) is True


# ── validate_assets ──────────────────────────────────────────────────────

class TestValidateAssets:
    def test_missing_image_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html', '<img src="/missing.png" alt="x">')
        assert v.validate_assets(f) is False
        assert "Missing image '/missing.png'" in v.errors[0]

    def test_missing_alt_warns(self, tmp_path):
        v = _validator(tmp_path)
        _write(tmp_path / 'photo.png')
        f = _write(tmp_path / 'index.html', '<img src="/photo.png">')
        v.validate_assets(f)
        assert any('missing alt attribute' in w for w in v.warnings)

    def test_existing_image_with_alt_is_clean(self, tmp_path):
        v = _validator(tmp_path)
        _write(tmp_path / 'photo.png')
        f = _write(tmp_path / 'index.html', '<img src="/photo.png" alt="a photo">')
        assert v.validate_assets(f) is True
        assert v.errors == [] and v.warnings == []

    def test_missing_css_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html',
                   '<link rel="stylesheet" href="/missing.css">')
        assert v.validate_assets(f) is False
        assert "Missing CSS file '/missing.css'" in v.errors[0]

    def test_missing_js_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html', '<script src="/missing.js"></script>')
        assert v.validate_assets(f) is False
        assert "Missing JavaScript file '/missing.js'" in v.errors[0]

    def test_worker_served_js_path_is_not_flagged(self, tmp_path):
        """/js/script.js is proxied at runtime by the Cloudflare Worker, never
        written to public/ — the on-disk check must not flag it as missing."""
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html', '<script src="/js/script.js"></script>')
        assert v.validate_assets(f) is True

    def test_missing_picture_source_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'index.html',
                   '<source srcset="/missing.avif 1x">')
        assert v.validate_assets(f) is False
        assert "Missing source image '/missing.avif'" in v.errors[0]


# ── validate_css_assets ──────────────────────────────────────────────────

class TestValidateCssAssets:
    def test_missing_css_url_asset_errors(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'style.css', "body { background: url('/img/missing.png'); }")
        assert v.validate_css_assets(f) is False
        assert "Missing asset '/img/missing.png'" in v.errors[0]

    def test_existing_css_url_asset_passes(self, tmp_path):
        v = _validator(tmp_path)
        _write(tmp_path / 'img' / 'bg.png')
        f = _write(tmp_path / 'style.css', "body { background: url('/img/bg.png'); }")
        assert v.validate_css_assets(f) is True

    def test_data_and_external_css_urls_are_skipped(self, tmp_path):
        v = _validator(tmp_path)
        f = _write(tmp_path / 'style.css',
                   "a { background: url('data:image/png;base64,AA=='); }\n"
                   "b { background: url('https://cdn.example.com/x.png'); }")
        assert v.validate_css_assets(f) is True


# ── run_validation (end-to-end) ──────────────────────────────────────────

class TestRunValidation:
    def test_clean_site_passes(self, tmp_path):
        _write(tmp_path / 'index.html',
               '<html><head><title>Home</title></head>'
               '<body><a href="/about/">about</a></body></html>')
        _write(tmp_path / 'about' / 'index.html',
               '<html><head><title>About</title></head><body>hi</body></html>')
        v = _validator(tmp_path)
        assert v.run_validation() is True
        assert v.errors == []

    def test_broken_site_fails(self, tmp_path):
        _write(tmp_path / 'index.html',
               '<html><head><title>Home</title></head>'
               '<body><a href="/nowhere/">gone</a></body></html>')
        v = _validator(tmp_path)
        assert v.run_validation() is False
        assert v.errors

    def test_no_html_files_fails(self, tmp_path):
        v = _validator(tmp_path)
        assert v.run_validation() is False
        assert 'No HTML files found!' in v.errors[0]
