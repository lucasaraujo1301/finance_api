from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from modules.core.i18n import activate, deactivate
from modules.core.utils import resolve_locale


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        locale = resolve_locale(request.headers.get("Accept-Language"))
        token = activate(locale)

        try:
            return await call_next(request)
        finally:
            deactivate(token)
