from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
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
async def get_all_books(db: Session = Depends(get_db)):
    """Anyone can view the list of all books."""
    books = db.query(Book).all()
    return books

@router.get("/{book_id}")
async def get_single_book(book_id: int):
    return {"message": f"Here is the book with id: {book_id}"}

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