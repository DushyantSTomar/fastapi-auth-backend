from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException, status

fake_users_db = []

def get_user_by_email(email: str):
    for user in fake_users_db:
        if user["email"] == email:
            return user
    return None

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_user(user: UserCreate) -> UserResponse:
    if get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    new_user = {
        "id": len(fake_users_db) + 1,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_active": True
    }
    fake_users_db.append(new_user)
    return UserResponse(**new_user)
