from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse
from src.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(
    prefix = "/auth",
    tags = ["Authentication"]
)

@router.post("/register", response_model = UserResponse)
async def user_register(user: UserCreate,db: Session = Depends(get_db)):
    # 1. Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # 2. Hash their password
    hashed_password = get_password_hash(user.password)

    # 3. Create the new user object (don't save the plain password!)
    new_user = User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_password,
        address = user.address,
        phone_number = user.phone_number
        # role defaults to "customer"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
async def user_login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm uses username by default
    # But we are going to expenct the user to tyoe their email into that field

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code = 401, detail = "Incorrect credentials", headers = {"WWW-Authenticate": "Bearer"})

    if not user.is_active:
        raise HTTPException(status_code = 400, detail = "Inactive user")

    access_token = create_access_token(data = {"sub": str(user.id)})
    
    # Set the token in an HTTP-Only cookie to prevent XSS attacks from reading it via JavaScript
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        secure=False, # Set to True in production with HTTPS
        max_age=1800 # 30 minutes
    )
    
    # We still return the JSON so the frontend knows the login succeeded
    return {"access_token": access_token, "token_type": "bearer", "message": "Successfully logged in"}

@router.post("/logout")
async def user_logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}

    
