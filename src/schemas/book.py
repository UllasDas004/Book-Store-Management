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
    cover_image_url: Optional[str] = None
    short_reviews: Optional[str] = None
    stock_quantity: int = Field(default=0, ge=0)

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True