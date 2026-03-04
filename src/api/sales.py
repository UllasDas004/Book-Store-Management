from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.db.database import get_db
from src.models.interaction import Sale, CartItem
from src.models.book import Book
from src.models.user import User
from src.schemas.interaction import SaleCreate, SaleResponse, CartItemCreate, CartItemResponse, CartResponse
from src.api.deps import get_current_active_user

router = APIRouter(
    prefix = "/sales",
    tags = ["Sales & Cart"]
)

@router.post("/", response_model = SaleResponse, status_code = status.HTTP_201_CREATED)
async def add_to_cart(cart_item: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Add a book to the cart"""

    book = db.query(Book).filter(Book.id == cart_item.book_id).first()
    if not book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")

    if book.quantity < cart_item.quantity:
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
        if not book or book.quantity < item.quantity:
            db.rollback()
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"Not enough stock available for {item.book.title if item.book else "Unknown"}")
    
        book.quantity -= item.quantity

        sale = Sale(
            user_id = current_user.id,
            book_id = item.book_id,
            quantity = item.quantity,
            total_price = item.book.price * item.quantity
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
