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

class BookResponse(BookBase):
    id: int
    stock_quantity: int = Field(default=0, ge=0)
    admin_id: Optional[int] = None
    
    reviews: list["ReviewResponse"] = []

    class Config:
        from_attributes = True

from src.schemas.interaction import ReviewResponse
BookResponse.model_rebuild()