from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyHeader

from modules.core.database import AsyncDbDep
from modules.core.logger import logger
from modules.service_account.exceptions import ApiKeyMissing
from modules.service_account.models import ServiceAccountModel
from modules.service_account.repository import ServiceAccountRepository
from modules.service_account.services import ServiceAccountService

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


def get_service_account_repository(db_session: AsyncDbDep) -> ServiceAccountRepository:
    return ServiceAccountRepository(db_session)


async def get_service_account_service(
    repository: Annotated[ServiceAccountRepository, Depends(get_service_account_repository)],
) -> ServiceAccountService:
    return ServiceAccountService(logger, repository)


async def get_current_service_account(
    api_key: Annotated[str | None, Depends(api_key_header)],
    service: Annotated[ServiceAccountService, Depends(get_service_account_service)],
) -> ServiceAccountModel:
    if not api_key:
        raise ApiKeyMissing()

    return await service.get_by_api_key(api_key)


CurrentServiceAccount = Annotated[ServiceAccountModel, Depends(get_current_service_account)]
ServiceAccountRepositoryDep = Annotated[
    ServiceAccountRepository,
    Depends(get_service_account_repository),
]
