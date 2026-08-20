from fastapi import APIRouter, status

from modules.service_account.dependencies import CurrentServiceAccount
from modules.user.dependencies import AuthServiceDep, Superuser, UserServiceDep
from modules.user.schemas import (
    CreateUserSchema,
    LoginSchema,
    RefreshTokenSchema,
    TelegramUserCreateSchema,
    TokenSchema,
)

router = APIRouter(prefix="/users", tags=["users"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login(data: LoginSchema, auth_service: AuthServiceDep):
    return await auth_service.login(data)


@auth_router.post("/refresh", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def refresh_token(data: RefreshTokenSchema, auth_service: AuthServiceDep):
    return await auth_service.refresh_token(data.refresh_token)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserSchema, user_service: UserServiceDep,  _: Superuser):
    return await user_service.create_user(data)


@router.post("/telegram", status_code=status.HTTP_201_CREATED)
async def create_telegram_user(
    data: TelegramUserCreateSchema,
    user_service: UserServiceDep,
    _: CurrentServiceAccount,
):
    return await user_service.create_telegram_user(data)
