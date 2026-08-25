"""Tests for the sitemap-image existence helpers in wp_to_static_generator.

`image_url_to_output_path` and `image_file_present` are pure functions that map
a same-domain image URL back to its on-disk file in the output directory and
verify that the file was actually generated. They keep the image sitemap honest
so Google is never handed an <image:loc> that 404s.
"""

from wp_to_static_generator import image_file_present, image_url_to_output_path

DOMAIN = 'https://jameskilby.co.uk'


class TestImageUrlToOutputPath:
    def test_same_domain_absolute_url_maps_into_output_dir(self, tmp_path):
        path = image_url_to_output_path(
            f'{DOMAIN}/wp-content/uploads/img.png', DOMAIN, tmp_path)
        assert path == tmp_path / 'wp-content/uploads/img.png'

    def test_root_relative_url_maps_into_output_dir(self, tmp_path):
        path = image_url_to_output_path(
            '/wp-content/uploads/img.png', DOMAIN, tmp_path)
        assert path == tmp_path / 'wp-content/uploads/img.png'

    def test_off_domain_url_returns_none(self, tmp_path):
        assert image_url_to_output_path(
            'https://cdn.example.com/a/img.png', DOMAIN, tmp_path) is None

    def test_domain_root_returns_none(self, tmp_path):
        assert image_url_to_output_path(DOMAIN, DOMAIN, tmp_path) is None

    def test_query_string_and_fragment_stripped(self, tmp_path):
        path = image_url_to_output_path(
            f'{DOMAIN}/wp-content/uploads/img.png?ver=3#x', DOMAIN, tmp_path)
        assert path == tmp_path / 'wp-content/uploads/img.png'

    def test_percent_encoding_decoded(self, tmp_path):
        path = image_url_to_output_path(
            f'{DOMAIN}/wp-content/uploads/my%20image.png', DOMAIN, tmp_path)
        assert path == tmp_path / 'wp-content/uploads/my image.png'


class TestImageFilePresent:
    def _write(self, tmp_path, rel, data=b'x'):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
        return f

    def test_present_non_empty_file_is_true(self, tmp_path):
        self._write(tmp_path, 'wp-content/uploads/img.png')
        assert image_file_present(
            f'{DOMAIN}/wp-content/uploads/img.png', DOMAIN, tmp_path) is True

    def test_absent_file_is_false(self, tmp_path):
        assert image_file_present(
            f'{DOMAIN}/wp-content/uploads/missing.png', DOMAIN, tmp_path) is False

    def test_zero_byte_file_is_false(self, tmp_path):
        self._write(tmp_path, 'wp-content/uploads/empty.png', data=b'')
        assert image_file_present(
            f'{DOMAIN}/wp-content/uploads/empty.png', DOMAIN, tmp_path) is False

    def test_off_domain_url_is_false(self, tmp_path):
        assert image_file_present(
            'https://cdn.example.com/a/img.png', DOMAIN, tmp_path) is False

    def test_query_string_variant_resolves_to_the_file(self, tmp_path):
        self._write(tmp_path, 'wp-content/uploads/img.png')
        assert image_file_present(
            f'{DOMAIN}/wp-content/uploads/img.png?ver=9', DOMAIN, tmp_path) is True

    def test_percent_encoded_path_resolves_to_the_file(self, tmp_path):
        self._write(tmp_path, 'wp-content/uploads/my image.png')
        assert image_file_present(
            f'{DOMAIN}/wp-content/uploads/my%20image.png', DOMAIN, tmp_path) is True

    def test_directory_is_not_treated_as_a_file(self, tmp_path):
        (tmp_path / 'wp-content/uploads').mkdir(parents=True)
        assert image_file_present(
            f'{DOMAIN}/wp-content/uploads', DOMAIN, tmp_path) is False
