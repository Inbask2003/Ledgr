import hashlib
import secrets
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.model.api_key import ApiKey
from app.model.merchant import Merchant
from app.repository.api_key import ApiKeyRepository


def _hash(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


async def create_api_key(
    repo: ApiKeyRepository, merchant: Merchant, name: str
) -> tuple[ApiKey, str]:
    prefix = f"sk_{secrets.token_hex(6)}"
    full_key = f"{prefix}_{secrets.token_hex(24)}"

    api_key = ApiKey(
        merchant_id=merchant.id,
        name=name,
        prefix=prefix,
        key_hash=_hash(full_key),
        last4=full_key[-4:],
    )
    await repo.add(api_key)
    return api_key, full_key


async def resolve_api_key(repo: ApiKeyRepository, raw_key: str) -> ApiKey | None:
    parts = raw_key.split("_")
    if len(parts) != 3 or parts[0] != "sk":
        return None

    api_key = await repo.get_active_by_prefix(f"sk_{parts[1]}")
    if api_key is None:
        return None
    if not secrets.compare_digest(api_key.key_hash, _hash(raw_key)):
        return None
    return api_key


async def revoke_api_key(repo: ApiKeyRepository, merchant: Merchant, key_id: UUID) -> ApiKey:
    api_key = await repo.get(merchant.id, key_id)
    if api_key is None:
        raise NotFoundError("API key not found")
    if api_key.revoked_at is not None:
        return api_key
    return await repo.revoke(api_key)
