from fastapi import APIRouter, Depends, status

from modules.entry.dependencies import get_entry_service
from modules.entry.schemas import EntryRequestSchema, EntryResponseSchema
from modules.entry.services import EntryService
from modules.user.dependencies import get_current_user
from modules.user.models import User

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("/", response_model=EntryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_entry(
    data: EntryRequestSchema,
    entry_service: EntryService = Depends(get_entry_service),
    user: User = Depends(get_current_user),
):
    return await entry_service.create(user_id=user.id, data=data)
