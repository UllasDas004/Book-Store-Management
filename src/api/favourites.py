from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.db.database import get_db
from src.models.interaction import Favourite
from src.models.book import Book
from src.models.user import User
from src.schemas.interaction import FavouriteCreate, FavouriteResponse
from src.api.deps import get_current_active_user

router = APIRouter(
    prefix = "/favourites",
    tags = ["Favourites"]
)

@router.post("/", response_model=FavouriteResponse, status_code=status.HTTP_201_CREATED)
async def create_favourite(
    favourite: FavouriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    book = db.query(Book).filter(Book.id == favourite.book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    existing_fav = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.book_id == favourite.book_id
    ).first()

    if existing_fav:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already added to favourites"
        )
    
    new_fav = Favourite(
        user_id = current_user.id,
        book_id = favourite.book_id
    )

    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)

    return new_fav


@router.get("/", response_model = List[FavouriteResponse])
async def get_favourites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    favourites = db.query(Favourite).filter(Favourite.user_id == current_user.id).all()
    return favourites


@router.delete("/{favourite_id}", status_code = status.HTTP_204_NO_CONTENT)
async def remove_favourite(
    favourite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    existing_fav = db.query(Favourite).filter(
        Favourite.id == favourite_id,
        Favourite.user_id == current_user.id
    ).first()

    if not existing_fav:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favourite not found"
        )
    
    db.delete(existing_fav)
    db.commit()

    return