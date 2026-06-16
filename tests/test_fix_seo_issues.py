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
