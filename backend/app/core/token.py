import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
from app.core.config import settings


async def create_access_token(email: str):
    issued_time = datetime.now(timezone.utc)
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": email, "exp": expire_time,"iat":issued_time}

    access_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return access_token

async def verify_access_token(access_token: str):
    try:
        payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=settings.jwt_algorithm)
        return payload
    except InvalidTokenError:
        return None
