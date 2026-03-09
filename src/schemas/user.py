from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Base fields all users share
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    address: Optional[str] = Field(default=None, min_length=3, max_length=200)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=15)

# What we expect when they create an account (Register)
class UserCreate(UserBase):
    password: str = Field(min_length=8)

# What we send back to the client (Notice we NEVER send the password back!)
class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, min_length=3, max_length=200)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=15)

class UserPasswordUpdate(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class TopVendorResponse(BaseModel):
    admin_id: int
    username: str
    total_books_sold: int

    class Config:
        from_attributes = True