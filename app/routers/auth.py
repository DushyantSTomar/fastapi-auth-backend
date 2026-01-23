from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import UserLogin, Token
from app.services import user as user_service
from app.core.security import create_access_token
from app.core.deps import get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    return user_service.create_user(user)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_in: UserLogin):
    user = user_service.authenticate_user(user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(subject=user["email"])
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    return current_user
