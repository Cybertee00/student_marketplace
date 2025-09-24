from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, Token, LoginRequest
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from datetime import datetime, timedelta
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) |
        (User.username == user_data.username) |
        (User.phone == user_data.phone)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email, username, or phone already exists"
        )
    
    # Create new user with verification setup
    hashed_password = get_password_hash(user_data.password)
    
    # Generate verification token and OTP
    verification_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    db_user = User(
        name=user_data.name,
        surname=user_data.surname,
        email=user_data.email,
        phone=user_data.phone,
        username=user_data.username,
        password=hashed_password,
        is_email_verified=False,  # New users must verify email
        email_verification_token=verification_token,
        email_verification_expires_at=expires_at
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log verification details for development
    print(f"Development Mode: New user registered - {user_data.email}")
    print(f"Verification token: {verification_token}")
    print(f"Token expires at: {expires_at}")
    
    return db_user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = authenticate_user(db, login_data.identifier, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2FA only applies during registration, not during login
    # Create access token with user ID for WebSocket compatibility
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
