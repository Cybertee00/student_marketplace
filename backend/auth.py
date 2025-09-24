from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import TokenData
from config import get_jwt_secret_key, get_jwt_algorithm, get_jwt_expire_minutes

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=get_jwt_expire_minutes())
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_jwt_secret_key(), algorithm=get_jwt_algorithm())
    return encoded_jwt

def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=[get_jwt_algorithm()])
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        
        # Check if sub is a numeric user ID or username
        try:
            user_id = int(sub)
            token_data = TokenData(user_id=user_id)
        except ValueError:
            # If not numeric, treat as username
            token_data = TokenData(username=sub)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    token_data = verify_token(token, credentials_exception)
    
    # Find user by user_id or username/email/phone
    if token_data.user_id is not None:
        user = db.query(User).filter(User.id == token_data.user_id).first()
    else:
        user = db.query(User).filter(
            (User.username == token_data.username) |
            (User.email == token_data.username) |
            (User.phone == token_data.username)
        ).first()
    
    if user is None:
        raise credentials_exception
    return user

def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    """Authenticate a user by identifier (username, email, or phone) and password."""
    # Find user by identifier
    user = db.query(User).filter(
        (User.username == identifier) |
        (User.email == identifier) |
        (User.phone == identifier)
    ).first()
    
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

async def get_current_user_websocket(token: str) -> User:
    """Get current user from WebSocket token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=[get_jwt_algorithm()])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except (JWTError, ValueError):
        raise credentials_exception
    
    # Get database session
    db = next(get_db())
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user