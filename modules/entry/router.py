from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page

from modules.entry.dependencies import get_entry_service
from modules.entry.schemas import EntryFilterSchema, EntryRequestSchema, EntrySchema, TelegramEntryRequestSchema
from modules.entry.services import EntryService
from modules.service_account.dependencies import get_current_service_account
from modules.service_account.models import ServiceAccountModel

router = APIRouter(prefix="/entries", tags=["entries"])
HARDCODED_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("/", response_model=EntrySchema, status_code=status.HTTP_201_CREATED)
async def create_entry(
    data: EntryRequestSchema,
    entry_service: Annotated[EntryService, Depends(get_entry_service)],
):
    return await entry_service.create(user_id=HARDCODED_USER_ID, data=data)


@router.get("/", response_model=Page[EntrySchema])
async def get_entries(
    entry_service: Annotated[EntryService, Depends(get_entry_service)],
    query_params: Annotated[EntryFilterSchema, Query()],
):
    return await entry_service.get_all(HARDCODED_USER_ID, query_params)


@router.post("/telegram", response_model=EntrySchema, status_code=status.HTTP_201_CREATED)
async def create_from_telegram(
    data: TelegramEntryRequestSchema,
    entry_service: Annotated[EntryService, Depends(get_entry_service)],
    service_account: Annotated[ServiceAccountModel, Depends(get_current_service_account)]
):
    return await entry_service.create_from_telegram(data=data, service_account_id=service_account.id)
