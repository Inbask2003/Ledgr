from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.model.enums import LedgerDirection


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    merchant_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("merchants.id"), index=True, nullable=False
    )
    payment_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("payments.id"), nullable=True
    )
    refund_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("refunds.id"), nullable=True
    )

    account: Mapped[str] = mapped_column(String(32), nullable=False)
    direction: Mapped[LedgerDirection] = mapped_column(String(8), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
