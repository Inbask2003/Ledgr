import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
from app.core.config import settings


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire_time = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire_time, "iat": now}

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_access_token(access_token: str) -> dict | None:
    try:
        return jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError:
        return None
