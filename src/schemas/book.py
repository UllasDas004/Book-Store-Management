from pydantic import BaseModel, Field
from typing import Optional

class BookBase(BaseModel):
    isbn: str = Field(min_length=4, max_length=10)
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    publisher: str = Field(min_length=1, max_length=255)
    edition: Optional[str] = Field(default=None, max_length=50)
    publication_year: Optional[int] = Field(default=None, ge=1000, le=9999)
    price: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    discount_percentage: Optional[float] = Field(default=0.0, ge=0, le=100)

class BookCreate(BookBase):
    stock_quantity: int = Field(default=0, ge=0)

class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(default=None, min_length=4, max_length=10)
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    publisher: Optional[str] = Field(default=None, min_length=1, max_length=255)
    edition: Optional[str] = Field(default=None, max_length=50)
    publication_year: Optional[int] = Field(default=None, ge=1000, le=9999)
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    stock_quantity: Optional[int] = Field(default=None, ge=0)

class BookResponse(BookBase):
    id: int
    stock_quantity: int = Field(default=0, ge=0)
    admin_id: Optional[int] = None

    class Config:
        from_attributes = True

from src.schemas.interaction import ReviewResponse

class BookDetailResponse(BookResponse):
    reviews: list["ReviewResponse"] = []

    class Config:
        from_attributes = True

BookDetailResponse.model_rebuild()