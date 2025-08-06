import pytest
from app.utils import (
    generate_shortcode,
    is_valid_url,
    is_valid_shortcode,
    is_auto_generated_shortcode_valid,
)


class TestShortcodeGeneration:

    def test_generate_shortcode_default_length(self):
        shortcode = generate_shortcode()
        assert len(shortcode) == 6

    def test_generate_shortcode_custom_length(self):
        shortcode = generate_shortcode(10)
        assert len(shortcode) == 10

    def test_generate_shortcode_valid_characters(self):
        shortcode = generate_shortcode()
        valid_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        )
        assert all(c in valid_chars for c in shortcode)


class TestURLValidation:

    def test_valid_urls(self):
        valid_urls = [
            "https://www.example.com",
            "http://example.com",
            "https://subdomain.example.com/path",
            "https://example.com:8080/path?query=value",
            "ftp://ftp.example.com",
        ]
        for url in valid_urls:
            assert is_valid_url(url), f"URL should be valid: {url}"

    def test_invalid_urls(self):
        invalid_urls = [
            "not-a-url",
            "http://",
            "://example.com",
            "",
            "example.com",  # No scheme
            "http:///path",  # No netloc
        ]
        for url in invalid_urls:
            assert not is_valid_url(url), f"URL should be invalid: {url}"


class TestShortcodeValidation:

    def test_valid_shortcodes(self):
        valid_shortcodes = [
            "abc123",
            "test_code",
            "a",
            "123456",
            "UPPERCASE",
            "mixed_Case_123",
        ]
        for shortcode in valid_shortcodes:
            assert is_valid_shortcode(
                shortcode
            ), f"Shortcode should be valid: {shortcode}"

    def test_invalid_shortcodes(self):
        invalid_shortcodes = ["", None]
        for shortcode in invalid_shortcodes:
            assert not is_valid_shortcode(
                shortcode
            ), f"Shortcode should be invalid: {shortcode}"

    def test_auto_generated_shortcode_validation(self):
        # Valid codes
        valid_auto = ["abc123", "ABC_12", "test_1", "123456"]
        for shortcode in valid_auto:
            assert is_auto_generated_shortcode_valid(
                shortcode
            ), f"Auto shortcode should be valid: {shortcode}"

        # invalid codes
        invalid_auto = ["toolong123", "short", "abc-12", "abc 12", "abc@12", ""]
        for shortcode in invalid_auto:
            assert not is_auto_generated_shortcode_valid(
                shortcode
            ), f"Auto shortcode should be invalid: {shortcode}"
