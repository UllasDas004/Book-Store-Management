from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.user import User
from src.schemas.user import UserResponse, UserUpdate, UserPasswordUpdate
from src.api.deps import get_current_active_user, get_current_admin_user
from src.core.security import verify_password, get_password_hash
router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)

@router.get("/me", response_model = UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model = UserResponse)
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_active_user),db: Session = Depends(get_db)):
    update_data = user_update.model_dump(exclude_unset = True)

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password", status_code=status.HTTP_200_OK)
async def update_password(
    password_data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}

@router.delete("/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "You cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    db.delete(user)
    db.commit()
    return