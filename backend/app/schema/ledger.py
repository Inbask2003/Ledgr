from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.model.enums import LedgerDirection


class LedgerEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payment_id: UUID | None
    refund_id: UUID | None
    account: str
    direction: LedgerDirection
    amount: int
    currency: str
    description: str
    created_at: datetime


class LedgerBalance(BaseModel):
    merchant_id: UUID
    currency: str
    balance: int
