from auth.hash_password import HashToken
from database.connection import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from models.users import User
from sqlmodel import select
import uuid

user_router = APIRouter(
    tags=["User"],
)

hash_token = HashToken()


@user_router.post("/signup")
async def sign_user_up(user: User,
                       session=Depends(get_session)) -> dict:
    user_exist = select(User).where(User.username == user.username)
    results = session.exec(user_exist)
    user_exist = results.first()
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username exists."
        )
    token = str(uuid.uuid4())
    hashed_token = hash_token.create_hash(token)
    user.token = hashed_token
    session.add(user)
    session.commit()
    session.refresh(user)
    return {
            "user_id": user.id,
            "token": token
        }
