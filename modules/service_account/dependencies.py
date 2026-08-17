from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.core.logger import logger
from modules.service_account.exceptions import ApiKeyMissing
from modules.service_account.models import ServiceAccountModel
from modules.service_account.services import ServiceAccountService

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def get_service_account_service(
    db_session: Annotated[AsyncSession, Depends(get_db)],
) -> ServiceAccountService:
    return ServiceAccountService(logger, db_session)


async def get_current_service_account(
    api_key: Annotated[str | None, Depends(api_key_header)],
    service: Annotated[ServiceAccountService, Depends(get_service_account_service)],
) -> ServiceAccountModel:
    if not api_key:
        raise ApiKeyMissing()

    return await service.get_by_api_key(api_key)
