from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.entry.dependencies import get_entry_service
from modules.entry.schemas import EntryRequestSchema, EntrySchema
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
