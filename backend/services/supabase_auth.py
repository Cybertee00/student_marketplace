"""
Supabase Authentication Service
Handles all authentication operations using Supabase Auth
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from supabase import Client
from supabase_config import supabase, supabase_admin
from typing import Optional
from datetime import datetime

class SupabaseAuthService:
    """Service for handling Supabase authentication"""
    
    def __init__(self):
        self.client = supabase
        self.admin_client = supabase_admin
    
    async def sign_up(
        self, 
        email: str, 
        password: str, 
        user_data: dict
    ) -> dict:
        """
        Register new user with Supabase Auth
        
        Args:
            email: User email
            password: User password
            user_data: Additional user metadata (name, surname, username, phone)
        
        Returns:
            Dictionary with user and session
        """
        try:
            # Sign up with Supabase Auth
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": user_data.get("name"),
                        "surname": user_data.get("surname"),
                        "username": user_data.get("username"),
                        "phone": user_data.get("phone")
                    }
                }
            })
            
            if response.user:
                return {
                    "user": response.user,
                    "session": response.session
                }
            else:
                raise HTTPException(status_code=400, detail="Registration failed")
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def sign_in(self, email: str, password: str) -> dict:
        """
        Sign in user with Supabase Auth
        
        Args:
            email: User email
            password: User password
        
        Returns:
            Dictionary with access_token, refresh_token, and user
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.session:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": response.user
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    async def get_user(self, token: str):
        """
        Get user from Supabase token
        
        Args:
            token: JWT access token
        
        Returns:
            User object
        """
        try:
            # Verify token and get user
            user = self.client.auth.get_user(token)
            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def sign_out(self, token: str) -> dict:
        """
        Sign out user
        
        Args:
            token: JWT access token
        
        Returns:
            Success message
        """
        try:
            self.client.auth.set_session(token)
            self.client.auth.sign_out()
            return {"message": "Signed out successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            New access token and refresh token
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

# Create instance
supabase_auth = SupabaseAuthService()

# Dependency to extract bearer token
security = HTTPBearer()

def get_bearer_token(authorization: str = Depends(security)):
    """Extract bearer token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return authorization.credentials

# Dependency to get current user from token
async def get_supabase_user(token: str = Depends(get_bearer_token)):
    """Get current user from Supabase token"""
    try:
        user = await supabase_auth.get_user(token)
        return user
    except:
        raise HTTPException(status_code=401, detail="Not authenticated")

