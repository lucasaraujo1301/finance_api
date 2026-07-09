from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from modules.core.handlers import register_exception_handlers
from modules.core.logger import logger
from modules.core.middlewares import ProcessTimeMiddleware
from modules.user.router import router as user_router

app = FastAPI()

app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(CorrelationIdMiddleware)

register_exception_handlers(app)

app.include_router(user_router, prefix="/api/v1")

@app.get("/exception")
async def test_logs():
    logger.info("Testing")
    return {}
