from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
import shutil
import os
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import List, Optional
from src.db.database import get_db
from src.models.book import Book
from src.models.user import User
from src.schemas.book import BookCreate, BookResponse
from src.api.deps import get_current_admin_user


router = APIRouter(
    prefix = "/books",
    tags = ["Books"]
)

from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

@router.get("/", response_model = List[BookResponse])
@limiter.limit("60/minute")
async def get_all_books(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None
):
    """Anyone can view the list of all books."""
    query = db.query(Book)
    if search:
        # Use pg_trgm similarity to handle typos (score > 0.3 is a good starting point)
        query = query.filter(
            or_(
                func.similarity(Book.title, search) > 0.3,
                func.similarity(Book.author, search) > 0.3,
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%"),
                Book.isbn.ilike(f"%{search}%")
            )
        )
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))
        
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)
        
    if sort_by == "price_asc":
        query = query.order_by(Book.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Book.price.desc())
    elif sort_by == "newest":
        query = query.order_by(Book.id.desc())
    elif search:
        # Default order by closest match if search is provided
        query = query.order_by(func.similarity(Book.title, search).desc())
    
    books = query.offset(skip).limit(limit).all()
    return books

@router.get("/{book_id}", response_model = BookResponse)
async def get_single_book(book_id: int,db: Session = Depends(get_db)):
    db_book = db.query(Book).options(joinedload(Book.reviews)).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    return db_book

@router.post("/",response_model = BookResponse, status_code = status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """"Only an Admin can add a new book to the inventory"""

    db_book = db.query(Book).filter(Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Book with this ISBN already exists")
    
    new_book = Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@router.put("/{book_id}", response_model = BookResponse, status_code = status.HTTP_201_CREATED)
async def update_book(
    book_id: int,
    book_update: BookCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Only an admin can update a book"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.model_dump().items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Only an Admin can delete a book"""
    
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    
    db.delete(db_book)
    db.commit()
    return None


@router.post("/{book_id}/cover", response_model = BookResponse)
async def upload_book_cover(
    book_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Only an admin can upload a book cover"""
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid file type")
    
    filename = f"{book_id}_{file.filename.replace(' ','_')}"
    file_path = f"src/static/images/{filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_book.cover_image_url = f"/static/images/{filename}"
    db.commit()
    db.refresh(db_book)
    return db_book