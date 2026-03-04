from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.interaction import Review
from src.models.book import Book
from src.models.user import User
from src.schemas.interaction import ReviewCreate, ReviewResponse
from src.api.deps import get_current_active_user

router = APIRouter(
    prefix = "/books",
    tags = ["Reviews"]
)

@router.post("/{book_id}/reviews",
    response_model = ReviewResponse,
    status_code = status.HTTP_201_CREATED
)
async def add_review(
    book_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Allow a logged in user to leave a review for a book"""

    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Book not found"
        )
    
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Rating must be between 1 and 5"
        )

    existing_review = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.book_id == book_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "You have already reviewed this book"
        )

    new_review = Review(
        book_id = book_id,
        user_id = current_user.id,
        rating = review.rating,
        comment = review.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review