from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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

@router.get("/", response_model = List[BookResponse])
async def get_all_books(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    category: Optional[str] = None
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
        # Order by closest match
        query = query.order_by(func.similarity(Book.title, search).desc())
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))
    
    books = query.offset(skip).limit(limit).all()
    return books

@router.get("/{book_id}")
async def get_single_book(book_id: int,db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
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