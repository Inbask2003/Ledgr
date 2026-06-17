from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthError
from app.core.token import verify_access_token
from app.db.session import get_db
from app.model.merchant import Merchant
from app.repository.merchant import MerchantRepository
from app.repository.payment import PaymentRepository
from app.repository.ledger import LedgerRepository
from app.repository.refund import RefundRepository
from app.repository.api_key import ApiKeyRepository
from app.repository.webhook import WebhookRepository
from app.repository.audit import AuditRepository
from app.service.api_key import resolve_api_key

security = HTTPBearer(auto_error=False)


def get_merchant_repo(db: AsyncSession = Depends(get_db)) -> MerchantRepository:
    return MerchantRepository(db)


def get_payment_repo(db: AsyncSession = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(db)


def get_ledger_repo(db: AsyncSession = Depends(get_db)) -> LedgerRepository:
    return LedgerRepository(db)


def get_refund_repo(db: AsyncSession = Depends(get_db)) -> RefundRepository:
    return RefundRepository(db)


def get_api_key_repo(db: AsyncSession = Depends(get_db)) -> ApiKeyRepository:
    return ApiKeyRepository(db)


def get_webhook_repo(db: AsyncSession = Depends(get_db)) -> WebhookRepository:
    return WebhookRepository(db)


def get_audit_repo(db: AsyncSession = Depends(get_db)) -> AuditRepository:
    return AuditRepository(db)


async def get_current_merchant(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    repo: MerchantRepository = Depends(get_merchant_repo),
    api_key_repo: ApiKeyRepository = Depends(get_api_key_repo),
) -> Merchant:
    if credentials is None:
        raise AuthError("Missing authentication credentials")

    token = credentials.credentials

    if token.startswith("sk_"):
        api_key = await resolve_api_key(api_key_repo, token)
        if api_key is None:
            raise AuthError("Invalid API key")
        merchant = await repo.get_by_id(api_key.merchant_id)
    else:
        payload = verify_access_token(token)
        if payload is None:
            raise AuthError("Invalid or expired token")
        email = payload.get("sub")
        if not email:
            raise AuthError("Malformed token")
        merchant = await repo.get_by_email(email)

    if merchant is None or not merchant.is_active:
        raise AuthError("Merchant account is not active")

    request.state.merchant_id = merchant.id
    return merchant
