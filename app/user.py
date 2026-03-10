
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import  AsyncSession
from typing import Annotated
from app.auth import verify_access_token, Oauth2_scheme
from app.db import get_async_session , User
from jose import JWTError, jwt
from app.config import settings

async def get_current_user(
    token: str = Depends(Oauth2_scheme), 
    session: AsyncSession = Depends(get_async_session)
):
    credentials_exception = HTTPException(
        status_code= 401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload =verify_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except Exception as e:
        print(f"DEBUG: Auth Error: {e}")
        raise credentials_exception