from fastapi import APIRouter, status

from modules.core.schemas import ApiResponse
from modules.service_account.dependencies import CurrentServiceAccount
from modules.user.dependencies import AuthServiceDep, CurrentUser, PasswordSetupUser, Superuser, UserServiceDep
from modules.user.schemas import (
    CreateUserSchema,
    LoginSchema,
    PasswordUpdateSchema,
    PatchUserSchema,
    RefreshTokenSchema,
    TelegramUserCreateSchema,
    TelegramUserResponseSchema,
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


@router.patch("/password", response_model=ApiResponse[None], status_code=status.HTTP_200_OK)
async def update_password(data: PasswordUpdateSchema, user_service: UserServiceDep, user: PasswordSetupUser):
    await user_service.update_password(user, data)
    return ApiResponse(data=None)


@router.post("/", response_model=ApiResponse[UserSchema], status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserSchema, user_service: UserServiceDep, _: Superuser):
    return ApiResponse(data=await user_service.create_user(data))


@router.post("/telegram", response_model=ApiResponse[TelegramUserResponseSchema], status_code=status.HTTP_201_CREATED)
async def create_telegram_user(
    data: TelegramUserCreateSchema,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    _: CurrentServiceAccount,
):
    user = await user_service.create_telegram_user(data)
    return ApiResponse(
        data=TelegramUserResponseSchema(
            **user.model_dump(),
            password_update_url=auth_service.create_password_update_url(user),
        )
    )


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
