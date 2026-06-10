"""Sanity tests for config.py invariants other scripts rely on."""

import re

from config import Config


def test_person_same_as_derives_from_social_profiles():
    assert Config.PERSON_SAME_AS == tuple(p['url'] for p in Config.SOCIAL_PROFILES)


def test_social_profiles_have_required_fields():
    for profile in Config.SOCIAL_PROFILES:
        assert profile['name']
        assert profile['url'].startswith('https://')
        assert profile['color'].startswith('#')


def test_noindex_patterns_compile():
    for pattern in Config.NOINDEX_PATH_PATTERNS:
        re.compile(pattern)


def test_utterances_repo_is_owner_slash_name():
    assert re.fullmatch(r'[\w.-]+/[\w.-]+', Config.UTTERANCES_REPO)


def test_default_og_image_is_a_root_relative_path():
    assert Config.DEFAULT_OG_IMAGE_PATH.startswith('/')
    assert not Config.DEFAULT_OG_IMAGE_PATH.startswith('//')


def test_urls_have_no_trailing_slash():
    # Scripts concatenate paths onto these — a trailing slash would double up.
    assert not Config.WP_URL.endswith('/')
    assert not Config.TARGET_DOMAIN.endswith('/')
