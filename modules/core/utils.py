from babel import Locale, UnknownLocaleError

from modules.core.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES


def resolve_locale(language_tag: str | None) -> str:
    if not language_tag:
        return DEFAULT_LOCALE

    try:
        locale = Locale.parse(language_tag, sep="-")
    except UnknownLocaleError, ValueError:
        return DEFAULT_LOCALE

    normalized_locale = str(locale)

    # Exact match: pt-BR becomes pt_BR.
    if normalized_locale in SUPPORTED_LOCALES:
        return normalized_locale

    # Regional fallback: es-ES or es-MX becomes es.
    if locale.language in SUPPORTED_LOCALES:
        return locale.language

    return DEFAULT_LOCALE
