"""Tests for FAQPage JSON-LD generation in wp_to_static_generator.

Covers the pure extraction helper (_extract_faq_pairs) and the injection
method (add_faq_schema), both of which must be conservative: they only emit
FAQ structured data for content that genuinely has a FAQ section.
"""

import json

from bs4 import BeautifulSoup

from wp_to_static_generator import WordPressStaticGenerator


def _gen():
    # Network is never touched by the schema helpers; build a generator with
    # incremental mode off so no cache/state is initialised.
    return WordPressStaticGenerator(
        wp_url='https://wp.example',
        auth_token='x',
        output_dir='/tmp/faq-test-out',
        target_domain='https://example.com',
        use_incremental=False,
    )


def _soup(article_html, body_class='single-post'):
    return BeautifulSoup(
        f'<html><head><title>t</title></head>'
        f'<body class="{body_class}"><article>{article_html}</article></body></html>',
        'html.parser',
    )


# ── _extract_faq_pairs ────────────────────────────────────────────────────

def test_heading_based_faq_pairs_extracted():
    soup = _soup(
        '<h2>FAQ</h2>'
        '<h3>What is it?</h3><p>It is a thing.</p>'
        '<h3>How much?</h3><p>It is free.</p>'
    )
    pairs = WordPressStaticGenerator._extract_faq_pairs(soup)
    assert pairs == [
        {'question': 'What is it?', 'answer': 'It is a thing.'},
        {'question': 'How much?', 'answer': 'It is free.'},
    ]


def test_frequently_asked_questions_heading_is_recognised():
    soup = _soup(
        '<h2>Frequently Asked Questions</h2>'
        '<h3>Q one?</h3><p>A one.</p>'
        '<h3>Q two?</h3><p>A two.</p>'
    )
    pairs = WordPressStaticGenerator._extract_faq_pairs(soup)
    assert len(pairs) == 2


def test_definition_list_faq_extracted():
    soup = _soup(
        '<h2>FAQ</h2>'
        '<dl>'
        '<dt>First question</dt><dd>First answer.</dd>'
        '<dt>Second question</dt><dd>Second answer.</dd>'
        '</dl>'
    )
    pairs = WordPressStaticGenerator._extract_faq_pairs(soup)
    assert pairs == [
        {'question': 'First question', 'answer': 'First answer.'},
        {'question': 'Second question', 'answer': 'Second answer.'},
    ]


def test_section_ends_at_next_same_level_heading():
    soup = _soup(
        '<h2>FAQ</h2>'
        '<h3>In scope?</h3><p>Yes.</p>'
        '<h2>Related Posts</h2>'
        '<h3>Not a question?</h3><p>Should be ignored.</p>'
    )
    pairs = WordPressStaticGenerator._extract_faq_pairs(soup)
    assert pairs == [{'question': 'In scope?', 'answer': 'Yes.'}]


def test_subheading_without_question_mark_is_skipped():
    soup = _soup(
        '<h2>FAQ</h2>'
        '<h3>Just a note</h3><p>Not a question.</p>'
        '<h3>Real question?</h3><p>Real answer.</p>'
    )
    pairs = WordPressStaticGenerator._extract_faq_pairs(soup)
    assert pairs == [{'question': 'Real question?', 'answer': 'Real answer.'}]


def test_no_faq_section_returns_empty():
    soup = _soup('<h2>Introduction</h2><p>Hello.</p>')
    assert WordPressStaticGenerator._extract_faq_pairs(soup) == []


def test_faq_in_word_boundary_only():
    # "FAQS" appearing inside another word must not trip detection.
    soup = _soup('<h2>Effaqsomething overview</h2><p>x</p>')
    assert WordPressStaticGenerator._extract_faq_pairs(soup) == []


# ── add_faq_schema ────────────────────────────────────────────────────────

def _faq_schemas(soup):
    out = []
    for s in soup.find_all('script', type='application/ld+json'):
        data = json.loads(s.string)
        if data.get('@type') == 'FAQPage':
            out.append(data)
    return out


def test_add_faq_schema_injects_for_valid_faq():
    soup = _soup(
        '<h2>FAQ</h2>'
        '<h3>What is it?</h3><p>A thing.</p>'
        '<h3>Why?</h3><p>Because.</p>'
    )
    _gen().add_faq_schema(soup)
    schemas = _faq_schemas(soup)
    assert len(schemas) == 1
    entities = schemas[0]['mainEntity']
    assert entities[0]['@type'] == 'Question'
    assert entities[0]['name'] == 'What is it?'
    assert entities[0]['acceptedAnswer']['text'] == 'A thing.'
    assert len(entities) == 2


def test_single_question_is_not_emitted():
    soup = _soup('<h2>FAQ</h2><h3>Only one?</h3><p>Yes.</p>')
    _gen().add_faq_schema(soup)
    assert _faq_schemas(soup) == []


def test_no_faq_no_schema():
    soup = _soup('<h2>Body</h2><p>No questions here.</p>')
    _gen().add_faq_schema(soup)
    assert _faq_schemas(soup) == []


def test_not_injected_on_non_article_pages():
    soup = _soup(
        '<h2>FAQ</h2><h3>A?</h3><p>1.</p><h3>B?</h3><p>2.</p>',
        body_class='archive',
    )
    _gen().add_faq_schema(soup)
    assert _faq_schemas(soup) == []


def test_existing_faqpage_schema_not_duplicated():
    soup = _soup(
        '<h2>FAQ</h2><h3>A?</h3><p>1.</p><h3>B?</h3><p>2.</p>'
    )
    existing = soup.new_tag('script', type='application/ld+json')
    existing.string = json.dumps({'@context': 'https://schema.org',
                                  '@type': 'FAQPage', 'mainEntity': []})
    soup.head.append(existing)
    _gen().add_faq_schema(soup)
    # Still only the one we pre-seeded — no second FAQPage added.
    assert len(_faq_schemas(soup)) == 1
