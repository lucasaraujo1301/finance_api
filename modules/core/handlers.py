from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic_core import ErrorDetails
from sqlalchemy.exc import IntegrityError

from modules.core.config import settings
from modules.core.expcetion import BaseException, SystemException, ValidationException
from modules.core.logger import logger
from modules.core.schemas import ApiError, ApiResponse, ValidationErrorDetail


def convert_validation_errors(errors: list[ErrorDetails]) -> list[ValidationErrorDetail]:
    return [
        ValidationErrorDetail(
            loc=str(error["loc"][-1]),
            msg=error["msg"],
            type=error["type"],
        )
        for error in errors
    ]


def error_response(exception: BaseException, detail: list[ValidationErrorDetail] | None = None) -> dict:
    return ApiResponse(
        success=False,
        errors=ApiError(code=exception.error_code, message=exception.message, detail=detail),
    ).model_dump(mode="json")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exception = ValidationException()
        return JSONResponse(
            status_code=exception.status_code,
            content=error_response(exception, convert_validation_errors(cast(list[ErrorDetails], exc.errors()))),
        )

    @app.exception_handler(BaseException)
    async def http_exception_handler(request: Request, exc: BaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        exception = SystemException()
        return JSONResponse(
            status_code=409,
            content=error_response(exception),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        if settings.ENVIRONMENT != "test":
            logger.exception(exc)
        exception = SystemException()
        return JSONResponse(status_code=exception.status_code, content=error_response(exception))
