import pytest

from modules.core.i18n import _, activate, deactivate


@pytest.mark.parametrize(("locale", "expected_message"), [("en", "Hello!"), ("pt-BR", "Olá!"), ("es", "¡Hola!")])
def test_translations(locale: str, expected_message: str):
    token = activate(locale)

    try:
        assert _("Hello!") == expected_message
    finally:
        deactivate(token)
