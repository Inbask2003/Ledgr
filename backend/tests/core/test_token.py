import jwt
from datetime import datetime, timezone, timedelta

from app.core import token
from app.core.config import settings


def test_token_roundtrip():
    access_token = token.create_access_token("priya@example.com")
    payload = token.verify_access_token(access_token)

    assert payload is not None
    assert payload["sub"] == "priya@example.com"


def test_verify_rejects_garbage():
    assert token.verify_access_token("not-a-real-token") is None


def test_verify_rejects_expired():
    expired = jwt.encode(
        {
            "sub": "karthik@example.com",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    assert token.verify_access_token(expired) is None
