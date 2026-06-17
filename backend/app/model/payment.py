from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.model.enums import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("merchant_id", "idempotency_key", name="uq_payment_merchant_idempotency"),
    )

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    merchant_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("merchants.id"), index=True, nullable=False
    )

    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount_refunded: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[PaymentStatus] = mapped_column(
        String(32), default=PaymentStatus.CREATED, index=True, nullable=False
    )
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
