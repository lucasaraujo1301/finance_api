from fastapi import APIRouter, status

from modules.core.schemas import ApiResponse
from modules.service_account.dependencies import CurrentServiceAccount
from modules.user.dependencies import AuthServiceDep, CurrentUser, Superuser, UserServiceDep
from modules.user.schemas import (
    CreateUserSchema,
    LoginSchema,
    PatchUserSchema,
    RefreshTokenSchema,
    TelegramUserCreateSchema,
    TokenSchema,
    UserSchema,
)

router = APIRouter(prefix="/users", tags=["users"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=ApiResponse[TokenSchema], status_code=status.HTTP_200_OK)
async def login(data: LoginSchema, auth_service: AuthServiceDep):
    return ApiResponse(data=await auth_service.login(data))


@auth_router.post("/refresh", response_model=ApiResponse[TokenSchema], status_code=status.HTTP_200_OK)
async def refresh_token(data: RefreshTokenSchema, auth_service: AuthServiceDep):
    return ApiResponse(data=await auth_service.refresh_token(data.refresh_token))


@router.post("/", response_model=ApiResponse[UserSchema], status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserSchema, user_service: UserServiceDep, _: Superuser):
    return ApiResponse(data=await user_service.create_user(data))


@router.post("/telegram", response_model=ApiResponse[UserSchema], status_code=status.HTTP_201_CREATED)
async def create_telegram_user(
    data: TelegramUserCreateSchema,
    user_service: UserServiceDep,
    _: CurrentServiceAccount,
):
    return ApiResponse(data=await user_service.create_telegram_user(data))


@router.get("/me", status_code=status.HTTP_200_OK, response_model=ApiResponse[UserSchema])
async def me(
    user_service: UserServiceDep,
    user: CurrentUser,
):
    return ApiResponse(data=await user_service.get_by_id(user.id))


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=ApiResponse[UserSchema])
async def update_me(
    data: PatchUserSchema,
    user_service: UserServiceDep,
    user: CurrentUser,
):
    return ApiResponse(data=await user_service.update_user(user, data))
