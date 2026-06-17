from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.audit import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(self, merchant_id: UUID | None, method: str, path: str, status_code: int) -> None:
        self.db.add(
            AuditLog(merchant_id=merchant_id, method=method, path=path, status_code=status_code)
        )
        await self.db.commit()

    async def list_for_merchant(
        self, merchant_id: UUID, *, limit: int = 50, offset: int = 0
    ) -> tuple[list[AuditLog], int]:
        base = select(AuditLog).where(AuditLog.merchant_id == merchant_id)
        total = await self.db.scalar(select(func.count()).select_from(base.subquery()))
        stmt = base.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), int(total or 0)
