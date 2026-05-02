from pydantic import BaseModel, EmailStr, Field

class MerchantBase(BaseModel):
    email: EmailStr
    business_name : str = Field(min_length=5, max_length=255)

class MerchantCreate(MerchantBase):
    password: str = Field(min_length=8, max_length=255)