from logging import Logger

from sqlalchemy.ext.asyncio import AsyncSession

from modules.service_account.exceptions import ServiceAccountAlreadyExists, ServiceAccountNotFound
from modules.service_account.models import ServiceAccountModel
from modules.service_account.repository import ServiceAccountRepository
from modules.service_account.schemas import (
    CreatedServiceAccountSchema,
    CreateServiceAccountSchema,
    ServiceAccountSchema,
)
from modules.service_account.utils import generate_api_key, hash_api_key


class ServiceAccountService:
    def __init__(self, logger: Logger, db_session: AsyncSession):
        self.logger = logger
        self._repository = ServiceAccountRepository(db_session)

    async def create(self, data: CreateServiceAccountSchema) -> CreatedServiceAccountSchema:
        if await self._repository.get_by_name(data.name):
            raise ServiceAccountAlreadyExists()

        raw_key, encrypted_key = generate_api_key()
        service_account = ServiceAccountModel(name=data.name, api_key=encrypted_key)

        self.logger.info("Creating service account")
        await self._repository.create(service_account)

        account_data = ServiceAccountSchema.model_validate(service_account).model_dump()
        return CreatedServiceAccountSchema(**account_data, api_key=raw_key)

    async def get_by_api_key(self, api_key: str) -> ServiceAccountModel:
        service_account = await self._repository.get_by_api_key(hash_api_key(api_key))
        if service_account is None:
            raise ServiceAccountNotFound()

        return service_account
