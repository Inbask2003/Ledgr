from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.model.enums import PaymentStatus


class PaymentCreate(BaseModel):
    amount: int = Field(gt=0, description="Amount in paise")
    currency: Literal["INR"] = "INR"
    description: str | None = Field(default=None, max_length=500)
    idempotency_key: str | None = Field(default=None, max_length=255)


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    merchant_id: UUID
    amount: int
    amount_refunded: int
    currency: str
    description: str | None
    status: PaymentStatus
    failure_reason: str | None
    created_at: datetime
    captured_at: datetime | None


class PaymentPage(BaseModel):
    items: list[PaymentOut]
    total: int
    limit: int
    offset: int
