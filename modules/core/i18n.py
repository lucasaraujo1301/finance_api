import gettext

from contextvars import ContextVar, Token
from functools import lru_cache
from pathlib import Path

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = {"es", "pt_BR"}
LOCALES_DIR = Path(__file__).resolve().parents[2] / "locales"

_current_locale: ContextVar[str] = ContextVar(
    "current_locale",
    default=DEFAULT_LOCALE,
)


@lru_cache(maxsize=None)
def _get_translation(locale: str) -> gettext.NullTranslations:
    return gettext.translation(
        domain="messages",
        localedir=LOCALES_DIR,
        languages=[locale],
        fallback=True,
    )


def activate(locale: str) -> Token[str]:
    normalized_locale = locale.replace("-", "_")
    if normalized_locale not in SUPPORTED_LOCALES:
        normalized_locale = DEFAULT_LOCALE

    return _current_locale.set(normalized_locale)


def deactivate(token: Token[str]) -> None:
    _current_locale.reset(token)


def get_locale() -> str:
    return _current_locale.get()


def gettext_(message: str) -> str:
    return _get_translation(get_locale()).gettext(message)


def ngettext(singular: str, plural: str, count: int) -> str:
    return _get_translation(get_locale()).ngettext(singular, plural, count)


_ = gettext_
