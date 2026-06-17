from fastapi import APIRouter, Depends

from app.schema.auth import AuthBase, TokenOut
from app.core.dependencies import get_merchant_repo
from app.repository.merchant import MerchantRepository
from app.core.security import verify_password, hash_password
from app.core.token import create_access_token
from app.core.exceptions import AuthError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

_DUMMY_HASH = hash_password("ledgr-timing-guard")


@router.post("/login", response_model=TokenOut)
async def login(credentials: AuthBase, repo: MerchantRepository = Depends(get_merchant_repo)):
    merchant = await repo.get_by_email(credentials.email)

    stored_hash = merchant.password_hash if merchant else _DUMMY_HASH
    if not verify_password(credentials.password, stored_hash) or not merchant:
        logger.warning("failed login attempt for %s", credentials.email)
        raise AuthError("Incorrect email or password")

    access_token = create_access_token(merchant.email)
    return TokenOut(access_token=access_token)
