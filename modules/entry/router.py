from typing import Annotated

from fastapi import APIRouter, Query, status
from fastapi_pagination import Page

from modules.core.schemas import ApiResponse
from modules.entry.dependencies import EntryServiceDep
from modules.entry.schemas import (
    EntryFilterSchema,
    EntryRequestSchema,
    EntrySchema,
    TelegramEntryRequestSchema,
)
from modules.service_account.dependencies import CurrentServiceAccount
from modules.user.dependencies import CurrentUser

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("/", response_model=ApiResponse[EntrySchema], status_code=status.HTTP_201_CREATED)
async def create_entry(data: EntryRequestSchema, entry_service: EntryServiceDep, user: CurrentUser):
    return ApiResponse(data=await entry_service.create(user_id=user.id, data=data))


@router.get("/", response_model=Page[EntrySchema])
async def get_entries(
    entry_service: EntryServiceDep, query_params: Annotated[EntryFilterSchema, Query()], user: CurrentUser
):
    return await entry_service.get_all(user.id, query_params)


@router.post("/telegram", response_model=ApiResponse[EntrySchema], status_code=status.HTTP_201_CREATED)
async def create_from_telegram(
    data: TelegramEntryRequestSchema, entry_service: EntryServiceDep, service_account: CurrentServiceAccount
):
    return ApiResponse(data=await entry_service.create_from_telegram(data=data, service_account_id=service_account.id))
