from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.refund import Refund


class RefundRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, refund: Refund) -> Refund:
        self.db.add(refund)
        await self.db.flush()
        return refund

    async def list_for_payment(self, merchant_id: UUID, payment_id: UUID) -> list[Refund]:
        stmt = (
            select(Refund)
            .where(Refund.merchant_id == merchant_id, Refund.payment_id == payment_id)
            .order_by(Refund.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
