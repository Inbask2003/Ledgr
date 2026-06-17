from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("payments.id"), index=True, nullable=False
    )
    merchant_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("merchants.id"), index=True, nullable=False
    )

    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
