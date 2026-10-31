"""Tests for the SEO fixer's pure transforms."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from fix_seo_issues import SEOFixer


@pytest.fixture
def fixer(tmp_path):
    return SEOFixer(public_dir=str(tmp_path))


def _soup(html):
    return BeautifulSoup(html, 'html.parser')


class TestCleanTruncate:
    def test_short_text_passes_through(self):
        assert SEOFixer._clean_truncate('Short text.', 100) == 'Short text.'

    def test_cuts_at_sentence_boundary(self):
        # The sentence terminator must land in the latter half of the window
        # for the sentence cut to be taken (avoids overly short snippets).
        text = 'First sentence goes here nicely. Second part continues even longer.'
        out = SEOFixer._clean_truncate(text, 40)
        assert out == 'First sentence goes here nicely.'

    def test_early_sentence_break_falls_back_to_word_cut(self):
        # Terminator in the first half of the window → word-boundary cut wins.
        text = 'First sentence here. Second sentence is much longer and goes on.'
        out = SEOFixer._clean_truncate(text, 40)
        assert out == 'First sentence here. Second sentence is'

    def test_cuts_at_word_boundary_without_ellipsis(self):
        text = 'word ' * 50
        out = SEOFixer._clean_truncate(text, 32)
        assert len(out) <= 32
        assert not out.endswith('...')
        assert not out.endswith(' ')

    def test_never_breaks_mid_word(self):
        text = 'supercalifragilistic expialidocious words continue here'
        out = SEOFixer._clean_truncate(text, 30)
        assert out in text  # a clean prefix cut at a word boundary


class TestFixMultipleH1:
    def test_extra_h1s_demoted_to_h2(self, fixer):
        soup = _soup('<body><h1>Keep</h1><h1>Demote</h1><h1>Demote too</h1></body>')
        assert fixer.fix_multiple_h1(soup, Path('x.html')) is True
        assert len(soup.find_all('h1')) == 1
        assert soup.find('h1').get_text() == 'Keep'
        assert len(soup.find_all('h2')) == 2

    def test_single_h1_untouched(self, fixer):
        soup = _soup('<body><h1>Only</h1></body>')
        assert fixer.fix_multiple_h1(soup, Path('x.html')) is False
        assert len(soup.find_all('h1')) == 1


class TestEnsureImageAltText:
    def test_alt_derived_from_filename(self, fixer):
        soup = _soup('<img src="/wp-content/uploads/my-test-image.png">')
        assert fixer.ensure_image_alt_text(soup, Path('x.html')) is True
        assert soup.find('img')['alt'] == 'My Test Image'

    def test_existing_alt_untouched(self, fixer):
        soup = _soup('<img src="/a.png" alt="Hand written alt">')
        assert fixer.ensure_image_alt_text(soup, Path('x.html')) is False
        assert soup.find('img')['alt'] == 'Hand written alt'

    def test_srcless_image_gets_generic_alt(self, fixer):
        soup = _soup('<img>')
        fixer.ensure_image_alt_text(soup, Path('x.html'))
        assert soup.find('img')['alt'] == 'Image'


class TestFixTitleLength:
    def test_truncated_title_restored_from_jsonld(self, fixer):
        soup = _soup(
            '<head><title>How to configure VMware vSphere with...</title>'
            '<script type="application/ld+json">'
            '{"@graph": [{"@type": "TechArticle", '
            '"headline": "How to configure VMware vSphere with NSX overlay networking"}]}'
            '</script></head>'
        )
        assert fixer.fix_title_length(soup, Path('x.html')) is True
        assert soup.find('title').get_text() == (
            'How to configure VMware vSphere with NSX overlay networking')

    def test_untruncated_title_left_alone(self, fixer):
        soup = _soup('<head><title>A perfectly fine title</title></head>')
        assert fixer.fix_title_length(soup, Path('x.html')) is False

    def test_no_jsonld_means_no_change(self, fixer):
        soup = _soup('<head><title>Broken title that ends with...</title></head>')
        assert fixer.fix_title_length(soup, Path('x.html')) is False
        assert soup.find('title').get_text() == 'Broken title that ends with...'


class TestFixArticleEntityLinks:
    """M1 (author → Person @id) + L3 (about/mentions topic entities)."""

    def _article_page(self, *, graph):
        import json
        return _soup(
            '<head><script type="application/ld+json">'
            + json.dumps({"@graph": graph})
            + '</script></head>'
        )

    def _graph_of(self, soup):
        import json
        return json.loads(soup.find('script', type='application/ld+json').string)['@graph']

    def test_author_linked_to_person_id_when_person_node_present(self, fixer):
        soup = self._article_page(graph=[
            {"@type": "Person", "@id": "https://jameskilby.co.uk/#person",
             "name": "James Kilby"},
            {"@type": "TechArticle", "headline": "A post",
             "author": {"@type": "Person", "name": "James Kilby"}},
        ])
        assert fixer.fix_article_entity_links(soup, Path('x.html')) is True
        article = next(i for i in self._graph_of(soup) if i["@type"] == "TechArticle")
        assert article["author"]["@id"] == "https://jameskilby.co.uk/#person"

    def test_author_not_fabricated_without_person_node(self, fixer):
        # No Person node in the graph → never emit a dangling author reference.
        soup = self._article_page(graph=[
            {"@type": "TechArticle", "headline": "A post about nothing matched"},
        ])
        assert fixer.fix_article_entity_links(soup, Path('x.html')) is False
        article = self._graph_of(soup)[0]
        assert "author" not in article

    def test_existing_author_id_is_left_untouched(self, fixer):
        soup = self._article_page(graph=[
            {"@type": "Person", "@id": "https://jameskilby.co.uk/#person",
             "name": "James Kilby"},
            {"@type": "TechArticle", "headline": "A post",
             "author": {"@id": "https://jameskilby.co.uk/#someone-else"}},
        ])
        # author already has an @id, and headline matches no topic → no change.
        assert fixer.fix_article_entity_links(soup, Path('x.html')) is False

    def test_about_and_mentions_from_section_and_keywords(self, fixer):
        soup = self._article_page(graph=[
            {"@type": "TechArticle",
             "headline": "Tuning the homelab",
             "articleSection": "VMware",
             "keywords": ["vSphere", "Kubernetes", "homelab"]},
        ])
        assert fixer.fix_article_entity_links(soup, Path('x.html')) is True
        article = self._graph_of(soup)[0]
        # primary `about` comes from the section (VMware)
        assert article["about"]["name"] == "VMware"
        assert "wikidata.org/wiki/Q14958" in article["about"]["@id"]
        names = {m["name"] for m in article["mentions"]}
        assert {"VMware", "VMware vSphere", "Kubernetes"} <= names

    def test_no_topic_match_means_no_about_mentions(self, fixer):
        soup = self._article_page(graph=[
            {"@type": "Person", "@id": "https://jameskilby.co.uk/#person",
             "name": "James Kilby"},
            {"@type": "TechArticle", "headline": "A quiet day in the garden",
             "author": {"@type": "Person", "name": "James Kilby"}},
        ])
        # author still gets linked, but no topic entities are invented.
        assert fixer.fix_article_entity_links(soup, Path('x.html')) is True
        article = next(i for i in self._graph_of(soup) if i["@type"] == "TechArticle")
        assert "about" not in article
        assert "mentions" not in article

    def test_idempotent(self, fixer):
        soup = self._article_page(graph=[
            {"@type": "Person", "@id": "https://jameskilby.co.uk/#person",
             "name": "James Kilby"},
            {"@type": "TechArticle", "headline": "Cloudflare workers",
             "articleSection": "Cloudflare",
             "author": {"@type": "Person", "name": "James Kilby"}},
        ])
        assert fixer.fix_article_entity_links(soup, Path('x.html')) is True
        # second pass over the now-enriched soup is a no-op
        assert fixer.fix_article_entity_links(soup, Path('x.html')) is False

    def test_whole_word_matching_avoids_substrings(self):
        # 'aws' must not match inside 'laws'; 'docker' must not match 'dockers'
        # appearing only as a substring of another token is fine to skip.
        matched = SEOFixer._match_topic_entities("new laws about flaws", "")
        assert matched == []


class TestFixTitleDropBrandSuffix:
    def test_long_full_title_drops_suffix(self, fixer):
        # Full title (body + " - James Kilby" = 73c) exceeds the 60c SERP
        # target, so the suffix is shed and only the body remains.
        title = 'How to configure VMware vSphere with NSX overlay networking - James Kilby'
        assert len(title) > SEOFixer._TITLE_SERP_MAX_CHARS
        soup = _soup(f'<head><title>{title}</title></head>')
        assert fixer.fix_title_drop_brand_suffix(soup, Path('post.html')) is True
        assert soup.find('title').get_text() == (
            'How to configure VMware vSphere with NSX overlay networking')

    def test_short_full_title_keeps_suffix(self, fixer):
        # Full title (30c) fits within the 60c target — keep the suffix for
        # brand recall and leave the tag untouched.
        title = 'Short post title - James Kilby'
        assert len(title) <= SEOFixer._TITLE_SERP_MAX_CHARS
        soup = _soup(f'<head><title>{title}</title></head>')
        assert fixer.fix_title_drop_brand_suffix(soup, Path('post.html')) is False
        assert soup.find('title').get_text() == title

    def test_no_brand_suffix_left_alone(self, fixer):
        # A long title without a recognisable brand suffix is not touched.
        title = 'A very long standalone title with no branded site-name suffix at all'
        soup = _soup(f'<head><title>{title}</title></head>')
        assert fixer.fix_title_drop_brand_suffix(soup, Path('post.html')) is False
        assert soup.find('title').get_text() == title

    def test_homepage_untouched(self, fixer, tmp_path):
        # index.html is owned by fix_homepage_title — skip it even when its
        # full title is long enough to otherwise trigger a suffix drop.
        title = 'How to configure VMware vSphere with NSX overlay networking - James Kilby'
        soup = _soup(f'<head><title>{title}</title></head>')
        home = tmp_path / 'index.html'
        assert fixer.fix_title_drop_brand_suffix(soup, home) is False
        assert soup.find('title').get_text() == title


def _ld(graph):
    import json
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph})
            + '</script>')


def _graph(soup):
    import json
    return json.loads(soup.find('script', type='application/ld+json').string)['@graph']


PERSON = {'@type': ['Person', 'Organization'], '@id': 'https://jameskilby.co.uk/#person',
          'name': 'James Kilby'}
WP_AUTHOR = {'@type': 'Person', '@id': 'https://jameskilby.co.uk/author/admin/', 'name': 'James'}


class TestAuthorEntity:
    def test_wp_author_rewritten_to_person_and_orphan_dropped(self, fixer):
        article = {'@type': 'Article', '@id': 'https://jameskilby.co.uk/evs/#richSnippet',
                   'headline': 'EVS', 'author': {'@id': WP_AUTHOR['@id'], 'name': 'James'}}
        soup = _soup(f'<head>{_ld([PERSON, WP_AUTHOR, article])}</head>')
        assert fixer.fix_article_entity_links(soup, Path('evs.html')) is True
        graph = _graph(soup)
        art = next(n for n in graph if n['@type'] == 'Article')
        assert art['author'] == {'@id': PERSON['@id']}
        assert all(n.get('@id') != WP_AUTHOR['@id'] for n in graph)

    def test_idempotent(self, fixer):
        article = {'@type': 'Article', 'headline': 'x', 'author': {'@id': PERSON['@id']}}
        soup = _soup(f'<head>{_ld([PERSON, article])}</head>')
        assert fixer.fix_article_entity_links(soup, Path('p.html')) is False

    def test_wp_author_person_not_enriched(self, fixer):
        soup = _soup(f'<head>{_ld([dict(PERSON), dict(WP_AUTHOR)])}</head>')
        fixer.fix_person_enrichment(soup, Path('p.html'))
        graph = _graph(soup)
        wp = next(n for n in graph if n['@id'] == WP_AUTHOR['@id'])
        assert 'sameAs' not in wp


class TestArticleDates:
    def test_dates_taken_from_webpage_and_meta_aligned(self, fixer):
        webpage = {'@type': 'WebPage', '@id': 'https://jameskilby.co.uk/p/#webpage',
                   'datePublished': '2025-09-02T16:01:48+00:00',
                   'dateModified': '2026-06-05T18:42:51+00:00'}
        article = {'@type': 'TechArticle', 'headline': 'x',
                   'datePublished': '2025-09-02T16:01:48', 'dateModified': '2026-03-10T20:35:11'}
        soup = _soup('<head><meta property="article:published_time" content="2025-09-02T16:01:48">'
                     '<meta property="article:modified_time" content="2026-03-10T20:35:11">'
                     f'{_ld([webpage, article])}</head>')
        assert fixer.fix_techarticle_dedupe_and_dates(soup, Path('p.html')) is True
        art = next(n for n in _graph(soup) if n['@type'] == 'TechArticle')
        assert art['datePublished'] == '2025-09-02T16:01:48+00:00'
        assert art['dateModified'] == '2026-06-05T18:42:51+00:00'
        assert soup.find('meta', property='article:modified_time')['content'] == art['dateModified']
        assert fixer.fix_techarticle_dedupe_and_dates(soup, Path('p.html')) is False

    def test_naive_dates_get_utc_offset_without_webpage(self, fixer):
        article = {'@type': 'Article', 'headline': 'x',
                   'datePublished': '2020-01-01T10:00:00', 'dateModified': '2020-02-01T10:00:00'}
        soup = _soup(f'<head>{_ld([article])}</head>')
        assert fixer.fix_techarticle_dedupe_and_dates(soup, Path('p.html')) is True
        art = _graph(soup)[0]
        assert art['datePublished'] == '2020-01-01T10:00:00+00:00'
        assert art['dateModified'] == '2020-02-01T10:00:00+00:00'


class TestDuplicateOrganization:
    def test_standalone_organization_dropped_when_person_is_org(self, fixer):
        org = {'@type': 'Organization', '@id': 'https://jameskilby.co.uk/#organization',
               'name': 'James Kilby'}
        site = {'@type': 'WebSite', '@id': 'https://jameskilby.co.uk/#website',
                'publisher': {'@id': org['@id']}}
        soup = _soup(f'<head>{_ld([dict(PERSON), site, org])}</head>')
        assert fixer.fix_organization_sameas(soup, Path('p.html')) is True
        graph = _graph(soup)
        assert all(n.get('@id') != org['@id'] for n in graph)
        assert next(n for n in graph if n['@type'] == 'WebSite')['publisher'] == {'@id': PERSON['@id']}

    def test_organization_kept_without_person_identity(self, fixer):
        org = {'@type': 'Organization', '@id': 'https://jameskilby.co.uk/#organization',
               'name': 'James Kilby'}
        soup = _soup(f'<head>{_ld([org])}</head>')
        fixer.fix_organization_sameas(soup, Path('index.html'))
        assert _graph(soup)[0]['@id'] == org['@id']


class TestStaleNoindex:
    ARTICLE = {'@type': 'Article', 'headline': 'x'}

    def _page(self, tmp_path, rel, robots, graph):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        soup = _soup(f'<head><meta name="robots" content="{robots}">{_ld(graph)}</head>')
        return soup, path

    def test_removed_from_content_page_no_longer_listed(self, fixer, tmp_path):
        soup, path = self._page(tmp_path, 'evs/index.html', 'noindex,follow', [self.ARTICLE])
        assert fixer.fix_thin_archive_noindex(soup, path) is True
        assert 'noindex' not in soup.find('meta', attrs={'name': 'robots'})['content']

    def test_non_content_page_keeps_noindex(self, fixer, tmp_path):
        soup, path = self._page(tmp_path, '404.html', 'noindex,follow', [])
        assert fixer.fix_thin_archive_noindex(soup, path) is False
        assert soup.find('meta', attrs={'name': 'robots'})['content'] == 'noindex,follow'

    def test_rank_math_noindex_left_alone(self, fixer, tmp_path):
        soup, path = self._page(tmp_path, 'some-page/index.html', 'noindex, follow', [self.ARTICLE])
        assert fixer.fix_thin_archive_noindex(soup, path) is False
