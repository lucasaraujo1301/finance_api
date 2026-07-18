from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page

from modules.entry.dependencies import get_entry_service
from modules.entry.schemas import EntryFilterSchema, EntryRequestSchema, EntrySchema
from modules.entry.services import EntryService
from modules.user.dependencies import get_current_user
from modules.user.models import UserModel

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("/", response_model=EntrySchema, status_code=status.HTTP_201_CREATED)
async def create_entry(
    data: EntryRequestSchema,
    entry_service: Annotated[EntryService, Depends(get_entry_service)],
    user: Annotated[UserModel, Depends(get_current_user)],
):
    return await entry_service.create(user_id=user.id, data=data)


@router.get("/", response_model=Page[EntrySchema])
async def get_entries(
    entry_service: Annotated[EntryService, Depends(get_entry_service)],
    user: Annotated[UserModel, Depends(get_current_user)],
    query_params: Annotated[EntryFilterSchema, Query()],
):
    return await entry_service.get_all(user.id, query_params)
