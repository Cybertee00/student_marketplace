from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime
from database import get_db
from models import User
from schemas import UserResponse, ProfileUpdateRequest, PasswordChangeRequest
from auth import get_current_user, verify_password, get_password_hash
from routers.images import save_uploaded_file

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile information."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information."""
    # Update allowed fields
    if profile_data.name is not None:
        current_user.name = profile_data.name
    if profile_data.surname is not None:
        current_user.surname = profile_data.surname
    if profile_data.phone is not None:
        # Check if phone is already taken by another user
        existing_user = db.query(User).filter(
            User.phone == profile_data.phone,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        current_user.phone = profile_data.phone
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/upload-picture")
def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture for current user."""
    print(f"Profile picture upload request from user {current_user.username}")
    print(f"File: {file.filename}, Size: {file.size}, Content-Type: {file.content_type}")
    
    # Validate file type - check both content_type and filename extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    is_valid_content_type = file.content_type and file.content_type.startswith('image/')
    is_valid_extension = file.filename and any(file.filename.lower().endswith(ext) for ext in allowed_extensions)
    
    if not (is_valid_content_type or is_valid_extension):
        print(f"Invalid file type: content_type={file.content_type}, filename={file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (jpg, jpeg, png, gif, bmp, webp)"
        )
    
    # Validate file size (max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        print(f"File too large: {file.size} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    try:
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1].lower()
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{unique_id}{ext}"
        
        # Save to local storage
        profile_dir = "profile_pictures"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        
        filename = save_uploaded_file(file, profile_dir)
        file_url = f"/images/profile/{filename}"
        
        # Update user's profile picture with filename
        current_user.profile_img = filename
        db.commit()
        
        print(f"Profile picture saved locally: {filename}")
        return {
            "message": "Profile picture uploaded successfully (local storage)",
            "profile_picture": filename,
            "public_url": file_url
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload profile picture: {str(e)}"
        )

@router.delete("/remove-picture")
def remove_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove current user's profile picture."""
    try:
        # Remove the old profile picture file if it exists
        if current_user.profile_img:
            old_file_path = os.path.join("profile_pictures", current_user.profile_img)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # Clear the profile picture field
        current_user.profile_img = None
        db.commit()
        
        return {"message": "Profile picture removed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove profile picture: {str(e)}"
        )

@router.post("/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Hash new password and update
    current_user.password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
