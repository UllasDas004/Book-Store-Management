from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.db.database import get_db
from src.models.interaction import Sale, CartItem
from src.models.book import Book
from src.models.user import User
from src.schemas.interaction import SaleCreate, SaleResponse, CartItemCreate, CartItemResponse, CartResponse
from src.api.deps import get_current_active_user, get_current_admin_user
from pydantic import BaseModel

router = APIRouter(
    prefix = "/sales",
    tags = ["Sales & Cart"]
)

@router.post("/", response_model = CartItemResponse, status_code = status.HTTP_201_CREATED)
async def add_to_cart(cart_item: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Add a book to the cart"""

    book = db.query(Book).filter(Book.id == cart_item.book_id).first()
    if not book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")

    if book.stock_quantity < cart_item.quantity:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Not enough stock available")
    
    existing_item = db.query(CartItem).filter(CartItem.user_id == current_user.id, CartItem.book_id == cart_item.book_id).first()

    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    new_cart_item = CartItem(
        user_id = current_user.id,
        book_id = cart_item.book_id,
        quantity = cart_item.quantity
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item
    

@router.get("/cart", response_model = CartResponse)
async def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all items in the cart"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    total_price = sum(item.book.price * item.quantity for item in cart_items if item.book)
    return CartResponse(items = cart_items, total_price = total_price)


@router.delete("/cart/{item_id}", status_code = status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove an item from the cart"""
    cart_item = db.query(CartItem).filter(CartItem.user_id == current_user.id, CartItem.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Item not found")
    db.delete(cart_item)
    db.commit()


@router.post("/sale", response_model = List[SaleResponse], status_code = status.HTTP_201_CREATED)
async def checkout_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Purchase all items in the cart and reduce the stocks"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Cart is empty")

    sales_records = []

    for item in cart_items:
        book = db.query(Book).filter(Book.id == item.book_id).with_for_update().first()
        if not book or book.stock_quantity < item.quantity:
            db.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"Not enough stock available for {item.book.title if item.book else "Unknown"}")
    
        book.stock_quantity -= item.quantity

        discount_multiplier = (100 - book.discount_percentage) / 100
        discounted_price = book.price * discount_multiplier

        sale = Sale(
            user_id = current_user.id,
            book_id = item.book_id,
            quantity = item.quantity,
            total_price = discounted_price * item.quantity
        )

        db.add(sale)
        sales_records.append(sale)

        db.delete(item)

    db.commit()
    for sale in sales_records:
        db.refresh(sale)
    return sales_records

@router.get("/history", response_model = List[SaleResponse])
async def get_sale_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all sales history for the current user"""
    sales = db.query(Sale).filter(Sale.user_id == current_user.id).all()
    return sales

class CartQuantityUpdate(BaseModel):
    quantity: int

@router.put("/cart/{item_id}", response_model = CartItemResponse)
async def update_cart_quantity(
    item_id: int,
    update_data: CartQuantityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """"Update the exact quantity of a item already in the cart."""
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.id == item_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Item not found")
    
    book = db.query(Book).filter(Book.id == cart_item.book_id).first()

    if book.stock_quantity < update_data.quantity:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Not enough stock available")
    
    if update_data.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        raise HTTPException(status_code = status.HTTP_204_NO_CONTENT)
    
    cart_item.quantity = update_data.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


class SalesStatusUpdate(BaseModel):
    status: str

@router.put("/{sale_id}/status", response_model = SaleResponse)
async def update_sales_status(
    sale_id: int,
    status_update: SalesStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Sale not found")
    
    valid_status = ["Pending", "Shipped", "Delivered", "Cancelled"]
    if status_update.status not in valid_status:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid status")
    
    sale.status = status_update.status
    db.commit()
    db.refresh(sale)
    return sale