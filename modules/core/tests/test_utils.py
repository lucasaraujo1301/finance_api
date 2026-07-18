import pytest

from modules.core.i18n import DEFAULT_LOCALE
from modules.core.utils import resolve_locale


@pytest.mark.parametrize("language_tag", [None, ""])
def test_resolve_locale_returns_default_when_tag_is_missing(language_tag: str | None):
    assert resolve_locale(language_tag) == DEFAULT_LOCALE


@pytest.mark.parametrize(
    ("language_tag", "expected"),
    [
        ("pt-BR", "pt_BR"),
        ("es", "es"),
    ],
)
def test_resolve_locale_returns_supported_locale(language_tag: str, expected: str):
    assert resolve_locale(language_tag) == expected


@pytest.mark.parametrize("language_tag", ["es-ES", "es-MX"])
def test_resolve_locale_falls_back_to_supported_base_language(language_tag: str):
    assert resolve_locale(language_tag) == "es"


@pytest.mark.parametrize("language_tag", ["en-US", "fr-FR", "not-a-locale"])
def test_resolve_locale_returns_default_for_unsupported_or_invalid_tag(language_tag: str):
    assert resolve_locale(language_tag) == DEFAULT_LOCALE
