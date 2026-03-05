from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta, timezone
from src.db.database import get_db
from src.models.requisition import Requisition
from src.models.book import Book
from src.models.interaction import Sale
from src.models.user import User
from src.schemas.interaction import RequisitionCreate, RequisitionResponse
from src.api.deps import get_current_admin_user

router = APIRouter(
    prefix = "/requisitions",
    tags = ["Requisitions (Admin Only)"]
)

@router.post("/", response_model = RequisitionResponse, status_code = status.HTTP_201_CREATED)
async def create_requisitions(
    req_data: RequisitionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    book = db.query(Book).filter(Book.id == req_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Book not found"
        )
    if req_data.quantity <= 0:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Quantity must be greater than 0"
        )

    new_req = Requisition(
        user_id = current_admin.id,
        book_id = req_data.book_id,
        quantity = req_data.quantity,
        status = "pending"
    )

    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return new_req


@router.post("/auto", response_model=List[RequisitionResponse], status_code=status.HTTP_201_CREATED)
async def auto_generate_requisitions(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Admin Only: Auto-generate requisitions based on low stock and last 3 months of sales."""
    
    # Threshold for low stock
    LOW_STOCK_THRESHOLD = 10
    
    # Date 3 months ago
    three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
    
    # 1. Find all books with stock < 10
    low_stock_books = db.query(Book).filter(Book.stock_quantity < LOW_STOCK_THRESHOLD).all()
    
    generated_requisitions = []
    
    for book in low_stock_books:
        # Check if there is already a pending requisition for this book
        existing_req = db.query(Requisition).filter(
            Requisition.book_id == book.id,
            Requisition.status == "pending"
        ).first()
        
        if existing_req:
            continue # We already have a pending order for this book!
        
        # Calculate how many of this book sold in the last 3 months
        sales_data = db.query(func.sum(Sale.quantity)).filter(
            Sale.book_id == book.id,
            Sale.timestamp >= three_months_ago
        ).scalar()
        
        # If it sold well, order that many. If not, order a default of 10.
        quantity_to_order = sales_data if sales_data and sales_data > 0 else 10
        
        new_req = Requisition(
            user_id=current_admin.id,
            book_id=book.id,
            quantity=quantity_to_order,
            status="pending"
        )
        
        db.add(new_req)
        generated_requisitions.append(new_req)
        
    db.commit()
    
    for req in generated_requisitions:
        db.refresh(req)
        
    return generated_requisitions


@router.get("/", response_model = List[RequisitionResponse])
async def get_all_requisitions(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    return db.query(Requisition).all()


@router.put("/{req_id}/receive", response_model = RequisitionResponse)
async def receive_requisition(
    req_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    req = db.query(Requisition).filter(Requisition.id == req_id).first()
    if not req:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Requisition not found"
        )
    if req.status == "completed":
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Requisition is already completed"
        )
    
    book = db.query(Book).filter(Book.id == req.book_id).with_for_update().first()
    book.stock_quantity += req.quantity

    req.status = "completed"
    
    db.commit()
    db.refresh(req)
    return req