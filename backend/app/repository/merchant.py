from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.merchant import Merchant


class MerchantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_merchant(self, merchant: Merchant) -> Merchant:
        self.db.add(merchant)
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant

    async def get_by_email(self, email: str) -> Merchant | None:
        stmt = select(Merchant).where(Merchant.email == email, Merchant.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, merchant_id) -> Merchant | None:
        stmt = select(Merchant).where(Merchant.id == merchant_id, Merchant.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
