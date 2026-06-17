from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.api_key import ApiKey


class ApiKeyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, api_key: ApiKey) -> ApiKey:
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def list_for_merchant(self, merchant_id: UUID) -> list[ApiKey]:
        stmt = (
            select(ApiKey)
            .where(ApiKey.merchant_id == merchant_id)
            .order_by(ApiKey.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_by_prefix(self, prefix: str) -> ApiKey | None:
        stmt = select(ApiKey).where(ApiKey.prefix == prefix, ApiKey.revoked_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get(self, merchant_id: UUID, key_id: UUID) -> ApiKey | None:
        stmt = select(ApiKey).where(ApiKey.id == key_id, ApiKey.merchant_id == merchant_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, api_key: ApiKey) -> ApiKey:
        api_key.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key
