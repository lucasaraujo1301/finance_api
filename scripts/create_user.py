import argparse
import asyncio
import sys

from pwdlib import PasswordHash

from modules.core.database import AsyncSessionLocal, engine
from modules.core.logger import logger
from modules.user.repository import UserRepository
from modules.user.schemas import CreateUserSchema
from modules.user.services import UserService


async def create_user(email: str, telegram_id: str, password: str, is_superuser: bool) -> None:
    try:
        async with AsyncSessionLocal() as session:
            repository = UserRepository(session)
            service = UserService(logger, repository, PasswordHash.recommended())
            user = await service.create_user(
                CreateUserSchema(
                    email=email,
                    telegram_id=telegram_id,
                    password=password,
                    is_superuser=is_superuser,
                )
            )

        sys.stdout.write(f"Created user: {user.telegram_id}\nSuperuser: {is_superuser}\n")
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a user with an email, Telegram ID, and password.")
    parser.add_argument("email", help="Unique email address")
    parser.add_argument("telegram_id", help="Unique Telegram ID")
    parser.add_argument("password", help="User password")
    parser.add_argument("--superuser", action="store_true", help="Create the user as a superuser")
    args = parser.parse_args()
    asyncio.run(create_user(args.email, args.telegram_id, args.password, args.superuser))


if __name__ == "__main__":
    main()
