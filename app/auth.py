from datetime import UTC, datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.config import settings

hasher = PasswordHash.recommended()

Oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/User/token")

def hash_password(password: str):
    return hasher.hash(password)

def verify_password(plain_password: str, password_hash: str):
    return hasher.verify(plain_password,password_hash)

def create_access_token(data: dict, expire_delta: timedelta | None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(UTC) + expire_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes = settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm= settings.algorithm
    )
    return encode_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        if isinstance(payload, str):
            import json
            payload = json.loads(payload)

        return payload

    except (JWTError, AttributeError) as e: 
        return None
        