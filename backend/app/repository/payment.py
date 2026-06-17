from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.enums import PaymentStatus
from app.model.payment import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def insert(self, values: dict) -> Payment:
        stmt = pg_insert(Payment).values(**values).returning(Payment.id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return await self.get(values["merchant_id"], result.scalar_one())

    async def insert_if_absent(self, values: dict) -> Payment | None:
        # Race-free idempotency: the database decides the winner. A loser gets no
        # row back (DO NOTHING) and the service falls back to reading the winner.
        stmt = (
            pg_insert(Payment)
            .values(**values)
            .on_conflict_do_nothing(index_elements=["merchant_id", "idempotency_key"])
            .returning(Payment.id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        inserted_id = result.scalar_one_or_none()
        if inserted_id is None:
            return None
        return await self.get(values["merchant_id"], inserted_id)

    async def get(self, merchant_id: UUID, payment_id: UUID) -> Payment | None:
        stmt = select(Payment).where(
            Payment.id == payment_id, Payment.merchant_id == merchant_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, merchant_id: UUID, key: str) -> Payment | None:
        stmt = select(Payment).where(
            Payment.merchant_id == merchant_id, Payment.idempotency_key == key
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        merchant_id: UUID,
        *,
        status: PaymentStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        min_amount: int | None = None,
        max_amount: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Payment], int]:
        filters = [Payment.merchant_id == merchant_id]
        if status is not None:
            filters.append(Payment.status == status)
        if date_from is not None:
            filters.append(Payment.created_at >= date_from)
        if date_to is not None:
            filters.append(Payment.created_at <= date_to)
        if min_amount is not None:
            filters.append(Payment.amount >= min_amount)
        if max_amount is not None:
            filters.append(Payment.amount <= max_amount)

        total = await self.db.scalar(
            select(func.count()).select_from(Payment).where(*filters)
        )

        stmt = (
            select(Payment)
            .where(*filters)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), int(total or 0)

    async def expire_stale(self, cutoff: datetime) -> int:
        stmt = (
            update(Payment)
            .where(Payment.status == PaymentStatus.CREATED, Payment.created_at < cutoff)
            .values(status=PaymentStatus.EXPIRED)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def commit(self) -> None:
        await self.db.commit()

    async def refresh(self, payment: Payment) -> None:
        await self.db.refresh(payment)
