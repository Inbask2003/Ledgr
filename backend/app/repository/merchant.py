from sqlalchemy.ext.asyncio import AsyncSession
from app.model.merchant import Merchant

class MerchantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_merchant(self, merchant: Merchant):
        self.db.add(merchant)
        await self.db.commit()
        await self.db.refresh(merchant)
        return merchant