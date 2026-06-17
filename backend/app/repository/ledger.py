from datetime import datetime
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.enums import LedgerAccount, LedgerDirection
from app.model.ledger import LedgerEntry


class LedgerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_entries(self, entries: list[LedgerEntry]) -> None:
        self.db.add_all(entries)
        await self.db.flush()

    async def list(
        self,
        merchant_id: UUID,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[LedgerEntry], int]:
        filters = [LedgerEntry.merchant_id == merchant_id]
        if date_from is not None:
            filters.append(LedgerEntry.created_at >= date_from)
        if date_to is not None:
            filters.append(LedgerEntry.created_at <= date_to)

        total = await self.db.scalar(
            select(func.count()).select_from(LedgerEntry).where(*filters)
        )

        stmt = (
            select(LedgerEntry)
            .where(*filters)
            .order_by(LedgerEntry.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), int(total or 0)

    async def balance(self, merchant_id: UUID, currency: str = "INR") -> int:
        signed = func.sum(
            case(
                (LedgerEntry.direction == LedgerDirection.CREDIT, LedgerEntry.amount),
                else_=-LedgerEntry.amount,
            )
        )
        stmt = select(signed).where(
            LedgerEntry.merchant_id == merchant_id,
            LedgerEntry.account == LedgerAccount.MERCHANT_BALANCE,
            LedgerEntry.currency == currency,
        )
        return int(await self.db.scalar(stmt) or 0)
