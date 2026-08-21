import argparse
import asyncio
import sys

from modules.core.database import AsyncSessionLocal, engine
from modules.core.logger import logger
from modules.service_account.schemas import CreateServiceAccountSchema
from modules.service_account.services import ServiceAccountService


async def create_service_account(name: str) -> None:
    try:
        async with AsyncSessionLocal() as session:
            service = ServiceAccountService(logger, session)
            service_account = await service.create(CreateServiceAccountSchema(name=name))
            await session.commit()

        sys.stdout.write(f"Service account: {service_account.name}\nAPI key: {service_account.api_key}\n")
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a service account and display its API key.")
    parser.add_argument("name", help="Unique service-account name")
    args = parser.parse_args()
    asyncio.run(create_service_account(args.name))


if __name__ == "__main__":
    main()
