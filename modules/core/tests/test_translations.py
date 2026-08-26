import pytest

from modules.core.i18n import _, activate, deactivate, ngettext


@pytest.mark.parametrize(("locale", "expected_message"), [("en", "Hello!"), ("pt-BR", "Olá!"), ("es", "¡Hola!")])
def test_translations(locale: str, expected_message: str):
    token = activate(locale)

    try:
        assert _("Hello!") == expected_message
    finally:
        deactivate(token)


def test_ngettext_returns_plural_for_count_greater_than_one():
    token = activate("en")

    try:
        assert ngettext("entry", "entries", 2) == "entries"
    finally:
        deactivate(token)
