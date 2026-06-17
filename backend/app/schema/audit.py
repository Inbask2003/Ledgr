from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    method: str
    path: str
    status_code: int
    created_at: datetime


class AuditLogPage(BaseModel):
    items: list[AuditLogOut]
    total: int
    limit: int
    offset: int
