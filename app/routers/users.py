from typing import Annotated
from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    return current_user
