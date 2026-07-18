import pytest

from modules.core.i18n import _, activate


@pytest.mark.parametrize(("locale", "expected_message"), [("en", "Hello!"), ("pt-BR", "Olá!"), ("es", "¡Holá!")])
def test_translations(locale: str, expected_message: str):
    activate(locale)
    assert _("Hello!") == expected_message
