from fastapi import FastAPI

from modules.core.handlers import register_exception_handlers
from modules.core.middlewares import ProcessTimeMiddleware
from modules.user.router import router as user_router

app = FastAPI()
register_exception_handlers(app)
app.add_middleware(ProcessTimeMiddleware)

app.include_router(user_router, prefix="/api/v1")
