from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.model.enums import WebhookStatus


class WebhookEndpointIn(BaseModel):
    url: HttpUrl


class WebhookEndpointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    secret: str
    created_at: datetime
    updated_at: datetime


class WebhookEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    payment_id: UUID | None
    status: WebhookStatus
    attempts: int
    last_error: str | None
    next_attempt_at: datetime
    delivered_at: datetime | None
    created_at: datetime


class WebhookEventPage(BaseModel):
    items: list[WebhookEventOut]
    total: int
    limit: int
    offset: int
