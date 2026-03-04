from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.schemas.book import BookResponse

class CartItemBase(BaseModel):
    book_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    book: BookResponse

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_price: float


class FavouriteBase(BaseModel):
    book_id: int

class FavouriteCreate(FavouriteBase):
    pass

class FavouriteResponse(FavouriteBase):
    id: int
    user_id: int
    book: BookResponse

    class Config:
        from_attributes = True




class SaleBase(BaseModel):
    book_id: int
    quantity: int

class SaleCreate(SaleBase):
    pass

class SaleResponse(SaleBase):
    id: int
    user_id: int
    total_price: float
    status: str
    timestamp: datetime
    book: BookResponse

    class Config:
        from_attributes = True



class RequisitionBase(BaseModel):
    book_id: int
    quantity: int

class RequisitionCreate(RequisitionBase):
    pass

class RequisitionResponse(RequisitionBase):
    id: int
    user_id: int
    book: BookResponse
    status: str
    created_at: datetime

    class Config:
        from_attributes = True



class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    book_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
