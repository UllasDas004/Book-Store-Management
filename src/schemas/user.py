from pydantic import BaseModel, EmailStr
from typing import Optional

# Base fields all users share
class UserBase(BaseModel):
    username: str
    email: EmailStr
    address: Optional[str] = None
    phone_number: Optional[str] = None

# What we expect when they create an account (Register)
class UserCreate(UserBase):
    password: str

# What we send back to the client (Notice we NEVER send the password back!)
class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True
