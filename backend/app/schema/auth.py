from pydantic import BaseModel, EmailStr, Field

class AuthBase(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)