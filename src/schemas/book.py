from pydantic import BaseModel, Field
from typing import Optional

class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    edition: Optional[str] = None
    publication_year: Optional[int] = None
    price: float = Field(gt=0)
    category: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    discount_percentage: Optional[float] = Field(default=0.0, ge=0, le=100)

class BookCreate(BookBase):
    stock_quantity: int = Field(default=0, ge=0)

class BookUpdate(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    edition: Optional[str] = None
    publication_year: Optional[int] = None
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
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