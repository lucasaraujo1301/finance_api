from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from modules.core.handlers import register_exception_handlers
from modules.core.middlewares import LocaleMiddleware, ProcessTimeMiddleware
from modules.entry.router import router as entry_router
from modules.user.router import router as user_router

app = FastAPI()

app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(LocaleMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(user_router, prefix="/api/v1")
app.include_router(entry_router, prefix="/api/v1")

register_exception_handlers(app)

add_pagination(app)
