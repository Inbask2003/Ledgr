from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.enums import WebhookStatus
from app.model.webhook import WebhookEndpoint, WebhookEvent


class WebhookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_endpoint(self, merchant_id: UUID) -> WebhookEndpoint | None:
        stmt = select(WebhookEndpoint).where(WebhookEndpoint.merchant_id == merchant_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save_endpoint(self, endpoint: WebhookEndpoint) -> WebhookEndpoint:
        self.db.add(endpoint)
        await self.db.commit()
        await self.db.refresh(endpoint)
        return endpoint

    async def delete_endpoint(self, endpoint: WebhookEndpoint) -> None:
        await self.db.delete(endpoint)
        await self.db.commit()

    async def add_event(self, event: WebhookEvent) -> WebhookEvent:
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_event(self, merchant_id: UUID, event_id: UUID) -> WebhookEvent | None:
        stmt = select(WebhookEvent).where(
            WebhookEvent.id == event_id, WebhookEvent.merchant_id == merchant_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_events(
        self, merchant_id: UUID, *, limit: int = 50, offset: int = 0
    ) -> tuple[list[WebhookEvent], int]:
        base = select(WebhookEvent).where(WebhookEvent.merchant_id == merchant_id)
        total = await self.db.scalar(
            select(func.count()).select_from(base.subquery())
        )
        stmt = base.order_by(WebhookEvent.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), int(total or 0)

    async def due_events(self, now: datetime, limit: int = 20) -> list[WebhookEvent]:
        stmt = (
            select(WebhookEvent)
            .where(
                WebhookEvent.status == WebhookStatus.PENDING,
                WebhookEvent.next_attempt_at <= now,
            )
            .order_by(WebhookEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def commit(self) -> None:
        await self.db.commit()
