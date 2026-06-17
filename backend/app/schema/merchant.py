from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MerchantBase(BaseModel):
    email: EmailStr
    business_name: str = Field(min_length=5, max_length=255)


class MerchantCreate(MerchantBase):
    password: str = Field(min_length=8, max_length=255)


class MerchantOut(MerchantBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
