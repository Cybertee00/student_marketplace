from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, Token, LoginRequest
from services.supabase_auth import supabase_auth, get_supabase_user
from supabase_config import supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user using Supabase Auth"""
    try:
        # Register with Supabase
        result = await supabase_auth.sign_up(
            email=user_data.email,
            password=user_data.password,
            user_data={
                "name": user_data.name,
                "surname": user_data.surname,
                "username": user_data.username,
                "phone": user_data.phone
            }
        )
        
        # Get profile from database (automatically created by trigger)
        profile_response = supabase.table("profiles").select("*").eq("id", result["user"].id).single().execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Profile creation failed"
            )
        
        profile = profile_response.data
        
        return UserResponse(
            id=profile["id"],
            name=profile["name"],
            surname=profile["surname"],
            email=profile["email"],
            phone=profile.get("phone"),
            username=profile["username"],
            profile_img=profile.get("profile_img"),
            created_at=profile["created_at"],
            is_email_verified=profile.get("is_email_verified", False),
            is_phone_verified=profile.get("is_phone_verified", False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login user using Supabase Auth"""
    try:
        # Try email first
        try:
            result = await supabase_auth.sign_in(
                email=login_data.identifier,
                password=login_data.password
            )
            
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token"),
                "token_type": "bearer"
            }
        except:
            # If email fails, try username/phone lookup
            # Query profile to get email
            profile_response = supabase.table("profiles").select("email").or_(
                f"username.eq.{login_data.identifier},phone.eq.{login_data.identifier}"
            ).single().execute()
            
            if not profile_response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            result = await supabase_auth.sign_in(
                email=profile_response.data["email"],
                password=login_data.password
            )
            
            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token"),
                "token_type": "bearer"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user = Depends(get_supabase_user)):
    """Get current user information"""
    try:
        # Extract user ID from Supabase user response
        # Supabase get_user returns UserResponse with .user attribute
        user_id = user.user.id if hasattr(user, 'user') else user.id
        
        # Get profile from Supabase
        profile_response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile = profile_response.data
        
        return UserResponse(
            id=profile["id"],
            name=profile["name"],
            surname=profile["surname"],
            email=profile["email"],
            phone=profile.get("phone"),
            username=profile["username"],
            profile_img=profile.get("profile_img"),
            created_at=profile["created_at"],
            is_email_verified=profile.get("is_email_verified", False),
            is_phone_verified=profile.get("is_phone_verified", False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
