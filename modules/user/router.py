from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.user.dependencies import get_user_service
from modules.user.schemas import CreateUserSchema
from modules.user.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserSchema, user_service: Annotated[UserService, Depends(get_user_service)]):
    return await user_service.create_user(data)
