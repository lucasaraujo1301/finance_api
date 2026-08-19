from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.service_account.dependencies import get_current_service_account
from modules.service_account.models import ServiceAccountModel
from modules.user.dependencies import get_auth_service, get_user_service
from modules.user.schemas import (
    CreateUserSchema,
    LoginSchema,
    RefreshTokenSchema,
    TelegramUserCreateSchema,
    TokenSchema,
)
from modules.user.services import AuthService, UserService

router = APIRouter(prefix="/users", tags=["users"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=TokenSchema)
async def login(data: LoginSchema, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    return await auth_service.login(data)


@auth_router.post("/refresh", response_model=TokenSchema)
async def refresh_token(data: RefreshTokenSchema, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    return await auth_service.refresh_token(data.refresh_token)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserSchema, user_service: Annotated[UserService, Depends(get_user_service)]):
    return await user_service.create_user(data)


@router.post("/telegram/", status_code=status.HTTP_201_CREATED)
async def create_telegram_user(
    data: TelegramUserCreateSchema,
    user_service: Annotated[UserService, Depends(get_user_service)],
    _: Annotated[ServiceAccountModel, Depends(get_current_service_account)],
):
    return await user_service.create_telegram_user(data)
