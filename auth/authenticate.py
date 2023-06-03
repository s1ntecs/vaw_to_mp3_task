from fastapi import Depends, HTTPException, status
from database.connection import get_session
from models.users import User
from auth.hash_password import HashToken

hash_token = HashToken()


async def authenticate(token: str,
                       user_id: int,
                       session=Depends(get_session)) -> bool:
    user_exist = session.get(User, user_id)
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id = {user_id} does not exist."
        )
    if not hash_token.verify_hash(token, user_exist.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token."
        )
