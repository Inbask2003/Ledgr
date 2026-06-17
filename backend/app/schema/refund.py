from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RefundCreate(BaseModel):
    amount: int | None = Field(default=None, gt=0, description="Amount in paise; omit for a full refund")
    reason: str | None = Field(default=None, max_length=255)


class RefundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payment_id: UUID
    amount: int
    currency: str
    reason: str | None
    created_at: datetime
