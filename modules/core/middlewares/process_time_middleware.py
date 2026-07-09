import time

from starlette.middleware.base import BaseHTTPMiddleware

from modules.core.logger import logger


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"{request.method} {request.url.path} {response.status_code} {process_time:.4f}s")
        return response
