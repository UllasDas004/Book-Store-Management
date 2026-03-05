from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError 
from sqlalchemy.orm import Session
from src.core.config import settings
from src.db.database import get_db
from src.models.user import User

# We set auto_error=False so it doesn't immediately fail if the Authorization header is missing.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_token_from_header_or_cookie(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> str:
    # 1. If the token is manually passed in the Authorization header (e.g. Swagger UI), use it.
    if token:
        return token
    
    # 2. Otherwise, look for the 'access_token' cookie set by the backend.
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        # Our cookie stores it as "Bearer <token>", so we strip the prefix.
        if cookie_token.startswith("Bearer "):
            return cookie_token.split(" ")[1]
        return cookie_token
        
    # 3. If neither header nor cookie is present, raise 401 Unauthorized.
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Not authenticated",
        headers = {"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(token: str = Depends(get_token_from_header_or_cookie), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code = 400, detail = "Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "The user doesn't have enough privileges")
    return current_user