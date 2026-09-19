"""Tests for MarkdownExporter's content-extraction and formatting logic.

Purely filesystem-driven (BeautifulSoup + html2text over local files, no
network), so these build small HTML fixtures under tmp_path.
"""

import json

from bs4 import BeautifulSoup

from markdown_exporter import MarkdownExporter


def _exporter(tmp_path):
    html_dir = tmp_path / 'public'
    md_dir = tmp_path / 'public' / 'markdown'
    html_dir.mkdir(parents=True, exist_ok=True)
    return MarkdownExporter(str(html_dir), str(md_dir), 'https://jameskilby.co.uk')


def _soup(html):
    return BeautifulSoup(html, 'html.parser')


# ── _extract_metadata ────────────────────────────────────────────────────

class TestExtractMetadata:
    def test_title_strips_site_name_suffix(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<title>My Post - jameskilby.co.uk</title>')
        html_file = exp.html_dir / 'my-post' / 'index.html'
        meta = exp._extract_metadata(soup, html_file)
        assert meta['title'] == 'My Post'

    def test_entry_title_h1_overrides_title_tag(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup(
            '<title>Generic Title</title>'
            '<h1 class="entry-title">The Real Headline</h1>'
        )
        meta = exp._extract_metadata(soup, exp.html_dir / 'index.html')
        assert meta['title'] == 'The Real Headline'

    def test_meta_description_and_og_image_extracted(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup(
            '<meta name="description" content="A summary.">'
            '<meta property="og:image" content="https://x/img.png">'
        )
        meta = exp._extract_metadata(soup, exp.html_dir / 'index.html')
        assert meta['description'] == 'A summary.'
        assert meta['image'] == 'https://x/img.png'

    def test_categories_and_tags_deduplicated(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup(
            '<a href="/category/homelab/">Homelab</a>'
            '<a href="/category/homelab/">Homelab</a>'
            '<a href="/tag/vmware/">VMware</a>'
        )
        meta = exp._extract_metadata(soup, exp.html_dir / 'index.html')
        assert meta['categories'] == ['Homelab']
        assert meta['tags'] == ['VMware']

    def test_author_defaults_when_absent(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<p>no author markup here</p>')
        meta = exp._extract_metadata(soup, exp.html_dir / 'index.html')
        assert meta['author'] == 'James Kilby'

    def test_author_element_used_when_present(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<a class="author-link">Jane Doe</a>')
        meta = exp._extract_metadata(soup, exp.html_dir / 'index.html')
        assert meta['author'] == 'Jane Doe'

    def test_url_from_canonical_link(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<link rel="canonical" href="https://jameskilby.co.uk/a-post/">')
        meta = exp._extract_metadata(soup, exp.html_dir / 'a-post' / 'index.html')
        assert meta['url'] == 'https://jameskilby.co.uk/a-post/'

    def test_url_constructed_from_path_without_canonical(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<p>no canonical link</p>')
        html_file = exp.html_dir / '2026' / '01' / 'a-post' / 'index.html'
        meta = exp._extract_metadata(soup, html_file)
        assert meta['url'] == 'https://jameskilby.co.uk/2026/01/a-post/'

    def test_root_url_when_relative_path_is_dot(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<p>no canonical</p>')
        meta = exp._extract_metadata(soup, exp.html_dir / 'index.html')
        assert meta['url'] == 'https://jameskilby.co.uk/'


# ── _extract_dates_from_jsonld ───────────────────────────────────────────

class TestExtractDatesFromJsonld:
    def test_extracts_dates_and_word_count(self, tmp_path):
        exp = _exporter(tmp_path)
        payload = json.dumps({
            '@type': 'BlogPosting',
            'datePublished': '2026-01-01T00:00:00Z',
            'dateModified': '2026-02-01T00:00:00Z',
            'wordCount': 1200,
            'timeRequired': 'PT6M',
        })
        soup = _soup(f'<script type="application/ld+json">{payload}</script>')
        dates = exp._extract_dates_from_jsonld(soup)
        assert dates['date_published'] == '2026-01-01T00:00:00Z'
        assert dates['date_modified'] == '2026-02-01T00:00:00Z'
        assert dates['word_count'] == 1200
        assert dates['reading_time'] == 'PT6M'

    def test_graph_structure_is_searched(self, tmp_path):
        exp = _exporter(tmp_path)
        payload = json.dumps({
            '@graph': [
                {'@type': 'WebSite'},
                {'@type': 'Article', 'datePublished': '2026-03-01'},
            ]
        })
        soup = _soup(f'<script type="application/ld+json">{payload}</script>')
        dates = exp._extract_dates_from_jsonld(soup)
        assert dates['date_published'] == '2026-03-01'

    def test_malformed_json_is_ignored_not_raised(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<script type="application/ld+json">{not valid json</script>')
        assert exp._extract_dates_from_jsonld(soup) == {}

    def test_no_jsonld_returns_empty_dict(self, tmp_path):
        exp = _exporter(tmp_path)
        assert exp._extract_dates_from_jsonld(_soup('<p>plain</p>')) == {}


# ── _extract_content_html ────────────────────────────────────────────────

class TestExtractContentHtml:
    def test_prefers_entry_content_selector(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup(
            '<body><div class="entry-content"><p>real</p></div>'
            '<main><p>fallback</p></main></body>'
        )
        content = exp._extract_content_html(soup)
        assert 'real' in content and 'fallback' not in content

    def test_falls_back_to_body_when_nothing_matches(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup('<body><p>just body text</p></body>')
        content = exp._extract_content_html(soup)
        assert 'just body text' in content

    def test_empty_soup_returns_empty_string(self, tmp_path):
        exp = _exporter(tmp_path)
        assert exp._extract_content_html(_soup('')) == ''

    def test_removes_unwanted_elements(self, tmp_path):
        exp = _exporter(tmp_path)
        soup = _soup(
            '<div class="entry-content">'
            '<p>keep me</p>'
            '<script>evil()</script>'
            '<nav>site nav</nav>'
            '<div class="social-share">share this</div>'
            '</div>'
        )
        content = exp._extract_content_html(soup)
        assert 'keep me' in content
        assert 'evil()' not in content
        assert 'site nav' not in content
        assert 'share this' not in content


# ── _clean_markdown ───────────────────────────────────────────────────────

class TestCleanMarkdown:
    def test_collapses_excess_blank_lines(self, tmp_path):
        exp = _exporter(tmp_path)
        assert exp._clean_markdown('a\n\n\n\n\nb') == 'a\n\nb'

    def test_absolutises_relative_image_and_link_paths(self, tmp_path):
        exp = _exporter(tmp_path)
        md = exp._clean_markdown('![alt](/img/x.png) and [text](/about/)')
        assert '![alt](https://jameskilby.co.uk/img/x.png)' in md
        assert '[text](https://jameskilby.co.uk/about/)' in md

    def test_strips_html_comments(self, tmp_path):
        exp = _exporter(tmp_path)
        assert exp._clean_markdown('a <!-- hidden --> b') == 'a  b'

    def test_removes_empty_code_blocks(self, tmp_path):
        exp = _exporter(tmp_path)
        assert '```\n```' not in exp._clean_markdown('before\n```\n```\nafter')


# ── _create_frontmatter ──────────────────────────────────────────────────

class TestCreateFrontmatter:
    def test_escapes_quotes_and_backslashes(self, tmp_path):
        exp = _exporter(tmp_path)
        fm = exp._create_frontmatter({'title': 'A "Quoted" C:\\Path'})
        assert 'title: "A \\"Quoted\\" C:\\\\Path"' in fm

    def test_lists_rendered_as_yaml_sequences(self, tmp_path):
        exp = _exporter(tmp_path)
        fm = exp._create_frontmatter({'categories': ['Homelab', 'VMware']})
        assert 'categories:\n  - Homelab\n  - VMware' in fm

    def test_wraps_in_yaml_delimiters(self, tmp_path):
        exp = _exporter(tmp_path)
        fm = exp._create_frontmatter({'title': 'T'})
        assert fm.startswith('---\n') and fm.endswith('\n---')

    def test_omits_absent_fields(self, tmp_path):
        exp = _exporter(tmp_path)
        fm = exp._create_frontmatter({'title': 'T'})
        assert 'description' not in fm
        assert 'categories' not in fm


# ── _export_single_post (integration) ────────────────────────────────────

class TestExportSinglePost:
    def test_writes_markdown_with_frontmatter_and_content(self, tmp_path):
        exp = _exporter(tmp_path)
        post_dir = exp.html_dir / '2026' / '01' / 'my-post'
        post_dir.mkdir(parents=True)
        (post_dir / 'index.html').write_text(
            '<html><head><title>My Post - jameskilby.co.uk</title>'
            '<meta name="description" content="A summary."></head>'
            '<body><div class="entry-content"><p>Hello world.</p></div></body>'
            '</html>',
            encoding='utf-8',
        )

        exp._export_single_post(post_dir / 'index.html', post_dir)

        nested = post_dir_out = exp.markdown_dir / '2026' / '01' / 'my-post' / 'index.md'
        flat = exp.markdown_dir / 'posts' / 'my-post.md'
        assert nested.exists() and flat.exists()

        content = nested.read_text(encoding='utf-8')
        assert content.startswith('---\n')
        assert 'title: "My Post"' in content
        assert 'description: "A summary."' in content
        assert 'Hello world.' in content
        assert content == flat.read_text(encoding='utf-8')
